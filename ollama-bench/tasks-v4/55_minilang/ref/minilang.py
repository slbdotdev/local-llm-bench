"""minilang reference implementation.

Strategy: hand-written recursive-descent parser (one function per precedence
level) producing tuple ASTs, evaluated over a linked chain of Env frames whose
slots are mutable Box objects (so letrec slots can start uninitialised).
"""

KEYWORDS = frozenset(["let", "letrec", "and", "in", "if", "then", "else",
                      "fun", "match", "with", "end", "ref", "true", "false"])
OP2 = ("->", ":=", "==", "!=", "<=", ">=", "&&", "||", "++")
OP1 = "+-*/%<>=(){},.|!"

CMPOPS = ("==", "!=", "<", "<=", ">", ">=")


class MiniError(Exception):
    def __init__(self, kind, msg=""):
        Exception.__init__(self, ("%s: %s" % (kind, msg)) if msg else kind)
        self.kind = kind


class Closure(object):
    __slots__ = ("param", "body", "env")

    def __init__(self, param, body, env):
        self.param = param
        self.body = body
        self.env = env


class Cell(object):
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v


class Box(object):
    __slots__ = ("v", "ready")

    def __init__(self, v, ready):
        self.v = v
        self.ready = ready


class Env(object):
    __slots__ = ("slots", "parent")

    def __init__(self, slots, parent):
        self.slots = slots
        self.parent = parent

    def find(self, name):
        e = self
        while e is not None:
            b = e.slots.get(name)
            if b is not None:
                return b
            e = e.parent
        return None


# ---------------------------------------------------------------- lexer
def _digit(c):
    return "0" <= c <= "9"


