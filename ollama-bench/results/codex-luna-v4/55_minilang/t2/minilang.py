"""A small, hand-written lexer, parser, and evaluator for MiniLang."""

class MiniError(Exception):
    _kinds = {"parse", "dup_field", "dup_binding", "unbound", "uninit",
              "type", "div_zero", "no_field", "no_match"}

    def __init__(self, kind):
        if kind not in self._kinds:
            kind = "parse"
        self.kind = kind
        super().__init__(kind)


_WORDS = {"let", "letrec", "and", "in", "if", "then", "else", "fun",
          "match", "with", "end", "ref", "true", "false"}
_OPS = ("->", ":=", "==", "!=", "<=", ">=", "&&", "||", "++",
        "+", "-", "*", "/", "%", "<", ">", "=", "(", ")", "{", "}",
        ",", ".", "|", "!")


def _is_letter(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def _is_digit(c):
    return "0" <= c <= "9"


def _lex(s):
    if not isinstance(s, str):
        raise MiniError("parse")
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
        elif _is_digit(c):
            j = i + 1
            while j < n and _is_digit(s[j]):
                j += 1
            if c == "0" and j > i + 1:
                raise MiniError("parse")
            number = 0
            for digit in s[i:j]:
                number = number * 10 + ord(digit) - ord("0")
            out.append(("INT", number))
            i = j
        elif c == '"':
            j = i + 1
            while j < n and s[j] not in '"\\\r\n':
                j += 1
            if j >= n or s[j] != '"':
                raise MiniError("parse")
            out.append(("STR", s[i + 1:j]))
            i = j + 1
        elif _is_letter(c):
            j = i + 1
            while j < n and (_is_letter(s[j]) or _is_digit(s[j])):
                j += 1
            word = s[i:j]
            if word in _WORDS:
                out.append((word, word))
            elif word == "_":
                out.append(("_", word))
            else:
                out.append(("ID", word))
            i = j
        else:
            op = next((x for x in _OPS if s.startswith(x, i)), None)
            if op is None:
                raise MiniError("parse")
            out.append((op, op))
            i += len(op)
    out.append(("EOF", None))
    return out


class _Parser:
    def __init__(self, source):
        self.t = _lex(source)
        self.i = 0

    def peek(self, kind=None):
        x = self.t[self.i]
        return x[0] == kind if kind is not None else x

    def take(self, kind):
        if not self.peek(kind):
            raise MiniError("parse")
        x = self.t[self.i]
        self.i += 1
        return x[1]

    def ident(self):
        return self.take("ID")

    def expr(self):
        if self.peek("let"):
            self.take("let"); name = self.ident(); self.take("=")
            a = self.expr(); self.take("in"); b = self.expr()
            return ("let", name, a, b)
        if self.peek("letrec"):
            self.take("letrec"); binds = []
            while True:
                name = self.ident(); self.take("="); binds.append((name, self.expr()))
                if not self.peek("and"):
                    break
                self.take("and")
            self.take("in"); body = self.expr()
            names = [x[0] for x in binds]
            if len(names) != len(set(names)):
                raise MiniError("dup_binding")
            return ("letrec", binds, body)
        if self.peek("if"):
            self.take("if"); c = self.expr(); self.take("then"); a = self.expr()
            self.take("else"); b = self.expr(); return ("if", c, a, b)
        if self.peek("fun"):
            self.take("fun"); p = self.ident(); self.take("->")
            return ("fun", p, self.expr())
        if self.peek("match"):
            self.take("match"); subject = self.expr(); self.take("with")
            arms = []
            if not self.peek("|"):
                raise MiniError("parse")
            while self.peek("|"):
                self.take("|"); pat = self.pattern(); _pat_vars(pat); self.take("->")
                arms.append((pat, self.expr()))
            self.take("end")
            return ("match", subject, arms)
        return self.assign()

    def assign(self):
        a = self.orx()
        if self.peek(":="):
            self.take(":="); return ("assign", a, self.expr())
        return a

    def orx(self):
        a = self.andx()
        while self.peek("||"):
            self.take("||"); a = ("bin", "||", a, self.andx())
        return a

    def andx(self):
        a = self.cmpx()
        while self.peek("&&"):
            self.take("&&"); a = ("bin", "&&", a, self.cmpx())
        return a

    def cmpx(self):
        a = self.catx()
        if self.peek() [0] in ("==", "!=", "<", "<=", ">", ">="):
            op = self.take(self.peek()[0]); a = ("bin", op, a, self.catx())
            if self.peek() [0] in ("==", "!=", "<", "<=", ">", ">="):
                raise MiniError("parse")
        return a

    def catx(self):
        a = self.addx()
        if self.peek("++"):
            self.take("++"); return ("bin", "++", a, self.catx())
        return a

    def addx(self):
        a = self.mulx()
        while self.peek()[0] in ("+", "-"):
            op = self.take(self.peek()[0]); a = ("bin", op, a, self.mulx())
        return a

    def mulx(self):
        a = self.unary()
        while self.peek()[0] in ("*", "/", "%"):
            op = self.take(self.peek()[0]); a = ("bin", op, a, self.unary())
        return a

    def unary(self):
        if self.peek()[0] in ("-", "!", "ref"):
            op = self.take(self.peek()[0]); return ("unary", op, self.unary())
        return self.app()

    def app(self):
        a = self.postfix()
        while self.peek()[0] in ("INT", "STR", "true", "false", "ID", "(", "{"):
            a = ("app", a, self.postfix())
        return a

    def postfix(self):
        a = self.atom()
        while self.peek("."):
            self.take("."); a = ("field", a, self.ident())
        return a

    def atom(self):
        if self.peek("INT"): return ("lit", self.take("INT"))
        if self.peek("STR"): return ("lit", self.take("STR"))
        if self.peek("true"): self.take("true"); return ("lit", True)
        if self.peek("false"): self.take("false"); return ("lit", False)
        if self.peek("ID"): return ("var", self.take("ID"))
        if self.peek("("):
            self.take("("); a = self.expr(); self.take(")"); return a
        if self.peek("{"):
            self.take("{"); fields = []; names = set()
            if not self.peek("}"):
                while True:
                    name = self.ident(); self.take("="); fields.append((name, self.expr()))
                    names.add(name)
                    if not self.peek(","): break
                    self.take(",")
            self.take("}")
            if len(names) != len(fields):
                raise MiniError("dup_field")
            return ("record", fields)
        raise MiniError("parse")

    def pattern(self):
        if self.peek("_"): self.take("_"); return ("wild",)
        if self.peek("INT"): return ("plit", self.take("INT"))
        if self.peek("STR"): return ("plit", self.take("STR"))
        if self.peek("true"): self.take("true"); return ("plit", True)
        if self.peek("false"): self.take("false"); return ("plit", False)
        if self.peek("ID"): return ("bind", self.take("ID"))
        if self.peek("{"):
            self.take("{"); fields = []; names = set(); vars_ = set()
            if not self.peek("}"):
                while True:
                    name = self.ident(); self.take("="); p = self.pattern()
                    names.add(name); fields.append((name, p))
                    if not self.peek(","): break
                    self.take(",")
            self.take("}")
            if len(names) != len(fields):
                raise MiniError("dup_field")
            vars_ = set()
            for _, q in fields:
                qvars = _pat_vars(q)
                if vars_ & qvars:
                    raise MiniError("dup_binding")
                vars_ |= qvars
            return ("prec", fields, vars_)
        raise MiniError("parse")


def _pat_vars(p):
    if p[0] == "bind": return {p[1]}
    if p[0] == "prec":
        r = set()
        for _, q in p[1]: r |= _pat_vars(q)
        if len(r) != sum(len(_pat_vars(q)) for _, q in p[1]):
            raise MiniError("dup_binding")
        return r
    return set()


class _Cell:
    def __init__(self, value): self.value = value
class _Slot:
    def __init__(self, value): self.value = value
class _Closure:
    def __init__(self, param, body, env): self.param, self.body, self.env = param, body, env
class _Env:
    def __init__(self, parent=None): self.parent, self.data = parent, {}
    def get(self, name):
        if name in self.data: return self.data[name]
        if self.parent is not None: return self.parent.get(name)
        raise MiniError("unbound")


_UNINIT = object()
def _value(env, name):
    x = env.get(name)
    if isinstance(x, _Slot):
        if x.value is _UNINIT: raise MiniError("uninit")
        return x.value
    return x

def _bool(x): return type(x) is bool
def _int(x): return type(x) is int

def _decimal(n):
    if n == 0:
        return "0"
    sign = "" if n > 0 else "-"
    n = abs(n); chars = []
    while n:
        chars.append(chr(ord("0") + n % 10)); n //= 10
    return sign + "".join(reversed(chars))

def _evaluate(a, env):
    k = a[0]
    if k == "lit": return a[1]
    if k == "var": return _value(env, a[1])
    if k == "fun": return _Closure(a[1], a[2], env)
    if k == "let":
        v = _evaluate(a[2], env); e = _Env(env); e.data[a[1]] = v; return _evaluate(a[3], e)
    if k == "letrec":
        e = _Env(env); cells = {}
        for name, _ in a[1]: cells[name] = _Slot(_UNINIT); e.data[name] = cells[name]
        for name, rhs in a[1]: cells[name].value = _evaluate(rhs, e)
        return _evaluate(a[2], e)
    if k == "if":
        c = _evaluate(a[1], env)
        if not _bool(c): raise MiniError("type")
        return _evaluate(a[2] if c else a[3], env)
    if k == "record":
        return {name: _evaluate(x, env) for name, x in a[1]}
    if k == "field":
        r = _evaluate(a[1], env)
        if not isinstance(r, dict): raise MiniError("type")
        if a[2] not in r: raise MiniError("no_field")
        return r[a[2]]
    if k == "app":
        f = _evaluate(a[1], env); v = _evaluate(a[2], env)
        if not isinstance(f, _Closure): raise MiniError("type")
        e = _Env(f.env); e.data[f.param] = v; return _evaluate(f.body, e)
    if k == "unary":
        if a[1] == "ref": return _Cell(_evaluate(a[2], env))
        v = _evaluate(a[2], env)
        if a[1] == "-":
            if not _int(v): raise MiniError("type")
            return -v
        if not isinstance(v, _Cell): raise MiniError("type")
        return v.value
    if k == "assign":
        left = _evaluate(a[1], env); right = _evaluate(a[2], env)
        if not isinstance(left, _Cell): raise MiniError("type")
        left.value = right; return right
    if k == "bin": return _binary(a[1], a[2], a[3], env)
    if k == "match":
        v = _evaluate(a[1], env)
        for p, body in a[2]:
            b = {}; 
            if _match(p, v, b):
                e = _Env(env); e.data.update(b); return _evaluate(body, e)
        raise MiniError("no_match")
    raise MiniError("parse")

def _binary(op, left, right, env):
    x = _evaluate(left, env)
    if op == "&&":
        if not _bool(x): raise MiniError("type")
        if not x: return False
        y = _evaluate(right, env)
        if not _bool(y): raise MiniError("type")
        return y
    if op == "||":
        if not _bool(x): raise MiniError("type")
        if x: return True
        y = _evaluate(right, env)
        if not _bool(y): raise MiniError("type")
        return y
    y = _evaluate(right, env)
    if op in ("+", "-", "*"):
        if op == "*" and type(x) is str:
            if not _int(y): raise MiniError("type")
            return x * max(0, y)
        if not (_int(x) and _int(y)): raise MiniError("type")
        return x + y if op == "+" else x - y if op == "-" else x * y
    if op in ("/", "%"):
        if not (_int(x) and _int(y)): raise MiniError("type")
        if y == 0: raise MiniError("div_zero")
        q = (abs(x) // abs(y)) * (-1 if (x < 0) != (y < 0) else 1)
        return q if op == "/" else x - (x // y) * y
    if op == "++":
        if type(x) is not str or type(y) not in (str, int, bool): raise MiniError("type")
        return x + (y if type(y) is str else ("true" if y else "false") if type(y) is bool else _decimal(y))
    if op in ("<", "<=", ">", ">="):
        if not ((type(x) is type(y) is int) or (type(x) is type(y) is str)): raise MiniError("type")
        return {"<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y}[op]
    if op in ("==", "!="):
        if type(x) is type(y) and type(x) in (int, str, bool): z = x == y
        elif isinstance(x, _Cell) and isinstance(y, _Cell): z = x is y
        else: raise MiniError("type")
        return z if op == "==" else not z
    raise MiniError("parse")

def _match(p, v, binds):
    if p[0] == "wild": return True
    if p[0] == "bind": binds[p[1]] = v; return True
    if p[0] == "plit": return type(v) is type(p[1]) and v == p[1]
    if not isinstance(v, dict): return False
    for name, q in p[1]:
        if name not in v or not _match(q, v[name], binds): return False
    return True

def _convert(v):
    if isinstance(v, _Closure): return "<fn>"
    if isinstance(v, _Cell): return "<ref>"
    if isinstance(v, dict): return {k: _convert(x) for k, x in v.items()}
    return v

def run(source):
    p = _Parser(source); tree = p.expr()
    if not p.peek("EOF"): raise MiniError("parse")
    return _convert(_evaluate(tree, _Env()))
