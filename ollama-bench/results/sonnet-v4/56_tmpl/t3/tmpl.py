"""A small text template engine implemented as pure string processing."""

import sys

try:
    sys.setrecursionlimit(20000)
except Exception:
    pass


class TemplateError(Exception):
    def __init__(self, kind, pos):
        super().__init__("%s @ %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


# ---------------------------------------------------------------------------
# Character classes (hand rolled, no `re`/`string`)
# ---------------------------------------------------------------------------

WS_CHARS = (' ', '\t', '\r', '\n', '\x0b', '\x0c')
WS_SET = frozenset(WS_CHARS)

KEYWORDS = frozenset(['true', 'false', 'none', 'not', 'and', 'or', 'in'])


def is_ws(c):
    return c in WS_SET


def is_digit(c):
    return '0' <= c <= '9'


def is_ident_start(c):
    return c == '_' or ('a' <= c <= 'z') or ('A' <= c <= 'Z')


def is_ident_cont(c):
    return is_ident_start(c) or is_digit(c)


def strip_ws(s):
    i = 0
    j = len(s)
    while i < j and s[i] in WS_SET:
        i += 1
    while j > i and s[j - 1] in WS_SET:
        j -= 1
    return s[i:j]


# ---------------------------------------------------------------------------
# Undefined sentinel
# ---------------------------------------------------------------------------

class _Undefined(object):
    __slots__ = ()

    def __repr__(self):
        return "Undefined"


UNDEFINED = _Undefined()


def type_of(v):
    if v is UNDEFINED:
        return 'undefined'
    if v is None:
        return 'none'
    if isinstance(v, bool):
        return 'bool'
    if isinstance(v, int):
        return 'number'
    if isinstance(v, str):
        return 'string'
    if isinstance(v, list):
        return 'list'
    if isinstance(v, dict):
        return 'map'
    # Anything else is treated as undefined-ish; shouldn't happen per spec.
    return 'undefined'


def truthy(v):
    t = type_of(v)
    if t == 'undefined' or t == 'none':
        return False
    if t == 'bool':
        return v
    if t == 'number':
        return v != 0
    if t == 'string':
        return v not in ('', '0', 'false')
    if t == 'list':
        return len(v) > 0
    if t == 'map':
        return len(v) > 0
    return False


def text_of(v):
    t = type_of(v)
    if t == 'undefined' or t == 'none':
        return ''
    if t == 'bool':
        return 'true' if v else 'false'
    if t == 'number':
        return str(v)
    if t == 'string':
        return v
    if t == 'list':
        return '[' + ', '.join(text_of(x) for x in v) + ']'
    if t == 'map':
        parts = []
        for k, val in v.items():
            parts.append(text_of(k) + ': ' + text_of(val))
        return '{' + ', '.join(parts) + '}'
    return ''


_ESCAPE_MAP = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&#34;', "'": '&#39;'}


def escape_text(s):
    out = []
    for ch in s:
        out.append(_ESCAPE_MAP.get(ch, ch))
    return ''.join(out)


def values_equal(a, b):
    ta, tb = type_of(a), type_of(b)
    if ta != tb:
        return False
    if ta == 'undefined' or ta == 'none':
        return True
    if ta in ('bool', 'number', 'string'):
        return a == b
    if ta == 'list':
        if len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if not values_equal(x, y):
                return False
        return True
    if ta == 'map':
        if len(a) != len(b):
            return False
        for k, v in a.items():
            if k not in b:
                return False
            if not values_equal(v, b[k]):
                return False
        return True
    return False


def eval_in(lv, rv):
    t = type_of(rv)
    if t == 'string':
        if type_of(lv) != 'string':
            return False
        return lv in rv
    if t == 'list':
        for item in rv:
            if values_equal(lv, item):
                return True
        return False
    if t == 'map':
        if type_of(lv) != 'string':
            return False
        return lv in rv
    return False


def _as_index(key):
    if isinstance(key, bool):
        return None
    if isinstance(key, int):
        return key
    if isinstance(key, str) and key != '' and all(is_digit(c) for c in key):
        return int(key)
    return None


def _fallback_pseudo(base, key, bt):
    if type_of(key) == 'string':
        if key == 'size':
            if bt in ('string', 'list', 'map'):
                return len(base)
            return UNDEFINED
        if key == 'keys':
            if bt == 'map':
                return list(base.keys())
            return UNDEFINED
        if key == 'type':
            return bt
    return UNDEFINED


def do_lookup(base, key):
    bt = type_of(base)
    if bt == 'undefined' or bt == 'none':
        return UNDEFINED
    if bt == 'map':
        if type_of(key) == 'string' and key in base:
            return base[key]
        return _fallback_pseudo(base, key, bt)
    if bt == 'list' or bt == 'string':
        idx = _as_index(key)
        if idx is not None:
            if 0 <= idx < len(base):
                return base[idx]
            return UNDEFINED
        return _fallback_pseudo(base, key, bt)
    return _fallback_pseudo(base, key, bt)


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

_OPENERS = {'{{': 'interp', '{%': 'block', '{#': 'comment'}
_CLOSERS = {'interp': '}}', 'block': '%}', 'comment': '#}'}


def lex(source):
    n = len(source)
    i = 0
    tokens = []
    text_start = 0
    while i < n:
        if source[i] == '{' and i + 1 < n and source[i + 1] in ('{', '%', '#'):
            tokens.append({'type': 'text', 'value': source[text_start:i]})
            tag_start = i
            opener = source[i:i + 2]
            kind = _OPENERS[opener]
            closer = _CLOSERS[kind]
            j = i + 2
            left = False
            if j < n and source[j] == '-':
                left = True
                j += 1
            idx = source.find(closer, j)
            if idx == -1:
                raise TemplateError('unclosed_tag', tag_start)
            body = source[j:idx]
            right = False
            if len(body) > 0 and body[-1] == '-':
                right = True
                body = body[:-1]
            tokens.append({'type': 'tag', 'kind': kind, 'pos': tag_start,
                            'left': left, 'right': right, 'body': body})
            i = idx + len(closer)
            text_start = i
        else:
            i += 1
    tokens.append({'type': 'text', 'value': source[text_start:n]})

    for k, tok in enumerate(tokens):
        if tok['type'] != 'text':
            continue
        v = tok['value']
        if k > 0 and tokens[k - 1]['type'] == 'tag' and tokens[k - 1]['right']:
            j = 0
            while j < len(v) and v[j] in WS_SET:
                j += 1
            v = v[j:]
        if k + 1 < len(tokens) and tokens[k + 1]['type'] == 'tag' and tokens[k + 1]['left']:
            j = len(v)
            while j > 0 and v[j - 1] in WS_SET:
                j -= 1
            v = v[:j]
        tok['value'] = v

    result = [t for t in tokens if not (t['type'] == 'tag' and t['kind'] == 'comment')]
    return result


# ---------------------------------------------------------------------------
# Expression parser
# ---------------------------------------------------------------------------

FILTER_ARITY = {
    'upper': 0, 'lower': 0, 'trim': 0, 'length': 0, 'first': 0,
    'safe': 0, 'escape': 0, 'default': 1, 'join': 1, 'replace': 2, 'slice': 2,
}


class ExprParser(object):
    def __init__(self, text, tag_pos):
        self.s = text
        self.n = len(text)
        self.i = 0
        self.pos = tag_pos

    def err(self, kind='syntax'):
        raise TemplateError(kind, self.pos)

    def skip_ws(self):
        while self.i < self.n and self.s[self.i] in WS_SET:
            self.i += 1

    def starts_with(self, lit):
        return self.s.startswith(lit, self.i)

    def read_ident(self):
        self.skip_ws()
        if self.i >= self.n:
            return None
        c = self.s[self.i]
        if not is_ident_start(c):
            return None
        j = self.i + 1
        while j < self.n and is_ident_cont(self.s[j]):
            j += 1
        word = self.s[self.i:j]
        self.i = j
        return word

    def try_kw(self, word):
        self.skip_ws()
        save = self.i
        if self.starts_with(word):
            end = self.i + len(word)
            nextc = self.s[end] if end < self.n else ''
            if not is_ident_cont(nextc):
                self.i = end
                return True
        self.i = save
        return False

    def read_string(self):
        self.skip_ws()
        q = self.s[self.i]
        self.i += 1
        out = []
        while True:
            if self.i >= self.n:
                self.err('syntax')
            c = self.s[self.i]
            if c == q:
                self.i += 1
                return ''.join(out)
            if c == '\\':
                self.i += 1
                if self.i >= self.n:
                    self.err('syntax')
                e = self.s[self.i]
                if e == 'n':
                    out.append('\n')
                elif e == 't':
                    out.append('\t')
                else:
                    out.append(e)
                self.i += 1
            else:
                out.append(c)
                self.i += 1

    def try_cmpop(self):
        self.skip_ws()
        for lit in ('==', '!=', '<=', '>='):
            if self.starts_with(lit):
                self.i += len(lit)
                return lit
        for lit in ('<', '>'):
            if self.starts_with(lit):
                self.i += len(lit)
                return lit
        if self.try_kw('in'):
            return 'in'
        return None

    # -- grammar --

    def parse_pipeline(self, allow_filters):
        node = self.parse_disjunct()
        while True:
            self.skip_ws()
            if self.starts_with('|'):
                if not allow_filters:
                    self.err('syntax')
                self.i += 1
                node = self.parse_filter(node)
            else:
                break
        return node

    def parse_disjunct(self):
        node = self.parse_conjunct()
        while self.try_kw('or'):
            rhs = self.parse_conjunct()
            node = ('or', node, rhs)
        return node

    def parse_conjunct(self):
        node = self.parse_negation()
        while self.try_kw('and'):
            rhs = self.parse_negation()
            node = ('and', node, rhs)
        return node

    def parse_negation(self):
        if self.try_kw('not'):
            inner = self.parse_negation()
            return ('not', inner)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_primary()
        op = self.try_cmpop()
        if op is None:
            return left
        right = self.parse_primary()
        return ('cmp', op, left, right)

    def parse_primary(self):
        node = self.parse_atom()
        while True:
            self.skip_ws()
            if self.starts_with('.'):
                self.i += 1
                key = self.parse_key()
                node = ('lookupkey', node, key)
            elif self.starts_with('['):
                self.i += 1
                idx_node = self.parse_primary()
                self.skip_ws()
                if not self.starts_with(']'):
                    self.err('syntax')
                self.i += 1
                node = ('lookupidx', node, idx_node)
            else:
                break
        return node

    def parse_key(self):
        self.skip_ws()
        if self.i < self.n and is_ident_start(self.s[self.i]):
            j = self.i + 1
            while j < self.n and is_ident_cont(self.s[j]):
                j += 1
            key = self.s[self.i:j]
            self.i = j
            return key
        if self.i < self.n and is_digit(self.s[self.i]):
            j = self.i
            while j < self.n and is_digit(self.s[j]):
                j += 1
            key = self.s[self.i:j]
            self.i = j
            return key
        self.err('syntax')

    def parse_atom(self):
        self.skip_ws()
        if self.i >= self.n:
            self.err('syntax')
        c = self.s[self.i]
        if is_digit(c):
            j = self.i
            while j < self.n and is_digit(self.s[j]):
                j += 1
            val = int(self.s[self.i:j])
            self.i = j
            return ('int', val)
        if c == "'" or c == '"':
            val = self.read_string()
            return ('str', val)
        save = self.i
        word = self.read_ident()
        if word is None:
            self.err('syntax')
        if word == 'true':
            return ('bool', True)
        if word == 'false':
            return ('bool', False)
        if word == 'none':
            return ('none',)
        if word in KEYWORDS:
            self.i = save
            self.err('syntax')
        return ('ident', word)

    def parse_filter(self, input_node):
        self.skip_ws()
        name = self.read_ident()
        if not name:
            self.err('syntax')
        if name not in FILTER_ARITY:
            self.err('unknown_filter')
        self.skip_ws()
        args = []
        if self.starts_with(':'):
            self.i += 1
            args = self.parse_arglist()
        self.skip_ws()
        if self.i < self.n and not self.starts_with('|'):
            self.err('syntax')
        if len(args) != FILTER_ARITY[name]:
            self.err('filter_args')
        return ('filter', input_node, name, args)

    def parse_arglist(self):
        args = [self.parse_one_arg()]
        while True:
            self.skip_ws()
            if self.starts_with(','):
                self.i += 1
                args.append(self.parse_one_arg())
            else:
                break
        return args

    def parse_one_arg(self):
        self.skip_ws()
        if self.i < self.n and self.s[self.i] in ("'", '"'):
            val = self.read_string()
            self.skip_ws()
            if self.i < self.n and self.s[self.i] not in (',', '|'):
                self.err('syntax')
            return val
        start = self.i
        j = self.i
        while j < self.n and self.s[j] not in (',', '|'):
            j += 1
        raw = self.s[start:j]
        self.i = j
        text = strip_ws(raw)
        return interpret_arg_text(text)


def interpret_arg_text(text):
    if text != '' and all(is_digit(c) for c in text):
        return int(text)
    if text == 'true':
        return True
    if text == 'false':
        return False
    if text == 'none':
        return None
    return text


def parse_full_expr(text, pos, allow_filters):
    if text == '':
        raise TemplateError('syntax', pos)
    p = ExprParser(text, pos)
    node = p.parse_pipeline(allow_filters)
    p.skip_ws()
    if p.i != p.n:
        p.err('syntax')
    return node


# ---------------------------------------------------------------------------
# Block-level (template) parsing
# ---------------------------------------------------------------------------

def split_name_rest(s):
    i = 0
    n = len(s)
    while i < n and s[i] not in WS_SET:
        i += 1
    name = s[:i]
    rest = strip_ws(s[i:])
    return name, rest


BLOCK_NAMES = frozenset(['if', 'elif', 'else', 'endif', 'for', 'empty', 'endfor', 'set'])
CLOSERS_CONT = frozenset(['elif', 'else', 'empty', 'endif', 'endfor'])


def parse_for_header(rest, pos):
    p = ExprParser(rest, pos)
    name = p.read_ident()
    if name is None or name in KEYWORDS:
        p.err('syntax')
    if not p.try_kw('in'):
        p.err('syntax')
    p.skip_ws()
    if p.i >= p.n:
        p.err('syntax')
    expr_node = p.parse_pipeline(True)
    p.skip_ws()
    if p.i != p.n:
        p.err('syntax')
    return name, expr_node


def parse_set_header(rest, pos):
    p = ExprParser(rest, pos)
    name = p.read_ident()
    if name is None or name in KEYWORDS:
        p.err('syntax')
    p.skip_ws()
    if p.i >= p.n or p.s[p.i] != '=':
        p.err('syntax')
    if p.starts_with('=='):
        p.err('syntax')
    p.i += 1
    p.skip_ws()
    if p.i >= p.n:
        p.err('syntax')
    expr_node = p.parse_pipeline(True)
    p.skip_ws()
    if p.i != p.n:
        p.err('syntax')
    return name, expr_node


def parse_template(tokens):
    idx = [0]

    def parse_body():
        nodes = []
        while idx[0] < len(tokens):
            tok = tokens[idx[0]]
            if tok['type'] == 'text':
                nodes.append({'type': 'text', 'value': tok['value']})
                idx[0] += 1
                continue
            kind = tok['kind']
            pos = tok['pos']
            rawbody = tok['body']
            if kind == 'interp':
                b = strip_ws(rawbody)
                if b == '':
                    raise TemplateError('syntax', pos)
                expr = parse_full_expr(b, pos, True)
                nodes.append({'type': 'interp', 'expr': expr, 'pos': pos})
                idx[0] += 1
                continue
            # block
            stripped = strip_ws(rawbody)
            if stripped == '':
                raise TemplateError('unknown_tag', pos)
            name, rest = split_name_rest(stripped)
            if name == 'if':
                idx[0] += 1
                node = parse_if_block(pos, rest)
                nodes.append(node)
                continue
            if name == 'for':
                idx[0] += 1
                node = parse_for_block(pos, rest)
                nodes.append(node)
                continue
            if name == 'set':
                idx[0] += 1
                if rest == '':
                    raise TemplateError('syntax', pos)
                sname, sexpr = parse_set_header(rest, pos)
                nodes.append({'type': 'set', 'name': sname, 'expr': sexpr, 'pos': pos})
                continue
            if name in CLOSERS_CONT:
                return nodes, (name, pos, rest)
            raise TemplateError('unknown_tag', pos)
        return nodes, None

    def parse_if_block(if_pos, if_rest):
        if if_rest == '':
            raise TemplateError('syntax', if_pos)
        cond = parse_full_expr(if_rest, if_pos, False)
        branches = [{'cond': cond, 'pos': if_pos, 'body': None}]
        seen_else = False
        while True:
            body, ctrl = parse_body()
            branches[-1]['body'] = body
            if ctrl is None:
                raise TemplateError('unclosed_block', if_pos)
            cname, cpos, crest = ctrl
            if cname == 'elif' and not seen_else:
                if crest == '':
                    raise TemplateError('syntax', cpos)
                cond2 = parse_full_expr(crest, cpos, False)
                branches.append({'cond': cond2, 'pos': cpos, 'body': None})
                idx[0] += 1
                continue
            elif cname == 'else' and not seen_else:
                if crest != '':
                    raise TemplateError('syntax', cpos)
                seen_else = True
                branches.append({'cond': None, 'pos': cpos, 'body': None})
                idx[0] += 1
                continue
            elif cname == 'endif':
                if crest != '':
                    raise TemplateError('syntax', cpos)
                idx[0] += 1
                break
            else:
                raise TemplateError('unexpected_tag', cpos)
        return {'type': 'if', 'branches': branches}

    def parse_for_block(for_pos, for_rest):
        loopname, expr_node = parse_for_header(for_rest, for_pos)
        body, ctrl = parse_body()
        empty_body = None
        if ctrl is not None and ctrl[0] == 'empty':
            cname, cpos, crest = ctrl
            if crest != '':
                raise TemplateError('syntax', cpos)
            idx[0] += 1
            empty_body, ctrl = parse_body()
        if ctrl is None:
            raise TemplateError('unclosed_block', for_pos)
        cname, cpos, crest = ctrl
        if cname == 'endfor':
            if crest != '':
                raise TemplateError('syntax', cpos)
            idx[0] += 1
        else:
            raise TemplateError('unexpected_tag', cpos)
        return {'type': 'for', 'name': loopname, 'expr': expr_node, 'pos': for_pos,
                'body': body, 'empty': empty_body}

    body, ctrl = parse_body()
    if ctrl is not None:
        raise TemplateError('unexpected_tag', ctrl[1])
    return body


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

def ascii_upper(s):
    out = []
    for c in s:
        if 'a' <= c <= 'z':
            out.append(chr(ord(c) - 32))
        else:
            out.append(c)
    return ''.join(out)


def ascii_lower(s):
    out = []
    for c in s:
        if 'A' <= c <= 'Z':
            out.append(chr(ord(c) + 32))
        else:
            out.append(c)
    return ''.join(out)


def length_of(v):
    t = type_of(v)
    if t in ('undefined', 'none', 'bool'):
        return 0
    if t == 'number':
        return len(str(v if v >= 0 else -v))
    if t == 'string' or t == 'list' or t == 'map':
        return len(v)
    return 0


def first_of(v):
    t = type_of(v)
    if t == 'string':
        return v[0] if len(v) > 0 else UNDEFINED
    if t == 'list':
        return v[0] if len(v) > 0 else UNDEFINED
    if t == 'map':
        if len(v) > 0:
            return next(iter(v.keys()))
        return UNDEFINED
    return UNDEFINED


def join_of(v, s):
    t = type_of(v)
    if t in ('undefined', 'none'):
        return ''
    if t in ('number', 'bool'):
        return text_of(v)
    if t == 'list':
        return s.join(text_of(x) for x in v)
    if t == 'string':
        return s.join(list(v))
    if t == 'map':
        return s.join(v.keys())
    return ''


def replace_all(s, a, b):
    if a == '':
        return s
    out = []
    i = 0
    n = len(s)
    la = len(a)
    while i < n:
        if s.startswith(a, i):
            out.append(b)
            i += la
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def _slice_arg_value(arg):
    if isinstance(arg, bool):
        return None
    if isinstance(arg, int):
        return arg if arg >= 0 else None
    if isinstance(arg, str):
        if arg != '' and all(is_digit(c) for c in arg):
            return int(arg)
        return None
    return None


def slice_of(val, start_arg, len_arg):
    s = _slice_arg_value(start_arg)
    l = _slice_arg_value(len_arg)
    if s is None or l is None:
        return val
    t = type_of(val)
    if t == 'list' or t == 'string':
        base = val
    else:
        base = text_of(val)
    n = len(base)
    start = min(s, n)
    end = min(start + l, n)
    return base[start:end]


def apply_filter(name, val, safe, args):
    if name == 'upper':
        return (ascii_upper(text_of(val)), safe)
    if name == 'lower':
        return (ascii_lower(text_of(val)), safe)
    if name == 'trim':
        return (strip_ws(text_of(val)), safe)
    if name == 'length':
        return (length_of(val), safe)
    if name == 'first':
        return (first_of(val), safe)
    if name == 'safe':
        return (val, True)
    if name == 'escape':
        return (escape_text(text_of(val)), True)
    if name == 'default':
        if not truthy(val):
            return (args[0], False)
        return (val, safe)
    if name == 'join':
        return (join_of(val, text_of(args[0])), safe)
    if name == 'replace':
        return (replace_all(text_of(val), text_of(args[0]), text_of(args[1])), safe)
    if name == 'slice':
        return (slice_of(val, args[0], args[1]), safe)
    raise TemplateError('unknown_filter', 0)  # unreachable


# ---------------------------------------------------------------------------
# Expression evaluation (render phase)
# ---------------------------------------------------------------------------

def lookup_scopes(name, scopes):
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]
    return (UNDEFINED, False)


