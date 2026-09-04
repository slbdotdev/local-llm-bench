import sys, random, inspect
fails = []
def check(name, cond):
    if not cond: fails.append(name)

try:
    import interp
    F = interp.evaluate
    IE = interp.InterpError
    check("InterpError subclass of Exception", isinstance(IE, type) and issubclass(IE, Exception))
except Exception as e:
    print("FAIL", [f"import: {e!r}"]); sys.exit(1)

def expect_ok(src, want):
    try:
        got = F(src)
        check(f"{src!r} -> {got!r}", type(got) is type(want) and got == want)
    except Exception as e:
        fails.append(f"{src!r} raised {type(e).__name__}: {e}")

def expect_err(src, name=None):
    try:
        got = F(src)
        fails.append(f"{src!r} returned {got!r}, expected InterpError ({name or src})")
    except IE:
        pass
    except Exception as e:
        fails.append(f"{src!r} raised {type(e).__name__}, not InterpError ({name or src})")

# --- values, arithmetic, precedence, associativity ---
expect_ok("42", 42)
expect_ok('"hi"', "hi")
expect_ok('""', "")
expect_ok("((((1))))", 1)
expect_ok("1 + 2 * 3", 7)
expect_ok("(1 + 2) * 3", 9)
expect_ok("2 * 3 + 4 * 5", 26)
expect_ok("10 - 4 - 3", 3)
expect_ok("10 - (4 - 3)", 9)
expect_ok("100 / 10 / 5", 2)
expect_ok("7 / 2", 3)
expect_ok("0 - 7 / 2", -3)
expect_ok("(0 - 7) / 2", -3)
expect_ok("(0 - 9) / 4", -2)
expect_ok("0 - 9 / 4", -2)
expect_ok("100 / 7 / 3", 4)
expect_ok("2 * 3 - 1", 5)
expect_ok("1 + 2 == 3", True)
expect_ok("1 + 2 == 4", False)
expect_ok("1 + 2 < 4", True)
expect_ok("let f = fn x -> x in f 1 == 1", True)
check("comparison is bool", isinstance(F("1 < 2"), bool) and isinstance(F("2 < 1"), bool))

# --- let, scoping, shadowing ---
expect_ok("let x = 1 in x", 1)
expect_ok("let x = 1 in let x = x + 2 in x * 10", 30)
expect_ok("let x = 1 in let y = 2 in x + y", 3)
expect_ok("let a = 2 in a * a + 1", 5)
expect_ok("let x = 5 in (fn x -> x * 2) 3", 6)
expect_err("let x = x in 1", "rhs not in own scope")

# --- closures ---
expect_ok("let add = fn x -> fn y -> x + y in add 3 4", 7)
expect_ok("let add = fn x -> fn y -> x + y in let f = add 10 in f 3", 13)
expect_ok("let y = 10 in let f = fn x -> x + y in let y = 99 in f 1", 11)
f = F("let y = 1 in fn x -> x + y")
g = F("let y = 100 in fn x -> x + y")
check("closure capture", callable(f) and f(1) == 2 and g(1) == 101)
f2 = F("fn x -> x * 2")
check("closure callable", callable(f2) and f2(5) == 10)
try:
    f3 = F("fn x -> x + 1")
    f3("a")
    fails.append("closure type mismatch not raised")
except IE:
    pass
except Exception as e:
    fails.append(f"closure mismatch raised {type(e).__name__}")
expect_ok("let f = fn x -> x + 1 in let g = fn x -> x * 10 in f (g 2)", 21)
expect_ok("let f = fn x -> x + 1 in 2 * f 2", 6)
expect_ok("let f = fn x -> x * 2 in 10 - f 2", 6)
expect_ok("let f = fn x -> x in 1 + f 2 * 3", 7)
expect_ok("let f = fn x -> fn y -> x + y in f 1 2 == 3", True)
expect_err("let f = fn x -> x - y in f 1", "unbound y in closure")
expect_ok("let y = 3 in let f = fn x -> x - y in f 10", 7)

# --- strings, if ---
expect_ok('if "a" == "a" then "yes" else "no"', "yes")
expect_ok('if "a" == "b" then 1 else 2', 2)
expect_ok("if 2 <= 2 then 1 else 0", 1)
expect_ok('if "ab" == "ab" then 1 else 0', 1)
expect_ok('let s = "ab" in if s == "ab" then s else "z"', "ab")
expect_ok("if 1 < 2 then 1 else 1 / 0", 1)
expect_ok("if 2 < 1 then 1 / 0 else 2", 2)
expect_ok("if 1 < 2 then 0 - 5 else x", -5)

