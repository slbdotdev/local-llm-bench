"""Hidden grader for 55_minilang: interpreter for a small expression language.

The oracle below (`_ora_*` / `_mo_*`) is an independent implementation: a regex-driven
scanner, a table-driven precedence-climbing parser, tagged-tuple values and flat dict
environments, versus the reference's recursive-descent parser and linked env chain.
"""
import sys, os, re, random, threading, inspect

TOTAL = 31
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    sys.stdout.flush()
    os._exit(1)


_t = threading.Timer(45.0, _watchdog)
_t.daemon = True
_t.start()

try:
    import minilang
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


class _MissingErr(Exception):
    pass


ME = getattr(minilang, "MiniError", None)
if not (isinstance(ME, type) and issubclass(ME, BaseException)):
    ME = _MissingErr

KINDS = frozenset(["parse", "dup_field", "dup_binding", "unbound", "uninit",
                   "type", "div_zero", "no_field", "no_match"])


# =====================================================================
# oracle: an independent implementation (different strategy)
# =====================================================================
_MO_KW = ("let", "letrec", "and", "in", "if", "then", "else", "fun", "match",
          "with", "end", "ref", "true", "false")
_MO_TOKRE = re.compile(
    r'(?P<ws>[ \t\r\n]+)'
    r'|(?P<num>[0-9]+)'
    r'|(?P<word>[A-Za-z_][A-Za-z0-9_]*)'
    r'|(?P<str>"[^"\\\n]*")'
    r'|(?P<op2>->|:=|==|!=|<=|>=|&&|\|\||\+\+)'
    r'|(?P<op1>[-+*/%<>=(){},.|!])')


class _OraErr(Exception):
    def __init__(self, kind):
        Exception.__init__(self, kind)
        self.kind = kind


def _ora_lex(src):
    out = []
    i = 0
    n = len(src)
    while i < n:
        m = _MO_TOKRE.match(src, i)
        if m is None:
            raise _OraErr("parse")
        i = m.end()
        g = m.lastgroup
        s = m.group()
        if g == "ws":
            continue
        if g == "num":
            if len(s) > 1 and s[0] == "0":
                raise _OraErr("parse")
            out.append(("INT", int(s)))
        elif g == "word":
            if s == "_":
                out.append(("WILD", s))
            elif s in _MO_KW:
                out.append((s, s))
            else:
                out.append(("IDENT", s))
        elif g == "str":
            out.append(("STR", s[1:-1]))
        else:
            out.append((s, s))
    out.append(("EOF", None))
    return out


def _ora_lex_checked(src):
    # detect unterminated / illegal strings that the scanner would leave behind
    return _ora_lex(src)


_MO_LEVEL = {":=": 2, "||": 3, "&&": 4, "==": 5, "!=": 5, "<": 5, "<=": 5,
             ">": 5, ">=": 5, "++": 6, "+": 7, "-": 7, "*": 8, "/": 8, "%": 8}
_MO_ASSOC = {2: "R", 3: "L", 4: "L", 5: "N", 6: "R", 7: "L", 8: "L"}
_MO_ATOMSTART = ("INT", "STR", "IDENT", "true", "false", "(", "{")


class _OraP(object):
    def __init__(self, toks):
        self.t = toks
        self.k = 0

    def kind(self):
        return self.t[self.k][0]

    def take(self, want):
        if self.t[self.k][0] != want:
            raise _OraErr("parse")
        v = self.t[self.k][1]
        self.k += 1
        return v

    def expr(self):
        h = self.kind()
        if h == "let":
            self.k += 1
            nm = self.take("IDENT")
            self.take("=")
            a = self.expr()
            self.take("in")
            return ("let", nm, a, self.expr())
        if h == "letrec":
            self.k += 1
            pairs = []
            while True:
                nm = self.take("IDENT")
                self.take("=")
                pairs.append((nm, self.expr()))
                if self.kind() == "and":
                    self.k += 1
                    continue
                break
            self.take("in")
            body = self.expr()
            seen = set()
            for nm, _ in pairs:
                if nm in seen:
                    raise _OraErr("dup_binding")
                seen.add(nm)
            return ("letrec", [p[0] for p in pairs], [p[1] for p in pairs], body)
        if h == "if":
            self.k += 1
            c = self.expr()
            self.take("then")
            a = self.expr()
            self.take("else")
            return ("if", c, a, self.expr())
        if h == "fun":
            self.k += 1
            p = self.take("IDENT")
            self.take("->")
            return ("fun", p, self.expr())
        if h == "match":
            self.k += 1
            subj = self.expr()
            self.take("with")
            arms = []
            while self.kind() == "|":
                self.k += 1
                pat = self.pat()
                vs = []
                _ora_pvars(pat, vs)
                if len(vs) != len(set(vs)):
                    raise _OraErr("dup_binding")
                self.take("->")
                arms.append((pat, self.expr()))
            if not arms:
                raise _OraErr("parse")
            self.take("end")
            return ("match", subj, arms)
        return self.bin(2)

    def bin(self, minlvl):
        left = self.unary()
        while True:
            op = self.kind()
            lvl = _MO_LEVEL.get(op)
            if lvl is None or lvl < minlvl:
                break
            assoc = _MO_ASSOC[lvl]
            self.k += 1
            if op == ":=":
                right = self.expr()
            elif assoc == "R":
                right = self.bin(lvl)
            else:
                right = self.bin(lvl + 1)
            left = ("bin", op, left, right)
            if assoc == "N" and _MO_LEVEL.get(self.kind()) == lvl:
                raise _OraErr("parse")
        return left

    def unary(self):
        h = self.kind()
        if h in ("-", "!", "ref"):
            self.k += 1
            return ({"-": "neg", "!": "deref", "ref": "mkref"}[h], self.unary())
        return self.app()

    def app(self):
        left = self.post()
        while self.kind() in _MO_ATOMSTART:
            left = ("app", left, self.post())
        return left

    def post(self):
        e = self.atom()
        while self.kind() == ".":
            self.k += 1
            e = ("field", e, self.take("IDENT"))
        return e

    def atom(self):
        h, v = self.t[self.k]
        if h == "INT":
            self.k += 1
            return ("lit", ("i", v))
        if h == "STR":
            self.k += 1
            return ("lit", ("s", v))
        if h in ("true", "false"):
            self.k += 1
            return ("lit", ("b", h == "true"))
        if h == "IDENT":
            self.k += 1
            return ("var", v)
        if h == "(":
            self.k += 1
            e = self.expr()
            self.take(")")
            return e
        if h == "{":
            self.k += 1
            items = []
            if self.kind() != "}":
                while True:
                    nm = self.take("IDENT")
                    self.take("=")
                    items.append((nm, self.expr()))
                    if self.kind() == ",":
                        self.k += 1
                        continue
                    break
            self.take("}")
            _ora_dupfields(items)
            return ("rec", items)
        raise _OraErr("parse")

    def pat(self):
        h, v = self.t[self.k]
        if h == "WILD":
            self.k += 1
            return ("pany", None)
        if h == "INT":
            self.k += 1
            return ("plit", ("i", v))
        if h == "STR":
            self.k += 1
            return ("plit", ("s", v))
        if h in ("true", "false"):
            self.k += 1
            return ("plit", ("b", h == "true"))
        if h == "IDENT":
            self.k += 1
            return ("pbind", v)
        if h == "{":
            self.k += 1
            items = []
            if self.kind() != "}":
                while True:
                    nm = self.take("IDENT")
                    self.take("=")
                    items.append((nm, self.pat()))
                    if self.kind() == ",":
                        self.k += 1
                        continue
                    break
            self.take("}")
            _ora_dupfields(items)
            return ("prec", items)
        raise _OraErr("parse")