def eval_cmp(op, lv, rv, pos):
    if op == '==' or op == '!=':
        eq = values_equal(lv, rv)
        return eq if op == '==' else (not eq)
    if op == 'in':
        return eval_in(lv, rv)
    lt, rt = type_of(lv), type_of(rv)
    if lt == 'number' and rt == 'number':
        a, b = lv, rv
    elif lt == 'string' and rt == 'string':
        a, b = lv, rv
    else:
        raise TemplateError('bad_operand', pos)
    if op == '<':
        return a < b
    if op == '<=':
        return a <= b
    if op == '>':
        return a > b
    if op == '>=':
        return a >= b
    raise TemplateError('bad_operand', pos)


def eval_expr(node, scopes, pos):
    kind = node[0]
    if kind == 'int' or kind == 'str' or kind == 'bool':
        return (node[1], False)
    if kind == 'none':
        return (None, False)
    if kind == 'ident':
        return lookup_scopes(node[1], scopes)
    if kind == 'lookupkey':
        bval, _ = eval_expr(node[1], scopes, pos)
        return (do_lookup(bval, node[2]), False)
    if kind == 'lookupidx':
        bval, _ = eval_expr(node[1], scopes, pos)
        kval, _ = eval_expr(node[2], scopes, pos)
        return (do_lookup(bval, kval), False)
    if kind == 'not':
        v, _ = eval_expr(node[1], scopes, pos)
        return (not truthy(v), False)
    if kind == 'and':
        lv, _ = eval_expr(node[1], scopes, pos)
        if not truthy(lv):
            return (False, False)
        rv, _ = eval_expr(node[2], scopes, pos)
        return (truthy(rv), False)
    if kind == 'or':
        lv, _ = eval_expr(node[1], scopes, pos)
        if truthy(lv):
            return (True, False)
        rv, _ = eval_expr(node[2], scopes, pos)
        return (truthy(rv), False)
    if kind == 'cmp':
        lv, _ = eval_expr(node[2], scopes, pos)
        rv, _ = eval_expr(node[3], scopes, pos)
        return (eval_cmp(node[1], lv, rv, pos), False)
    if kind == 'filter':
        ival, isafe = eval_expr(node[1], scopes, pos)
        return apply_filter(node[2], ival, isafe, node[3])
    raise TemplateError('syntax', pos)  # unreachable


