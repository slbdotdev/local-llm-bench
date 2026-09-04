"""A small hand-written interpreter: lexer, parser, evaluator.

No eval/exec/compile, no ast/operator/functools.
"""

import sys

sys.setrecursionlimit(10000)


class MiniError(Exception):
    def __init__(self, kind, msg=""):
        super().__init__(msg or kind)
        self.kind = kind


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

KEYWORDS = {
    "let", "letrec", "and", "in", "if", "then", "else",
    "fun", "match", "with", "end", "ref", "true", "false",
}

MULTI_OPS = ["->", ":=", "==", "!=", "<=", ">=", "&&", "||", "++"]
SINGLE_OPS = set("+-*/%<>=(){},.|!")


def tokenize(s):
    i = 0
    n = len(s)
    toks = []
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == '"':
            j = i + 1
            buf = []
            while True:
                if j >= n:
                    raise MiniError("parse", "unterminated string")
                ch = s[j]
                if ch == '"':
                    j += 1
                    break
                if ch == "\\" or ch == "\n":
                    raise MiniError("parse", "invalid character in string")
                buf.append(ch)
                j += 1
            toks.append(("STRING", "".join(buf)))
            i = j
            continue
        if "0" <= c <= "9":
            j = i
            while j < n and "0" <= s[j] <= "9":
                j += 1
            numstr = s[i:j]
            if len(numstr) > 1 and numstr[0] == "0":
                raise MiniError("parse", "leading zero in integer literal")
            toks.append(("INT", int(numstr)))
            i = j
            continue
        if c.isdigit():
            raise MiniError("parse", "non-ASCII digit")
        if ("A" <= c <= "Z") or ("a" <= c <= "z") or c == "_":
            j = i + 1
            while j < n and (
                ("A" <= s[j] <= "Z") or ("a" <= s[j] <= "z")
                or ("0" <= s[j] <= "9") or s[j] == "_"
            ):
                j += 1
            word = s[i:j]
            if word in KEYWORDS:
                toks.append((word, word))
            elif word == "_":
                toks.append(("_", "_"))
            else:
                toks.append(("IDENT", word))
            i = j
            continue
        if c.isalpha():
            raise MiniError("parse", "non-ASCII letter")
        matched = None
        for op in MULTI_OPS:
            if s[i:i + len(op)] == op:
                matched = op
                break
        if matched is not None:
            toks.append((matched, matched))
            i += len(matched)
            continue
        if c in SINGLE_OPS:
            toks.append((c, c))
            i += 1
            continue
        raise MiniError("parse", "unexpected character %r" % c)
    toks.append(("EOF", None))
    return toks


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

CMP_OPS = {"==", "!=", "<", "<=", ">", ">="}
ATOM_START = {"INT", "STRING", "true", "false", "IDENT", "(", "{"}


