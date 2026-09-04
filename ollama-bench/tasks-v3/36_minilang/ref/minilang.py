"""minilang: a tiny expression/statement language."""
import re

__all__ = ["LangError", "LexError", "ParseError", "UndefinedNameError",
           "TypeMismatchError", "DivideByZeroError", "run", "evaluate"]


class LangError(Exception):
    kind = "lang"

    def __init__(self, line, detail):
        self.line = line
        self.detail = detail
        Exception.__init__(self, "%s error at line %d: %s" % (self.kind, line, detail))


class LexError(LangError):
    kind = "lex"


class ParseError(LangError):
    kind = "parse"


class UndefinedNameError(LangError):
    kind = "name"


class TypeMismatchError(LangError):
    kind = "type"


class DivideByZeroError(LangError):
    kind = "zero"


# --------------------------------------------------------------- lexer
KEYWORDS = {"let", "print", "if", "else", "while", "and", "or", "not",
            "true", "false"}

_TOK = re.compile(r"""
    (?P<ws>[ \t\r]+)
  | (?P<nl>\n)
  | (?P<comment>\#[^\n]*)
  | (?P<num>[0-9][0-9A-Za-z_.]*)
  | (?P<name>[A-Za-z_][A-Za-z_0-9]*)
  | (?P<str>")
  | (?P<op>\*\*|==|!=|<=|>=|[-+*/%<>=(){};])
  | (?P<bad>.)
""", re.VERBOSE)

_NUMOK = re.compile(r"[0-9]+(\.[0-9]+)?\Z")
_ESC = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}


def tokenize(src):
    """-> list of (type, value, line).  type in num/str/name/kw/op/eof."""
    toks = []
    i = 0
    line = 1
    n = len(src)
    while i < n:
        m = _TOK.match(src, i)
        g = m.lastgroup
        text = m.group()
        if g == "ws" or g == "comment":
            i = m.end()
            continue
        if g == "nl":
            line += 1
            i = m.end()
            continue
        if g == "num":
            if not _NUMOK.match(text):
                raise LexError(line, "malformed number '%s'" % text)
            toks.append(("num", float(text) if "." in text else int(text), line))
            i = m.end()
            continue
        if g == "name":
            toks.append(("kw" if text in KEYWORDS else "name", text, line))
            i = m.end()
            continue
        if g == "op":
            toks.append(("op", text, line))
            i = m.end()
            continue
        if g == "str":
            j = i + 1
            parts = []
            startline = line
            while True:
                if j >= n or src[j] == "\n":
                    raise LexError(startline, "unterminated string")
                c = src[j]
                if c == '"':
                    j += 1
                    break
                if c == "\\":
                    if j + 1 >= n or src[j + 1] == "\n":
                        raise LexError(startline, "unterminated string")
                    e = src[j + 1]
                    if e not in _ESC:
                        raise LexError(startline, "invalid escape '\\%s'" % e)
                    parts.append(_ESC[e])
                    j += 2
                    continue
                parts.append(c)
                j += 1
            toks.append(("str", "".join(parts), startline))
            i = j
            continue
        raise LexError(line, "unexpected character '%s'" % text)
    toks.append(("eof", "", line))
    return toks


# --------------------------------------------------------------- parser
CMP_OPS = ("==", "!=", "<", "<=", ">", ">=")