def eval_for_sequence(expr_node, scopes, pos):
    val, _ = eval_expr(expr_node, scopes, pos)
    t = type_of(val)
    if t == 'undefined' or t == 'none':
        return []
    if t == 'list':
        return list(val)
    if t == 'string':
        return list(val)
    if t == 'map':
        return list(val.keys())
    raise TemplateError('not_iterable', pos)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_nodes(nodes, scopes):
    parts = []
    for node in nodes:
        nt = node['type']
        if nt == 'text':
            parts.append(node['value'])
        elif nt == 'interp':
            val, safe = eval_expr(node['expr'], scopes, node['pos'])
            txt = text_of(val)
            if not safe:
                txt = escape_text(txt)
            parts.append(txt)
        elif nt == 'if':
            for br in node['branches']:
                if br['cond'] is None:
                    parts.append(render_nodes(br['body'], scopes))
                    break
                v, _ = eval_expr(br['cond'], scopes, br['pos'])
                if truthy(v):
                    parts.append(render_nodes(br['body'], scopes))
                    break
        elif nt == 'for':
            seq = eval_for_sequence(node['expr'], scopes, node['pos'])
            if len(seq) == 0:
                if node['empty'] is not None:
                    parts.append(render_nodes(node['empty'], scopes))
            else:
                n = len(seq)
                newscope = {}
                scopes.append(newscope)
                try:
                    for i, item in enumerate(seq):
                        loop_map = {
                            'index': i + 1,
                            'index0': i,
                            'first': (i == 0),
                            'last': (i == n - 1),
                            'length': n,
                        }
                        newscope[node['name']] = (item, False)
                        newscope['loop'] = (loop_map, False)
                        parts.append(render_nodes(node['body'], scopes))
                finally:
                    scopes.pop()
        elif nt == 'set':
            val, safe = eval_expr(node['expr'], scopes, node['pos'])
            scopes[-1][node['name']] = (val, safe)
    return ''.join(parts)


def render(source, context):
    tokens = lex(source)
    ast = parse_template(tokens)
    global_scope = {}
    if isinstance(context, dict):
        for k, v in context.items():
            global_scope[k] = (v, False)
    scopes = [global_scope]
    return render_nodes(ast, scopes)
