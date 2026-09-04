import sys, random
fails = []
def check(name, cond):
    if not cond: fails.append(name)
def ref_merge(iv):
    s = set()
    for a, b in iv: s.update(range(a, b + 1))
    out = []; cur = None
    for x in sorted(s):
        if cur and x == cur[1] + 1: cur[1] = x
        else:
            if cur: out.append(tuple(cur))
            cur = [x, x]
    if cur: out.append(tuple(cur))
    return out
try:
    import intervals as I
    check("basic", I.merge([(1, 3), (2, 6), (8, 10), (15, 18)]) == [(1, 6), (8, 10), (15, 18)])
    check("adjacent", I.merge([(1, 3), (4, 6)]) == [(1, 6)])
    check("gap", I.merge([(1, 3), (5, 6)]) == [(1, 3), (5, 6)])
    check("unsorted", I.merge([(5, 6), (1, 3), (4, 4)]) == [(1, 6)])
    check("empty", I.merge([]) == [])
    check("single point", I.merge([(2, 2)]) == [(2, 2)])
    check("nested", I.merge([(1, 10), (2, 3), (4, 5)]) == [(1, 10)])
    src = [(5, 6), (1, 2)]; I.merge(src)
    check("not mutated", src == [(5, 6), (1, 2)])
    check("negative", I.merge([(-5, -3), (-2, 0)]) == [(-5, 0)])
    check("insert mid", I.insert([(1, 2), (5, 6), (9, 10)], (3, 7)) == [(1, 7), (9, 10)])
    check("insert new", I.insert([(1, 2), (9, 10)], (4, 5)) == [(1, 2), (4, 5), (9, 10)])
    check("insert empty", I.insert([], (1, 1)) == [(1, 1)])
    check("insert span all", I.insert([(1, 2), (9, 10)], (0, 20)) == [(0, 20)])
    check("insert adjacent", I.insert([(1, 2), (4, 5)], (3, 3)) == [(1, 5)])
    check("length", I.total_length([(1, 3), (3, 4), (10, 10)]) == 5)
    check("length empty", I.total_length([]) == 0)
    check("length overlap", I.total_length([(1, 10), (5, 15)]) == 15)
    for fn, arg in [(I.merge, [(3, 1)]), (I.insert, ([(1, 2)], (5, 4))), (I.total_length, [(2, 1)])]:
        try:
            fn(arg) if fn is not I.insert else fn(*arg); fails.append(f"no ValueError {fn.__name__}")
        except ValueError:
            pass
    random.seed(5)
    for i in range(60):
        iv = []
        for _ in range(random.randint(0, 8)):
            a = random.randint(-10, 30); iv.append((a, a + random.randint(0, 6)))
        want = ref_merge(iv)
        check(f"rand merge {i}", [tuple(x) for x in I.merge(iv)] == want)
        a = random.randint(-10, 30); new = (a, a + random.randint(0, 10))
        check(f"rand insert {i}", [tuple(x) for x in I.insert(want, new)] == ref_merge(want + [new]))
        check(f"rand len {i}", I.total_length(iv) == sum(b - a + 1 for a, b in want))
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
