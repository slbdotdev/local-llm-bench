"""A small hand-written text template engine (pure string processing)."""

import sys

try:
    sys.setrecursionlimit(10000)
except Exception:
    pass


class TemplateError(Exception):
    def __init__(self, kind, pos):
        super().__init__("%s at %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


class Undefined(object):
    __slots__ = ()

    def __repr__(self):
        return "Undefined"


UNDEFINED = Undefined()

WS_CHARS = " \t\r\n\v\f"

KEYWORDS = {"true", "false", "none", "not", "and", "or", "in"}

FILTERS_ARITY = {
    "upper": 0,
    "lower": 0,
    "trim": 0,
    "length": 0,
    "first": 0,
    "safe": 0,
    "escape": 0,
    "default": 1,
    "join": 1,
    "replace": 2,
    "slice": 2,
}

ESCAPE_MAP = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&#34;", "'": "&#39;"}

CONTINUATION_NAMES = {"else", "elif", "endif", "empty", "endfor"}
NODE_NAMES = {"if", "for", "set"}
ALLOWED_NAMES = CONTINUATION_NAMES | NODE_NAMES


# ---------------------------------------------------------------------------
# small char helpers
# ---------------------------------------------------------------------------

def is_alpha(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def is_digit(c):
    return "0" <= c <= "9"


def is_alnum_(c):
    return is_alpha(c) or is_digit(c) or c == "_"


def custom_strip(s):
    i = 0
    j = len(s)
    while i < j and s[i] in WS_CHARS:
        i += 1
    while j > i and s[j - 1] in WS_CHARS:
        j -= 1
    return s[i:j]


# ---------------------------------------------------------------------------
# Lexing
# ---------------------------------------------------------------------------

OPENERS = {"{{": "}}", "{%": "%}", "{#": "#}"}
KIND_OF_OPENER = {"{{": "interp", "{%": "block", "{#": "comment"}


def lex(source):
    n = len(source)
    i = 0
    items = []
    text_start = 0
    while i < n:
        c = source[i]
        if c == "{" and i + 1 < n and source[i + 1] in "{%#":
            opener = source[i:i + 2]
            closer = OPENERS[opener]
            kind = KIND_OF_OPENER[opener]
            if i > text_start:
                items.append({"type": "text", "raw": source[text_start:i]})
            open_pos = i
            search_start = i + 2
            left_marker = False
            if search_start < n and source[search_start] == "-":
                left_marker = True
                search_start += 1
            closer_pos = source.find(closer, search_start)
            if closer_pos == -1:
                raise TemplateError("unclosed_tag", open_pos)
            right_marker = False
            body_end = closer_pos
            if closer_pos > search_start and source[closer_pos - 1] == "-":
                right_marker = True
                body_end = closer_pos - 1
            body = source[search_start:body_end]
            tag_end = closer_pos + len(closer)
            items.append({
                "type": kind,
                "pos": open_pos,
                "body": body,
                "left": left_marker,
                "right": right_marker,
            })
            i = tag_end
            text_start = i
            continue
        i += 1
    if n > text_start:
        items.append({"type": "text", "raw": source[text_start:n]})
    return items


def apply_trim(items):
    result = []
    m = len(items)
    for idx, it in enumerate(items):
        if it["type"] != "text":
            result.append(it)
            continue
        s = it["raw"]
        prev = items[idx - 1] if idx - 1 >= 0 else None
        nxt = items[idx + 1] if idx + 1 < m else None
        if prev is not None and prev["type"] != "text" and prev.get("right"):
            k = 0
            while k < len(s) and s[k] in WS_CHARS:
                k += 1
            s = s[k:]
        if nxt is not None and nxt["type"] != "text" and nxt.get("left"):
            k = len(s)
            while k > 0 and s[k - 1] in WS_CHARS:
                k -= 1
            s = s[:k]
        result.append({"type": "text", "value": s})
    return result


def tokenize(source):
    items = lex(source)
    trimmed = apply_trim(items)
    tokens = [it for it in trimmed if it["type"] in ("text", "interp", "block")]
    return tokens


# ---------------------------------------------------------------------------
# Expression parsing
# ---------------------------------------------------------------------------

class ExprParser(object):
    def __init__(self, s, tag_pos):
        self.s = s
        self.n = len(s)
        self.i = 0
        self.tag_pos = tag_pos

    def err(self, kind="syntax"):
        raise TemplateError(kind, self.tag_pos)

    def skip_ws(self):
        while self.i < self.n and self.s[self.i] in WS_CHARS:
            self.i += 1

    def read_ident_raw(self):
        if self.i < self.n and (is_alpha(self.s[self.i]) or self.s[self.i] == "_"):
            start = self.i
            self.i += 1
            while self.i < self.n and is_alnum_(self.s[self.i]):
                self.i += 1
            return self.s[start:self.i]
        return None

    def match_keyword(self, kw):
        save = self.i
        ident = self.read_ident_raw()
        if ident == kw:
            return True
        self.i = save
        return False

    def read_string(self):
        quote = self.s[self.i]
        self.i += 1
        out = []
        while True:
            if self.i >= self.n:
                self.err("syntax")
            c = self.s[self.i]
            if c == quote:
                self.i += 1
                return "".join(out)
            if c == "\\":
                self.i += 1
                if self.i >= self.n:
                    self.err("syntax")
                e = self.s[self.i]
                if e == "n":
                    out.append("\n")
                elif e == "t":
                    out.append("\t")
                else:
                    out.append(e)
                self.i += 1
            else:
                out.append(c)
                self.i += 1

    def read_key_after_dot(self):
        ident = self.read_ident_raw()
        if ident is not None:
            return ident
        start = self.i
        while self.i < self.n and is_digit(self.s[self.i]):
            self.i += 1
        if self.i > start:
            return self.s[start:self.i]
        self.err("syntax")

    # ---- grammar ----

    def parse_atom(self):
        self.skip_ws()
        if self.i >= self.n:
            self.err("syntax")
        c = self.s[self.i]
        if is_digit(c):
            start = self.i
            while self.i < self.n and is_digit(self.s[self.i]):
                self.i += 1
            return ("int", int(self.s[start:self.i]))
        if c == '"' or c == "'":
            return ("str", self.read_string())
        save = self.i
        ident = self.read_ident_raw()
        if ident is not None:
            if ident == "true":
                return ("bool", True)
            if ident == "false":
                return ("bool", False)
            if ident == "none":
                return ("none",)
            if ident in ("not", "and", "or", "in"):
                self.i = save
                self.err("syntax")
            return ("var", ident)
        self.err("syntax")

    def parse_primary(self):
        self.skip_ws()
        node = self.parse_atom()
        while True:
            save = self.i
            self.skip_ws()
            if self.i < self.n and self.s[self.i] == ".":
                self.i += 1
                self.skip_ws()
                key = self.read_key_after_dot()
                node = ("lookup", node, ("str", key))
                continue
            if self.i < self.n and self.s[self.i] == "[":
                self.i += 1
                self.skip_ws()
                key_ast = self.parse_primary()
                self.skip_ws()
                if self.i < self.n and self.s[self.i] == "]":
                    self.i += 1
                else:
                    self.err("syntax")
                node = ("lookup", node, key_ast)
                continue
            self.i = save
            break
        return node

    def try_match_cmpop(self):
        for sym in ("==", "!=", "<=", ">="):
            if self.s[self.i:self.i + 2] == sym:
                self.i += 2
                return sym
        if self.i < self.n and self.s[self.i] in ("<", ">"):
            op = self.s[self.i]
            self.i += 1
            return op
        if self.match_keyword("in"):
            return "in"
        return None

    def parse_comparison(self):
        left = self.parse_primary()
        self.skip_ws()
        op = self.try_match_cmpop()
        if op is None:
            return left
        self.skip_ws()
        right = self.parse_primary()
        self.skip_ws()
        op2 = self.try_match_cmpop()
        if op2 is not None:
            self.err("syntax")
        return ("cmp", op, left, right)

    def parse_negation(self):
        self.skip_ws()
        if self.match_keyword("not"):
            self.skip_ws()
            operand = self.parse_negation()
            return ("not", operand)
        return self.parse_comparison()

    def parse_conjunct(self):
        left = self.parse_negation()
        parts = [left]
        while True:
            self.skip_ws()
            if self.match_keyword("and"):
                self.skip_ws()
                parts.append(self.parse_negation())
            else:
                break
        if len(parts) == 1:
            return parts[0]
        return ("and", parts)

    def parse_disjunct(self):
        left = self.parse_conjunct()
        parts = [left]
        while True:
            self.skip_ws()
            if self.match_keyword("or"):
                self.skip_ws()
                parts.append(self.parse_conjunct())
            else:
                break
        if len(parts) == 1:
            return parts[0]
        return ("or", parts)

    def parse_filter_args(self):
        args = []
        while True:
            self.skip_ws()
            val = self.parse_one_arg()
            args.append(val)
            self.skip_ws()
            if self.i < self.n and self.s[self.i] == ",":
                self.i += 1
                continue
            else:
                break
        return args

    def parse_one_arg(self):
        c = self.s[self.i] if self.i < self.n else ""
        if c == '"' or c == "'":
            s = self.read_string()
            self.skip_ws()
            nxt = self.s[self.i] if self.i < self.n else ""
            if nxt == "" or nxt == "," or nxt == "|":
                return s
            self.err("syntax")
        else:
            start = self.i
            while self.i < self.n and self.s[self.i] not in (",", "|"):
                self.i += 1
            raw = self.s[start:self.i]
            text = custom_strip(raw)
            if len(text) > 0 and all(ch in "0123456789" for ch in text):
                return int(text)
            if text == "true":
                return True
            if text == "false":
                return False
            if text == "none":
                return None
            return text

    def parse_filter(self):
        self.skip_ws()
        name = self.read_ident_raw()
        if name is None:
            self.err("syntax")
        if name not in FILTERS_ARITY:
            self.err("unknown_filter")
        self.skip_ws()
        args = []
        if self.i < self.n and self.s[self.i] == ":":
            self.i += 1
            args = self.parse_filter_args()
        self.skip_ws()
        if not (self.i == self.n or (self.i < self.n and self.s[self.i] == "|")):
            self.err("syntax")
        if len(args) != FILTERS_ARITY[name]:
            self.err("filter_args")
        return (name, args)

    def parse_top(self, allow_filters):
        node = self.parse_disjunct()
        if allow_filters:
            self.skip_ws()
            filters = []
            while self.i < self.n and self.s[self.i] == "|":
                self.i += 1
                f = self.parse_filter()
                filters.append(f)
                self.skip_ws()
            if filters:
                node = ("pipeline", node, filters)
        return node


def parse_expr_full(text, tag_pos, allow_filters):
    p = ExprParser(text, tag_pos)
    node = p.parse_top(allow_filters)
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError("syntax", tag_pos)
    return node


def parse_for_rest(rest, tag_pos):
    p = ExprParser(rest, tag_pos)
    p.skip_ws()
    name = p.read_ident_raw()
    if name is None or name in KEYWORDS:
        raise TemplateError("syntax", tag_pos)
    p.skip_ws()
    if not p.match_keyword("in"):
        raise TemplateError("syntax", tag_pos)
    p.skip_ws()
    if p.i >= p.n:
        raise TemplateError("syntax", tag_pos)
    expr_ast = p.parse_top(True)
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError("syntax", tag_pos)
    return name, expr_ast


def parse_set_rest(rest, tag_pos):
    p = ExprParser(rest, tag_pos)
    p.skip_ws()
    name = p.read_ident_raw()
    if name is None or name in KEYWORDS:
        raise TemplateError("syntax", tag_pos)
    p.skip_ws()
    if p.i < p.n and p.s[p.i] == "=" and not (p.i + 1 < p.n and p.s[p.i + 1] == "="):
        p.i += 1
    else:
        raise TemplateError("syntax", tag_pos)
    p.skip_ws()
    if p.i >= p.n:
        raise TemplateError("syntax", tag_pos)
    expr_ast = p.parse_top(True)
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError("syntax", tag_pos)
    return name, expr_ast


# ---------------------------------------------------------------------------
# Parsing (token stream -> node tree)
# ---------------------------------------------------------------------------

def split_name_rest(body):
    i = 0
    n = len(body)
    while i < n and body[i] not in WS_CHARS:
        i += 1
    name = body[:i]
    j = i
    while j < n and body[j] in WS_CHARS:
        j += 1
    rest = body[j:]
    return name, rest


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        self.n = len(tokens)

    def cur(self):
        return self.tokens[self.idx] if self.idx < self.n else None

    def parse_seq(self, stop_names):
        nodes = []
        while True:
            tok = self.cur()
            if tok is None:
                return nodes, None
            if tok["type"] == "text":
                nodes.append(("text", tok["value"]))
                self.idx += 1
                continue
            if tok["type"] == "interp":
                body = custom_strip(tok["body"])
                if body == "":
                    raise TemplateError("syntax", tok["pos"])
                ast = parse_expr_full(body, tok["pos"], True)
                nodes.append(("interp", ast, tok["pos"]))
                self.idx += 1
                continue
            # block tag
            body = custom_strip(tok["body"])
            if body == "":
                raise TemplateError("unknown_tag", tok["pos"])
            name, rest = split_name_rest(body)
            if name not in ALLOWED_NAMES:
                raise TemplateError("unknown_tag", tok["pos"])
            if name in stop_names:
                return nodes, (name, rest, tok["pos"])
            if name in CONTINUATION_NAMES:
                raise TemplateError("unexpected_tag", tok["pos"])
            if name == "if":
                node = self.parse_if(tok["pos"], rest)
            elif name == "for":
                node = self.parse_for(tok["pos"], rest)
            else:
                pname, pexpr = parse_set_rest(rest, tok["pos"])
                node = ("set", pname, pexpr, tok["pos"])
                self.idx += 1
            nodes.append(node)

    def parse_if(self, if_pos, rest):
        self.idx += 1
        if rest == "":
            raise TemplateError("syntax", if_pos)
        cond_ast = parse_expr_full(rest, if_pos, False)
        branches = []
        body, stopper = self.parse_seq({"elif", "else", "endif"})
        branches.append((cond_ast, if_pos, body))
        if stopper is None:
            raise TemplateError("unclosed_block", if_pos)
        name, srest, spos = stopper
        while name == "elif":
            self.idx += 1
            if srest == "":
                raise TemplateError("syntax", spos)
            c2 = parse_expr_full(srest, spos, False)
            body2, stopper = self.parse_seq({"elif", "else", "endif"})
            branches.append((c2, spos, body2))
            if stopper is None:
                raise TemplateError("unclosed_block", if_pos)
            name, srest, spos = stopper
        else_body = None
        if name == "else":
            self.idx += 1
            if srest != "":
                raise TemplateError("syntax", spos)
            else_body, stopper = self.parse_seq({"endif"})
            if stopper is None:
                raise TemplateError("unclosed_block", if_pos)
            name, srest, spos = stopper
        # name == 'endif'
        if srest != "":
            raise TemplateError("syntax", spos)
        self.idx += 1
        return ("if", branches, else_body)

    def parse_for(self, for_pos, rest):
        self.idx += 1
        if rest == "":
            raise TemplateError("syntax", for_pos)
        var_name, expr_ast = parse_for_rest(rest, for_pos)
        body, stopper = self.parse_seq({"empty", "endfor"})
        if stopper is None:
            raise TemplateError("unclosed_block", for_pos)
        sname, srest, spos = stopper
        empty_body = None
        if sname == "empty":
            self.idx += 1
            if srest != "":
                raise TemplateError("syntax", spos)
            empty_body, stopper = self.parse_seq({"endfor"})
            if stopper is None:
                raise TemplateError("unclosed_block", for_pos)
            sname, srest, spos = stopper
        if srest != "":
            raise TemplateError("syntax", spos)
        self.idx += 1
        return ("for", var_name, expr_ast, body, empty_body, for_pos)


def parse_tokens(tokens):
    p = Parser(tokens)
    nodes, stopper = p.parse_seq(set())
    return nodes


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------

def type_name(v):
    if v is UNDEFINED:
        return None
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "map"
    return None


def text_of(v):
    if v is UNDEFINED or v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return "[" + ", ".join(text_of(it) for it in v) + "]"
    if isinstance(v, dict):
        parts = []
        for k, val in v.items():
            parts.append(text_of(k) + ": " + text_of(val))
        return "{" + ", ".join(parts) + "}"
    return ""


def escape_text(s):
    out = []
    for ch in s:
        out.append(ESCAPE_MAP.get(ch, ch))
    return "".join(out)


def is_truthy(v):
    if v is UNDEFINED or v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0
    if isinstance(v, str):
        return v not in ("", "0", "false")
    if isinstance(v, list):
        return len(v) != 0
    if isinstance(v, dict):
        return len(v) != 0
    return True


def values_equal(a, b):
    ta, tb = type_name(a), type_name(b)
    if ta != tb:
        return False
    if ta is None:
        return True
    if ta in ("none",):
        return True
    if ta in ("bool", "number", "string"):
        return a == b
    if ta == "list":
        if len(a) != len(b):
            return False
        return all(values_equal(x, y) for x, y in zip(a, b))
    if ta == "map":
        if len(a) != len(b):
            return False
        for k, v in a.items():
            if k not in b:
                return False
            if not values_equal(v, b[k]):
                return False
        return True
    return False


def do_lookup(base, key):
    if base is UNDEFINED or base is None:
        return UNDEFINED
    if isinstance(base, dict):
        if isinstance(key, str) and key in base:
            return base[key]
    if isinstance(base, (list, str)):
        idx = None
        if isinstance(key, int) and not isinstance(key, bool):
            idx = key
        elif isinstance(key, str) and key != "" and all(c in "0123456789" for c in key):
            idx = int(key)
        if idx is not None:
            if 0 <= idx < len(base):
                return base[idx]
            return UNDEFINED
    if isinstance(key, str):
        if key == "size":
            if isinstance(base, (str, list, dict)):
                return len(base)
            return UNDEFINED
        if key == "keys":
            if isinstance(base, dict):
                return list(base.keys())
            return UNDEFINED
        if key == "type":
            tn = type_name(base)
            return tn if tn is not None else UNDEFINED
    return UNDEFINED


def do_in(x, y):
    if isinstance(y, str):
        return isinstance(x, str) and (x in y)
    if isinstance(y, list):
        return any(values_equal(x, item) for item in y)
    if isinstance(y, dict):
        return isinstance(x, str) and (x in y)
    return False


def do_cmp(op, a, b, tag_pos):
    if op == "==":
        return values_equal(a, b)
    if op == "!=":
        return not values_equal(a, b)
    if op == "in":
        return do_in(a, b)
    ta, tb = type_name(a), type_name(b)
    ok = (ta == "number" and tb == "number") or (ta == "string" and tb == "string")
    if not ok:
        raise TemplateError("bad_operand", tag_pos)
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    raise TemplateError("bad_operand", tag_pos)


def get_sequence(val, pos):
    if val is UNDEFINED or val is None:
        return []
    if isinstance(val, bool):
        raise TemplateError("not_iterable", pos)
    if isinstance(val, int):
        raise TemplateError("not_iterable", pos)
    if isinstance(val, str):
        return list(val)
    if isinstance(val, list):
        return list(val)
    if isinstance(val, dict):
        return list(val.keys())
    raise TemplateError("not_iterable", pos)


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def _ascii_upper_char(c):
    if "a" <= c <= "z":
        return chr(ord(c) - 32)
    return c


def _ascii_lower_char(c):
    if "A" <= c <= "Z":
        return chr(ord(c) + 32)
    return c


def _filter_length(v):
    if v is UNDEFINED or v is None:
        return 0
    if isinstance(v, bool):
        return 0
    if isinstance(v, int):
        return len(str(v))
    if isinstance(v, (str, list, dict)):
        return len(v)
    return 0


def _filter_first(v):
    if isinstance(v, str):
        return v[0] if len(v) > 0 else UNDEFINED
    if isinstance(v, list):
        return v[0] if len(v) > 0 else UNDEFINED
    if isinstance(v, dict):
        if len(v) > 0:
            return next(iter(v.keys()))
        return UNDEFINED
    return UNDEFINED


def _filter_join(v, sep):
    if v is UNDEFINED or v is None:
        return ""
    if isinstance(v, bool):
        return text_of(v)
    if isinstance(v, int):
        return text_of(v)
    if isinstance(v, str):
        return sep.join(list(v))
    if isinstance(v, list):
        return sep.join(text_of(it) for it in v)
    if isinstance(v, dict):
        return sep.join(text_of(k) for k in v.keys())
    return ""


def _custom_replace(t, a, b):
    if a == "":
        return t
    out = []
    i = 0
    la = len(a)
    n = len(t)
    while i < n:
        if t[i:i + la] == a:
            out.append(b)
            i += la
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def _slice_num(arg):
    if isinstance(arg, bool):
        return None
    if isinstance(arg, int):
        return arg if arg >= 0 else None
    if isinstance(arg, str) and len(arg) > 0 and all(c in "0123456789" for c in arg):
        return int(arg)
    return None


def _filter_slice(v, start_arg, len_arg):
    s = _slice_num(start_arg)
    l = _slice_num(len_arg)
    if s is None or l is None:
        return v
    if isinstance(v, list):
        return v[s:s + l]
    if isinstance(v, str):
        return v[s:s + l]
    t = text_of(v)
    return t[s:s + l]


def apply_filter(name, value, safe, args):
    if name == "upper":
        t = text_of(value)
        return ("".join(_ascii_upper_char(c) for c in t), safe)
    if name == "lower":
        t = text_of(value)
        return ("".join(_ascii_lower_char(c) for c in t), safe)
    if name == "trim":
        t = text_of(value)
        return (custom_strip(t), safe)
    if name == "length":
        return (_filter_length(value), safe)
    if name == "first":
        return (_filter_first(value), safe)
    if name == "safe":
        return (value, True)
    if name == "escape":
        t = text_of(value)
        return (escape_text(t), True)
    if name == "default":
        x = args[0]
        if not is_truthy(value):
            return (x, False)
        return (value, safe)
    if name == "join":
        sep = text_of(args[0])
        return (_filter_join(value, sep), safe)
    if name == "replace":
        a = text_of(args[0])
        b = text_of(args[1])
        t = text_of(value)
        return (_custom_replace(t, a, b), safe)
    if name == "slice":
        return (_filter_slice(value, args[0], args[1]), safe)
    # unreachable: parse-time already validated filter names
    return (value, safe)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def get_var(scopes, name):
    for sc in reversed(scopes):
        if name in sc:
            return sc[name]
    return (UNDEFINED, False)


def set_var(scopes, name, value, safe):
    scopes[-1][name] = (value, safe)


def eval_ast(node, scopes, tag_pos):
    kind = node[0]
    if kind == "int":
        return (node[1], False)
    if kind == "str":
        return (node[1], False)
    if kind == "bool":
        return (node[1], False)
    if kind == "none":
        return (None, False)
    if kind == "var":
        return get_var(scopes, node[1])
    if kind == "lookup":
        bval, _bsafe = eval_ast(node[1], scopes, tag_pos)
        kval, _ksafe = eval_ast(node[2], scopes, tag_pos)
        return (do_lookup(bval, kval), False)
    if kind == "not":
        v, _s = eval_ast(node[1], scopes, tag_pos)
        return (not is_truthy(v), False)
    if kind == "and":
        for part in node[1]:
            v, _s = eval_ast(part, scopes, tag_pos)
            if not is_truthy(v):
                return (False, False)
        return (True, False)
    if kind == "or":
        for part in node[1]:
            v, _s = eval_ast(part, scopes, tag_pos)
            if is_truthy(v):
                return (True, False)
        return (False, False)
    if kind == "cmp":
        lv, _ls = eval_ast(node[2], scopes, tag_pos)
        rv, _rs = eval_ast(node[3], scopes, tag_pos)
        return (do_cmp(node[1], lv, rv, tag_pos), False)
    if kind == "pipeline":
        v, s = eval_ast(node[1], scopes, tag_pos)
        for fname, fargs in node[2]:
            v, s = apply_filter(fname, v, s, fargs)
        return (v, s)
    raise TemplateError("syntax", tag_pos)


def render_nodes(nodes, scopes, out):
    for node in nodes:
        t = node[0]
        if t == "text":
            out.append(node[1])
        elif t == "interp":
            ast, pos = node[1], node[2]
            val, safe = eval_ast(ast, scopes, pos)
            txt = text_of(val)
            if not safe:
                txt = escape_text(txt)
            out.append(txt)
        elif t == "if":
            branches, else_body = node[1], node[2]
            done = False
            for cond_ast, cpos, body in branches:
                v, _s = eval_ast(cond_ast, scopes, cpos)
                if is_truthy(v):
                    render_nodes(body, scopes, out)
                    done = True
                    break
            if not done and else_body is not None:
                render_nodes(else_body, scopes, out)
        elif t == "for":
            var_name, expr_ast, body, empty_body, for_pos = node[1], node[2], node[3], node[4], node[5]
            val, _safe = eval_ast(expr_ast, scopes, for_pos)
            seq = get_sequence(val, for_pos)
            scopes.append({})
            if len(seq) == 0:
                if empty_body is not None:
                    render_nodes(empty_body, scopes, out)
            else:
                n = len(seq)
                for i, item in enumerate(seq):
                    scopes[-1]["loop"] = ({
                        "index": i + 1,
                        "index0": i,
                        "first": i == 0,
                        "last": i == n - 1,
                        "length": n,
                    }, False)
                    scopes[-1][var_name] = (item, False)
                    render_nodes(body, scopes, out)
            scopes.pop()
        elif t == "set":
            name, expr_ast, set_pos = node[1], node[2], node[3]
            val, safe = eval_ast(expr_ast, scopes, set_pos)
            set_var(scopes, name, val, safe)


def render(source, context):
    tokens = tokenize(source)
    nodes = parse_tokens(tokens)
    scopes = [{k: (v, False) for k, v in context.items()}]
    out = []
    render_nodes(nodes, scopes, out)
    return "".join(out)
