import sys, re, random, inspect

fails = []


def check(name, cond):
    if not cond:
        fails.append(name)


def _raises(exc, fn):
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


try:
    import fixed as M
    Fixed = M.Fixed

    src = inspect.getsource(M)
    check("no decimal/fractions import",
          not re.search(r"^\s*(?:import|from)\s+(?:decimal|fractions)\b", src, re.M))

    check("MalformedNumber is ValueError subclass",
          hasattr(M, "MalformedNumber") and issubclass(M.MalformedNumber, ValueError))
    MN = M.MalformedNumber
    RHE, RHU, RD = M.ROUND_HALF_EVEN, M.ROUND_HALF_UP, M.ROUND_DOWN
    check("rounding constants distinct", len({RHE, RHU, RD}) == 3)

    # ---------- construction / parsing ----------
    for lit, u, s in [
        ("1.5", 15, 1), ("1e2", 100, 0), ("1.23e-3", 123, 5), ("-0.0", 0, 1),
        ("-.5", -5, 1), ("5.", 5, 0), ("+3.20", 320, 2), ("0e-5", 0, 5),
        ("100e-2", 100, 2), ("-12e3", -12000, 0), ("1E2", 100, 0), ("0.000", 0, 3),
        (".5e1", 5, 0), ("5.e-1", 5, 1), ("-0", 0, 0), ("1.e2", 100, 0),
        (".5", 5, 1), ("007", 7, 0), ("0.0e0", 0, 1),
    ]:
        try:
            f = Fixed(lit)
            if f._units != u:
                fails.append(f"parse {lit!r} units: {f._units} != {u}")
            if f._scale != s:
                fails.append(f"parse {lit!r} scale: {f._scale} != {s}")
        except Exception as e:
            fails.append(f"parse {lit!r} raised {e!r}")

    check("non-str raises TypeError", _raises(TypeError, lambda: Fixed(1)))

    for bad in ["", " ", " 1", "1 ", "1.2.3", ".e3", "1e", "+", "-", "-.e2",
                "1e+", "e5", ".", "1_0", "0x10", "nan", "1.2e1.5", "1.2e",
                "+.", "1e- 2", "1.5 e3", "Inf"]:
        try:
            Fixed(bad)
            fails.append(f"no MalformedNumber for {bad!r}")
        except MN:
            pass
        except Exception as e:
            fails.append(f"{bad!r} raised {type(e).__name__}, not MalformedNumber")

    # ---------- string form ----------
    for lit, want in [
        ("1.5", "1.5"), ("1e2", "100"), ("1.23e-3", "0.00123"), ("-0", "0"),
        ("0.000", "0.000"), ("-0.0", "0.0"), ("-.5", "-0.5"), ("5.", "5"),
        ("100e-2", "1.00"), ("1.50", "1.50"), ("-12e3", "-12000"),
        ("0e-5", "0.00000"), ("-1.25", "-1.25"), ("+3.20", "3.20"),
        ("5.e-1", "0.5"), (".5e1", "5"), ("0.0e0", "0.0"),
    ]:
        try:
            got = str(Fixed(lit))
            if got != want:
                fails.append(f"str {lit!r}: got {got!r} want {want!r}")
        except Exception as e:
            fails.append(f"str {lit!r} raised {e!r}")

    # ---------- equality / hash / ordering ----------
    check("eq cross-scale", Fixed("1.50") == Fixed("1.5"))
    check("ne cross-scale", not (Fixed("1.5") != Fixed("1.50")))
    check("eq zero forms", Fixed("-0.0") == Fixed("0"))
    check("eq exp forms", Fixed("1e2") == Fixed("100"))
    check("hash agree", hash(Fixed("1.50")) == hash(Fixed("1.5")))
    check("hash zero agree", hash(Fixed("-0.0")) == hash(Fixed("0")))
    check("set dedup", len({Fixed("1.5"), Fixed("1.50"), Fixed("1.500")}) == 1)
    d = {Fixed("1.5"): "x"}
    check("dict lookup", d[Fixed("1.50")] == "x")
    check("eq int False", not (Fixed("1") == 1))
    check("ne int True", Fixed("1") != 1)
    check("order non-Fixed TypeError", _raises(TypeError, lambda: Fixed("1") < 1))
    for a, b, want in [("1.5", "1.45", False), ("1.45", "1.5", True),
                       ("-1.5", "-1.45", True), ("-1.45", "-1.5", False),
                       ("1.50", "1.5", False), ("0", "-0.0", False),
                       ("-1", "1", True), ("1e2", "99.999", False)]:
        got = Fixed(a) < Fixed(b)
        if got != want:
            fails.append(f"lt {a},{b}: got {got} want {want}")
        got = Fixed(b) > Fixed(a)
        if got != want:
            fails.append(f"gt {b},{a}: got {got} want {want}")

    # ---------- arithmetic ----------
    for (a, op, b), want in [
        (("1.5", "+", "2.25"), "3.75"), (("1", "+", "0.000"), "1.000"),
        (("0.1", "+", "0.2"), "0.3"), (("1.5", "-", "1.50"), "0.00"),
        (("-1.5", "-", "-1.5"), "0.0"), (("2.5", "-", "0.25"), "2.25"),
        (("1.5", "*", "0.2"), "0.30"), (("-2.0", "*", "3"), "-6.0"),
        (("-1.5", "*", "-0.2"), "0.30"), (("0", "*", "5.5"), "0.0"),
        (("1", "/", "3"), "0.333333333333"),
        (("2", "/", "2"), "1.000000000000"),
        (("1", "/", "8"), "0.125000000000"),
        (("10", "/", "4"), "2.500000000000"),
        (("1", "/", "8192"), "0.000122070312"),
        (("-1", "/", "8192"), "-0.000122070312"),
        (("3", "/", "8192"), "0.000366210938"),
        (("-1", "/", "3"), "-0.333333333333"),
        (("5", "/", "-2"), "-2.500000000000"),
        (("0", "/", "7"), "0.000000000000"),
    ]:
        try:
            fa, fb = Fixed(a), Fixed(b)
            got = str(fa + fb if op == "+" else fa - fb if op == "-"
                      else fa * fb if op == "*" else fa / fb)
            if got != want:
                fails.append(f"{a} {op} {b}: got {got!r} want {want!r}")
        except Exception as e:
            fails.append(f"{a} {op} {b} raised {e!r}")

    check("div by zero", _raises(ZeroDivisionError, lambda: Fixed("1") / Fixed("0")))
    check("div by zero scaled", _raises(ZeroDivisionError, lambda: Fixed("1") / Fixed("0.00")))

    f = Fixed("1.5") * Fixed("0.2")
    check("mul not normalised", f._units == 30 and f._scale == 2)

    # ---------- negation ----------
    for lit, want in [("0.0", "0.0"), ("-0.0", "0.0"), ("-1.5", "1.5"),
                      ("0", "0"), ("7.25", "-7.25")]:
        got = str(-Fixed(lit))
        if got != want:
            fails.append(f"neg {lit!r}: got {got!r} want {want!r}")

    # ---------- quantize ----------
    for lit, ns, mode, want in [
        ("2.5", 0, RHE, "2"), ("2.5", 0, RHU, "3"), ("2.5", 0, RD, "2"),
        ("3.5", 0, RHE, "4"), ("3.5", 0, RHU, "4"), ("3.5", 0, RD, "3"),
        ("-2.5", 0, RHE, "-2"), ("-2.5", 0, RHU, "-3"), ("-2.5", 0, RD, "-2"),
        ("0.125", 2, RHE, "0.12"), ("0.125", 2, RHU, "0.13"), ("0.125", 2, RD, "0.12"),
        ("-0.125", 2, RHE, "-0.12"), ("-0.125", 2, RHU, "-0.13"), ("-0.125", 2, RD, "-0.12"),
        ("-0.4", 0, RHE, "0"), ("-0.4", 0, RHU, "0"), ("-0.4", 0, RD, "0"),
        ("-0.5", 0, RHU, "-1"), ("-0.5", 0, RHE, "0"), ("-0.6", 0, RD, "0"),
        ("1.5", 4, RHE, "1.5000"), ("1.5", 4, RD, "1.5000"), ("2", 0, RHE, "2"),
        ("9.999", 2, RHE, "10.00"), ("9.999", 2, RHU, "10.00"), ("9.999", 2, RD, "9.99"),
        ("-9.999", 2, RHE, "-10.00"), ("-9.999", 2, RD, "-9.99"),
        ("-1.005", 2, RHE, "-1.00"), ("-1.005", 2, RHU, "-1.01"),
        ("0", 3, RHE, "0.000"), ("-0", 1, RHU, "0.0"),
        ("999.9995", 0, RHE, "1000"), ("999.9995", 3, RHU, "1000.000"),
    ]:
        try:
            got = str(Fixed(lit).quantize(ns, mode))
            if got != want:
                fails.append(f"quantize {lit!r} {ns} {mode}: got {got!r} want {want!r}")
        except Exception as e:
            fails.append(f"quantize {lit!r} {ns} {mode} raised {e!r}")

    got = str(Fixed("1.25").quantize(1))
    if got != "1.2":
        fails.append(f"quantize default rounding: got {got!r} want '1.2'")
    check("quantize neg scale ValueError", _raises(ValueError, lambda: Fixed("1").quantize(-1)))
    check("quantize bad rounding ValueError",
          _raises(ValueError, lambda: Fixed("1").quantize(1, "bogus")))
    q = Fixed("1.5").quantize(3)
    check("quantize returns Fixed", isinstance(q, Fixed) and q._units == 1500 and q._scale == 3)

    # ---------- randomised differential test (reference: ints only) ----------
    def ref_parse(s):
        m = re.fullmatch(r"([+-]?)(?:(\d+)(?:\.(\d*))?|\.(\d+))(?:[eE]([+-]?\d+))?", s)
        if not m:
            raise ValueError(s)
        sign = -1 if m.group(1) == "-" else 1
        ip = m.group(2) or ""
        fp = (m.group(3) or "") if m.group(2) is not None else (m.group(4) or "")
        exp = int(m.group(5)) if m.group(5) else 0
        coef = int(ip + fp)
        dd = len(fp)
        if exp > dd:
            units, scale = coef * 10 ** (exp - dd), 0
        else:
            units, scale = coef, dd - exp
        return (units * sign, scale)

    def rnorm(v):
        u, s = v
        if u == 0:
            return (0, 0)
        while s > 0 and u % 10 == 0:
            u //= 10
            s -= 1
        return (u, s)

    def radd(a, b):
        (ua, sa), (ub, sb) = a, b
        s = max(sa, sb)
        return (ua * 10 ** (s - sa) + ub * 10 ** (s - sb), s)

    def rsub(a, b):
        (ua, sa), (ub, sb) = a, b
        s = max(sa, sb)
        return (ua * 10 ** (s - sa) - ub * 10 ** (s - sb), s)

    def rmul(a, b):
        (ua, sa), (ub, sb) = a, b
        return (ua * ub, sa + sb)

    def rdiv(a, b):
        (ua, sa), (ub, sb) = a, b
        k = 12 - sa + sb
        if k >= 0:
            n, dd = abs(ua) * 10 ** k, abs(ub)
        else:
            n, dd = abs(ua), abs(ub) * 10 ** (-k)
        q, r = divmod(n, dd)
        if 2 * r > dd or (2 * r == dd and q % 2 == 1):
            q += 1
        if (ua < 0) != (ub < 0):
            q = -q
        return (q, 12)

    def rquant(v, ns, mode):
        u, s = v
        if ns >= s:
            return (u * 10 ** (ns - s), ns)
        div = 10 ** (s - ns)
        q, r = divmod(abs(u), div)
        if mode == "dn":
            pass
        elif mode == "hu":
            if 2 * r >= div:
                q += 1
        elif mode == "he":
            if 2 * r > div or (2 * r == div and q % 2 == 1):
                q += 1
        return (-q if u < 0 else q, ns)

    def rstr(v):
        u, s = v
        sign = "-" if u < 0 else ""
        u = abs(u)
        if s == 0:
            return sign + str(u)
        ip, fp = divmod(u, 10 ** s)
        return "%s%d.%0*d" % (sign, ip, s, fp)

    def rless(a, b):
        (ua, sa), (ub, sb) = a, b
        s = max(sa, sb)
        return ua * 10 ** (s - sa) < ub * 10 ** (s - sb)

    random.seed(24)

    def digits(nn):
        return "".join(random.choice("0123456789") for _ in range(nn))

    def rand_lit():
        sign = random.choice(["", "-", "+"])
        ip = digits(random.randint(1, 3))
        fp = digits(random.randint(0, 4))
        mant = ip
        if fp or random.random() < 0.6:
            mant += "." + fp
        if fp and random.random() < 0.2:
            mant = "." + fp
        r = random.random()
        if r < 0.2:
            mant += "e" + str(random.randint(-4, 4))
        elif r < 0.3:
            mant += "e+" + str(random.randint(0, 4))
        return sign + mant

    modes = [RHE, RHU, RD]
    refmodes = {RHE: "he", RHU: "hu", RD: "dn"}
    ncases = 0
    for i in range(400):
        la, lb = rand_lit(), rand_lit()
        try:
            fa, fb = Fixed(la), Fixed(lb)
        except MN:
            fails.append(f"rand parse rejected {la!r}")
            continue
        pa, pb = ref_parse(la), ref_parse(lb)
        if (fa._units, fa._scale) != pa:
            fails.append(f"diff parse {la!r}: got {(fa._units, fa._scale)} want {pa}")
            continue
        if str(fa) != rstr(pa):
            fails.append(f"diff str {la!r}: got {str(fa)!r} want {rstr(pa)!r}")
            continue
        if Fixed(str(fa)) != fa or str(Fixed(str(fa))) != str(fa):
            fails.append(f"diff roundtrip {la!r}: {str(fa)!r}")
            continue
        ncases += 1
        op = random.choice("+-*/<qnm")
        if op == "+":
            got, want = str(fa + fb), rstr(radd(pa, pb))
        elif op == "-":
            got, want = str(fa - fb), rstr(rsub(pa, pb))
        elif op == "*":
            got, want = str(fa * fb), rstr(rmul(pa, pb))
        elif op == "/":
            if pb[0] == 0:
                if not _raises(ZeroDivisionError, lambda: fa / fb):
                    fails.append(f"diff divzero missing for {la!r}/{lb!r}")
                continue
            got, want = str(fa / fb), rstr(rdiv(pa, pb))
        elif op == "<":
            got, want = str(fa < fb), str(rless(pa, pb))
        elif op == "q":
            ns = random.randint(0, 6)
            mode = random.choice(modes)
            got, want = str(fa.quantize(ns, mode)), rstr(rquant(pa, ns, refmodes[mode]))
        elif op == "n":
            got, want = str(-fa), rstr((-pa[0], pa[1]))
        else:
            s1 = str(fa + fb)
            got, want = str(Fixed(s1)), s1
        if got != want:
            fails.append(f"diff {op} {la!r} {lb!r}: got {got!r} want {want!r}")
        if rnorm(pa) == rnorm(pb) and hash(fa) != hash(fb):
            fails.append(f"diff hash mismatch {la!r} {lb!r}")
    check("enough random cases", ncases > 250)

except Exception as e:
    import traceback
    fails.append(f"exception: {e!r}: {traceback.format_exc()[-400:]}")

if fails:
    print("FAIL", fails[:12])
    sys.exit(1)
print("PASS")
