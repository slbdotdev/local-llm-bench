"""A small hand-written expression-language interpreter."""

class MiniError(Exception):
    _KINDS = {"parse", "dup_field", "dup_binding", "unbound", "uninit", "type", "div_zero", "no_field", "no_match"}
    def __init__(self, kind):
        if kind not in self._KINDS:
            kind = "parse"
        self.kind = kind
        super().__init__(kind)


_WORDS = {"let", "letrec", "and", "in", "if", "then", "else", "fun",
          "match", "with", "end", "ref", "true", "false"}
_OPS = ("->", ":=", "==", "!=", "<=", ">=", "&&", "||", "++",
        "+", "-", "*", "/", "%", "<", ">", "=", "(", ")", "{", "}",
        ",", ".", "|", "!")


def _letter(c):
    return ("A" <= c <= "Z") or ("a" <= c <= "z")


def _digit(c):
    return "0" <= c <= "9"


def _ident_start(c):
    return _letter(c) or c == "_"


def _ident_char(c):
    return _ident_start(c) or _digit(c)


def _lex(source):
    if not isinstance(source, str):
        raise MiniError("parse")
    out = []
    i = 0
    n = len(source)
    while i < n:
        c = source[i]
        if c in " \t\r\n":
            i += 1
            continue
        if _digit(c):
            start = i
            i += 1
            while i < n and _digit(source[i]):
                i += 1
            s = source[start:i]
            if len(s) > 1 and s[0] == "0":
                raise MiniError("parse")
            out.append(("INT", int(s)))
            continue
        if c == '"':
            i += 1
            start = i
            while i < n and source[i] not in '"\\\r\n':
                i += 1
            if i >= n or source[i] != '"':
                raise MiniError("parse")
            out.append(("STR", source[start:i]))
            i += 1
            continue
        if _ident_start(c):
            start = i
            i += 1
            while i < n and _ident_char(source[i]):
                i += 1
            s = source[start:i]
            if s == "_":
                out.append(("_", s))
            elif s in _WORDS:
                out.append((s, s))
            else:
                out.append(("ID", s))
            continue
        found = None
        for op in _OPS:
            if source.startswith(op, i):
                found = op
                break
        if found is None:
            raise MiniError("parse")
        out.append((found, found))
        i += len(found)
    out.append(("EOF", None))
    return out


