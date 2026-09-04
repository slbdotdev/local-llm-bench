import sys, random

TOTAL = 69
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = f"{name} raised {type(e).__name__}"
    if not ok:
        fails.append(name)


def check_raises(name, fn, exc):
    try:
        fn()
    except exc:
        return
    except Exception as e:
        fails.append(f"{name}: wrong exception {type(e).__name__}")
        return
    fails.append(f"{name}: no {exc.__name__}")


fmt = parse = None
try:
    import duration
    fmt = duration.format_duration
    parse = duration.parse_duration
except Exception as e:
    fails.append(f"import failed: {e!r}")

if fmt is not None and parse is not None:
    fmt_cases = [
        (0, "0s"), (45, "45s"), (60, "1m"), (3600, "1h"), (3661, "1h1m1s"),
        (86400, "1d"), (90061, "1d1h1m1s"), (59, "59s"), (3599, "59m59s"),
        (86400 * 2 + 5, "2d5s"), (3600 * 23 + 60 * 59 + 59, "23h59m59s"),
    ]
    for n_, want in fmt_cases:
        check(f"format({n_}) == {want!r}", lambda a=n_, w=want: fmt(a) == w)

    parse_cases = [
        ("0s", 0), ("45s", 45), ("1m", 60), ("1h", 3600), ("1h1m1s", 3661),
        ("1d", 86400), ("1d1h1m1s", 90061), ("59s", 59), ("59m59s", 3599),
        ("2d5s", 86400 * 2 + 5), ("23h59m59s", 3600 * 23 + 60 * 59 + 59),
    ]
    for s_, want in parse_cases:
        check(f"parse({s_!r}) == {want}", lambda a=s_, w=want: parse(a) == w)

    invalid = [
        "", "5", "1h1d", "24h", "60m", "60s", "00s", "01h", "1d0s", "1d0h5m",
        "0d", "0m", "0h", " 1h", "1h ", "1H", "1D", "1d1h1m1s ", "1m1h",
        "1s1m", "-1s", "1.5s", "1d1d", "1h1h", "1x", "1d1h1m1s1d",
    ]
    for s_ in invalid:
        check_raises(f"parse({s_!r}) raises ValueError", lambda a=s_: parse(a), ValueError)

    # round-trip: format then parse must recover the original integer
    random.seed(7)
    for _ in range(20):
        n_ = random.choice([random.randint(0, 120), random.randint(0, 100000), random.randint(0, 10_000_000)])
        check(f"round-trip {n_}", lambda a=n_: parse(fmt(a)) == a)

    check("format(0) is exactly '0s'", lambda: fmt(0) == "0s")

    n = max(0, min(TOTAL, TOTAL - len(fails)))
else:
    n = 0

print(f"SCORE {n}/{TOTAL}")
if fails:
    print("FAIL", fails[:12])
    sys.exit(1)
print("PASS")