class Parser(object):
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i]

    def at(self, typ, val):
        tk = self.t[self.i]
        return tk[0] == typ and tk[1] == val

    def advance(self):
        tk = self.t[self.i]
        self.i += 1
        return tk

    def err(self):
        tk = self.t[self.i]
        if tk[0] == "eof":
            return ParseError(tk[2], "unexpected end of input")
        return ParseError(tk[2], "unexpected '%s'" % (tk[1],))

    def expect(self, typ, val):
        if not self.at(typ, val):
            raise self.err()
        return self.advance()

    # statements ---------------------------------------------------
    def program(self):
        stmts = []
        while self.peek()[0] != "eof":
            stmts.append(self.statement())
        return stmts

    def statement(self):
        tk = self.peek()
        if tk[0] == "kw":
            if tk[1] == "let":
                self.advance()
                nm = self.peek()
                if nm[0] != "name":
                    raise self.err()
                self.advance()
                self.expect("op", "=")
                e = self.expression()
                self.expect("op", ";")
                return ("let", nm[1], e, tk[2])
            if tk[1] == "print":
                self.advance()
                e = self.expression()
                self.expect("op", ";")
                return ("print", e)
            if tk[1] == "if":
                self.advance()
                self.expect("op", "(")
                c = self.expression()
                self.expect("op", ")")
                then = self.statement()
                els = None
                if self.at("kw", "else"):
                    self.advance()
                    els = self.statement()
                return ("if", c, then, els)
            if tk[1] == "while":
                self.advance()
                self.expect("op", "(")
                c = self.expression()
                self.expect("op", ")")
                return ("while", c, self.statement())
            raise self.err()
        if tk[0] == "op" and tk[1] == "{":
            self.advance()
            body = []
            while not self.at("op", "}"):
                if self.peek()[0] == "eof":
                    raise self.err()
                body.append(self.statement())
            self.advance()
            return ("block", body)
        if tk[0] == "name":
            self.advance()
            self.expect("op", "=")
            e = self.expression()
            self.expect("op", ";")
            return ("assign", tk[1], e, tk[2])
        raise self.err()

    # expressions --------------------------------------------------
    def expression(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.at("kw", "or"):
            self.advance()
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.at("kw", "and"):
            self.advance()
            node = ("and", node, self.not_expr())
        return node

    def not_expr(self):
        if self.at("kw", "not"):
            self.advance()
            return ("not", self.not_expr())
        return self.cmp_expr()

    def cmp_expr(self):
        node = self.add()
        tk = self.peek()
        if tk[0] == "op" and tk[1] in CMP_OPS:
            self.advance()
            right = self.add()
            node = ("cmp", tk[1], node, right, tk[2])
            nxt = self.peek()
            if nxt[0] == "op" and nxt[1] in CMP_OPS:
                raise self.err()
        return node

    def add(self):
        node = self.mul()
        while True:
            tk = self.peek()
            if tk[0] == "op" and tk[1] in ("+", "-"):
                self.advance()
                node = ("bin", tk[1], node, self.mul(), tk[2])
            else:
                return node

    def mul(self):
        node = self.unary()
        while True:
            tk = self.peek()
            if tk[0] == "op" and tk[1] in ("*", "/", "%"):
                self.advance()
                node = ("bin", tk[1], node, self.unary(), tk[2])
            else:
                return node

    def unary(self):
        tk = self.peek()
        if tk[0] == "op" and tk[1] in ("+", "-"):
            self.advance()
            return ("un", tk[1], self.unary(), tk[2])
        return self.power()

    def power(self):
        node = self.primary()
        tk = self.peek()
        if tk[0] == "op" and tk[1] == "**":
            self.advance()
            return ("bin", "**", node, self.unary(), tk[2])
        return node

    def primary(self):
        tk = self.peek()
        if tk[0] == "num" or tk[0] == "str":
            self.advance()
            return ("const", tk[1])
        if tk[0] == "name":
            self.advance()
            return ("name", tk[1], tk[2])
        if tk[0] == "kw" and tk[1] in ("true", "false"):
            self.advance()
            return ("const", tk[1] == "true")
        if tk[0] == "op" and tk[1] == "(":
            self.advance()
            e = self.expression()
            self.expect("op", ")")
            return e
        raise self.err()


def parse(src):
    return Parser(tokenize(src)).program()


# --------------------------------------------------------------- runtime
class Scope(object):
    __slots__ = ("v", "parent")

    def __init__(self, parent=None):
        self.v = {}
        self.parent = parent


def is_num(x):
    return (x.__class__ is int) or (x.__class__ is float)


def truthy(x):
    if x.__class__ is bool:
        return x
    if x.__class__ is int:
        return x != 0
    if x.__class__ is float:
        return x != 0.0
    if x.__class__ is str:
        return x != ""
    return True


def render(x):
    if x.__class__ is bool:
        return "true" if x else "false"
    if x.__class__ is str:
        return x
    return repr(x)


def ev(node, sc):
    k = node[0]
    if k == "const":
        return node[1]
    if k == "name":
        s = sc
        nm = node[1]
        while s is not None:
            v = s.v
            if nm in v:
                return v[nm]
            s = s.parent
        raise UndefinedNameError(node[2], "undefined variable '%s'" % nm)
    if k == "bin":
        op = node[1]
        a = ev(node[2], sc)
        b = ev(node[3], sc)
        line = node[4]
        if op == "+":
            if a.__class__ is str and b.__class__ is str:
                return a + b
            if is_num(a) and is_num(b):
                return a + b
            raise TypeMismatchError(line, "bad operand types for '+'")
        if not (is_num(a) and is_num(b)):
            raise TypeMismatchError(line, "bad operand types for '%s'" % op)
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise DivideByZeroError(line, "division by zero")
            return a / b
        if op == "%":
            if b == 0:
                raise DivideByZeroError(line, "modulo by zero")
            return a % b
        # '**'
        if a == 0 and b < 0:
            raise DivideByZeroError(line, "zero to a negative power")
        r = a ** b
        if a.__class__ is int and b.__class__ is int and b < 0:
            return float(r)
        return r
    if k == "cmp":
        op = node[1]
        a = ev(node[2], sc)
        b = ev(node[3], sc)
        if op == "==" or op == "!=":
            if is_num(a) and is_num(b):
                eq = a == b
            elif a.__class__ is b.__class__:
                eq = a == b
            else:
                eq = False
            return eq if op == "==" else (not eq)
        ok = (is_num(a) and is_num(b)) or (a.__class__ is str and b.__class__ is str)
        if not ok:
            raise TypeMismatchError(node[4], "bad operand types for '%s'" % op)
        if op == "<":
            return a < b
        if op == "<=":
            return a <= b
        if op == ">":
            return a > b
        return a >= b
    if k == "un":
        a = ev(node[2], sc)
        if not is_num(a):
            raise TypeMismatchError(node[3], "bad operand type for unary '%s'" % node[1])
        return -a if node[1] == "-" else a
    if k == "not":
        return not truthy(ev(node[1], sc))
    if k == "and":
        a = ev(node[1], sc)
        return ev(node[2], sc) if truthy(a) else a
    if k == "or":
        a = ev(node[1], sc)
        return a if truthy(a) else ev(node[2], sc)
    raise AssertionError(k)


def exec_stmt(node, sc, out):
    k = node[0]
    if k == "print":
        out.append(render(ev(node[1], sc)))
        return
    if k == "let":
        val = ev(node[2], sc)
        if node[1] in sc.v:
            raise UndefinedNameError(node[3], "duplicate declaration '%s'" % node[1])
        sc.v[node[1]] = val
        return
    if k == "assign":
        val = ev(node[2], sc)
        s = sc
        nm = node[1]
        while s is not None:
            if nm in s.v:
                s.v[nm] = val
                return
            s = s.parent
        raise UndefinedNameError(node[3], "undefined variable '%s'" % nm)
    if k == "block":
        inner = Scope(sc)
        for st in node[1]:
            exec_stmt(st, inner, out)
        return
    if k == "if":
        if truthy(ev(node[1], sc)):
            exec_stmt(node[2], sc, out)
        elif node[3] is not None:
            exec_stmt(node[3], sc, out)
        return
    if k == "while":
        cond = node[1]
        body = node[2]
        while truthy(ev(cond, sc)):
            exec_stmt(body, sc, out)
        return
    raise AssertionError(k)


def run(src):
    prog = parse(src)
    out = []
    glob = Scope(None)
    for st in prog:
        exec_stmt(st, glob, out)
    return out


def evaluate(src):
    p = Parser(tokenize(src))
    node = p.expression()
    if p.peek()[0] != "eof":
        raise p.err()
    return ev(node, Scope(None))