def _ora_dupfields(items):
    seen = set()
    for nm, _ in items:
        if nm in seen:
            raise _OraErr("dup_field")
        seen.add(nm)


def _ora_pvars(p, acc):
    if p[0] == "pbind":
        acc.append(p[1])
    elif p[0] == "prec":
        for _, sub in p[1]:
            _ora_pvars(sub, acc)


def _ora_parse(src):
    p = _OraP(_ora_lex_checked(src))
    e = p.expr()
    if p.kind() != "EOF":
        raise _OraErr("parse")
    return e


# ---------------- values: ("i",int) ("s",str) ("b",bool) ("r",dict)
#                  ("c",param,body,env) ("m",[value])
def _ora_show(v):
    t = v[0]
    if t == "i" or t == "s" or t == "b":
        return v[1]
    if t == "r":
        return dict((k, _ora_show(x)) for k, x in v[1].items())
    if t == "m":
        return "<ref>"
    return "<fn>"


def _ora_text(v):
    if v[0] == "s":
        return v[1]
    if v[0] == "i":
        return "%d" % v[1]
    if v[0] == "b":
        return "true" if v[1] else "false"
    raise _OraErr("type")


def _ora_trunc_div(a, b):
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q


def _ora_floor_mod(a, b):
    return a - b * (a // b)


def _ora_binop(op, x, y):
    tx, ty = x[0], y[0]
    if op == ":=":
        if tx != "m":
            raise _OraErr("type")
        x[1][0] = y
        return y
    if op == "++":
        if tx != "s":
            raise _OraErr("type")
        return ("s", x[1] + _ora_text(y))
    if op in ("+", "-", "*", "/", "%"):
        if op == "*" and tx == "s":
            if ty != "i":
                raise _OraErr("type")
            return ("s", x[1] * y[1] if y[1] > 0 else "")
        if tx != "i" or ty != "i":
            raise _OraErr("type")
        a, b = x[1], y[1]
        if op == "+":
            return ("i", a + b)
        if op == "-":
            return ("i", a - b)
        if op == "*":
            return ("i", a * b)
        if b == 0:
            raise _OraErr("div_zero")
        return ("i", _ora_trunc_div(a, b) if op == "/" else _ora_floor_mod(a, b))
    if op in ("==", "!="):
        if tx == "m" and ty == "m":
            same = x is y
        elif tx == ty and tx in ("i", "s", "b"):
            same = x[1] == y[1]
        else:
            raise _OraErr("type")
        return ("b", same if op == "==" else not same)
    if not ((tx == "i" and ty == "i") or (tx == "s" and ty == "s")):
        raise _OraErr("type")
    a, b = x[1], y[1]
    return ("b", {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op])


class _OraFuel(Exception):
    pass


_ORA_STEPS = [0]


class _OraSlot(object):
    __slots__ = ("val", "on")

    def __init__(self, val, on):
        self.val = val
        self.on = on


def _ora_extend(env, more):
    d = dict(env)
    d.update(more)
    return d


def _ora_eval(e, env):
    _ORA_STEPS[0] += 1
    if _ORA_STEPS[0] > 20000:
        raise _OraFuel()
    h = e[0]
    if h == "lit":
        return e[1]
    if h == "var":
        s = env.get(e[1])
        if s is None:
            raise _OraErr("unbound")
        if not s.on:
            raise _OraErr("uninit")
        return s.val
    if h == "rec":
        d = {}
        for nm, sub in e[1]:
            d[nm] = _ora_eval(sub, env)
        return ("r", d)
    if h == "field":
        b = _ora_eval(e[1], env)
        if b[0] != "r":
            raise _OraErr("type")
        if e[2] not in b[1]:
            raise _OraErr("no_field")
        return b[1][e[2]]
    if h == "fun":
        return ("c", e[1], e[2], env)
    if h == "app":
        f = _ora_eval(e[1], env)
        a = _ora_eval(e[2], env)
        if f[0] != "c":
            raise _OraErr("type")
        return _ora_eval(f[2], _ora_extend(f[3], {f[1]: _OraSlot(a, True)}))
    if h == "neg":
        v = _ora_eval(e[1], env)
        if v[0] != "i":
            raise _OraErr("type")
        return ("i", -v[1])
    if h == "deref":
        v = _ora_eval(e[1], env)
        if v[0] != "m":
            raise _OraErr("type")
        return v[1][0]
    if h == "mkref":
        return ("m", [_ora_eval(e[1], env)])
    if h == "if":
        c = _ora_eval(e[1], env)
        if c[0] != "b":
            raise _OraErr("type")
        return _ora_eval(e[2] if c[1] else e[3], env)
    if h == "let":
        v = _ora_eval(e[2], env)
        return _ora_eval(e[3], _ora_extend(env, {e[1]: _OraSlot(v, True)}))
    if h == "letrec":
        slots = dict((nm, _OraSlot(None, False)) for nm in e[1])
        env2 = _ora_extend(env, slots)
        for nm, rhs in zip(e[1], e[2]):
            v = _ora_eval(rhs, env2)
            slots[nm].val = v
            slots[nm].on = True
        return _ora_eval(e[3], env2)
    if h == "match":
        subj = _ora_eval(e[1], env)
        for pat, body in e[2]:
            b = {}
            if _ora_match(pat, subj, b):
                return _ora_eval(body, _ora_extend(
                    env, dict((k, _OraSlot(v, True)) for k, v in b.items())))
        raise _OraErr("no_match")
    # bin
    op = e[1]
    if op == "&&" or op == "||":
        left = _ora_eval(e[2], env)
        if left[0] != "b":
            raise _OraErr("type")
        if left[1] == (op == "||"):
            return left
        right = _ora_eval(e[3], env)
        if right[0] != "b":
            raise _OraErr("type")
        return right
    x = _ora_eval(e[2], env)
    y = _ora_eval(e[3], env)
    return _ora_binop(op, x, y)


def _ora_match(p, v, b):
    h = p[0]
    if h == "pany":
        return True
    if h == "pbind":
        b[p[1]] = v
        return True
    if h == "plit":
        return v[0] == p[1][0] and v[1] == p[1][1]
    if v[0] != "r":
        return False
    for nm, sub in p[1]:
        if nm not in v[1]:
            return False
        if not _ora_match(sub, v[1][nm], b):
            return False
    return True


def _ora_run(src):
    _ORA_STEPS[0] = 0
    return _ora_show(_ora_eval(_ora_parse(src), {}))


# =====================================================================
# random program generation
# =====================================================================
_G_INTS = ["0", "1", "2", "3", "7", "10", "0", "5", "4"]
_G_STRS = ['""', '"a"', '"ab"', '"x"', '"hi"', '"Z"']
_G_BOOLS = ["true", "false"]
_G_FIELDS = ["a", "b", "c", "tag"]
_G_NAMES = ["x", "y", "z", "f", "g", "n", "q"]

_G_CHAIN_OPS = [
    ["+", "-"], ["*", "/", "%"], ["+", "-", "*", "/", "%"],
    ["++"], ["&&", "||"], ["==", "!=", "<", "<=", ">", ">="],
    ["+", "-", "++"], ["*", "%", "+"], ["&&", "||", "=="],
]

# small fragments with interesting, sharply different failure modes
_G_EFFECTS = [
    "(1 / 0)", "(1 % 0)", "zz", "(qq 1)", '"s"', "1", "0", "true", "false",
    "{a = 1}", "(fun w -> w)", "(ref 1)", "({a = 1}.b)", "(-1)",
    "(match 1 with | 2 -> 3 end)", "(letrec p = r and r = 1 in p)",
    "(let u = 5 in u)", "(!1)", '("a" ++ {a = 1})', "({a = 1} 2)",
    "(2 == \"a\")", "(true + 1)", "(\"ab\" * 2)",
]
_G_BINOPS = ["+", "-", "*", "/", "%", "++", "==", "!=", "<", "<=", ">", ">=",
             "&&", "||", ":="]


def _g_pattern(rng, depth, names):
    r = rng.random()
    if depth <= 0 or r < 0.30:
        c = rng.random()
        if c < 0.22:
            return "_"
        if c < 0.45:
            return rng.choice(_G_INTS)
        if c < 0.60:
            return rng.choice(_G_STRS)
        if c < 0.72:
            return rng.choice(_G_BOOLS)
        n = rng.choice(_G_NAMES)
        names.append(n)
        return n
    k = rng.randint(0, 2)
    if rng.random() < 0.6:
        flds = rng.sample(_G_FIELDS, k)
    else:
        flds = [rng.choice(_G_FIELDS) for _ in range(k)]
    return "{" + ", ".join("%s = %s" % (f, _g_pattern(rng, depth - 1, names))
                           for f in flds) + "}"


def _g_expr(rng, depth, scope):
    if depth <= 0:
        return _g_atom(rng, scope)
    r = rng.random()
    if r < 0.14:
        return _g_atom(rng, scope)
    if r < 0.34:
        ops = rng.choice(_G_CHAIN_OPS)
        k = rng.randint(2, 4)
        if k > 2 and ("==" in ops or "<" in ops) and rng.random() < 0.75:
            k = 2
        parts = [_g_expr(rng, depth - 1, scope)]
        for _ in range(k - 1):
            parts.append(rng.choice(ops))
            parts.append(_g_expr(rng, depth - 1, scope))
        return " ".join(parts)
    if r < 0.40:
        return rng.choice(["-", "!", "ref ", "- -", "!ref "]) + \
            _g_expr(rng, depth - 1, scope)
    if r < 0.47:
        return "if %s then %s else %s" % (_g_expr(rng, depth - 1, scope),
                                          _g_expr(rng, depth - 1, scope),
                                          _g_expr(rng, depth - 1, scope))
    if r < 0.56:
        n = rng.choice(_G_NAMES)
        return "let %s = %s in %s" % (n, _g_expr(rng, depth - 1, scope),
                                      _g_expr(rng, depth - 1, scope + [n]))
    if r < 0.64:
        ns = [rng.choice(_G_NAMES)]
        if rng.random() < 0.6:
            ns.append(rng.choice(_G_NAMES))
        inner = scope + ns
        parts = ["%s = %s" % (n, _g_expr(rng, depth - 1, inner)) for n in ns]
        return "letrec %s in %s" % (" and ".join(parts),
                                    _g_expr(rng, depth - 1, inner))
    if r < 0.70:
        n = rng.choice(_G_NAMES)
        return "(fun %s -> %s)" % (n, _g_expr(rng, depth - 1, scope + [n]))
    if r < 0.77:
        n = rng.choice(_G_NAMES)
        return "(fun %s -> %s) %s" % (n, _g_expr(rng, depth - 1, scope + [n]),
                                      _g_atom(rng, scope))
    if r < 0.85:
        k = rng.randint(0, 3)
        if rng.random() < 0.6:
            flds = rng.sample(_G_FIELDS, k)
        else:
            flds = [rng.choice(_G_FIELDS) for _ in range(k)]
        src = "{" + ", ".join("%s = %s" % (f, _g_expr(rng, depth - 1, scope))
                              for f in flds) + "}"
        if rng.random() < 0.5:
            src = "(" + src + ")." + rng.choice(_G_FIELDS)
        return src
    if r < 0.96:
        arms = []
        for _ in range(rng.randint(1, 3)):
            names = []
            pat = _g_pattern(rng, 2, names)
            arms.append("| %s -> %s" % (pat, _g_expr(rng, depth - 1, scope + names)))
        return "match %s with %s end" % (_g_expr(rng, depth - 1, scope),
                                         " ".join(arms))
    return "(%s)" % _g_expr(rng, depth - 1, scope)


def _g_atom(rng, scope):
    r = rng.random()
    if r < 0.30:
        return rng.choice(_G_INTS)
    if r < 0.45:
        return rng.choice(_G_STRS)
    if r < 0.55:
        return rng.choice(_G_BOOLS)
    if r < 0.62:
        return "{" + rng.choice(_G_FIELDS) + " = " + rng.choice(_G_INTS) + "}"
    if r < 0.68:
        return rng.choice(_G_NAMES)
    return rng.choice(scope) if scope else rng.choice(_G_INTS)


def gen_programs(seed, n, depth=3):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        s = _g_expr(rng, depth, [])
        if len(s) <= 260:
            out.append(s)
    return out


def gen_effect_programs(seed, n):
    """Programs whose point is *which* error fires (evaluation-order traps)."""
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        a = rng.choice(_G_EFFECTS)
        b = rng.choice(_G_EFFECTS)
        c = rng.choice(_G_EFFECTS)
        shape = rng.randint(0, 8)
        if shape <= 2:
            s = "%s %s %s" % (a, rng.choice(_G_BINOPS), b)
        elif shape == 3:
            s = "if %s then %s else %s" % (a, b, c)
        elif shape == 4:
            s = "%s %s" % (a, b)
        elif shape == 5:
            s = "%s.%s" % (a, rng.choice(_G_FIELDS))
        elif shape == 6:
            s = "%s%s" % (rng.choice(["-", "!", "ref "]), a)
        elif shape == 7:
            s = "let v = %s in %s %s v" % (a, b, rng.choice(_G_BINOPS))
        else:
            s = "match %s with | %s -> %s | _ -> %s end" % (
                a, rng.choice(["_", "1", '"s"', "true", "{a = _}", "w"]), b, c)
        out.append(s)
    return out


_G_MUTCHARS = list("(){}|,.+-*/%<>=!&:; \"_") + [
    "->", ":=", "==", "!=", "<=", ">=", "&&", "||", "++", "let", "in", "fun",
    "match", "with", "end", "if", "then", "else", "letrec", "and", "ref",
    "true", "x", "1", '"a"', "_"]


def gen_mutants(seed, n):
    """Well-formed programs mangled by a token-level edit (mostly parse errors)."""
    rng = random.Random(seed)
    base = gen_programs(seed + 1, n, depth=2)
    out = []
    for s in base:
        if not s:
            continue
        op = rng.randint(0, 2)
        i = rng.randrange(len(s))
        if op == 0:
            out.append(s[:i] + s[i + 1:])
        elif op == 1:
            out.append(s[:i] + rng.choice(_G_MUTCHARS) + s[i:])
        else:
            j = min(len(s), i + rng.randint(1, 4))
            out.append(s[:i] + rng.choice(_G_MUTCHARS) + s[j:])
    return out[:n]


def _g_num(rng):
    v = rng.randint(-13, 13)
    return "-" + str(-v) if v < 0 else str(v)


def gen_divmod(seed, n):
    """Integer division / modulo expressions, heavy on negative operands."""
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        a, b, c = _g_num(rng), _g_num(rng), _g_num(rng)
        o1, o2 = rng.choice("/%"), rng.choice("/%")
        shape = rng.randint(0, 6)
        if shape == 0:
            s = a + " " + o1 + " " + b
        elif shape == 1:
            s = "(" + a + " " + o1 + " " + b + ") " + o2 + " " + c
        elif shape == 2:
            s = a + " " + o1 + " " + b + " " + o2 + " " + c
        elif shape == 3:
            s = a + " / " + b + " * " + b + " + " + a + " % " + b
        elif shape == 4:
            s = "- (" + a + " " + o1 + " " + b + ")"
        elif shape == 5:
            s = a + " " + rng.choice(["+", "-", "*"]) + " " + b + " " + o1 + " " + c
        else:
            s = a + " " + o1 + " (" + b + " " + rng.choice(["+", "-"]) + " " + c + ")"
        out.append(s)
    return out


# =====================================================================
# candidate / oracle comparison helpers
# =====================================================================
def _same(a, b):
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, dict) or isinstance(b, dict):
        if not (isinstance(a, dict) and isinstance(b, dict)):
            return False
        if set(a.keys()) != set(b.keys()):
            return False
        for k in a:
            if not _same(a[k], b[k]):
                return False
        return True
    if type(a) is not type(b):
        return False
    return a == b