# --- runtime errors ---
expect_err("x", "unbound")
expect_err("let x = 1 in y", "unbound")
expect_err('"a" + 1', "type")
expect_err('1 + "a"', "type")
expect_err('"a" * 2', "type")
expect_err('"a" < "b"', "ordering")
expect_err('1 == "a"', "mixed eq")
expect_err('"a" != 1', "mixed eq")
expect_err("(1 < 2) == (2 < 1)", "bool cmp")
expect_err("(1 < 2) + 3", "bool arith")
expect_err("if 1 then 2 else 3", "cond")
expect_err('if "a" then 2 else 3', "cond")
expect_err("1 / 0", "div0")
expect_err("1 / (2 - 2)", "div0")
expect_err("(0 - 1) / 0", "div0")
expect_err("5 3", "nonfn")
expect_err('"f" 1', "nonfn")
expect_err("(1 < 2) 3", "nonfn")
expect_err("let f = 1 in f 2", "nonfn")
expect_err("(fn x -> x) == (fn x -> x)", "fn cmp")
expect_err("(fn x -> x)(1)(2)", "apply int result")

# --- parse errors ---
for bad in ["", "   ", "(", ")", "(1", "1)", "1 +", "1 + * 2", "1 * + 2",
            "let x = 1", "let x = 1 in", "let x 1 in x", "let x = in x",
            "let 1 = 2 in 3", "let if = 1 in 1", "let x = 1 in 1 in 2",
            "if 1 then 2", "if 1 else 2", "if then else", "fn x", "fn x 1",
            "fn -> 1", "fn 1 -> 2", "1 < 2 < 3", '"abc', 'a"b"', "-5",
            "1 + 2 +", "f (", "x )", "1 2 $ 3", "fn x ->", "@"]:
    expect_err(bad, "parse")

# --- randomised differential test against a brute-force AST evaluator ---
random.seed(17)
NAMES = ["x", "y", "f", "g"]
STRS = ["", "a", "b", "ab"]
CMP = ["==", "!=", "<", "<=", ">", ">="]

def gen(depth, scope):
    r = random.random()
    if depth <= 0 or r < 0.30:
        c = random.random()
        if c < 0.5:
            return ("int", random.randint(0, 9))
        if c < 0.75:
            return ("str", random.choice(STRS))
        if scope:
            return ("var", random.choice(sorted(scope)))
        return ("int", random.randint(0, 9))
    if r < 0.45:
        op = random.choice(["+", "-", "*", "/"])
        return ("bin", op, gen(depth - 1, scope), gen(depth - 1, scope))
    if r < 0.55:
        op = random.choice(CMP)
        return ("cmp", op, gen(depth - 1, scope), gen(depth - 1, scope))
    if r < 0.68:
        name = random.choice(NAMES)
        if random.random() < 0.35:
            p = random.choice(NAMES)
            body = gen(depth - 1, scope | {name, p})
            return ("let", name, ("fn", p, body), gen(depth - 1, scope | {name}))
        return ("let", name, gen(depth - 1, scope), gen(depth - 1, scope | {name}))
    if r < 0.78:
        name = random.choice(NAMES)
        return ("fn", name, gen(depth - 1, scope | {name}))
    if r < 0.90:
        c = random.random()
        if c < 0.5:
            p = random.choice(NAMES)
            f = ("fn", p, gen(depth - 1, scope | {p}))
        elif scope and random.random() < 0.8:
            f = ("var", random.choice(sorted(scope)))
        else:
            f = gen(depth - 1, scope)
        return ("app", f, gen(depth - 1, scope))
    return ("if", gen(depth - 1, scope), gen(depth - 1, scope), gen(depth - 1, scope))