def _alpha(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def lex(s):
    toks = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
            continue
        if _digit(c):
            j = i
            while j < n and _digit(s[j]):
                j += 1
            if j - i > 1 and s[i] == "0":
                raise MiniError("parse", "leading zero")
            toks.append(("INT", int(s[i:j])))
            i = j
            continue
        if _alpha(c):
            j = i
            while j < n and (_alpha(s[j]) or _digit(s[j])):
                j += 1
            w = s[i:j]
            i = j
            if w == "_":
                toks.append(("WILD", "_"))
            elif w in KEYWORDS:
                toks.append(("KW", w))
            else:
                toks.append(("IDENT", w))
            continue
        if c == '"':
            j = i + 1
            while True:
                if j >= n:
                    raise MiniError("parse", "unterminated string")
                if s[j] == '"':
                    break
                if s[j] == "\\" or s[j] == "\n":
                    raise MiniError("parse", "bad character in string")
                j += 1
            toks.append(("STR", s[i + 1:j]))
            i = j + 1
            continue
        if s[i:i + 2] in OP2:
            toks.append(("OP", s[i:i + 2]))
            i += 2
            continue
        if c in OP1:
            toks.append(("OP", c))
            i += 1
            continue
        raise MiniError("parse", "bad character %r" % c)
    toks.append(("EOF", None))
    return toks


# ---------------------------------------------------------------- parser
class Parser(object):
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i]

    def at_op(self, *vals):
        k, v = self.t[self.i]
        return k == "OP" and v in vals

    def at_kw(self, *vals):
        k, v = self.t[self.i]
        return k == "KW" and v in vals

    def eat_op(self, v):
        if not self.at_op(v):
            raise MiniError("parse", "expected %r" % v)
        self.i += 1

    def eat_kw(self, v):
        if not self.at_kw(v):
            raise MiniError("parse", "expected %r" % v)
        self.i += 1

    def ident(self):
        k, v = self.t[self.i]
        if k != "IDENT":
            raise MiniError("parse", "expected identifier")
        self.i += 1
        return v

    # ---- levels
    def expr(self):
        k, v = self.peek()
        if k == "KW":
            if v == "let":
                self.i += 1
                name = self.ident()
                self.eat_op("=")
                rhs = self.expr()
                self.eat_kw("in")
                return ("let", name, rhs, self.expr())
            if v == "letrec":
                self.i += 1
                names = []
                rhss = []
                while True:
                    names.append(self.ident())
                    self.eat_op("=")
                    rhss.append(self.expr())
                    if self.at_kw("and"):
                        self.i += 1
                        continue
                    break
                self.eat_kw("in")
                body = self.expr()
                if len(set(names)) != len(names):
                    raise MiniError("dup_binding", "letrec")
                return ("letrec", names, rhss, body)
            if v == "if":
                self.i += 1
                c = self.expr()
                self.eat_kw("then")
                a = self.expr()
                self.eat_kw("else")
                return ("if", c, a, self.expr())
            if v == "fun":
                self.i += 1
                p = self.ident()
                self.eat_op("->")
                return ("fun", p, self.expr())
            if v == "match":
                self.i += 1
                subj = self.expr()
                self.eat_kw("with")
                arms = []
                while self.at_op("|"):
                    self.i += 1
                    pat = self.pattern()
                    names = []
                    _pat_vars(pat, names)
                    if len(set(names)) != len(names):
                        raise MiniError("dup_binding", "pattern")
                    self.eat_op("->")
                    arms.append((pat, self.expr()))
                if not arms:
                    raise MiniError("parse", "match needs at least one arm")
                self.eat_kw("end")
                return ("match", subj, arms)
        return self.assign()

    def assign(self):
        left = self.orx()
        if self.at_op(":="):
            self.i += 1
            return ("bin", ":=", left, self.expr())
        return left

    def orx(self):
        left = self.andx()
        while self.at_op("||"):
            self.i += 1
            left = ("or", left, self.andx())
        return left

    def andx(self):
        left = self.cmpx()
        while self.at_op("&&"):
            self.i += 1
            left = ("and", left, self.cmpx())
        return left

    def cmpx(self):
        left = self.catx()
        if self.at_op(*CMPOPS):
            op = self.peek()[1]
            self.i += 1
            right = self.catx()
            if self.at_op(*CMPOPS):
                raise MiniError("parse", "chained comparison")
            return ("bin", op, left, right)
        return left

    def catx(self):
        left = self.addx()
        if self.at_op("++"):
            self.i += 1
            return ("bin", "++", left, self.catx())
        return left

    def addx(self):
        left = self.mulx()
        while self.at_op("+", "-"):
            op = self.peek()[1]
            self.i += 1
            left = ("bin", op, left, self.mulx())
        return left

    def mulx(self):
        left = self.unary()
        while self.at_op("*", "/", "%"):
            op = self.peek()[1]
            self.i += 1
            left = ("bin", op, left, self.unary())
        return left

    def unary(self):
        if self.at_op("-"):
            self.i += 1
            return ("neg", self.unary())
        if self.at_op("!"):
            self.i += 1
            return ("deref", self.unary())
        if self.at_kw("ref"):
            self.i += 1
            return ("mkref", self.unary())
        return self.app()

    def _starts_atom(self):
        k, v = self.peek()
        if k in ("INT", "STR", "IDENT"):
            return True
        if k == "KW" and v in ("true", "false"):
            return True
        if k == "OP" and v in ("(", "{"):
            return True
        return False

    def app(self):
        left = self.postfix()
        while self._starts_atom():
            left = ("app", left, self.postfix())
        return left

    def postfix(self):
        e = self.atom()
        while self.at_op("."):
            self.i += 1
            e = ("field", e, self.ident())
        return e

    def atom(self):
        k, v = self.peek()
        if k == "INT":
            self.i += 1
            return ("int", v)
        if k == "STR":
            self.i += 1
            return ("str", v)
        if k == "IDENT":
            self.i += 1
            return ("var", v)
        if k == "KW" and v in ("true", "false"):
            self.i += 1
            return ("bool", v == "true")
        if k == "OP" and v == "(":
            self.i += 1
            e = self.expr()
            self.eat_op(")")
            return e
        if k == "OP" and v == "{":
            self.i += 1
            names = []
            vals = []
            if not self.at_op("}"):
                while True:
                    names.append(self.ident())
                    self.eat_op("=")
                    vals.append(self.expr())
                    if self.at_op(","):
                        self.i += 1
                        continue
                    break
            self.eat_op("}")
            if len(set(names)) != len(names):
                raise MiniError("dup_field", "record literal")
            return ("rec", names, vals)
        raise MiniError("parse", "expected an atom")

    def pattern(self):
        k, v = self.peek()
        if k == "WILD":
            self.i += 1
            return ("pwild",)
        if k == "INT":
            self.i += 1
            return ("pint", v)
        if k == "STR":
            self.i += 1
            return ("pstr", v)
        if k == "KW" and v in ("true", "false"):
            self.i += 1
            return ("pbool", v == "true")
        if k == "IDENT":
            self.i += 1
            return ("pvar", v)
        if k == "OP" and v == "{":
            self.i += 1
            names = []
            pats = []
            if not self.at_op("}"):
                while True:
                    names.append(self.ident())
                    self.eat_op("=")
                    pats.append(self.pattern())
                    if self.at_op(","):
                        self.i += 1
                        continue
                    break
            self.eat_op("}")
            if len(set(names)) != len(names):
                raise MiniError("dup_field", "record pattern")
            return ("prec", names, pats)
        raise MiniError("parse", "expected a pattern")


def _pat_vars(p, out):
    if p[0] == "pvar":
        out.append(p[1])
    elif p[0] == "prec":
        for sub in p[2]:
            _pat_vars(sub, out)


def parse(src):
    p = Parser(lex(src))
    e = p.expr()
    if p.peek()[0] != "EOF":
        raise MiniError("parse", "trailing input")
    return e


# ---------------------------------------------------------------- values
def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_bool(v):
    return isinstance(v, bool)


def to_str(v):
    if isinstance(v, str):
        return v
    if is_bool(v):
        return "true" if v else "false"
    if is_int(v):
        return str(v)
    raise MiniError("type", "cannot convert to string")


def tdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