def _cand(src):
    try:
        return ("ok", minilang.run(src))
    except ME as e:
        return ("err", getattr(e, "kind", "<no .kind>"))
    except Exception as e:
        return ("boom", type(e).__name__)


def _cmp(src, want):
    got = _cand(src)
    if want[0] == "err":
        return got[0] == "err" and got[1] == want[1]
    return got[0] == "ok" and _same(want[1], got[1])


def _all(cases):
    def probe():
        for src, want in cases:
            if not _cmp(src, want):
                return False
        return True
    return probe


def _expect(src):
    try:
        return ("ok", _ora_run(src))
    except _OraFuel:
        return None
    except _OraErr as e:
        return ("err", e.kind)


def _split(progs):
    oks, errs = [], []
    for s in progs:
        w = _expect(s)
        if w is None:
            continue
        (oks if w[0] == "ok" else errs).append((s, w))
    return oks, errs


def _slice(cases, k, i):
    return [c for j, c in enumerate(cases) if j % k == i]


def E(k):
    return ("err", k)


def V(v):
    return ("ok", v)


# =====================================================================
# 1-17: values on well-formed programs
# =====================================================================
def api_probe():
    if not (isinstance(getattr(minilang, "MiniError", None), type)
            and issubclass(minilang.MiniError, Exception)):
        return False
    cases = [
        ("1 + 2 * 3", V(7)),
        ("let x = 4 in x * x", V(16)),
        ("letrec f = fun n -> if n == 0 then 1 else n * f (n - 1) in f 5", V(120)),
        ('match {tag = "pt", x = 3} with | {tag = "pt", x = v} -> v + 1 | _ -> 0 end',
         V(4)),
        ("let r = ref 2 in r := !r + 3", V(5)),
        ("{a = 1}.b", E("no_field")),
    ]
    return _all(cases)()


