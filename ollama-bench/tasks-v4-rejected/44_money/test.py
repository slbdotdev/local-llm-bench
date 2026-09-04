import sys, os, random, threading, inspect, decimal, re
from decimal import Decimal

TOTAL = 28
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
    import money
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

# --------------------------------------------------------------------------
# oracle (stdlib decimal); all helpers are prefixed _ora_ so they cannot clash
# --------------------------------------------------------------------------
_ORA_MODES = {
    "half_even": decimal.ROUND_HALF_EVEN,
    "half_up": decimal.ROUND_HALF_UP,
    "half_down": decimal.ROUND_HALF_DOWN,
    "ceiling": decimal.ROUND_CEILING,
    "floor": decimal.ROUND_FLOOR,
    "down": decimal.ROUND_DOWN,
    "up": decimal.ROUND_UP,
}
_ORA_ALL = sorted(_ORA_MODES)


def _ora_fmt(units, places):
    body = str(abs(units)).zfill(places + 1)
    if places:
        body = body[:-places] + "." + body[-places:]
    return ("-" + body) if units < 0 else body


def _ora_units(value, places, mode):
    """Round an exact Decimal to an integer number of 10**-places units."""
    with decimal.localcontext() as ctx:
        ctx.prec = 200
        q = value.quantize(Decimal(1).scaleb(-places), rounding=_ORA_MODES[mode])
        return int(q.scaleb(places))


def _ora_quantize(amount, places, mode):
    with decimal.localcontext() as ctx:
        ctx.prec = 200
        return _ora_fmt(_ora_units(Decimal(amount), places, mode), places)


def _ora_exact_units(amount, places):
    """Units at `places` of an amount that is exactly representable there."""
    with decimal.localcontext() as ctx:
        ctx.prec = 200
        return int(Decimal(amount).scaleb(places))