class _Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def peek(self, kind=None):
        k = self.t[self.i][0]
        return k if kind is None else k == kind

    def take(self, kind=None):
        tok = self.t[self.i]
        if kind is not None and tok[0] != kind:
            raise MiniError("parse")
        self.i += 1
        return tok[1]

    def name(self):
        if not self.peek("ID"):
            raise MiniError("parse")
        return self.take("ID")

    def expr(self):
        if self.peek("let"):
            self.take("let")
            x = self.name(); self.take("="); a = self.expr(); self.take("in")
            return ("let", x, a, self.expr())
        if self.peek("letrec"):
            self.take(); names = [self.name()]; self.take("="); vals = [self.expr()]
            while self.peek("and"):
                self.take(); names.append(self.name()); self.take("="); vals.append(self.expr())
            self.take("in"); body = self.expr()
            if len(set(names)) != len(names):
                raise MiniError("dup_binding")
            return ("letrec", names, vals, body)
        if self.peek("if"):
            self.take(); c = self.expr(); self.take("then"); a = self.expr()
            self.take("else"); return ("if", c, a, self.expr())
        if self.peek("fun"):
            self.take(); x = self.name(); self.take("->")
            return ("fun", x, self.expr())
        if self.peek("match"):
            self.take(); subject = self.expr(); self.take("with")
            arms = []
            while self.peek("|"):
                self.take(); p, vars_ = self.pattern(); self.take("->")
                # Pattern errors occur before parsing its body.
                if len(vars_) != len(set(vars_)):
                    raise MiniError("dup_binding")
                arms.append((p, self.expr()))
            self.take("end")
            if not arms:
                raise MiniError("parse")
            return ("match", subject, arms)
        return self.assign()

    def assign(self):
        a = self.orx()
        if self.peek(":="):
            self.take(); return ("bin", ":=", a, self.expr())
        return a

    def orx(self):
        a = self.andx()
        while self.peek("||"):
            self.take(); a = ("bin", "||", a, self.andx())
        return a

    def andx(self):
        a = self.cmpx()
        while self.peek("&&"):
            self.take(); a = ("bin", "&&", a, self.cmpx())
        return a

    def cmpx(self):
        a = self.catx()
        if self.peek() in ("==", "!=", "<", "<=", ">", ">="):
            op = self.take(); b = self.catx()
            if self.peek() in ("==", "!=", "<", "<=", ">", ">="):
                raise MiniError("parse")
            return ("bin", op, a, b)
        return a

    def catx(self):
        a = self.addx()
        if self.peek("++"):
            self.take(); return ("bin", "++", a, self.catx())
        return a

    def addx(self):
        a = self.mulx()
        while self.peek() in ("+", "-"):
            op = self.take(); a = ("bin", op, a, self.mulx())
        return a

    def mulx(self):
        a = self.unary()
        while self.peek() in ("*", "/", "%"):
            op = self.take(); a = ("bin", op, a, self.unary())
        return a

    def unary(self):
        if self.peek() in ("-", "!", "ref"):
            op = self.take(); return ("un", op, self.unary())
        return self.app()

    def app(self):
        a = self.postfix()
        while self.peek() in ("INT", "STR", "ID", "true", "false", "(", "{"):
            a = ("app", a, self.postfix())
        return a

    def postfix(self):
        a = self.atom()
        while self.peek("."):
            self.take(); a = ("field", a, self.name())
        return a

    def atom(self):
        if self.peek("INT"): return ("lit", self.take())
        if self.peek("STR"): return ("lit", self.take())
        if self.peek("true"): self.take(); return ("lit", True)
        if self.peek("false"): self.take(); return ("lit", False)
        if self.peek("ID"): return ("var", self.take())
        if self.peek("("):
            self.take(); a = self.expr(); self.take(")"); return a
        if self.peek("{"): return self.record()
        raise MiniError("parse")

    def record(self):
        self.take("{"); fields = []; names = set(); duplicate = False
        if not self.peek("}"):
            while True:
                name = self.name(); self.take("="); val = self.expr()
                fields.append((name, val))
                if name in names: duplicate = True
                names.add(name)
                if not self.peek(","): break
                self.take()
        self.take("}")
        if duplicate: raise MiniError("dup_field")
        return ("record", fields)

    def pattern(self):
        vars_ = []
        if self.peek("_"):
            self.take(); return ("wild",), vars_
        if self.peek("INT"): return ("lit", self.take()), vars_
        if self.peek("STR"): return ("lit", self.take()), vars_
        if self.peek("true"): self.take(); return ("lit", True), vars_
        if self.peek("false"): self.take(); return ("lit", False), vars_
        if self.peek("ID"):
            vars_.append(self.take()); return ("bind", vars_[0]), vars_
        if self.peek("{"):
            self.take(); fields = []; names = set(); duplicate = False
            if not self.peek("}"):
                while True:
                    f = self.name(); self.take("="); p, pv = self.pattern()
                    if f in names: duplicate = True
                    names.add(f); fields.append((f, p)); vars_.extend(pv)
                    if not self.peek(","): break
                    self.take()
            self.take("}")
            if duplicate: raise MiniError("dup_field")
            return ("recordpat", fields), vars_
        raise MiniError("parse")


class _Cell:
    def __init__(self, value=None, initialized=True):
        self.value, self.initialized = value, initialized


class _Slot(_Cell):
    pass


class _Closure:
    def __init__(self, param, body, env):
        self.param, self.body, self.env = param, body, env


def _lookup(env, name):
    for frame in reversed(env):
        if name in frame:
            v = frame[name]
            if isinstance(v, _Slot) and not v.initialized:
                raise MiniError("uninit")
            return v.value if isinstance(v, _Slot) else v
    raise MiniError("unbound")


def _is_int(v): return type(v) is int
def _is_str(v): return type(v) is str
def _is_bool(v): return type(v) is bool