check("API surface: MiniError(Exception).kind and the visible examples", api_probe)


def canon_probe():
    want = [("1 < 2", True), ("2 < 1", False), ("true", True), ("false", False),
            ("1 == 1", True), ("1 + 1", 2), ("0", 0), ("-0", 0), ('"a"', "a"),
            ('""', ""), ("{}", {}), ("ref 1", "<ref>"), ("fun x -> x", "<fn>"),
            ("{a = true, b = 1}", {"a": True, "b": 1}),
            ("{a = {b = fun x -> x}}", {"a": {"b": "<fn>"}}),
            ("{a = ref 1, b = {}}", {"a": "<ref>", "b": {}}),
            ("if 1 < 2 then 1 else 0", 1)]
    for src, w in want:
        got = _cand(src)
        if got[0] != "ok" or not _same(w, got[1]):
            return False
    return True


check("canonical Python result types (bool vs int, dict, <fn>/<ref>)", canon_probe)

check("precedence and associativity", _all([
    ("1 + 2 * 3", V(7)), ("10 - 4 - 3", V(3)), ("10 - (4 - 3)", V(9)),
    ("2 * 3 % 4", V(2)), ("- 7 / 2", V(-3)), ("-2 * 3", V(-6)), ("- - 1", V(1)),
    ("1 + 2 == 3", V(True)), ("true || false && false", V(True)),
    ("false && true || true", V(True)), ('"a" ++ "b" ++ "c"', V("abc")),
    ("let r = ref 1 in let s = ref 2 in r := s := 3", V(3)),
    ("(fun x -> x + 1) 2 + 3", V(6)),
    ("let f = fun x -> fun y -> x - y in f 10 3", V(7)),
    ("{a = {b = 2}}.a.b", V(2)), ("- (fun x -> 3) 1", V(-3)),
    ("!ref 4", V(4)), ("ref 1 == ref 1", V(False)),
    ("let f = fun x -> x + 1 in f 2 * 3", V(9)),
    ("1 + 2 * 3 - 4 / 2 % 3", V(5)),
]))

