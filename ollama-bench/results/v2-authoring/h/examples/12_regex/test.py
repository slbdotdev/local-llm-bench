import sys, re, random, inspect
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    import minire
    src = inspect.getsource(minire)
    check("no re import", not re.search(r"^\s*(import re\b|from re\b)", src, re.M))
    F = minire.fullmatch
    cases = [
        ("a*b", "aaab", True), ("a*b", "b", True), ("a*b", "aab a", False), ("colou?r", "color", True),
        ("colou?r", "colour", True), ("colou?r", "colouur", False), ("(ab|cd)+", "abcdab", True),
        ("(ab|cd)+", "", False), ("[^0-9]+", "ab1", False), ("[^0-9]+", "ab", True), ("", "", True),
        ("", "a", False), (".", "", False), (".", "x", True), ("a.c", "abc", True), ("a\\.c", "abc", False),
        ("a\\.c", "a.c", True), ("[a-c]+", "abcabc", True), ("[a-c]+", "abd", False), ("[]a]+", "]a]", True),
        ("[-a]+", "-a-", True), ("[a-]+", "a--", True), ("a|b|c", "b", True), ("a|b|c", "d", False),
        ("(a|ab)(c|bcd)(d*)", "abcd", True), ("(a*)*b", "aaab", True), ("(a*)*", "", True),
        ("x(ab)?y", "xy", True), ("x(ab)?y", "xaby", True), ("x(ab)?y", "xay", False),
        ("\\\\", "\\", True), ("a+", "", False), ("(a|b)*c", "ababc", True), ("(a|b)*c", "ababd", False),
        ("[0-9]+\\.[0-9]*", "3.14", True), ("[0-9]+\\.[0-9]*", ".14", False), ("(x|y)(x|y)", "xy", True),
        ("((a)(b))+", "abab", True), ("a(b|)c", "ac", True), ("a(b|)c", "abc", True),
    ]
    for p, t, want in cases:
        try:
            got = F(p, t)
            check(f"{p!r} vs {t!r} -> {got}", got == want)
        except Exception as e:
            fails.append(f"{p!r} vs {t!r} raised {e!r}")
    for bad in ["(", ")", "a)", "(a", "[abc", "*a", "+", "?", "a\\", "a|*", "(|*)"]:
        try:
            F(bad, "a"); fails.append(f"no ValueError for {bad!r}")
        except ValueError:
            pass
        except Exception as e:
            fails.append(f"{bad!r} raised {type(e).__name__}")
    # Randomised differential test against Python's re on a restricted grammar.
    random.seed(12)
    def gen(depth=0):
        r = random.random()
        if depth > 2 or r < 0.45:
            atom = random.choice(["a", "b", "c", ".", "[ab]", "[^a]", "[a-c]"])
        elif r < 0.7:
            atom = "(" + gen(depth + 1) + "|" + gen(depth + 1) + ")"
        else:
            atom = "(" + gen(depth + 1) + gen(depth + 1) + ")"
        q = random.choice(["", "", "*", "+", "?"])
        s = atom + q
        if random.random() < 0.5 and depth < 2:
            s += gen(depth + 1)
        return s
    n = 0
    for i in range(300):
        p = gen()
        if len(p) > 24: continue
        t = "".join(random.choice("abc") for _ in range(random.randint(0, 6)))
        want = re.fullmatch(p, t) is not None
        try:
            got = F(p, t)
        except Exception as e:
            fails.append(f"rand {p!r} vs {t!r} raised {e!r}"); continue
        n += 1
        if got != want: fails.append(f"rand {p!r} vs {t!r}: got {got} want {want}")
    check("enough random cases", n > 150)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:12]); sys.exit(1)
print("PASS")