def _ora_allocate(total, weights, places):
    T = _ora_exact_units(total, places)
    n = len(weights)
    if n == 0:
        return []
    k = 0
    for w in weights:
        k = max(k, len(w.split(".")[1]) if "." in w else 0)
    ws = [_ora_exact_units(w, k) for w in weights]
    S = sum(ws)
    if S == 0:
        ws = [1] * n
        S = n
    q = [(T * ws[i]) // S for i in range(n)]
    r = [T * ws[i] - S * q[i] for i in range(n)]
    left = T - sum(q)
    for i in sorted(range(n), key=lambda i: (-r[i], i))[:left]:
        q[i] += 1
    return [_ora_fmt(v, places) for v in q]


def _ora_add_tax(net, rate, places, mode):
    with decimal.localcontext() as ctx:
        ctx.prec = 200
        nu = _ora_exact_units(net, places)
        tax = _ora_units(Decimal(net) * Decimal(rate) / Decimal(100), places, mode)
    return (_ora_fmt(nu, places), _ora_fmt(tax, places), _ora_fmt(nu + tax, places))


def _ora_extract_tax(gross, rate, places, mode):
    with decimal.localcontext() as ctx:
        ctx.prec = 200
        gu = _ora_exact_units(gross, places)
        tax = _ora_units(Decimal(gross) * Decimal(rate) / (Decimal(100) + Decimal(rate)),
                         places, mode)
    return (_ora_fmt(gu - tax, places), _ora_fmt(tax, places), _ora_fmt(gu, places))


# --------------------------------------------------------------------------
# handles on the candidate
# --------------------------------------------------------------------------
def _missing(*a, **k):
    raise AttributeError("attribute missing from money")


Q = getattr(money, "quantize", _missing)
AL = getattr(money, "allocate", _missing)
AT = getattr(money, "add_tax", _missing)
ET = getattr(money, "extract_tax", _missing)
ME = getattr(money, "MoneyError", None)

_CANON = re.compile(r"^-?(0|[1-9][0-9]*)(\.[0-9]+)?$")


def _canonical(s, places):
    if not isinstance(s, str) or _CANON.match(s) is None:
        return False
    if places:
        if "." not in s or len(s.split(".")[1]) != places:
            return False
    elif "." in s:
        return False
    return not (s.startswith("-") and set(s[1:]) <= set("0."))


def _raises(fn):
    if not (isinstance(ME, type) and issubclass(ME, ValueError)):
        return False
    try:
        fn()
    except ME:
        return True
    except Exception:
        return False
    return False


def _bucket(cases, fn):
    def probe():
        for c in cases:
            if not fn(c):
                return False
        return True
    return probe


# --------------------------------------------------------------------------
# 1-2: hygiene
# --------------------------------------------------------------------------
def no_forbidden_import():
    src = inspect.getsource(money)
    if re.search(r"\b(import|from)\s+(decimal|fractions)\b", src):
        return False
    if re.search(r"__import__\s*\(\s*['\"](?:decimal|fractions)['\"]", src):
        return False
    return True


check("money.py does not use decimal/fractions", no_forbidden_import)

check("MoneyError and the seven rounding constants",
      lambda: isinstance(ME, type) and issubclass(ME, ValueError)
      and all(getattr(money, "ROUND_" + m.upper(), None) == m for m in _ORA_ALL))

# --------------------------------------------------------------------------
# 3-4: validation
# --------------------------------------------------------------------------
_BAD = ["", " ", " 1", "1 ", "1.", ".5", "1.2.3", "1e3", "1_0", "--1", "+-1",
        "abc", "nan", "1,000.00", "0x10", "1.-2", "-", "+", ".", "1..2", None,
        5, 5.0, ["1"]]


def bad_amounts():
    for b in _BAD:
        if not _raises(lambda b=b: Q(b, 2, "half_even")):
            return False
    for b in _BAD[:12]:
        if not _raises(lambda b=b: AL(b, ["1"], 2)):
            return False
        if not _raises(lambda b=b: AL("1.00", [b], 2)):
            return False
        if not _raises(lambda b=b: AT(b, "10", 2, "half_even")):
            return False
        if not _raises(lambda b=b: AT("1.00", b, 2, "half_even")):
            return False
        if not _raises(lambda b=b: ET("1.00", b, 2, "half_even")):
            return False
    return True


def bad_args():
    bad_places = [-1, -3, "2", 2.0, None]
    bad_modes = ["HALF_EVEN", "half-even", "", None, "banker", "half_odd", 0]
    for p in bad_places:
        if not _raises(lambda p=p: Q("1.5", p, "half_even")):
            return False
        if not _raises(lambda p=p: AL("1", ["1"], p)):
            return False
        if not _raises(lambda p=p: AT("1", "5", p, "half_even")):
            return False
    for m in bad_modes:
        if not _raises(lambda m=m: Q("1.5", 2, m)):
            return False
        if not _raises(lambda m=m: ET("1.00", "5", 2, m)):
            return False
    # negative weights / rates, non-representable amounts, empty weights
    if not _raises(lambda: AL("1.00", ["1", "-1"], 2)):
        return False
    if not _raises(lambda: AL("1.005", ["1"], 2)):
        return False
    if not _raises(lambda: AL("0.1", ["1"], 0)):
        return False
    if not _raises(lambda: AL("1.00", [], 2)):
        return False
    if not _raises(lambda: AT("1.00", "-5", 2, "half_even")):
        return False
    if not _raises(lambda: ET("1.00", "-0.5", 2, "half_even")):
        return False
    if not _raises(lambda: AT("1.005", "5", 2, "half_even")):
        return False
    if not _raises(lambda: ET("1.005", "5", 2, "half_even")):
        return False
    # these must NOT raise
    return (AL("0.00", [], 2) == [] and Q("1.5", 0, "up") == "2"
            and AT("0", "0", 0, "down") == ("0", "0", "0"))


check("malformed amount strings raise MoneyError", bad_amounts)
check("bad places / mode / weight / rate raise MoneyError", bad_args)

# --------------------------------------------------------------------------
# quantize: randomised differential, one bucket per rounding mode
# --------------------------------------------------------------------------
_DIG = "0123456789"


def _gen_quant(seed, count):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        places = rng.choice([0, 0, 1, 2, 2, 3, 4, 6])
        kind = rng.random()
        if kind < 0.34:                       # exact tie at `places`
            ip = str(rng.randint(0, 999))
            fr = "".join(rng.choice(_DIG) for _ in range(places)) + "5"
        elif kind < 0.54:                     # tiny magnitude
            ip = "0"
            fr = "".join(rng.choice(_DIG) for _ in range(places + rng.randint(1, 3)))
        elif kind < 0.74:                     # near a tie but not exactly on it
            ip = str(rng.randint(0, 99))
            fr = ("".join(rng.choice(_DIG) for _ in range(places)) + "5"
                  + rng.choice(["0", "1", "9", "00", "01", "000"]))
        else:                                 # plain values, some already short
            ip = str(rng.randint(0, 10 ** rng.randint(1, 6)))
            fr = "".join(rng.choice(_DIG) for _ in range(rng.randint(0, places + 3)))
        s = ip + ("." + fr if fr else "")
        if rng.random() < 0.5:
            s = "-" + s
        out.append((s, places))
    return out


_QCASES = _gen_quant(9001, 240)


def _q_probe(mode, cases):
    def probe():
        for amount, places in cases:
            if Q(amount, places, mode) != _ora_quantize(amount, places, mode):
                return False
        return True
    return probe


for _m in _ORA_ALL:
    check("quantize differential: mode %s" % _m, _q_probe(_m, _QCASES))

# dedicated tie bucket: every mode against exact halves, both signs
_TIES = []
_rng = random.Random(4242)
for _i in range(90):
    _p = _rng.choice([0, 0, 1, 2, 3])
    _v = "%d.%s5" % (_rng.randint(0, 40), "".join(_rng.choice(_DIG) for _ in range(_p)))
    _TIES.append((_v, _p))
    _TIES.append(("-" + _v, _p))
_TIES += [("0.5", 0), ("-0.5", 0), ("1.5", 0), ("-1.5", 0), ("2.5", 0), ("-2.5", 0),
          ("0.005", 2), ("-0.005", 2), ("0.015", 2), ("-0.015", 2), ("0.125", 2),
          ("-0.125", 2), ("9.995", 2), ("-9.995", 2), ("0.05", 1), ("-0.05", 1)]

check("quantize: exact halves under every mode",
      _bucket([(a, p, m) for (a, p) in _TIES for m in _ORA_ALL],
              lambda c: Q(c[0], c[1], c[2]) == _ora_quantize(c[0], c[1], c[2])))

# sign at zero: results that collapse to zero must never print "-0"
_ZCASES = []
_rng = random.Random(777)
for _i in range(70):
    _p = _rng.choice([0, 0, 1, 2, 3])
    _v = "0." + "0" * _p + "".join(_rng.choice(_DIG) for _ in range(_rng.randint(1, 3)))
    _ZCASES.append(("-" + _v, _p))
    _ZCASES.append((_v, _p))
_ZCASES += [("-0.4", 0), ("-0.5", 0), ("-0.6", 0), ("-0.0", 0), ("-0", 0), ("-0.00", 2),
            ("-0.001", 2), ("-0.999", 0), ("-0.004", 2), ("+0.4", 0), ("-0.0049", 2)]


def zero_sign():
    for amount, places in _ZCASES:
        for m in _ORA_ALL:
            got = Q(amount, places, m)
            if got != _ora_quantize(amount, places, m) or not _canonical(got, places):
                return False
    return True


check("quantize: zero results are never negative", zero_sign)

# formatting / padding / canonical output
_FCASES = [("0", 0), ("0", 4), ("-0", 3), ("+0.0", 2), ("007.50", 3), ("+12.5", 0),
           ("0.5", 8), ("-0.5", 8), ("00012", 2), ("123456789012.345", 5),
           ("-000.0001", 6), ("9.999", 2), ("-9.999", 2), ("99.5", 0), ("0.0000001", 8),
           ("-0.0000001", 8), ("1", 0), ("-1", 0), ("10.00", 1), ("-10.00", 1)]


def formatting():
    for amount, places in _FCASES:
        for m in _ORA_ALL:
            got = Q(amount, places, m)
            if got != _ora_quantize(amount, places, m) or not _canonical(got, places):
                return False
    return True


check("quantize: canonical formatting and zero padding", formatting)

# --------------------------------------------------------------------------
# allocate: randomised differential, split by case family
# --------------------------------------------------------------------------
def _gen_alloc(seed, count, family):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        places = rng.choice([0, 1, 2, 2, 2, 3])
        n = rng.randint(1, 7)
        if family == "equal":
            weights = ["1"] * n
        elif family == "mixed":
            weights = [str(rng.randint(0, 9)) for _ in range(n)]
        elif family == "frac":
            weights = ["%d.%s" % (rng.randint(0, 30),
                                  "".join(rng.choice(_DIG) for _ in range(rng.randint(1, 3))))
                       for _ in range(n)]
        elif family == "zero":
            weights = ["0"] * n if rng.random() < 0.5 else \
                ["0"] * (n - 1) + [rng.choice(["0", "0.0", "0.000"])]
        else:  # neg
            weights = [str(rng.randint(0, 5)) for _ in range(n)]
        units = rng.randint(0, 20000)
        if family == "neg":
            units = -units
        elif rng.random() < 0.2:
            units = -units
        out.append((_ora_fmt(units, places), weights, places))
    return out


_A_EQUAL = _gen_alloc(11, 90, "equal")
_A_MIXED = _gen_alloc(12, 90, "mixed")
_A_FRAC = _gen_alloc(13, 90, "frac")
_A_NEG = _gen_alloc(14, 90, "neg")
_A_ZERO = _gen_alloc(15, 60, "zero")
_A_ALL = _A_EQUAL + _A_MIXED + _A_FRAC + _A_NEG + _A_ZERO


def _alloc_probe(cases):
    def probe():
        for total, weights, places in cases:
            if AL(total, list(weights), places) != _ora_allocate(total, weights, places):
                return False
        return True
    return probe


check("allocate: equal weights", _alloc_probe(_A_EQUAL))
check("allocate: mixed integer weights (some zero)", _alloc_probe(_A_MIXED))
check("allocate: fractional weights", _alloc_probe(_A_FRAC))
check("allocate: negative totals", _alloc_probe(_A_NEG))
check("allocate: all-zero weight vectors", _alloc_probe(_A_ZERO))


def alloc_invariants():
    for total, weights, places in _A_ALL:
        got = AL(total, list(weights), places)
        if not isinstance(got, list) or len(got) != len(weights):
            return False
        acc = 0
        for s in got:
            if not _canonical(s, places):
                return False
            acc += _ora_exact_units(s, places)
        if acc != _ora_exact_units(total, places):
            return False
    return True


check("allocate: shares are canonical and sum exactly to the total", alloc_invariants)

_A_EDGE = [("0.00", ["1", "2", "3"], 2), ("0.00", ["0", "0"], 2),
           ("-0.01", ["1", "1", "1"], 2), ("0.01", ["1", "1", "1"], 2),
           ("-0.03", ["1", "1", "1", "1"], 2), ("5", ["1"], 0), ("-5", ["1"], 0),
           ("7", ["1", "1", "1"], 0), ("-7", ["1", "1", "1"], 0),
           ("-0.05", ["3", "1"], 2), ("100.00", ["0", "1", "0"], 2),
           ("1.00", ["0", "0", "0"], 2), ("-1.00", ["0", "0", "0"], 2),
           ("0.10", ["0.001", "0.002"], 2), ("10.00", ["2", "0", "1"], 2),
           ("1.00", ["1", "0"], 2), ("-1.00", ["1", "0"], 2),
           ("0.02", ["1", "1", "1"], 2), ("-0.02", ["1", "1", "1"], 2),
           ("9.99", ["1", "1", "1", "1", "1", "1", "1"], 2),
           ("-9.99", ["1", "1", "1", "1", "1", "1", "1"], 2),
           ("0", ["1", "1"], 0), ("-0.00", ["1", "1"], 2)]


def alloc_edges():
    for total, weights, places in _A_EDGE:
        got = AL(total, list(weights), places)
        if got != _ora_allocate(total, weights, places):
            return False
        for s in got:
            if not _canonical(s, places):
                return False
    return AL("0", [], 0) == [] and AL("0.000", [], 3) == []


check("allocate: edge totals, zero shares and empty weight lists", alloc_edges)

# --------------------------------------------------------------------------
# tax
# --------------------------------------------------------------------------
def _gen_tax(seed, count):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        places = rng.choice([0, 2, 2, 2, 3, 4])
        units = rng.randint(0, 500000)
        if rng.random() < 0.35:
            units = -units
        amount = _ora_fmt(units, places)
        r = rng.random()
        if r < 0.3:
            rate = str(rng.choice([0, 5, 7, 10, 19, 20, 25, 100, 200]))
        elif r < 0.7:
            rate = "%d.%s" % (rng.randint(0, 30),
                              "".join(rng.choice(_DIG) for _ in range(rng.randint(1, 3))))
        else:
            rate = "%d.5" % rng.randint(0, 20)
        out.append((amount, rate, places, rng.choice(_ORA_ALL)))
    return out


_TAX_A = _gen_tax(21, 120)
_TAX_B = _gen_tax(22, 120)


def _tax_probe(cases, fn, ora):
    def probe():
        for amount, rate, places, mode in cases:
            got = fn(amount, rate, places, mode)
            want = ora(amount, rate, places, mode)
            if tuple(got) != want:
                return False
        return True
    return probe


check("add_tax differential A", _tax_probe(_TAX_A, AT, _ora_add_tax))
check("add_tax differential B", _tax_probe(_TAX_B, AT, _ora_add_tax))
check("extract_tax differential A", _tax_probe(_TAX_A, ET, _ora_extract_tax))
check("extract_tax differential B", _tax_probe(_TAX_B, ET, _ora_extract_tax))


def tax_invariants():
    for amount, rate, places, mode in _TAX_A + _TAX_B:
        for fn in (AT, ET):
            got = fn(amount, rate, places, mode)
            if not isinstance(got, tuple) or len(got) != 3:
                return False
            if not all(_canonical(s, places) for s in got):
                return False
            net, tax, gross = (_ora_exact_units(s, places) for s in got)
            if net + tax != gross:
                return False
    return True


check("tax: canonical triples with net + tax == gross exactly", tax_invariants)

_TAX_EDGE = [("0.00", "19", 2), ("0", "0", 0), ("-100.00", "19", 2),
             ("-0.01", "50", 2), ("0.01", "50", 2), ("-0.03", "50", 2),
             ("0.03", "50", 2), ("1.00", "0", 2), ("-1.00", "0", 2),
             ("0.10", "5", 2), ("-0.10", "5", 2), ("100.00", "100", 2),
             ("-100.00", "100", 2), ("1.00", "300", 2), ("0.05", "10", 2),
             ("-0.05", "10", 2), ("250", "20", 0), ("-250", "20", 0),
             ("12345.67", "8.875", 2), ("-12345.67", "8.875", 2),
             ("0.02", "25", 2), ("-0.02", "25", 2), ("999.99", "0.5", 2)]


def tax_edges(fn, ora):
    def probe():
        for amount, rate, places in _TAX_EDGE:
            for mode in _ORA_ALL:
                got = fn(amount, rate, places, mode)
                if tuple(got) != ora(amount, rate, places, mode):
                    return False
                if not all(_canonical(s, places) for s in got):
                    return False
        return True
    return probe


check("add_tax: edge amounts, zero and large rates, every mode",
      tax_edges(AT, _ora_add_tax))
check("extract_tax: edge amounts, zero and large rates, every mode",
      tax_edges(ET, _ora_extract_tax))

_t.cancel()
report()