check("integer division and modulo with negative operands", _all([
    ("-7 / 2", V(-3)), ("7 / -2", V(-3)), ("-7 / -2", V(3)), ("7 / 2", V(3)),
    ("-7 % 2", V(1)), ("7 % -2", V(-1)), ("-7 % -2", V(-1)), ("7 % 2", V(1)),
    ("(0 - 9) % 5", V(1)), ("0 - 9 % 5", V(-4)), ("-1 / 2", V(0)),
    ("-1 % 2", V(1)), ("5 % 5", V(0)), ("-5 % 5", V(0)), ("5 % -5", V(0)),
    ("-10 / 3", V(-3)), ("-10 % 3", V(2)), ("10 / -3", V(-3)), ("10 % -3", V(-2)),
    ("-1 / -1", V(1)), ("0 / -3", V(0)), ("0 % -3", V(0)), ("-13 / 4", V(-3)),
    ("-13 % 4", V(3)), ("13 % -4", V(-3)),
]))

check("string concatenation and repetition", _all([
    ('"ab" * 3', V("ababab")), ('"ab" * 0', V("")), ('"ab" * -1', V("")),
    ('"" * -3', V("")), ('"n=" ++ 1', V("n=1")), ('"b:" ++ true', V("b:true")),
    ('"x" ++ -5', V("x-5")), ('("a" ++ 1) ++ "b"', V("a1b")), ('"" ++ ""', V("")),
    ('"a" ++ "b" ++ 2', V("ab2")), ('"a" ++ ("b" ++ 2)', V("ab2")),
    ('"a" ++ "" ++ "c"', V("ac")), ('"z" * 1', V("z")), ('"ab" * 2 ++ "c"', V("ababc")),
    ('"n=" ++ 0 - 1', V("n=-1")),
]))