def _eval(node, env):
    tag = node[0]
    if tag == "lit": return node[1]
    if tag == "var": return _lookup(env, node[1])
    if tag == "fun": return _Closure(node[1], node[2], list(env))
    if tag == "let":
        v = _eval(node[2], env); return _eval(node[3], env + [{node[1]: v}])
    if tag == "letrec":
        frame = {x: _Slot(initialized=False) for x in node[1]}; e = env + [frame]
        for x, rhs in zip(node[1], node[2]):
            frame[x].value = _eval(rhs, e); frame[x].initialized = True
        return _eval(node[3], e)
    if tag == "if":
        c = _eval(node[1], env)
        if not _is_bool(c): raise MiniError("type")
        return _eval(node[2] if c else node[3], env)
    if tag == "record":
        return {k: _eval(v, env) for k, v in node[1]}
    if tag == "field":
        r = _eval(node[1], env)
        if type(r) is not dict: raise MiniError("type")
        if node[2] not in r: raise MiniError("no_field")
        return r[node[2]]
    if tag == "app":
        fn = _eval(node[1], env); arg = _eval(node[2], env)
        if not isinstance(fn, _Closure): raise MiniError("type")
        return _eval(fn.body, fn.env + [{fn.param: arg}])
    if tag == "match":
        value = _eval(node[1], env)
        for p, body in node[2]:
            bindings = _match(p, value)
            if bindings is not None: return _eval(body, env + [bindings])
        raise MiniError("no_match")
    if tag == "un":
        v = _eval(node[2], env); op = node[1]
        if op == "ref": return _Cell(v)
        if op == "-":
            if not _is_int(v): raise MiniError("type")
            return -v
        if not isinstance(v, _Cell): raise MiniError("type")
        if not v.initialized: raise MiniError("uninit")
        return v.value
    if tag == "bin":
        op = node[1]
        a = _eval(node[2], env)
        if op == "&&":
            if not _is_bool(a): raise MiniError("type")
            if not a: return False
            b = _eval(node[3], env)
            if not _is_bool(b): raise MiniError("type")
            return b
        if op == "||":
            if not _is_bool(a): raise MiniError("type")
            if a: return True
            b = _eval(node[3], env)
            if not _is_bool(b): raise MiniError("type")
            return b
        b = _eval(node[3], env)
        if op == ":=":
            if not isinstance(a, _Cell): raise MiniError("type")
            a.value, a.initialized = b, True; return b
        if op in ("+", "-", "*", "/", "%"):
            if op == "*" and _is_str(a):
                if not _is_int(b): raise MiniError("type")
                return a * max(0, b)
            if not (_is_int(a) and _is_int(b)): raise MiniError("type")
            if op == "+": return a + b
            if op == "-": return a - b
            if op == "*": return a * b
            if b == 0: raise MiniError("div_zero")
            if op == "/":
                q = abs(a) // abs(b)
                return -q if (a < 0) != (b < 0) else q
            return a % b
        if op == "++":
            if not _is_str(a): raise MiniError("type")
            if _is_str(b): return a + b
            if _is_int(b): return a + str(b)
            if _is_bool(b): return a + ("true" if b else "false")
            raise MiniError("type")
        if op in ("<", "<=", ">", ">="):
            if not ((_is_int(a) and _is_int(b)) or (_is_str(a) and _is_str(b))):
                raise MiniError("type")
            if op == "<": return a < b
            if op == "<=": return a <= b
            if op == ">": return a > b
            return a >= b
        if op in ("==", "!="):
            if isinstance(a, _Cell) or isinstance(b, _Cell):
                if not (isinstance(a, _Cell) and isinstance(b, _Cell)): raise MiniError("type")
                same = a is b
            elif type(a) is type(b) and (type(a) in (int, str, bool)):
                same = a == b
            else: raise MiniError("type")
            return (not same) if op == "!=" else same
    raise MiniError("parse")


def _match(p, v):
    tag = p[0]
    if tag == "wild": return {}
    if tag == "bind": return {p[1]: v}
    if tag == "lit": return {} if type(v) is type(p[1]) and v == p[1] else None
    if type(v) is not dict: return None
    result = {}
    for f, sub in p[1]:
        if f not in v: return None
        got = _match(sub, v[f])
        if got is None: return None
        result.update(got)
    return result


def _convert(v):
    if type(v) in (int, str, bool): return v
    if type(v) is dict: return {k: _convert(x) for k, x in v.items()}
    if isinstance(v, _Closure): return "<fn>"
    if isinstance(v, _Cell): return "<ref>"
    raise MiniError("type")


def run(source):
    parser = _Parser(_lex(source))
    tree = parser.expr()
    if not parser.peek("EOF"):
        raise MiniError("parse")
    return _convert(_eval(tree, []))
