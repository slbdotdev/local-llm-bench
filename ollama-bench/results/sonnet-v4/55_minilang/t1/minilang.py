"""A hand-written lexer/parser/evaluator for a small expression language.

No eval/exec/compile, no ast/operator/functools imports -- everything below
is built from scratch using only the Python standard library basics.
"""


class MiniError(Exception):
    """The only exception type this module raises for bad input."""

    def __init__(self, kind, msg=""):
        super().__init__(msg or kind)
        self.kind = kind


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

RESERVED = {
    "let", "letrec", "and", "in", "if", "then", "else",
    "fun", "match", "with", "end", "ref", "true", "false", "_",
}

MULTI_OPS = ["->", ":=", "==", "!=", "<=", ">=", "&&", "||", "++"]
SINGLE_OPS = set("+-*/%<>=(){},.|!")


def _is_alpha(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def _is_digit(c):
    return "0" <= c <= "9"


def _is_alnum(c):
    return _is_alpha(c) or _is_digit(c) or c == "_"


def tokenize(source):
    tokens = []
    i = 0
    n = len(source)
    while i < n:
        c = source[i]
        if c in " \t\r\n":
            i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and source[j] not in '"\\\n':
                j += 1
            if j >= n or source[j] != '"':
                raise MiniError("parse", "unterminated string")
            tokens.append(("STRING", source[i + 1:j]))
            i = j + 1
            continue
        if c == "0":
            if i + 1 < n and _is_digit(source[i + 1]):
                raise MiniError("parse", "leading zero in integer literal")
            tokens.append(("INT", 0))
            i += 1
            continue
        if "1" <= c <= "9":
            j = i
            while j < n and _is_digit(source[j]):
                j += 1
            tokens.append(("INT", int(source[i:j])))
            i = j
            continue
        if _is_alpha(c) or c == "_":
            j = i
            while j < n and _is_alnum(source[j]):
                j += 1
            word = source[i:j]
            i = j
            if word in RESERVED:
                tokens.append((word, word))
            else:
                tokens.append(("IDENT", word))
            continue
        matched = False
        for op in MULTI_OPS:
            if source.startswith(op, i):
                tokens.append((op, op))
                i += len(op)
                matched = True
                break
        if matched:
            continue
        if c in SINGLE_OPS:
            tokens.append((c, c))
            i += 1
            continue
        raise MiniError("parse", "unexpected character %r" % c)
    tokens.append(("EOF", None))
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

ATOM_STARTERS = {"INT", "STRING", "true", "false", "IDENT", "(", "{"}
CMP_OPS = {"==", "!=", "<", "<=", ">", ">="}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def peek_type(self):
        return self.tokens[self.pos][0]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, ttype):
        tok = self.advance()
        if tok[0] != ttype:
            raise MiniError("parse", "expected %s, got %s" % (ttype, tok[0]))
        return tok

    # -- expr dispatch -----------------------------------------------------

    def parse_expr(self):
        t = self.peek_type()
        if t == "let":
            return self.parse_let()
        if t == "letrec":
            return self.parse_letrec()
        if t == "if":
            return self.parse_if()
        if t == "fun":
            return self.parse_fun()
        if t == "match":
            return self.parse_match()
        return self.parse_assign()

    def parse_let(self):
        self.advance()
        name = self.expect("IDENT")[1]
        self.expect("=")
        e1 = self.parse_expr()
        self.expect("in")
        e2 = self.parse_expr()
        return ("let", name, e1, e2)

    def parse_letrec(self):
        self.advance()
        bindings = []
        name = self.expect("IDENT")[1]
        self.expect("=")
        e = self.parse_expr()
        bindings.append((name, e))
        while self.peek_type() == "and":
            self.advance()
            name = self.expect("IDENT")[1]
            self.expect("=")
            e = self.parse_expr()
            bindings.append((name, e))
        self.expect("in")
        body = self.parse_expr()
        names = [nm for nm, _ in bindings]
        if len(names) != len(set(names)):
            raise MiniError("dup_binding", "repeated letrec name")
        return ("letrec", bindings, body)

    def parse_if(self):
        self.advance()
        c = self.parse_expr()
        self.expect("then")
        a = self.parse_expr()
        self.expect("else")
        b = self.parse_expr()
        return ("if", c, a, b)

    def parse_fun(self):
        self.advance()
        param = self.expect("IDENT")[1]
        self.expect("->")
        body = self.parse_expr()
        return ("fun", param, body)

    def parse_match(self):
        self.advance()
        e = self.parse_expr()
        self.expect("with")
        arms = []
        while self.peek_type() == "|":
            arms.append(self.parse_arm())
        if not arms:
            raise MiniError("parse", "match with no arms")
        self.expect("end")
        return ("match", e, arms)

    def parse_arm(self):
        self.expect("|")
        pat = self.parse_pattern()
        names = []
        _collect_pattern_vars(pat, names)
        if len(names) != len(set(names)):
            raise MiniError("dup_binding", "repeated pattern variable")
        self.expect("->")
        body = self.parse_expr()
        return (pat, body)

    # -- precedence chain ----------------------------------------------

    def parse_assign(self):
        left = self.parse_or()
        if self.peek_type() == ":=":
            self.advance()
            right = self.parse_expr()
            return ("assign", left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek_type() == "||":
            self.advance()
            right = self.parse_and()
            left = ("or", left, right)
        return left

    def parse_and(self):
        left = self.parse_cmp()
        while self.peek_type() == "&&":
            self.advance()
            right = self.parse_cmp()
            left = ("and", left, right)
        return left

    def parse_cmp(self):
        left = self.parse_cat()
        t = self.peek_type()
        if t in CMP_OPS:
            self.advance()
            right = self.parse_cat()
            left = ("cmp", t, left, right)
        return left

    def parse_cat(self):
        left = self.parse_add()
        if self.peek_type() == "++":
            self.advance()
            right = self.parse_cat()
            left = ("concat", left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek_type() in ("+", "-"):
            op = self.advance()[0]
            right = self.parse_mul()
            left = ("binop", op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek_type() in ("*", "/", "%"):
            op = self.advance()[0]
            right = self.parse_unary()
            left = ("binop", op, left, right)
        return left

    def parse_unary(self):
        t = self.peek_type()
        if t in ("-", "!", "ref"):
            self.advance()
            operand = self.parse_unary()
            return ("unary", t, operand)
        return self.parse_app()

    def parse_app(self):
        left = self.parse_postfix()
        while self.peek_type() in ATOM_STARTERS:
            arg = self.parse_postfix()
            left = ("app", left, arg)
        return left

    def parse_postfix(self):
        atom = self.parse_atom()
        while self.peek_type() == ".":
            self.advance()
            name = self.expect("IDENT")[1]
            atom = ("field", atom, name)
        return atom

    def parse_atom(self):
        t = self.peek_type()
        if t == "INT":
            v = self.advance()[1]
            return ("int", v)
        if t == "STRING":
            v = self.advance()[1]
            return ("str", v)
        if t == "true":
            self.advance()
            return ("bool", True)
        if t == "false":
            self.advance()
            return ("bool", False)
        if t == "IDENT":
            name = self.advance()[1]
            return ("var", name)
        if t == "(":
            self.advance()
            e = self.parse_expr()
            self.expect(")")
            return e
        if t == "{":
            return self.parse_record()
        raise MiniError("parse", "unexpected token %s" % t)

    def parse_record(self):
        self.expect("{")
        fields = []
        if self.peek_type() != "}":
            name = self.expect("IDENT")[1]
            self.expect("=")
            e = self.parse_expr()
            fields.append((name, e))
            while self.peek_type() == ",":
                self.advance()
                name = self.expect("IDENT")[1]
                self.expect("=")
                e = self.parse_expr()
                fields.append((name, e))
        self.expect("}")
        names = [nm for nm, _ in fields]
        if len(names) != len(set(names)):
            raise MiniError("dup_field", "repeated field name")
        return ("record", fields)

    # -- patterns --------------------------------------------------------

    def parse_pattern(self):
        t = self.peek_type()
        if t == "_":
            self.advance()
            return ("wildcard",)
        if t == "INT":
            v = self.advance()[1]
            return ("intpat", v)
        if t == "STRING":
            v = self.advance()[1]
            return ("strpat", v)
        if t == "true":
            self.advance()
            return ("boolpat", True)
        if t == "false":
            self.advance()
            return ("boolpat", False)
        if t == "IDENT":
            name = self.advance()[1]
            return ("varpat", name)
        if t == "{":
            return self.parse_record_pattern()
        raise MiniError("parse", "unexpected token in pattern %s" % t)

    def parse_record_pattern(self):
        self.expect("{")
        fields = []
        if self.peek_type() != "}":
            name = self.expect("IDENT")[1]
            self.expect("=")
            p = self.parse_pattern()
            fields.append((name, p))
            while self.peek_type() == ",":
                self.advance()
                name = self.expect("IDENT")[1]
                self.expect("=")
                p = self.parse_pattern()
                fields.append((name, p))
        self.expect("}")
        names = [nm for nm, _ in fields]
        if len(names) != len(set(names)):
            raise MiniError("dup_field", "repeated field name in pattern")
        return ("recordpat", fields)


def _collect_pattern_vars(pat, out):
    tag = pat[0]
    if tag == "varpat":
        out.append(pat[1])
    elif tag == "recordpat":
        for _, sub in pat[1]:
            _collect_pattern_vars(sub, out)


# ---------------------------------------------------------------------------
# Runtime values
# ---------------------------------------------------------------------------

class Box:
    __slots__ = ("value", "initialized")

    def __init__(self, value=None, initialized=False):
        self.value = value
        self.initialized = initialized


class Env:
    __slots__ = ("table", "parent")

    def __init__(self, parent=None, table=None):
        self.parent = parent
        self.table = table if table is not None else {}

    def lookup(self, name):
        env = self
        while env is not None:
            box = env.table.get(name)
            if box is not None:
                return box
            env = env.parent
        raise MiniError("unbound", "unbound name %r" % name)


class Closure:
    __slots__ = ("param", "body", "env")

    def __init__(self, param, body, env):
        self.param = param
        self.body = body
        self.env = env


class RefCell:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


def _is_bool(v):
    return isinstance(v, bool)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_str(v):
    return isinstance(v, str)


def _is_record(v):
    return isinstance(v, dict)


def _is_closure(v):
    return isinstance(v, Closure)


def _is_ref(v):
    return isinstance(v, RefCell)


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

def eval_node(node, env):
    tag = node[0]

    if tag == "int" or tag == "str" or tag == "bool":
        return node[1]

    if tag == "var":
        box = env.lookup(node[1])
        if not box.initialized:
            raise MiniError("uninit", "read of uninitialised binding %r" % node[1])
        return box.value

    if tag == "record":
        d = {}
        for name, expr in node[1]:
            d[name] = eval_node(expr, env)
        return d

    if tag == "fun":
        return Closure(node[1], node[2], env)

    if tag == "app":
        fv = eval_node(node[1], env)
        av = eval_node(node[2], env)
        if not _is_closure(fv):
            raise MiniError("type", "attempt to call a non-function")
        new_env = Env(fv.env, {fv.param: Box(av, True)})
        return eval_node(fv.body, new_env)

    if tag == "field":
        ev = eval_node(node[1], env)
        if not _is_record(ev):
            raise MiniError("type", "field access on non-record")
        name = node[2]
        if name not in ev:
            raise MiniError("no_field", "no field %r" % name)
        return ev[name]

    if tag == "let":
        v1 = eval_node(node[2], env)
        new_env = Env(env, {node[1]: Box(v1, True)})
        return eval_node(node[3], new_env)

    if tag == "letrec":
        bindings, body = node[1], node[2]
        new_env = Env(env, {})
        for name, _ in bindings:
            new_env.table[name] = Box(None, False)
        for name, expr in bindings:
            v = eval_node(expr, new_env)
            box = new_env.table[name]
            box.value = v
            box.initialized = True
        return eval_node(body, new_env)

    if tag == "if":
        cv = eval_node(node[1], env)
        if not _is_bool(cv):
            raise MiniError("type", "if condition must be bool")
        return eval_node(node[2] if cv else node[3], env)

    if tag == "and":
        lv = eval_node(node[1], env)
        if not _is_bool(lv):
            raise MiniError("type", "&& left operand must be bool")
        if lv is False:
            return False
        rv = eval_node(node[2], env)
        if not _is_bool(rv):
            raise MiniError("type", "&& right operand must be bool")
        return rv

    if tag == "or":
        lv = eval_node(node[1], env)
        if not _is_bool(lv):
            raise MiniError("type", "|| left operand must be bool")
        if lv is True:
            return True
        rv = eval_node(node[2], env)
        if not _is_bool(rv):
            raise MiniError("type", "|| right operand must be bool")
        return rv

    if tag == "assign":
        lv = eval_node(node[1], env)
        rv = eval_node(node[2], env)
        if not _is_ref(lv):
            raise MiniError("type", ":= left operand must be a ref")
        lv.value = rv
        return rv

    if tag == "cmp":
        op = node[1]
        lv = eval_node(node[2], env)
        rv = eval_node(node[3], env)
        return _eval_cmp(op, lv, rv)

    if tag == "concat":
        lv = eval_node(node[1], env)
        rv = eval_node(node[2], env)
        if not _is_str(lv):
            raise MiniError("type", "++ left operand must be str")
        if _is_str(rv):
            s = rv
        elif _is_int(rv):
            s = str(rv)
        elif _is_bool(rv):
            s = "true" if rv else "false"
        else:
            raise MiniError("type", "++ right operand has bad type")
        return lv + s

    if tag == "binop":
        op = node[1]
        lv = eval_node(node[2], env)
        rv = eval_node(node[3], env)
        return _eval_binop(op, lv, rv)

    if tag == "unary":
        op = node[1]
        v = eval_node(node[2], env)
        if op == "-":
            if not _is_int(v):
                raise MiniError("type", "unary - requires int")
            return -v
        if op == "!":
            if not _is_ref(v):
                raise MiniError("type", "! requires ref")
            return v.value
        if op == "ref":
            return RefCell(v)

    if tag == "match":
        scrutinee = eval_node(node[1], env)
        for pat, body in node[2]:
            binds = {}
            if _match_pattern(pat, scrutinee, binds):
                table = {name: Box(val, True) for name, val in binds.items()}
                new_env = Env(env, table)
                return eval_node(body, new_env)
        raise MiniError("no_match", "no matching arm")

    raise MiniError("parse", "internal: unknown node %r" % (tag,))


def _eval_cmp(op, lv, rv):
    if op == "==" or op == "!=":
        eq = _compare_eq(lv, rv)
        if eq is None:
            raise MiniError("type", "== / != on incompatible types")
        return eq if op == "==" else (not eq)
    if _is_int(lv) and _is_int(rv):
        a, b = lv, rv
    elif _is_str(lv) and _is_str(rv):
        a, b = lv, rv
    else:
        raise MiniError("type", "ordering comparison needs two ints or two strs")
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    return a >= b


def _compare_eq(lv, rv):
    if _is_int(lv) and _is_int(rv):
        return lv == rv
    if _is_str(lv) and _is_str(rv):
        return lv == rv
    if _is_bool(lv) and _is_bool(rv):
        return lv == rv
    if _is_ref(lv) and _is_ref(rv):
        return lv is rv
    return None


def _eval_binop(op, lv, rv):
    if op == "+":
        if not _is_int(lv):
            raise MiniError("type", "+ left operand must be int")
        if not _is_int(rv):
            raise MiniError("type", "+ right operand must be int")
        return lv + rv
    if op == "-":
        if not _is_int(lv):
            raise MiniError("type", "- left operand must be int")
        if not _is_int(rv):
            raise MiniError("type", "- right operand must be int")
        return lv - rv
    if op == "*":
        if _is_int(lv):
            if not _is_int(rv):
                raise MiniError("type", "* right operand must be int")
            return lv * rv
        if _is_str(lv):
            if not _is_int(rv):
                raise MiniError("type", "string repetition needs int count")
            n = rv
            if n <= 0:
                return ""
            return lv * n
        raise MiniError("type", "* left operand must be int or str")
    # / and %
    if not _is_int(lv):
        raise MiniError("type", "%s left operand must be int" % op)
    if not _is_int(rv):
        raise MiniError("type", "%s right operand must be int" % op)
    if rv == 0:
        raise MiniError("div_zero", "division by zero")
    if op == "/":
        q_abs = abs(lv) // abs(rv)
        if (lv < 0) != (rv < 0):
            return -q_abs
        return q_abs
    # floored remainder: Python's native % is already floored (sign of divisor)
    return lv % rv


def _match_pattern(pat, val, binds):
    tag = pat[0]
    if tag == "wildcard":
        return True
    if tag == "varpat":
        binds[pat[1]] = val
        return True
    if tag == "intpat":
        return _is_int(val) and val == pat[1]
    if tag == "strpat":
        return _is_str(val) and val == pat[1]
    if tag == "boolpat":
        return _is_bool(val) and val == pat[1]
    if tag == "recordpat":
        if not _is_record(val):
            return False
        for name, subpat in pat[1]:
            if name not in val:
                return False
            if not _match_pattern(subpat, val[name], binds):
                return False
        return True
    return False


def _to_py(v):
    if _is_bool(v):
        return v
    if _is_int(v):
        return v
    if _is_str(v):
        return v
    if _is_record(v):
        return {k: _to_py(val) for k, val in v.items()}
    if _is_closure(v):
        return "<fn>"
    if _is_ref(v):
        return "<ref>"
    raise MiniError("type", "cannot convert value")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run(source):
    tokens = tokenize(source)
    parser = Parser(tokens)
    node = parser.parse_expr()
    if parser.peek_type() != "EOF":
        raise MiniError("parse", "trailing tokens after expression")
    root_env = Env(None, {})
    value = eval_node(node, root_env)
    return _to_py(value)