check("comparison results", _all([
    ("1 == 1", V(True)), ("1 != 2", V(True)), ('"a" == "a"', V(True)),
    ("true == true", V(True)), ("true != false", V(True)), ('"a" < "b"', V(True)),
    ('"b" < "a"', V(False)), ('"Z" < "a"', V(True)), ('"ab" < "b"', V(True)),
    ('"" < "a"', V(True)), ("(1 < 2) == (2 < 3)", V(True)),
    ("let r = ref 1 in r == r", V(True)), ("ref 1 != ref 1", V(True)),
    ("let r = ref 1 in let s = r in r == s", V(True)),
    ("2 <= 2", V(True)), ("2 >= 3", V(False)), ("-1 < 0", V(True)),
    ('"abc" >= "abc"', V(True)),
]))

check("short-circuit results and side effects", _all([
    ("false && (1 / 0)", V(False)), ("true || (1 / 0)", V(True)),
    ("false && 1", V(False)), ("true || zz", V(True)), ("true && false", V(False)),
    ("false || true", V(True)), ("true && true", V(True)), ("false || false", V(False)),
    ("let r = ref 0 in let b = false && (r := 1) == 1 in !r", V(0)),
    ("let r = ref 0 in let b = true && (r := 1) == 1 in !r", V(1)),
    ("let r = ref 0 in let b = true || (r := 1) == 1 in !r", V(0)),
    ("let r = ref 0 in let b = false || (r := 1) == 1 in !r", V(1)),
    ("if true then 1 else zz", V(1)), ("if false then zz else 2", V(2)),
    ("false && false && (1 / 0)", V(False)),
]))

check("records and field access", _all([
    ("{}", V({})), ('{a = 1, b = "x"}', V({"a": 1, "b": "x"})),
    ("let r = {a = 1} in r.a + r.a", V(2)), ("{a = 1}.a", V(1)),
    ("{a = {b = {c = 3}}}.a.b.c", V(3)),
    ("{a = fun x -> x, b = ref 1}", V({"a": "<fn>", "b": "<ref>"})),
    ("let r = {a = 1, b = 2} in r.b - r.a", V(1)),
    ("(fun r -> r.a) {a = 7}", V(7)),
    ("{a = 1 + 1, b = 2 * 2}", V({"a": 2, "b": 4})),
    ("let r = ref {a = 1} in (!r).a", V(1)),
    ("{a = {}}", V({"a": {}})),
]))

check("match: arm order, nesting, literal kinds", _all([
    ("match 1 with | _ -> 5 end", V(5)),
    ('match 1 with | 1 -> "a" | _ -> "b" end', V("a")),
    ('match "1" with | 1 -> "int" | _ -> "other" end', V("other")),
    ("match true with | 1 -> 0 | true -> 9 end", V(9)),
    ("match {a = 1, b = 2} with | {a = 1} -> 10 | {a = 1, b = 2} -> 20 end", V(10)),
    ("match {a = 1} with | {a = 1, b = 2} -> 10 | {a = x} -> x end", V(1)),
    ("match {a = {b = 5}} with | {a = {b = v}} -> v end", V(5)),
    ("match 1 with | {} -> 0 | _ -> 1 end", V(1)),
    ("match {} with | {} -> 7 end", V(7)),
    ("match {a = 1} with | {a = x} -> x | {a = x} -> 2 end", V(1)),
    ("let x = 9 in match 1 with | x -> x end", V(1)),
    ("match 1 with | x -> x end", V(1)),
    ("match ref 1 with | {} -> 1 | _ -> 2 end", V(2)),
    ("match fun x -> x with | {a = _} -> 1 | y -> 2 end", V(2)),
    ("match {a = 1, b = 2} with | {b = 2, a = 2} -> 1 | {b = 2, a = 1} -> 2 end", V(2)),
    ('match {a = "s"} with | {a = 1} -> 1 | {a = true} -> 2 | {a = "s"} -> 3 end', V(3)),
    ("let y = 1 in match {a = 2} with | {a = y} -> y | _ -> y end", V(2)),
]))

check("let / letrec / closures / shadowing", _all([
    ("let x = 1 in let x = x + 2 in x * 10", V(30)),
    ("let y = 10 in let f = fun x -> x + y in let y = 99 in f 1", V(11)),
    ("letrec a = 1 and b = a in b", V(1)),
    ("letrec f = fun n -> if n <= 0 then 0 else n + f (n - 1) in f 4", V(10)),
    ("letrec e = fun n -> if n == 0 then true else o (n - 1) and "
     "o = fun n -> if n == 0 then false else e (n - 1) in e 5", V(False)),
    ("let f = fun x -> zz in 1", V(1)),
    ("letrec f = fun x -> x and g = f in g 3", V(3)),
    ("let x = 1 in (fun x -> x + 1) 5", V(6)),
    ("let f = fun x -> fun y -> x in f 1 2", V(1)),
    ("(fun f -> f 3) (fun x -> x * 2)", V(6)),
    ("let x = 2 in let f = fun y -> x * y in let x = 100 in f 3", V(6)),
    ("letrec fib = fun n -> if n < 2 then n else fib (n - 1) + fib (n - 2) in fib 10",
     V(55)),
    ("letrec a = 1 and b = a + 1 and c = b + a in c", V(3)),
    ("(fun f -> 8) (fun x -> x)", V(8)),
]))

