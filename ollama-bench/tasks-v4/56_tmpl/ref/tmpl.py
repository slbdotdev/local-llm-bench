"""Reference implementation: a small template engine.

Strategy: lex to a flat node list, parse into a recursive AST with recursive
descent, then render by walking the tree.
"""

WS = " \t\r\n\x0b\x0c"
_D = "0123456789"
_L = "abcdefghijklmnopqrstuvwxyz"
_U = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ID0 = set(_L + _U + "_")
_IDC = set(_L + _U + "_" + _D)
_KW = ("true", "false", "none", "not", "and", "or", "in")


class TemplateError(Exception):
    def __init__(self, kind, pos):
        Exception.__init__(self, "%s at %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


class _Undef(object):
    __slots__ = ()

    def __repr__(self):
        return "<undefined>"


UNDEF = _Undef()


# ---------------------------------------------------------------- values
def _tname(v):
    if v is UNDEF:
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
    return "string"


def _truthy(v):
    if v is UNDEF or v is None or v is False:
        return False
    if v is True:
        return True
    if isinstance(v, int):
        return v != 0
    if isinstance(v, str):
        return v != "" and v != "0" and v != "false"
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return True


def _text(v):
    if v is UNDEF or v is None:
        return ""
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return "[" + ", ".join(_text(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(_text(k) + ": " + _text(x) for k, x in v.items()) + "}"
    return str(v)


_EMAP = {"&": "&amp;", "<": "&lt;", ">": "&gt;", chr(34): "&#34;", chr(39): "&#39;"}


def _esc(s):
    out = []
    for c in s:
        out.append(_EMAP.get(c, c))
    return "".join(out)


def _eq(a, b):
    ta, tb = _tname(a), _tname(b)
    if ta != tb:
        return False
    if ta is None or ta == "none":
        return True
    if ta == "list":
        if len(a) != len(b):
            return False
        for i in range(len(a)):
            if not _eq(a[i], b[i]):
                return False
        return True
    if ta == "map":
        if len(a) != len(b):
            return False
        for k in a:
            if k not in b or not _eq(a[k], b[k]):
                return False
        return True
    return a == b


def _inop(a, b):
    if isinstance(b, str):
        return isinstance(a, str) and (a in b)
    if isinstance(b, list):
        for x in b:
            if _eq(a, x):
                return True
        return False
    if isinstance(b, dict):
        if not isinstance(a, str):
            return False
        return a in b
    return False


def _lookup(c, key):
    if c is UNDEF or c is None:
        return UNDEF
    if isinstance(c, dict):
        try:
            if key in c:
                return c[key]
        except TypeError:
            pass
    elif isinstance(c, (list, str)):
        idx = None
        if isinstance(key, bool):
            idx = None
        elif isinstance(key, int):
            idx = key
        elif isinstance(key, str) and key != "" and all(ch in _D for ch in key):
            idx = int(key)
        if idx is not None:
            if 0 <= idx < len(c):
                return c[idx]
            return UNDEF
    if key == "size":
        if isinstance(c, (str, list, dict)):
            return len(c)
        return UNDEF
    if key == "keys":
        if isinstance(c, dict):
            return list(c.keys())
        return UNDEF
    if key == "type":
        t = _tname(c)
        return UNDEF if t is None else t
    return UNDEF


def _isnum(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _cmp(op, a, b, pos):
    if op == "==":
        return _eq(a, b)
    if op == "!=":
        return not _eq(a, b)
    if op == "in":
        return _inop(a, b)
    if not ((_isnum(a) and _isnum(b)) or (isinstance(a, str) and isinstance(b, str))):
        raise TemplateError("bad_operand", pos)
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    return a >= b


# ---------------------------------------------------------------- filters
FILTERS = {"upper": 0, "lower": 0, "length": 0, "trim": 0, "first": 0,
           "safe": 0, "escape": 0, "default": 1, "join": 1,
           "replace": 2, "slice": 2}


def _upper(s):
    return "".join(chr(ord(c) - 32) if "a" <= c <= "z" else c for c in s)


def _lower(s):
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)


def _toint(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    if isinstance(v, str) and v != "" and all(c in _D for c in v):
        return int(v)
    return None


def _apply(name, args, v, safe):
    if name == "safe":
        return v, True
    if name == "escape":
        return _esc(_text(v)), True
    if name == "upper":
        return _upper(_text(v)), safe
    if name == "lower":
        return _lower(_text(v)), safe
    if name == "trim":
        return _text(v).strip(WS), safe
    if name == "length":
        if v is UNDEF or v is None or isinstance(v, bool):
            return 0, safe
        if isinstance(v, int):
            return len(str(v)), safe
        if isinstance(v, (str, list, dict)):
            return len(v), safe
        return 0, safe
    if name == "first":
        if isinstance(v, (str, list)):
            return (v[0] if len(v) > 0 else UNDEF), safe
        if isinstance(v, dict):
            for k in v:
                return k, safe
            return UNDEF, safe
        return UNDEF, safe
    if name == "default":
        if _truthy(v):
            return v, safe
        return args[0], False
    if name == "join":
        sep = _text(args[0])
        if v is UNDEF or v is None:
            return "", safe
        if isinstance(v, list):
            return sep.join(_text(x) for x in v), safe
        if isinstance(v, str):
            return sep.join(list(v)), safe
        if isinstance(v, dict):
            return sep.join(_text(k) for k in v), safe
        return _text(v), safe
    if name == "replace":
        a, b = _text(args[0]), _text(args[1])
        s = _text(v)
        if a == "":
            return s, safe
        return s.replace(a, b), safe
    if name == "slice":
        st, ln = _toint(args[0]), _toint(args[1])
        if st is None or ln is None:
            return v, safe
        if isinstance(v, (str, list)):
            return v[st:st + ln], safe
        return _text(v)[st:st + ln], safe
    return v, safe


# ---------------------------------------------------------------- lexer
def _lex(src):
    raw = []
    i = 0
    n = len(src)
    start = 0
    while i < n:
        if src[i] == "{" and i + 1 < n and src[i + 1] in "{%#":
            o = src[i + 1]
            closer = {"{": "}}", "%": "%}", "#": "#}"}[o]
            if start < i:
                raw.append(["text", src[start:i], False, False])
            j = i + 2
            lt = False
            if j < n and src[j] == "-":
                lt = True
                j += 1
            k = src.find(closer, j)
            if k < 0:
                raise TemplateError("unclosed_tag", i)
            body = src[j:k]
            rt = False
            if body.endswith("-"):
                rt = True
                body = body[:-1]
            raw.append(["tag", o, i, body, lt, rt])
            i = k + 2
            start = i
        else:
            i += 1
    if start < n:
        raw.append(["text", src[start:], False, False])
    out = []
    for idx, it in enumerate(raw):
        if it[0] != "text":
            out.append(it)
            continue
        s = it[1]
        prv = raw[idx - 1] if idx > 0 else None
        nxt = raw[idx + 1] if idx + 1 < len(raw) else None
        if prv is not None and prv[0] == "tag" and prv[5]:
            s = s.lstrip(WS)
        if nxt is not None and nxt[0] == "tag" and nxt[4]:
            s = s.rstrip(WS)
        out.append(["text", s, False, False])
    return [it for it in out if not (it[0] == "tag" and it[1] == "#")]


# ---------------------------------------------------------------- expressions
class _Lx(object):
    def __init__(self, s, pos):
        self.s = s
        self.n = len(s)
        self.i = 0
        self.pos = pos
        self.advance()

    def err(self):
        raise TemplateError("syntax", self.pos)

    def advance(self):
        s, n = self.s, self.n
        i = self.i
        while i < n and s[i] in WS:
            i += 1
        self.begin = i
        if i >= n:
            self.kind = "eof"
            self.val = None
            self.i = i
            self.end = i
            return
        c = s[i]
        if c in _ID0:
            j = i
            while j < n and s[j] in _IDC:
                j += 1
            self.kind = "name"
            self.val = s[i:j]
        elif c in _D:
            j = i
            while j < n and s[j] in _D:
                j += 1
            self.kind = "int"
            self.val = s[i:j]
        elif c == chr(34) or c == chr(39):
            v, j = self.rdstr(i)
            self.kind = "str"
            self.val = v
        elif s[i:i + 2] in ("==", "!=", "<=", ">="):
            self.kind = "op"
            self.val = s[i:i + 2]
            j = i + 2
        elif c in "<>.[]|,:":
            self.kind = "op"
            self.val = c
            j = i + 1
        else:
            self.err()
        self.i = j
        self.end = j

    def rdstr(self, i):
        s, n = self.s, self.n
        q = s[i]
        j = i + 1
        out = []
        while True:
            if j >= n:
                self.err()
            c = s[j]
            if c == "\\":
                if j + 1 >= n:
                    self.err()
                d = s[j + 1]
                out.append("\n" if d == "n" else ("\t" if d == "t" else d))
                j += 2
                continue
            if c == q:
                return "".join(out), j + 1
            out.append(c)
            j += 1


def _p_or(lx):
    parts = [_p_and(lx)]
    while lx.kind == "name" and lx.val == "or":
        lx.advance()
        parts.append(_p_and(lx))
    return parts[0] if len(parts) == 1 else ("or", parts)


def _p_and(lx):
    parts = [_p_not(lx)]
    while lx.kind == "name" and lx.val == "and":
        lx.advance()
        parts.append(_p_not(lx))
    return parts[0] if len(parts) == 1 else ("and", parts)


def _p_not(lx):
    if lx.kind == "name" and lx.val == "not":
        lx.advance()
        return ("not", _p_not(lx))
    return _p_cmp(lx)


_CMPOPS = ("==", "!=", "<", "<=", ">", ">=")


def _isc(lx):
    if lx.kind == "op" and lx.val in _CMPOPS:
        return lx.val
    if lx.kind == "name" and lx.val == "in":
        return "in"
    return None


def _p_cmp(lx):
    a = _p_prim(lx)
    op = _isc(lx)
    if op is None:
        return a
    lx.advance()
    b = _p_prim(lx)
    if _isc(lx) is not None:
        lx.err()
    return ("cmp", op, a, b)


def _p_prim(lx):
    if lx.kind == "int":
        node = ("lit", int(lx.val))
        lx.advance()
    elif lx.kind == "str":
        node = ("lit", lx.val)
        lx.advance()
    elif lx.kind == "name":
        nm = lx.val
        if nm == "true":
            node = ("lit", True)
        elif nm == "false":
            node = ("lit", False)
        elif nm == "none":
            node = ("lit", None)
        elif nm in _KW:
            lx.err()
        else:
            node = ("name", nm)
        lx.advance()
    else:
        lx.err()
    while True:
        if lx.kind == "op" and lx.val == ".":
            lx.advance()
            if lx.kind == "name" or lx.kind == "int":
                key = lx.val
            else:
                lx.err()
            lx.advance()
            node = ("get", node, ("lit", key))
        elif lx.kind == "op" and lx.val == "[":
            lx.advance()
            k = _p_prim(lx)
            if not (lx.kind == "op" and lx.val == "]"):
                lx.err()
            lx.advance()
            node = ("get", node, k)
        else:
            break
    return node


def _skipws(s, i):
    while i < len(s) and s[i] in WS:
        i += 1
    return i


def _coerce(raw):
    if raw != "" and all(c in _D for c in raw):
        return int(raw)
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "none":
        return None
    return raw


def _read_args(s, i, pos):
    args = []
    n = len(s)
    lx = _Lx("", pos)
    lx.s = s
    lx.n = n
    while True:
        i = _skipws(s, i)
        if i < n and (s[i] == chr(34) or s[i] == chr(39)):
            v, j = lx.rdstr(i)
            i = _skipws(s, j)
            if i < n and s[i] not in ",|":
                raise TemplateError("syntax", pos)
            args.append(v)
        else:
            j = i
            while j < n and s[j] not in ",|":
                j += 1
            args.append(_coerce(s[i:j].strip(WS)))
            i = j
        if i < n and s[i] == ",":
            i += 1
            continue
        return args, i


def _parse_pipe(text, pos, allow_filters):
    lx = _Lx(text, pos)
    if lx.kind == "eof":
        raise TemplateError("syntax", pos)
    node = _p_or(lx)
    filters = []
    while lx.kind != "eof":
        if not (lx.kind == "op" and lx.val == "|") or not allow_filters:
            raise TemplateError("syntax", pos)
        i = _skipws(text, lx.end)
        j = i
        while j < len(text) and text[j] in _IDC:
            j += 1
        name = text[i:j]
        if name == "" or name[0] in _D:
            raise TemplateError("syntax", pos)
        if name not in FILTERS:
            raise TemplateError("unknown_filter", pos)
        i = _skipws(text, j)
        args = []
        if i < len(text) and text[i] == ":":
            args, i = _read_args(text, i + 1, pos)
        if len(args) != FILTERS[name]:
            raise TemplateError("filter_args", pos)
        filters.append((name, args))
        lx.i = i
        lx.advance()
    return (node, filters)


def _ident(s, i, pos):
    i = _skipws(s, i)
    j = i
    while j < len(s) and s[j] in _IDC:
        j += 1
    nm = s[i:j]
    if nm == "" or nm[0] in _D or nm in _KW:
        raise TemplateError("syntax", pos)
    return nm, j


# ---------------------------------------------------------------- parser
_ENDERS = ("elif", "else", "endif", "empty", "endfor")


class _P(object):
    def __init__(self, items):
        self.items = items
        self.k = 0

    def parse_body(self, terms, opener_pos):
        body = []
        while True:
            if self.k >= len(self.items):
                if terms:
                    raise TemplateError("unclosed_block", opener_pos)
                return body, None
            it = self.items[self.k]
            if it[0] == "text":
                if it[1]:
                    body.append(("text", it[1]))
                self.k += 1
                continue
            pos = it[2]
            bd = it[3].strip(WS)
            if it[1] == "{":
                if bd == "":
                    raise TemplateError("syntax", pos)
                body.append(("out", pos, _parse_pipe(bd, pos, True)))
                self.k += 1
                continue
            if bd == "":
                raise TemplateError("unknown_tag", pos)
            sp = 0
            while sp < len(bd) and bd[sp] not in WS:
                sp += 1
            name = bd[:sp]
            rest = bd[sp:].strip(WS)
            if name in _ENDERS:
                if name not in terms:
                    raise TemplateError("unexpected_tag", pos)
                if name != "elif" and rest != "":
                    raise TemplateError("syntax", pos)
                self.k += 1
                return body, (name, pos, rest)
            if name == "set":
                nm, i = _ident(rest, 0, pos)
                i = _skipws(rest, i)
                if not (i < len(rest) and rest[i] == "=" and rest[i:i + 2] != "=="):
                    raise TemplateError("syntax", pos)
                body.append(("set", pos, nm, _parse_pipe(rest[i + 1:], pos, True)))
                self.k += 1
            elif name == "if":
                self.k += 1
                if rest == "":
                    raise TemplateError("syntax", pos)
                branches = []
                cpos = pos
                cond = _parse_pipe(rest, pos, False)
                while True:
                    blk, end = self.parse_body(("elif", "else", "endif"), pos)
                    branches.append((cpos, cond, blk))
                    if end[0] == "endif":
                        body.append(("if", pos, branches, []))
                        break
                    if end[0] == "else":
                        eb, e2 = self.parse_body(("endif",), pos)
                        body.append(("if", pos, branches, eb))
                        break
                    if end[2] == "":
                        raise TemplateError("syntax", end[1])
                    cpos = end[1]
                    cond = _parse_pipe(end[2], end[1], False)
            elif name == "for":
                self.k += 1
                nm, i = _ident(rest, 0, pos)
                i = _skipws(rest, i)
                if rest[i:i + 2] != "in" or (i + 2 < len(rest) and rest[i + 2] in _IDC):
                    raise TemplateError("syntax", pos)
                itr = rest[i + 2:].strip(WS)
                if itr == "":
                    raise TemplateError("syntax", pos)
                itr = _parse_pipe(itr, pos, True)
                blk, end = self.parse_body(("empty", "endfor"), pos)
                emp = []
                if end[0] == "empty":
                    emp, e2 = self.parse_body(("endfor",), pos)
                body.append(("for", pos, nm, itr, blk, emp))
            else:
                raise TemplateError("unknown_tag", pos)


# ---------------------------------------------------------------- render
def _look(scopes, name):
    for s in reversed(scopes):
        if name in s:
            return s[name]
    return (UNDEF, False)


def _ev(node, scopes, pos):
    t = node[0]
    if t == "lit":
        return node[1]
    if t == "name":
        return _look(scopes, node[1])[0]
    if t == "get":
        return _lookup(_ev(node[1], scopes, pos), _ev(node[2], scopes, pos))
    if t == "not":
        return not _truthy(_ev(node[1], scopes, pos))
    if t == "and":
        for p in node[1]:
            if not _truthy(_ev(p, scopes, pos)):
                return False
        return True
    if t == "or":
        for p in node[1]:
            if _truthy(_ev(p, scopes, pos)):
                return True
        return False
    return _cmp(node[1], _ev(node[2], scopes, pos), _ev(node[3], scopes, pos), pos)


def _ev_pipe(pipe, scopes, pos):
    node, filters = pipe
    if node[0] == "name":
        v, safe = _look(scopes, node[1])
    else:
        v, safe = _ev(node, scopes, pos), False
    for name, args in filters:
        v, safe = _apply(name, args, v, safe)
    return v, safe


def _iterable(v, pos):
    if v is UNDEF or v is None:
        return []
    if isinstance(v, list):
        return list(v)
    if isinstance(v, str):
        return list(v)
    if isinstance(v, dict):
        return list(v.keys())
    raise TemplateError("not_iterable", pos)


def _run(body, scopes, out):
    for nd in body:
        t = nd[0]
        if t == "text":
            out.append(nd[1])
        elif t == "out":
            v, safe = _ev_pipe(nd[2], scopes, nd[1])
            s = _text(v)
            out.append(s if safe else _esc(s))
        elif t == "set":
            scopes[-1][nd[2]] = _ev_pipe(nd[3], scopes, nd[1])
        elif t == "if":
            hit = False
            for cpos, cond, blk in nd[2]:
                if _truthy(_ev_pipe(cond, scopes, cpos)[0]):
                    _run(blk, scopes, out)
                    hit = True
                    break
            if not hit:
                _run(nd[3], scopes, out)
        else:
            pos, name, itr, blk, emp = nd[1], nd[2], nd[3], nd[4], nd[5]
            items = _iterable(_ev_pipe(itr, scopes, pos)[0], pos)
            scopes.append({})
            try:
                if items:
                    n = len(items)
                    for i, item in enumerate(items):
                        scopes[-1][name] = (item, False)
                        scopes[-1]["loop"] = ({"index": i + 1, "index0": i,
                                               "first": i == 0, "last": i == n - 1,
                                               "length": n}, False)
                        _run(blk, scopes, out)
                else:
                    _run(emp, scopes, out)
            finally:
                scopes.pop()


def render(source, context):
    items = _lex(source)
    p = _P(items)
    body, end = p.parse_body((), 0)
    top = {}
    for k, v in (context or {}).items():
        top[k] = (v, False)
    out = []
    _run(body, [top], out)
    return "".join(out)