def rend(n):
    """Render AST to source with minimal parentheses honouring the precedence table."""
    k = n[0]
    if k == "int": return str(n[1]), 5
    if k == "str": return '"' + n[1] + '"', 5
    if k == "var": return n[1], 5
    if k == "if":
        c, _ = rend(n[1]); t, tp = rend(n[2]); e, _ = rend(n[3])
        if tp == 0: t = "(" + t + ")"
        return f"if {c} then {t} else {e}", 0
    if k == "let":
        a, _ = rend(n[2]); b, _ = rend(n[3])
        return f"let {n[1]} = {a} in {b}", 0
    if k == "fn":
        b, _ = rend(n[2])
        return f"fn {n[1]} -> {b}", 0
    if k == "cmp":
        l, lp = rend(n[2]); r, rp = rend(n[3])
        if lp < 2: l = "(" + l + ")"
        if rp < 2: r = "(" + r + ")"
        return f"{l} {n[1]} {r}", 1
    if k == "app":
        l, lp = rend(n[1]); r, rp = rend(n[2])
        if lp < 4: l = "(" + l + ")"
        if rp < 5: r = "(" + r + ")"
        return f"{l} {r}", 4
    # bin
    op = n[1]; p = 3 if op in ("*", "/") else 2
    l, lp = rend(n[2]); r, rp = rend(n[3])
    if lp < p: l = "(" + l + ")"
    if rp <= p: r = "(" + r + ")"
    return f"{l} {op} {r}", p

class RefErr(Exception):
    pass

def tdiv(a, b):
    if b == 0:
        raise RefErr("div0")
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q

def rev(n, env):
    k = n[0]
    if k in ("int", "str"):
        return n[1]
    if k == "var":
        if n[1] not in env:
            raise RefErr("unbound")
        return env[n[1]]
    if k == "let":
        return rev(n[3], {**env, n[1]: rev(n[2], env)})
    if k == "fn":
        captured = dict(env)
        return lambda a, c=captured, p=n[1], b=n[2]: rev(b, {**c, p: a})
    if k == "app":
        f = rev(n[1], env); a = rev(n[2], env)
        if not callable(f):
            raise RefErr("nonfn")
        return f(a)
    if k == "if":
        c = rev(n[1], env)
        if not isinstance(c, bool):
            raise RefErr("cond")
        return rev(n[2] if c else n[3], env)
    if k == "cmp":
        op = n[1]; l = rev(n[2], env); r = rev(n[3], env)
        if isinstance(l, bool) or isinstance(r, bool):
            raise RefErr("boolcmp")
        if op in ("==", "!="):
            ok = (isinstance(l, int) and isinstance(r, int)) or \
                 (isinstance(l, str) and isinstance(r, str))
            if not ok:
                raise RefErr("mixed")
            return (l == r) if op == "==" else (l != r)
        if not (isinstance(l, int) and isinstance(r, int)):
            raise RefErr("ordering")
        return {"<": l < r, "<=": l <= r, ">": l > r, ">=": l >= r}[op]
    if k == "bin":
        op = n[1]; l = rev(n[2], env); r = rev(n[3], env)
        if not (isinstance(l, int) and not isinstance(l, bool) and
                isinstance(r, int) and not isinstance(r, bool)):
            raise RefErr("arith")
        if op == "+": return l + r
        if op == "-": return l - r
        if op == "*": return l * r
        return tdiv(l, r)
    raise RefErr("bad node")

def probe(v, depth, exc):
    if callable(v):
        if depth >= 2:
            return ("fn",)
        subs = []
        for arg in (0, 1):
            try:
                subs.append(probe(v(arg), depth + 1, exc))
            except exc:
                subs.append(("err",))
        return ("fn", tuple(subs))
    return ("val", type(v).__name__, v)

def ref_outcome(ast):
    try:
        return probe(rev(ast, {}), 0, RefErr)
    except RefErr:
        return ("err",)

def sol_outcome(src):
    try:
        v = F(src)
    except IE:
        return ("err",)
    except Exception as e:
        return ("badexc", repr(e))
    try:
        return probe(v, 0, IE)
    except IE:
        return ("err",)
    except Exception as e:
        return ("badexc", repr(e))

ncases = 0
for i in range(500):
    ast = gen(3, set())
    src = rend(ast)[0]
    if len(src) > 80:
        continue
    ncases += 1
    want = ref_outcome(ast)
    got = sol_outcome(src)
    if got != want:
        tag = "mismatch" if got[0] != "badexc" else "wrong exception type"
        fails.append(f"rand {src!r}: got {got} want {want} ({tag})")
check("enough random cases", ncases > 300)

if fails:
    print("FAIL", fails[:12]); sys.exit(1)
print("PASS")