check("ref cells and assignment", _all([
    ("let r = ref 1 in r := 5", V(5)),
    ("let r = ref 1 in let q = r := 5 in !r", V(5)),
    ("let r = ref 1 in !r + !r", V(2)),
    ("ref 1", V("<ref>")), ("fun x -> x", V("<fn>")),
    ("let r = ref (ref 1) in !!r", V(1)),
    ("let r = ref 1 in (r := 2) + !r", V(4)),
    ("let r = ref 1 in !r + (r := 2)", V(3)),
    ("let r = ref 1 in let s = r in s := 9", V(9)),
    ("let r = ref 1 in let s = r in let q = s := 9 in !r", V(9)),
    ("let r = ref 1 in let s = ref 1 in let q = s := 9 in !r", V(1)),
    ('let r = ref "a" in r := !r ++ "b"', V("ab")),
    ("let r = ref 0 in let f = fun x -> r := !r + x in let q = f 3 in !r", V(3)),
    ("let mk = fun v -> ref v in let a = mk 1 in let b = mk 1 in a == b", V(False)),
]))

_VALS, _ERRS = _split(gen_programs(55101, 1400))
for _i in range(3):
    check("randomised differential, values (bucket %d)" % (_i + 1),
          _all(_slice(_VALS, 3, _i)))

_DVALS, _DERRS = _split(gen_programs(55202, 700, depth=4))
check("randomised differential, values in deeper programs", _all(_DVALS))

_MVALS, _MERRS = _split(gen_divmod(55303, 900))
for _i in range(2):
    check("randomised differential, div/mod values (bucket %d)" % (_i + 1),
          _all(_slice(_MVALS, 2, _i)))

_EVALS, _EERRS = _split(gen_effect_programs(55404, 1300))
check("randomised differential, mixed-fragment values", _all(_EVALS))

# =====================================================================
# 18-30: strictness, error kinds and error ordering
# =====================================================================
_SRC = inspect.getsource(minilang)

check("does not import ast or use eval/exec/compile",
      lambda: not re.search(r"^[ \t]*(?:import|from)[ \t]+ast\b", _SRC, re.M)
      and not re.search(r"(?<![\w.])(?:eval|exec|compile)\s*\(\s*[\"'a-zA-Z_]", _SRC))

check("does not import operator or functools",
      lambda: not re.search(r"^[ \t]*(?:import|from)[ \t]+(?:operator|functools)\b",
                            _SRC, re.M))

check("lexical strictness: leading zeros, ASCII only, reserved words", _all([
    ("007", E("parse")), ("01", E("parse")), ("1 + 007", E("parse")),
    ("0", V(0)), ("40", V(40)), ("10 + 0", V(10)),
    (u"\u0967", E("parse")), (u"x\u00e9", E("parse")), (u"\u00e9", E("parse")),
    ("_", E("parse")), ("let _ = 1 in 2", E("parse")), ("_ + 1", E("parse")),
    ("{end = 1}", E("parse")), ("fun in -> 1", E("parse")),
    ("let ref = 1 in 2", E("parse")), ("match 1 with | end -> 1 end", E("parse")),
    ("{a = 1}.end", E("parse")), ("1.5", E("parse")), ('"a\\b"', E("parse")),
    ('"abc', E("parse")), ('"a\nb"', E("parse")), ("a; b", E("parse")),
    ("1 & 2", E("parse")), ("1 :: 2", E("parse")), ("1 ? 2", E("parse")),
    ("true_ ", E("unbound")), ("_x", E("unbound")),
]))

check("error kinds are exactly right", _all([
    ("zz", E("unbound")), ("let x = 1 in y", E("unbound")),
    ("letrec a = b and b = 1 in a", E("uninit")), ("letrec x = x in 1", E("uninit")),
    ("let x = 1 in letrec x = x in 0", E("uninit")),
    ("1 / 0", E("div_zero")), ("1 % 0", E("div_zero")), ("1 / (2 - 2)", E("div_zero")),
    ("{a = 1}.b", E("no_field")), ("{}.a", E("no_field")),
    ("match 3 with | 1 -> 0 | 2 -> 0 end", E("no_match")),
    ("match {a = 1} with | {b = _} -> 0 end", E("no_match")),
    ("{a = 1, a = 2}", E("dup_field")),
    ("match 1 with | {a = _, a = _} -> 1 end", E("dup_field")),
    ("letrec x = 1 and x = 2 in x", E("dup_binding")),
    ("match {a = 1} with | {a = x, b = x} -> 1 end", E("dup_binding")),
    ("1 . a", E("type")), ("!1", E("type")), ("1 := 2", E("type")),
    ('2 * "ab"', E("type")), ('1 ++ "a"', E("type")), ('"a" ++ 1 ++ "b"', E("type")),
    ('1 == "a"', E("type")), ("{a = 1} == {a = 1}", E("type")),
    ("(fun x -> x) == (fun x -> x)", E("type")), ("true == 1", E("type")),
    ('1 < "a"', E("type")), ("true < false", E("type")), ('- "a"', E("type")),
    ("1 2 3", E("type")), ("true && 1", E("type")), ("1 && true", E("type")),
    ('"a" ++ ref 1', E("type")), ('"a" ++ {a = 1}', E("type")),
    ("1 < 2 < 3", E("parse")), ("1 == 2 == 3", E("parse")),
]))


def leak_probe():
    """No matter how broken the input, only MiniError with a legal kind escapes."""
    nasty = ["", "   ", "(", ")", "{", "}", "|", "!", "1 +", "* 2", "let", "letrec",
             "fun", "match", "end", "in", "->", ":=", "..", "1..2", '"', '""" ',
             "x.", "x.1", "{,}", "1 2 3", "((((1))))", "match 1 with | -> 2 end",
             "if true then 1", "fun x - > x", "1 <= 2 >= 3", "007", u"\u00e9",
             "letrec in", "ref", "!", "-", "1 / 0", "{a = 1}.b", "zz",
             "1 " * 40, "(" * 30 + "1" + ")" * 30, "let x = 1 in " * 12 + "x"]
    nasty += [s for s, _ in _slice(_MUT, 9, 0)]
    for src in nasty:
        got = _cand(src)
        if got[0] == "boom":
            return False
        if got[0] == "err" and got[1] not in KINDS:
            return False
    return True


