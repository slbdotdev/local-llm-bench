import sys, random
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    from schedule import select

    # ---- fixed edge cases ----
    cases = [
        ([], []),
        ([("a", 0, 5, 3)], ["a"]),
        ([("a", 0, 5, 0)], []),
        ([("a", 0, 5, -2)], []),
        ([("a", 3, 3, 4)], ["a"]),                                  # zero-length, w>0
        ([("a", 3, 3, 0)], []),
        ([("a", 3, 3, -1)], []),
        ([("a", 0, 5, 3), ("b", 5, 10, 4)], ["a", "b"]),            # touching, no conflict
        ([("a", 0, 5, 3), ("b", 4, 10, 9)], ["b"]),                 # overlap
        ([("a", 0, 10, 5), ("b", 0, 4, 3), ("c", 4, 10, 3)], ["b", "c"]),  # 6 beats 5, touching pair
        ([("a", 0, 4, 2), ("b", 4, 8, 2), ("c", 0, 8, 4)], ["c"]),  # weight tie -> fewest jobs
        ([("x", 0, 10, 6), ("a", 0, 5, 3), ("b", 5, 10, 3)], ["x"]),  # fewest beats lex-smaller pair
        ([("a", 0, 5, 3), ("b", 0, 5, 3)], ["a"]),                  # identical: fewest then lex
        ([("a", 0, 5, 2), ("b", 0, 5, 2), ("c", 5, 9, 2), ("d", 5, 9, 2)], ["a", "c"]),
        ([("a", 0, 6, 5), ("z1", 3, 3, 1), ("z2", 3, 3, 1)], ["a", "z1", "z2"]),  # zero-length inside
        ([("a", 0, 6, 5), ("z", 3, 3, 0)], ["a"]),                  # zero-length w=0 excluded
        ([("a", 0, 6, 5), ("z", 3, 3, -1)], ["a"]),                 # zero-length w<0 excluded
        ([("n", 0, 5, 1), ("m", 5, 5, 1)], ["m", "n"]),             # zero-length touches job
        ([("j2", 0, 5, 1), ("j10", 5, 9, 1), ("j1", 9, 12, 1)], ["j1", "j10", "j2"]),  # string order
        ([("b", 0, 5, 4), ("a", 0, 5, -3)], ["b"]),                 # negative ignored
        ([("p", 2, 2, 1), ("q", 2, 2, 1), ("r", 2, 2, 1)], ["p", "q", "r"]),  # all at same instant
        ([("a", 0, 2, 1), ("b", 1, 3, 1), ("c", 2, 4, 1), ("d", 3, 5, 1)], ["a", "c"]),
        ([("z", 0, 9, 4), ("a", 0, 3, 2), ("b", 3, 6, 2), ("c", 6, 9, 2)], ["a", "b", "c"]),
    ]
    for jobs, want in cases:
        snap = [tuple(j) for j in jobs]
        try:
            got = select(jobs)
        except Exception as e:
            fails.append(f"fixed {jobs!r} raised {e!r}"); continue
        check(f"fixed {jobs!r} -> {want}", got == want)
        check(f"fixed {jobs!r} input intact", [tuple(j) for j in jobs] == snap)
        check(f"fixed {jobs!r} list of str sorted", isinstance(got, list) and got == sorted(got)
              and all(isinstance(x, str) for x in got))

    # ---- brute-force reference over all subsets ----
    def brute(jobs):
        n = len(jobs)
        best = None
        for mask in range(1 << n):
            chosen = [jobs[i] for i in range(n) if (mask >> i) & 1]
            ok = True
            for a in range(len(chosen)):
                _, s1, e1, _ = chosen[a]
                for b in range(a + 1, len(chosen)):
                    _, s2, e2, _ = chosen[b]
                    if s1 < e1 and s2 < e2 and s1 < e2 and s2 < e1:
                        ok = False; break
                if not ok: break
            if not ok: continue
            w = sum(j[3] for j in chosen)
            key = (-w, len(chosen), tuple(sorted(j[0] for j in chosen)))
            if best is None or key < best:
                best = key
        return list(best[2])

    NAMES = [a + b for a in "abcdef" for b in "abcdef"] + ["j1", "j2", "j10", "j20"]
    random.seed(1801)
    nrand = 0
    # phase 1: general mixed instances
    for it in range(220):
        n = random.randint(0, 9)
        ids = random.sample(NAMES, n)
        jobs = []
        for jid in ids:
            s = random.randint(0, 10)
            e = s + random.choice([0, 0, 0, 1, 1, 1, 2, 3, 5])
            jobs.append((jid, s, e, random.choice([-2, -1, 0, 0, 1, 1, 2, 3, 4])))
        want = brute(jobs)
        try:
            got = select(jobs)
        except Exception as ex:
            fails.append(f"rand {jobs!r} raised {ex!r}"); continue
        nrand += 1
        if got != want:
            fails.append(f"rand {jobs!r}: got {got} want {want}")
    # phase 2: dense ties (equal weights, tiny timeline) to stress rules 4 and 5
    for it in range(220):
        n = random.randint(0, 8)
        ids = random.sample(NAMES, n)
        jobs = []
        for jid in ids:
            s = random.randint(0, 6)
            e = s + random.choice([0, 0, 1, 1, 2])
            jobs.append((jid, s, e, random.choice([0, 1, 1, 1, 2])))
        want = brute(jobs)
        try:
            got = select(jobs)
        except Exception as ex:
            fails.append(f"tie {jobs!r} raised {ex!r}"); continue
        nrand += 1
        if got != want:
            fails.append(f"tie {jobs!r}: got {got} want {want}")
    # phase 3: all zero-length jobs at a few instants
    for it in range(120):
        n = random.randint(0, 10)
        ids = random.sample(NAMES, n)
        jobs = [(jid, random.randint(0, 3), ) for jid in ids]
        jobs = [(jid, t, t, random.choice([-1, 0, 1, 2])) for (jid, t) in jobs]
        want = brute(jobs)
        try:
            got = select(jobs)
        except Exception as ex:
            fails.append(f"zlen {jobs!r} raised {ex!r}"); continue
        nrand += 1
        if got != want:
            fails.append(f"zlen {jobs!r}: got {got} want {want}")
    check("enough random cases", nrand >= 500)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:12]); sys.exit(1)
print("PASS")