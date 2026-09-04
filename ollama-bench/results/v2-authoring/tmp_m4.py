"""A tiny expression-language interpreter."""

KEYWORDS = {"let", "in", "if", "then", "else", "fn"}
CMP_OPS = {"==", "!=", "<", "<=", ">", ">="}


class InterpError(Exception):
    """Raised for every parse error and runtime error."""


def tokenize(src):
    toks = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < n and src[j].isdigit():
                j += 1
            toks.append(("int", int(src[i:j])))
            i = j
        elif c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == '\\' or src[j] == '\n':
                    raise InterpError("bad character in string literal")
                j += 1
            if j >= n:
                raise InterpError("unterminated string literal")
            toks.append(("str", src[i + 1:j]))
            i = j + 1
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (src[j].isalnum() or src[j] == '_'):
                j += 1
            w = src[i:j]
            toks.append(("kw" if w in KEYWORDS else "id", w))
            i = j
        elif src[i:i + 2] in ("->", "==", "!=", "<=", ">="):
            toks.append(("op", src[i:i + 2]))
            i += 2
        elif c in "+-*/()<>=":
            toks.append(("op", c))
            i += 1
        else:
            raise InterpError(f"unexpected character {c!r}")
    toks.append(("eof", None))
    return toks


class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self):
        return self.toks[self.i]

    def advance(self):
        t = self.toks[self.i]
        self.i += 1
        return t

    def expect_op(self, op):
        t = self.advance()
        if t != ("op", op):
            raise InterpError(f"expected {op!r}")
        return t

    def expect_ident(self):
        t = self.advance()
        if t[0] != "id":
            raise InterpError("expected identifier")
        return t[1]

    def expr(self):
        t = self.peek()
        if t[0] == "kw":
            if t[1] == "if":
                return self.ifexpr()
            if t[1] == "let":
                return self.letexpr()
            if t[1] == "fn":
                return self.fnexpr()
        return self.cmpexpr()

    def ifexpr(self):
        self.advance()  # if
        c = self.expr()
        t = self.advance()
        if t != ("kw", "then"):
            raise InterpError("expected 'then'")
        a = self.expr()
        t = self.advance()
        if t != ("kw", "else"):
            raise InterpError("expected 'else'")
        b = self.expr()
        return ("if", c, a, b)

    def letexpr(self):
        self.advance()  # let
        name = self.expect_ident()
        self.expect_op("=")
        e1 = self.expr()
        t = self.advance()
        if t != ("kw", "in"):
            raise InterpError("expected 'in'")
        e2 = self.expr()
        return ("let", name, e1, e2)

    def fnexpr(self):
        self.advance()  # fn
        name = self.expect_ident()
        t = self.advance()
        if t != ("op", "->"):
            raise InterpError("expected '->'")
        return ("fn", name, self.expr())

    def cmpexpr(self):
        l = self.addexpr()
        t = self.peek()
        if t[0] == "op" and t[1] in CMP_OPS:
            op = self.advance()[1]
            r = self.addexpr()
            t2 = self.peek()
            if t2[0] == "op" and t2[1] in CMP_OPS:
                raise InterpError("chained comparison")
            return ("cmp", op, l, r)
        return l

    def addexpr(self):
        l = self.mulexpr()
        while True:
            t = self.peek()
            if t[0] == "op" and t[1] in ("+", "-"):
                op = self.advance()[1]
                l = ("bin", op, l, self.mulexpr())
            else:
                return l

    def mulexpr(self):
        l = self.appexpr()
        while True:
            t = self.peek()
            if t[0] == "op" and t[1] in ("*", "/"):
                op = self.advance()[1]
                l = ("bin", op, l, self.appexpr())
            else:
                return l

    def appexpr(self):
        l = self.atom()
        while True:
            t = self.peek()
            if t[0] in ("int", "str", "id") or (t == ("op", "(")):
                l = ("app", l, self.atom())
            else:
                return l

    def atom(self):
        t = self.advance()
        if t[0] == "int":
            return ("int", t[1])
        if t[0] == "str":
            return ("str", t[1])
        if t[0] == "id":
            return ("var", t[1])
        if t == ("op", "("):
            e = self.expr()
            t = self.advance()
            if t != ("op", ")"):
                raise InterpError("expected ')'")
            return e
        raise InterpError("expected an expression")


def trunc_div(l, r):
    if r == 0:
        raise InterpError("division by zero")
    q = abs(l) // abs(r)
    return q if (l >= 0) == (r >= 0) else -q


def ev(node, env):
    k = node[0]
    if k in ("int", "str"):
        return node[1]
    if k == "var":
        if node[1] not in env:
            raise InterpError(f"unbound identifier {node[1]!r}")
        return env[node[1]]
    if k == "let":
        v = ev(node[2], env)
        return ev(node[3], {**env, node[1]: v})
    if k == "fn":
        captured = GLOBAL_ENV
        param, body = node[1], node[2]

        def fn(arg):
            return ev(body, {**captured, param: arg})
        return fn
    if k == "app":
        f = ev(node[1], env)
        a = ev(node[2], env)
        if not callable(f):
            raise InterpError("applying a non-function")
        return f(a)
    if k == "if":
        c = ev(node[1], env)
        if not isinstance(c, bool):
            raise InterpError("if condition must be a boolean")
        return ev(node[2] if c else node[3], env)
    if k == "cmp":
        op = node[1]
        l = ev(node[2], env)
        r = ev(node[3], env)
        if isinstance(l, bool) or isinstance(r, bool):
            raise InterpError("booleans cannot be compared")
        if op in ("==", "!="):
            same = ((isinstance(l, int) and isinstance(r, int)) or
                    (isinstance(l, str) and isinstance(r, str)))
            if not same:
                raise InterpError("type mismatch in comparison")
            return (l == r) if op == "==" else (l != r)
        if not (isinstance(l, int) and isinstance(r, int)):
            raise InterpError("ordering comparison requires integers")
        return {"<": l < r, "<=": l <= r, ">": l > r, ">=": l >= r}[op]
    if k == "bin":
        op = node[1]
        l = ev(node[2], env)
        r = ev(node[3], env)
        if (not isinstance(l, int) or isinstance(l, bool) or
                not isinstance(r, int) or isinstance(r, bool)):
            raise InterpError("arithmetic requires integers")
        if op == "+":
            return l + r
        if op == "-":
            return l - r
        if op == "*":
            return l * r
        return trunc_div(l, r)
    raise InterpError("internal error")


GLOBAL_ENV = {}
def evaluate(source: str):
    """Parse and evaluate one expression of the language."""
    p = Parser(tokenize(source))
    ast = p.expr()
    if p.peek()[0] != "eof":
        raise InterpError("unexpected trailing input")
    GLOBAL_ENV.clear(); GLOBAL_ENV.update({}); r = ev(ast, {}); return r