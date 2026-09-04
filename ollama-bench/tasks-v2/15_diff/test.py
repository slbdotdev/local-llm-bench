import sys, random, time, inspect
fails = []
def check(name, cond):
    if not cond: fails.append(name)
def lcs(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]
def valid(a, b, script):
    i = 0; out = []; cost = 0
    for op, line in script:
        if op == "=":
            if i >= len(a) or a[i] != line: return False, "bad ="
            out.append(line); i += 1
        elif op == "-":
            if i >= len(a) or a[i] != line: return False, "bad -"
            i += 1; cost += 1
        elif op == "+":
            out.append(line); cost += 1
        else:
            return False, "bad op"
    if i != len(a): return False, "leftover a"
    if out != b: return False, "does not produce b"
    want = len(a) + len(b) - 2 * lcs(a, b)
    if cost != want: return False, f"not minimal {cost} vs {want}"
    return True, ""
try:
    import mydiff
    check("no difflib", "difflib" not in inspect.getsource(mydiff))
    D, A = mydiff.diff, mydiff.apply
    cases = [(["a", "b", "c"], ["a", "c", "d"]), ([], []), (["a"], []), ([], ["a"]), (["a", "a", "a"], ["a", "a"]),
             (["x"], ["y"]), (list("abcabba"), list("cbabac")), (list("kitten"), list("sitting")),
             (["same"] * 5, ["same"] * 5), (list("abc"), list("cba")), (list("aXbXc"), list("XaXbXc"))]
    for a, b in cases:
        try:
            s = D(list(a), list(b)); ok, why = valid(a, b, s)
            check(f"diff {a} -> {b}: {why}", ok)
            check(f"apply {a} -> {b}", A(list(a), s) == b)
        except Exception as e:
            fails.append(f"{a}->{b} raised {e!r}")
    try:
        A(["a", "b"], [("=", "a"), ("-", "x")]); fails.append("apply no ValueError on mismatch")
    except ValueError:
        pass
    try:
        A(["a", "b"], [("=", "a")]); fails.append("apply no ValueError on leftover")
    except ValueError:
        pass
    random.seed(4)
    for i in range(60):
        a = [random.choice("abcd") for _ in range(random.randint(0, 12))]
        b = list(a)
        for _ in range(random.randint(0, 5)):
            if b and random.random() < 0.5: b.pop(random.randrange(len(b)))
            else: b.insert(random.randint(0, len(b)), random.choice("abcd"))
        s = D(list(a), list(b)); ok, why = valid(a, b, s)
        if not ok: fails.append(f"rand {i}: {why}")
        if A(list(a), s) != b: fails.append(f"rand apply {i}")
    big_a = [str(random.randint(0, 50)) for _ in range(400)]
    big_b = [x for x in big_a if random.random() < 0.9] + [str(random.randint(0, 50)) for _ in range(40)]
    t0 = time.time(); s = D(list(big_a), list(big_b)); dt = time.time() - t0
    ok, why = valid(big_a, big_b, s)
    check(f"big valid {why}", ok)
    check("big fast", dt < 3.0)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
