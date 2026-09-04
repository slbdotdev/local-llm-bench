import sys, random
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    from deps import resolve, CycleError
    check("subclass", issubclass(CycleError, ValueError))
    check("ex1", resolve({"app": ["lib", "util"], "lib": ["util"]}) == ["util", "lib", "app"])
    check("ex2", resolve({"b": [], "a": []}) == ["a", "b"])
    check("empty", resolve({}) == [])
    check("tie-break", resolve({"z": ["m"], "a": ["m"], "m": []}) == ["m", "a", "z"])
    check("implicit nodes", resolve({"x": ["c", "a"]}) == ["a", "c", "x"])
    check("diamond", resolve({"d": ["b", "c"], "b": ["a"], "c": ["a"]}) == ["a", "b", "c", "d"])
    check("alpha among ready", resolve({"b": ["a"], "c": []}) == ["a", "b", "c"])
    for cyc in [{"a": ["b"], "b": ["a"]}, {"a": ["a"]}, {"a": ["b"], "b": ["c"], "c": ["a"], "d": []}]:
        try:
            resolve(cyc); fails.append(f"no CycleError for {cyc}")
        except CycleError as e:
            cy = getattr(e, "cycle", None)
            ok = isinstance(cy, list) and len(cy) >= 2 and cy[0] == cy[-1]
            if ok:
                for u, v in zip(cy, cy[1:]):
                    # v depends on u or u depends on v: accept either direction
                    if not (u in cyc.get(v, []) or v in cyc.get(u, [])): ok = False
            check(f"cycle attr {cyc}", ok)
    random.seed(11)
    for i in range(30):
        n = random.randint(2, 15)
        names = [f"n{k:02d}" for k in range(n)]
        random.shuffle(names)
        d = {x: [] for x in names}
        for a_i in range(n):
            for b_i in range(a_i):
                if random.random() < 0.3:
                    d[names[a_i]].append(names[b_i])  # depends on earlier index: acyclic
        order = resolve(d)
        pos = {x: k for k, x in enumerate(order)}
        ok = sorted(order) == sorted(names) and all(pos[y] < pos[x] for x in d for y in d[x])
        # determinism: rerun gives same result
        ok = ok and resolve(d) == order
        check(f"rand {i}", ok)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