class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0

    def peek(self):
        return self.toks[self.pos]

    def at(self, ttype):
        return self.toks[self.pos][0] == ttype

    def advance(self):
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def expect(self, ttype):
        if not self.at(ttype):
            raise MiniError("parse", "expected %s, got %s" % (ttype, self.peek()[0]))
        return self.advance()

    # -- expr ----------------------------------------------------------
    def parse_expr(self):
        ttype = self.peek()[0]
        if ttype == "let":
            self.advance()
            name = self.expect("IDENT")[1]
            self.expect("=")
            e1 = self.parse_expr()
            self.expect("in")
            e2 = self.parse_expr()
            return ("let", name, e1, e2)
        if ttype == "letrec":
            self.advance()
            bindings = []
            name = self.expect("IDENT")[1]
            self.expect("=")
            e = self.parse_expr()
            bindings.append((name, e))
            while self.at("and"):
                self.advance()
                name = self.expect("IDENT")[1]
                self.expect("=")
                e = self.parse_expr()
                bindings.append((name, e))
            self.expect("in")
            body = self.parse_expr()
            names = [b[0] for b in bindings]
            if len(set(names)) != len(names):
                raise MiniError("dup_binding", "duplicate name in letrec")
            return ("letrec", bindings, body)
        if ttype == "if":
            self.advance()
            c = self.parse_expr()
            self.expect("then")
            a = self.parse_expr()
            self.expect("else")
            b = self.parse_expr()
            return ("if", c, a, b)
        if ttype == "fun":
            self.advance()
            param = self.expect("IDENT")[1]
            self.expect("->")
            body = self.parse_expr()
            return ("fun", param, body)
        if ttype == "match":
            self.advance()
            e = self.parse_expr()
            self.expect("with")
            arms = [self.parse_arm()]
            while self.at("|"):
                arms.append(self.parse_arm())
            self.expect("end")
            return ("match", e, arms)
        return self.parse_assign()

    def parse_arm(self):
        self.expect("|")
        pat = self.parse_pattern()
        names = []
        collect_pattern_vars(pat, names)
        if len(set(names)) != len(names):
            raise MiniError("dup_binding", "duplicate variable in pattern")
        self.expect("->")
        body = self.parse_expr()
        return (pat, body)

    def parse_pattern(self):
        t = self.peek()
        if t[0] == "_":
            self.advance()
            return ("wildcard",)
        if t[0] == "INT":
            self.advance()
            return ("pint", t[1])
        if t[0] == "STRING":
            self.advance()
            return ("pstr", t[1])
        if t[0] == "true":
            self.advance()
            return ("pbool", True)
        if t[0] == "false":
            self.advance()
            return ("pbool", False)
        if t[0] == "IDENT":
            self.advance()
            return ("pvar", t[1])
        if t[0] == "{":
            self.advance()
            fields = []
            if not self.at("}"):
                fname = self.expect("IDENT")[1]
                self.expect("=")
                subp = self.parse_pattern()
                fields.append((fname, subp))
                while self.at(","):
                    self.advance()
                    fname = self.expect("IDENT")[1]
                    self.expect("=")
                    subp = self.parse_pattern()
                    fields.append((fname, subp))
            self.expect("}")
            names = [f[0] for f in fields]
            if len(set(names)) != len(names):
                raise MiniError("dup_field", "duplicate field in pattern")
            return ("precord", fields)
        raise MiniError("parse", "invalid pattern")

    def parse_assign(self):
        left = self.parse_or()
        if self.at(":="):
            self.advance()
            right = self.parse_expr()
            return ("assign", left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.at("||"):
            self.advance()
            right = self.parse_and()
            left = ("or", left, right)
        return left

    def parse_and(self):
        left = self.parse_cmp()
        while self.at("&&"):
            self.advance()
            right = self.parse_cmp()
            left = ("and", left, right)
        return left

    def parse_cmp(self):
        left = self.parse_cat()
        if self.peek()[0] in CMP_OPS:
            op = self.advance()[0]
            right = self.parse_cat()
            return ("cmp", op, left, right)
        return left

    def parse_cat(self):
        left = self.parse_add()
        if self.at("++"):
            self.advance()
            right = self.parse_cat()
            return ("concat", left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek()[0] in ("+", "-"):
            op = self.advance()[0]
            right = self.parse_mul()
            left = ("binop", op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek()[0] in ("*", "/", "%"):
            op = self.advance()[0]
            right = self.parse_unary()
            left = ("binop", op, left, right)
        return left

    def parse_unary(self):
        t = self.peek()
        if t[0] == "-":
            self.advance()
            e = self.parse_unary()
            return ("neg", e)
        if t[0] == "!":
            self.advance()
            e = self.parse_unary()
            return ("deref", e)
        if t[0] == "ref":
            self.advance()
            e = self.parse_unary()
            return ("mkref", e)
        return self.parse_app()

    def parse_app(self):
        first = self.parse_postfix()
        while self.peek()[0] in ATOM_START:
            arg = self.parse_postfix()
            first = ("app", first, arg)
        return first

    def parse_postfix(self):
        e = self.parse_atom()
        while self.at("."):
            self.advance()
            name = self.expect("IDENT")[1]
            e = ("field", e, name)
        return e

    def parse_atom(self):
        t = self.peek()
        if t[0] == "INT":
            self.advance()
            return ("int", t[1])
        if t[0] == "STRING":
            self.advance()
            return ("str", t[1])
        if t[0] == "true":
            self.advance()
            return ("bool", True)
        if t[0] == "false":
            self.advance()
            return ("bool", False)
        if t[0] == "IDENT":
            self.advance()
            return ("var", t[1])
        if t[0] == "(":
            self.advance()
            e = self.parse_expr()
            self.expect(")")
            return e
        if t[0] == "{":
            return self.parse_record()
        raise MiniError("parse", "invalid expression")

    def parse_record(self):
        self.expect("{")
        fields = []
        if not self.at("}"):
            fname = self.expect("IDENT")[1]
            self.expect("=")
            e = self.parse_expr()
            fields.append((fname, e))
            while self.at(","):
                self.advance()
                fname = self.expect("IDENT")[1]
                self.expect("=")
                e = self.parse_expr()
                fields.append((fname, e))
        self.expect("}")
        names = [f[0] for f in fields]
        if len(set(names)) != len(names):
            raise MiniError("dup_field", "duplicate field in record")
        return ("record", fields)


def collect_pattern_vars(pat, out):
    tag = pat[0]
    if tag == "pvar":
        out.append(pat[1])
    elif tag == "precord":
        for _, subpat in pat[1]:
            collect_pattern_vars(subpat, out)


# ---------------------------------------------------------------------------
# Runtime values: tagged tuples ('int', n) / ('str', s) / ('bool', b) /
# ('record', dict) / ('closure', param, body, env) / ('ref', Cell)
# ---------------------------------------------------------------------------

class Cell:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


UNINIT = object()


class Env:
    __slots__ = ("vars", "parent")

    def __init__(self, parent):
        self.vars = {}
        self.parent = parent

    def lookup(self, name):
        e = self
        while e is not None:
            if name in e.vars:
                v = e.vars[name]
                if v is UNINIT:
                    raise MiniError("uninit", name)
                return v
            e = e.parent
        raise MiniError("unbound", name)

    def define(self, name, val):
        self.vars[name] = val


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def eval_expr(node, env):
    tag = node[0]

    if tag == "int":
        return ("int", node[1])
    if tag == "str":
        return ("str", node[1])
    if tag == "bool":
        return ("bool", node[1])
    if tag == "var":
        return env.lookup(node[1])

    if tag == "let":
        _, name, e1, e2 = node
        v1 = eval_expr(e1, env)
        newenv = Env(env)
        newenv.define(name, v1)
        return eval_expr(e2, newenv)

    if tag == "letrec":
        _, bindings, body = node
        newenv = Env(env)
        for name, _e in bindings:
            newenv.define(name, UNINIT)
        for name, e in bindings:
            v = eval_expr(e, newenv)
            newenv.vars[name] = v
        return eval_expr(body, newenv)

    if tag == "if":
        _, c, a, b = node
        cv = eval_expr(c, env)
        if cv[0] != "bool":
            raise MiniError("type", "if condition must be bool")
        if cv[1]:
            return eval_expr(a, env)
        return eval_expr(b, env)

    if tag == "fun":
        _, param, body = node
        return ("closure", param, body, env)

    if tag == "match":
        _, e, arms = node
        v = eval_expr(e, env)
        for pat, body in arms:
            bindings = {}
            if match_pattern(pat, v, bindings):
                newenv = Env(env)
                for k, val in bindings.items():
                    newenv.define(k, val)
                return eval_expr(body, newenv)
        raise MiniError("no_match", "no matching arm")

    if tag == "or":
        _, a, b = node
        av = eval_expr(a, env)
        if av[0] != "bool":
            raise MiniError("type", "|| left operand must be bool")
        if av[1]:
            return ("bool", True)
        bv = eval_expr(b, env)
        if bv[0] != "bool":
            raise MiniError("type", "|| right operand must be bool")
        return bv

    if tag == "and":
        _, a, b = node
        av = eval_expr(a, env)
        if av[0] != "bool":
            raise MiniError("type", "&& left operand must be bool")
        if not av[1]:
            return ("bool", False)
        bv = eval_expr(b, env)
        if bv[0] != "bool":
            raise MiniError("type", "&& right operand must be bool")
        return bv

    if tag == "assign":
        _, target, value = node
        tv = eval_expr(target, env)
        vv = eval_expr(value, env)
        if tv[0] != "ref":
            raise MiniError("type", "assignment target must be a ref")
        tv[1].value = vv
        return vv

    if tag == "cmp":
        _, op, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        return eval_cmp(op, av, bv)

    if tag == "concat":
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        if av[0] != "str":
            raise MiniError("type", "++ left operand must be str")
        return ("str", av[1] + render_for_concat(bv))

    if tag == "binop":
        _, op, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        return eval_binop(op, av, bv)

    if tag == "neg":
        _, e = node
        v = eval_expr(e, env)
        if v[0] != "int":
            raise MiniError("type", "unary - requires int")
        return ("int", -v[1])

    if tag == "deref":
        _, e = node
        v = eval_expr(e, env)
        if v[0] != "ref":
            raise MiniError("type", "! requires ref")
        return v[1].value

    if tag == "mkref":
        _, e = node
        v = eval_expr(e, env)
        return ("ref", Cell(v))

    if tag == "app":
        _, f, a = node
        fv = eval_expr(f, env)
        av = eval_expr(a, env)
        if fv[0] != "closure":
            raise MiniError("type", "cannot apply non-function")
        _, param, body, cenv = fv
        newenv = Env(cenv)
        newenv.define(param, av)
        return eval_expr(body, newenv)

    if tag == "field":
        _, e, name = node
        v = eval_expr(e, env)
        if v[0] != "record":
            raise MiniError("type", "field access requires record")
        if name not in v[1]:
            raise MiniError("no_field", name)
        return v[1][name]

    if tag == "record":
        _, fields = node
        d = {}
        for name, e in fields:
            d[name] = eval_expr(e, env)
        return ("record", d)

    raise MiniError("parse", "unknown node")


def match_pattern(pat, val, bindings):
    tag = pat[0]
    if tag == "wildcard":
        return True
    if tag == "pvar":
        bindings[pat[1]] = val
        return True
    if tag == "pint":
        return val[0] == "int" and val[1] == pat[1]
    if tag == "pstr":
        return val[0] == "str" and val[1] == pat[1]
    if tag == "pbool":
        return val[0] == "bool" and val[1] == pat[1]
    if tag == "precord":
        if val[0] != "record":
            return False
        rec = val[1]
        for fname, subpat in pat[1]:
            if fname not in rec:
                return False
            if not match_pattern(subpat, rec[fname], bindings):
                return False
        return True
    return False


def eval_cmp(op, av, bv):
    if op == "==" or op == "!=":
        if av[0] != bv[0]:
            raise MiniError("type", "== / != type mismatch")
        t = av[0]
        if t == "int" or t == "str" or t == "bool":
            eq = av[1] == bv[1]
        elif t == "ref":
            eq = av[1] is bv[1]
        else:
            raise MiniError("type", "== / != not supported for this type")
        return ("bool", eq if op == "==" else not eq)
    else:
        if av[0] == "int" and bv[0] == "int":
            a, b = av[1], bv[1]
        elif av[0] == "str" and bv[0] == "str":
            a, b = av[1], bv[1]
        else:
            raise MiniError("type", "ordering requires two ints or two strings")
        if op == "<":
            r = a < b
        elif op == "<=":
            r = a <= b
        elif op == ">":
            r = a > b
        else:
            r = a >= b
        return ("bool", r)


def render_for_concat(v):
    if v[0] == "str":
        return v[1]
    if v[0] == "int":
        return str(v[1])
    if v[0] == "bool":
        return "true" if v[1] else "false"
    raise MiniError("type", "++ right operand has invalid type")


def trunc_div(a, b):
    q, r = divmod(a, b)
    if r != 0 and ((a < 0) != (b < 0)):
        q += 1
    return q


def eval_binop(op, av, bv):
    if op == "+":
        if av[0] != "int" or bv[0] != "int":
            raise MiniError("type", "+ requires two ints")
        return ("int", av[1] + bv[1])
    if op == "-":
        if av[0] != "int" or bv[0] != "int":
            raise MiniError("type", "- requires two ints")
        return ("int", av[1] - bv[1])
    if op == "*":
        if av[0] == "int" and bv[0] == "int":
            return ("int", av[1] * bv[1])
        if av[0] == "str":
            if bv[0] != "int":
                raise MiniError("type", "str * requires int on the right")
            n = bv[1]
            return ("str", av[1] * n if n > 0 else "")
        raise MiniError("type", "* type mismatch")
    if op == "/":
        if av[0] != "int" or bv[0] != "int":
            raise MiniError("type", "/ requires two ints")
        if bv[1] == 0:
            raise MiniError("div_zero", "division by zero")
        return ("int", trunc_div(av[1], bv[1]))
    if op == "%":
        if av[0] != "int" or bv[0] != "int":
            raise MiniError("type", "%% requires two ints")
        if bv[1] == 0:
            raise MiniError("div_zero", "modulo by zero")
        return ("int", av[1] % bv[1])
    raise MiniError("parse", "unknown operator")


def to_python(v):
    tag = v[0]
    if tag == "int" or tag == "bool" or tag == "str":
        return v[1]
    if tag == "record":
        return {k: to_python(val) for k, val in v[1].items()}
    if tag == "closure":
        return "<fn>"
    if tag == "ref":
        return "<ref>"
    raise MiniError("parse", "unknown value")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(source):
    toks = tokenize(source)
    parser = Parser(toks)
    ast = parser.parse_expr()
    if not parser.at("EOF"):
        raise MiniError("parse", "leftover tokens after expression")
    env = Env(None)
    val = eval_expr(ast, env)
    return to_python(val)
