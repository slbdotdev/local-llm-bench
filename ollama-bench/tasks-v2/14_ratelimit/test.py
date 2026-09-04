import sys, random, inspect, math
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    import ratelimit
    src = inspect.getsource(ratelimit)
    check("no time.time", "time.time(" not in src and "monotonic(" not in src)
    R = ratelimit.SlidingWindowLimiter
    r = R(2, 10.0)
    check("a0", r.allow("a", 0.0) is True)
    check("a5", r.allow("a", 5.0) is True)
    check("a9", r.allow("a", 9.0) is False)
    check("retry 1", math.isclose(r.retry_after("a", 9.0), 1.0))
    check("remaining 0", r.remaining("a", 9.0) == 0)
    check("a10 boundary", r.allow("a", 10.0) is True)
    check("remaining after", r.remaining("a", 10.0) == 0)
    check("retry 5", math.isclose(r.retry_after("a", 10.0), 5.0))
    check("retry 0 when free", r.retry_after("b", 0.0) == 0.0)
    check("remaining new key", r.remaining("b", 0.0) == 2)
    check("keys tracked", set(r.keys()) == {"a"})
    check("a15 boundary", r.allow("a", 15.0) is True)
    check("a20 ok", r.allow("a", 20.0) is True)
    check("keys pruned", set(r.keys()) == {"a"})
    check("a60 expired all", r.remaining("a", 60.0) == 2 and set(r.keys()) == set())
    r.allow("z", 1.0); r.reset("z")
    check("reset", r.remaining("z", 1.0) == 2 and "z" not in r.keys())
    for bad in [(0, 1.0), (1, 0.0), (1, -1.0)]:
        try:
            R(*bad); fails.append(f"no ValueError {bad}")
        except ValueError:
            pass
    # Randomised differential test against a brute-force model.
    random.seed(9)
    for trial in range(40):
        limit = random.randint(1, 4); window = random.choice([1.0, 2.5, 7.0])
        r = R(limit, window); log = {}
        now = {}
        for step in range(60):
            key = random.choice("xy")
            now[key] = now.get(key, 0.0) + random.choice([0.0, 0.5, 1.0, 2.5, 7.0])
            t = now[key]
            inwin = [x for x in log.get(key, []) if t - window < x <= t]
            want_rem = limit - len(inwin)
            want_allow = want_rem > 0
            want_retry = 0.0 if want_allow else (min(inwin) + window - t)
            got_rem = r.remaining(key, t); got_retry = r.retry_after(key, t); got = r.allow(key, t)
            if got_rem != want_rem: fails.append(f"rand rem {trial}/{step}: {got_rem} vs {want_rem}"); break
            if not math.isclose(got_retry, want_retry, abs_tol=1e-9): fails.append(f"rand retry {trial}/{step}: {got_retry} vs {want_retry}"); break
            if got != want_allow: fails.append(f"rand allow {trial}/{step}: {got} vs {want_allow}"); break
            if got: log.setdefault(key, []).append(t)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