# ---------------------------------------------------------------- eval
def ev(node, env):
    t = node[0]
    if t == "int" or t == "str" or t == "bool":
        return node[1]
    if t == "var":
        b = env.find(node[1])
        if b is None:
            raise MiniError("unbound", node[1])
        if not b.ready:
            raise MiniError("uninit", node[1])
        return b.v
    if t == "rec":
        d = {}
        for name, sub in zip(node[1], node[2]):
            d[name] = ev(sub, env)
        return d
    if t == "field":
        base = ev(node[1], env)
        if not isinstance(base, dict):
            raise MiniError("type", "field access on non-record")
        if node[2] not in base:
            raise MiniError("no_field", node[2])
        return base[node[2]]
    if t == "fun":
        return Closure(node[1], node[2], env)
    if t == "app":
        f = ev(node[1], env)
        a = ev(node[2], env)
        if not isinstance(f, Closure):
            raise MiniError("type", "calling a non-function")
        return ev(f.body, Env({f.param: Box(a, True)}, f.env))
    if t == "neg":
        v = ev(node[1], env)
        if not is_int(v):
            raise MiniError("type", "negation of non-integer")
        return -v
    if t == "deref":
        v = ev(node[1], env)
        if not isinstance(v, Cell):
            raise MiniError("type", "dereference of non-ref")
        return v.v
    if t == "mkref":
        return Cell(ev(node[1], env))
    if t == "if":
        c = ev(node[1], env)
        if not is_bool(c):
            raise MiniError("type", "condition is not a boolean")
        return ev(node[2] if c else node[3], env)
    if t == "and" or t == "or":
        l = ev(node[1], env)
        if not is_bool(l):
            raise MiniError("type", "boolean operator on non-boolean")
        if (t == "and") != l:          # and+false, or+true
            return l
        r = ev(node[2], env)
        if not is_bool(r):
            raise MiniError("type", "boolean operator on non-boolean")
        return r
    if t == "let":
        v = ev(node[2], env)
        return ev(node[3], Env({node[1]: Box(v, True)}, env))
    if t == "letrec":
        slots = {}
        for name in node[1]:
            slots[name] = Box(None, False)
        inner = Env(slots, env)
        for name, rhs in zip(node[1], node[2]):
            v = ev(rhs, inner)
            slots[name].v = v
            slots[name].ready = True
        return ev(node[3], inner)
    if t == "match":
        subj = ev(node[1], env)
        for pat, body in node[2]:
            binds = {}
            if match_pat(pat, subj, binds):
                return ev(body, Env(dict((k, Box(v, True)) for k, v in binds.items()), env))
        raise MiniError("no_match", "no arm matched")
    if t == "bin":
        return ev_bin(node[1], ev(node[2], env), ev(node[3], env))
    raise MiniError("parse", "bad node")


def match_pat(p, v, binds):
    k = p[0]
    if k == "pwild":
        return True
    if k == "pvar":
        binds[p[1]] = v
        return True
    if k == "pint":
        return is_int(v) and v == p[1]
    if k == "pstr":
        return isinstance(v, str) and v == p[1]
    if k == "pbool":
        return is_bool(v) and v == p[1]
    if k == "prec":
        if not isinstance(v, dict):
            return False
        for name, sub in zip(p[1], p[2]):
            if name not in v:
                return False
            if not match_pat(sub, v[name], binds):
                return False
        return True
    return False


def ev_bin(op, a, b):
    if op == ":=":
        if not isinstance(a, Cell):
            raise MiniError("type", "assignment to non-ref")
        a.v = b
        return b
    if op == "++":
        if not isinstance(a, str):
            raise MiniError("type", "++ needs a string on the left")
        return a + to_str(b)
    if op in ("+", "-", "*", "/", "%"):
        if op == "*" and isinstance(a, str):
            if not is_int(b):
                raise MiniError("type", "string repeat needs an integer count")
            return a * b if b > 0 else ""
        if not is_int(a) or not is_int(b):
            raise MiniError("type", "arithmetic on non-integers")
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if b == 0:
            raise MiniError("div_zero", op)
        return tdiv(a, b) if op == "/" else a % b
    if op in ("==", "!="):
        if isinstance(a, Cell) and isinstance(b, Cell):
            r = a is b
        elif is_bool(a) and is_bool(b):
            r = a == b
        elif is_int(a) and is_int(b):
            r = a == b
        elif isinstance(a, str) and isinstance(b, str):
            r = a == b
        else:
            raise MiniError("type", "cannot compare these values")
        return r if op == "==" else not r
    # < <= > >=
    if is_int(a) and is_int(b):
        pass
    elif isinstance(a, str) and isinstance(b, str):
        pass
    else:
        raise MiniError("type", "ordering needs two ints or two strings")
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    return a >= b


# ---------------------------------------------------------------- API
def export(v):
    if isinstance(v, Closure):
        return "<fn>"
    if isinstance(v, Cell):
        return "<ref>"
    if isinstance(v, dict):
        return dict((k, export(x)) for k, x in v.items())
    return v


def run(source):
    ast = parse(source)
    return export(ev(ast, Env({}, None)))