_MUTP = gen_mutants(55505, 900)
_MUT = [(s, w) for s, w in [(s, _expect(s)) for s in _MUTP] if w is not None]

check("every rejection raises MiniError with a legal .kind", leak_probe)

check("evaluation order: operands fully evaluated before any type check", _all([
    ("zz + (1 / 0)", E("unbound")), ("(1 / 0) + zz", E("div_zero")),
    ("true + (1 / 0)", E("div_zero")), ("(1 / 0) + true", E("div_zero")),
    ('"x" / 0', E("type")), ('"x" % 0', E("type")),
    ("{a = 1}.b + (1 / 0)", E("no_field")), ("(1 / 0) + {a = 1}.b", E("div_zero")),
    ("1 (1 / 0)", E("div_zero")), ("zz (1 / 0)", E("unbound")),
    ("(1 / 0) zz", E("div_zero")), ('"a" ++ (1 / 0)', E("div_zero")),
    ("(1 / 0) ++ \"a\"", E("div_zero")), ('1 ++ (1 / 0)', E("div_zero")),
    ("{a = 1} == (1 / 0)", E("div_zero")), ("- (1 / 0)", E("div_zero")),
    ("(1 / 0) := 2", E("div_zero")), ("1 := (2 / 0)", E("div_zero")),
    ("let r = ref 1 in r := zz", E("unbound")),
    ("{a = zz, b = 1 / 0}", E("unbound")), ("{b = 1 / 0, a = zz}", E("div_zero")),
    ('"s" * (1 / 0)', E("div_zero")), ("true * zz", E("unbound")),
    ("let x = (1 / 0) in zz", E("div_zero")),
    ("letrec a = (1 / 0) and b = zz in 1", E("div_zero")),
    ("match zz with | _ -> (1 / 0) end", E("unbound")),
    ("(zz) . a", E("unbound")), ("!(1 / 0)", E("div_zero")),
]))

check("evaluation order: &&, || and if check before evaluating the rest", _all([
    ("1 && (1 / 0)", E("type")), ("1 || (1 / 0)", E("type")),
    ("1 && zz", E("type")), ('"a" || zz', E("type")),
    ("(1 / 0) && false", E("div_zero")), ("(1 / 0) || true", E("div_zero")),
    ("zz && true", E("unbound")), ("zz || true", E("unbound")),
    ("true && 1", E("type")), ("false || 1", E("type")),
    ("true && zz", E("unbound")), ("false || zz", E("unbound")),
    ("false && zz", V(False)), ("true || zz", V(True)),
    ("if 1 then (1 / 0) else 2", E("type")), ("if zz then 1 else 2", E("unbound")),
    ("if (1 / 0) then 1 else 2", E("div_zero")),
    ("if true then 1 else (1 / 0)", V(1)), ("if false then (1 / 0) else 1", V(1)),
    ("if {a = 1} then 1 else 2", E("type")),
    ("false && 1 && (1 / 0)", V(False)),
    ("true || 1 || (1 / 0)", V(True)),
]))

check("parse-time errors beat runtime errors, in the stated order", _all([
    ("(1 / 0) + (1 < 2 < 3)", E("parse")), ("zz + {a = 1, a = 2}", E("dup_field")),
    ("letrec x = 1 and x = 2 in {a = 1, a = 2}", E("dup_field")),
    ("letrec x = 1 and x = 2 in 0", E("dup_binding")),
    ("letrec x = 1 and x = 2 in zz", E("dup_binding")),
    ("match 1 with | {a = v, b = v} -> {c = 1, c = 2} end", E("dup_binding")),
    ("match 1 with | {a = v} -> {c = 1, c = 2} | {b = w, c = w} -> 0 end",
     E("dup_field")),
    ("(1 / 0) + {a = 1, a = 2}", E("dup_field")),
    ("{a = 1, a = 2} + (1 / 0)", E("dup_field")),
    ("zz + (1 <", E("parse")), ("1 / 0 +", E("parse")),
    ("let x = zz in {b = 1, b = 2}", E("dup_field")),
    ("letrec q = 1 and q = 2 in 1 < 2 < 3", E("parse")),
    ("match 1 with | {a = v, b = v} -> 1 < 2 < 3 end", E("dup_binding")),
]))

check("parse errors", _all([
    ("", E("parse")), ("   ", E("parse")), ("(", E("parse")), ("1 +", E("parse")),
    ("1 + * 2", E("parse")), ("let x = 1 in", E("parse")),
    ("let 1 = 2 in 3", E("parse")), ("let let = 1 in 2", E("parse")),
    ("fun -> x", E("parse")), ("match 1 with end", E("parse")),
    ("match 1 with | _ -> 1", E("parse")), ("f let x = 1 in x", E("parse")),
    ("{a = 1", E("parse")), ("{a}", E("parse")), ("x.", E("parse")),
    ("x.1", E("parse")), ("ref", E("parse")), ("1 <= 2 >= 3", E("parse")),
    ("end", E("parse")), ("(1))", E("parse")), ("{,}", E("parse")),
    ("fun x - > x", E("parse")), ("match 1 with | -> 2 end", E("parse")),
    ("if true then 1", E("parse")), ("1 in 2", E("parse")), ("(1, 2)", E("parse")),
    ("match 1 with | 1 -> 2 end end", E("parse")), ("let x = 1 x", E("parse")),
    ("fun x -> ", E("parse")), ("letrec x = 1 in", E("parse")),
    ("letrec x = 1 and in x", E("parse")), ("1 ++", E("parse")),
    ("if 1 then 2", E("parse")), ("{a = 1}.", E("parse")),
]))

_ALLERR = _ERRS + _DERRS + _MERRS
for _i in range(2):
    check("randomised differential, error kinds (bucket %d)" % (_i + 1),
          _all(_slice(_ALLERR, 2, _i)))

check("randomised differential, which error fires first", _all(_EERRS))

check("randomised differential, mutated programs", _all(_MUT))

_t.cancel()
report()
