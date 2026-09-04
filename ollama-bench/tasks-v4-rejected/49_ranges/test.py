import sys, os, re, random, threading, inspect

TOTAL = 22
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
    import ranges
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


class _Missing(object):
    def __init__(self, *a, **k):
        raise AttributeError("RangeSet missing from ranges")


RS = getattr(ranges, "RangeSet", _Missing)

# --------------------------------------------------------------------------
# Inlined oracle: model the reals in [-10, 10] plus two infinite tails as a
# finite list of "atoms" (single points and the open gaps between them), so
# every set operation becomes a plain set operation on atom indices.
#   atom 0                        -> (-inf, -10)
#   atom 1 + 2*(k - _ORC_LO)      -> the single point k          (odd index)
#   atom 2 + 2*(k - _ORC_LO)      -> the open gap (k, k+1)       (even index)
#   atom _ORC_N - 1               -> (10, +inf)
# --------------------------------------------------------------------------
_ORC_LO, _ORC_HI = -10, 10
_ORC_N = 2 + (_ORC_HI - _ORC_LO) * 2 + 1
_ORC_FULL = frozenset(range(_ORC_N))


def _orc_point(k):
    return 1 + 2 * (k - _ORC_LO)


def _orc_atoms_of(iv):
    lo, hi, lc, rc = iv[0], iv[1], iv[2], iv[3]
    if lo is None:
        a = 0
    else:
        a = _orc_point(lo) if lc else _orc_point(lo) + 1
    if hi is None:
        b = _ORC_N - 1
    else:
        b = _orc_point(hi) if rc else _orc_point(hi) - 1
    if a > b:
        return frozenset()
    return frozenset(range(a, b + 1))


def _orc_set(ivlist):
    s = set()
    for iv in ivlist:
        s |= _orc_atoms_of(iv)
    return frozenset(s)


def _orc_canon(atoms):
    """Turn a set of atom indices into the canonical interval list."""
    out = []
    xs = sorted(atoms)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
            j += 1
        a, b = xs[i], xs[j]
        if a == 0:
            lo, lc = None, False
        elif a % 2 == 1:
            lo, lc = _ORC_LO + (a - 1) // 2, True
        else:
            lo, lc = _ORC_LO + (a - 2) // 2, False
        if b == _ORC_N - 1:
            hi, rc = None, False
        elif b % 2 == 1:
            hi, rc = _ORC_LO + (b - 1) // 2, True
        else:
            hi, rc = _ORC_LO + (b - 2) // 2 + 1, False
        out.append((lo, hi, lc, rc))
        i = j + 1
    return out


def _orc_measure(atoms):
    tot = 0
    for lo, hi, lc, rc in _orc_canon(atoms):
        if lo is None or hi is None:
            return float("inf")
        tot += hi - lo
    return tot


def _orc_to_string(atoms):
    ivs = _orc_canon(atoms)
    if not ivs:
        return "{}"
    parts = []
    for lo, hi, lc, rc in ivs:
        a = "-inf" if lo is None else str(lo)
        b = "+inf" if hi is None else str(hi)
        parts.append(("[" if lc else "(") + a + "," + b + ("]" if rc else ")"))
    return " U ".join(parts)


def _orc_contains(atoms, x):
    if x < _ORC_LO:
        i = 0
    elif x > _ORC_HI:
        i = _ORC_N - 1
    elif float(x) == int(x):
        i = _orc_point(int(x))
    else:
        k = int(x) if x > 0 else int(x) - 1
        i = _orc_point(k) + 1
    return i in atoms


def _orc_op(name, sa, sb):
    if name == "union":
        return sa | sb
    if name == "intersect":
        return sa & sb
    if name == "difference":
        return sa - sb
    if name == "symmetric_difference":
        return sa ^ sb
    raise ValueError(name)


# --------------------------------------------------------------------------
# Case generators
# --------------------------------------------------------------------------
def _orc_b(rng):
    return rng.random() < 0.5


def _orc_ivs(rng, vals, start, n):
    out = []
    for i in range(n):
        a, b = vals[start + 2 * i], vals[start + 2 * i + 1]
        out.append((min(a, b), max(a, b), _orc_b(rng), _orc_b(rng)))
    return out


def _orc_gen_plain(rng):
    """Straightforward lists: every endpoint distinct, no degenerate interval."""
    n = rng.randint(1, 3)
    vals = rng.sample(range(-9, 10), 2 * n)
    rng.shuffle(vals)
    return _orc_ivs(rng, vals, 0, n)


def _orc_gen_plain_pair(rng):
    """A pair of straightforward lists sharing no endpoint value."""
    n1, n2 = rng.randint(1, 2), rng.randint(1, 2)
    vals = rng.sample(range(-9, 10), 2 * (n1 + n2))
    rng.shuffle(vals)
    return _orc_ivs(rng, vals, 0, n1), _orc_ivs(rng, vals, 2 * n1, n2)


def _orc_gen_degen(rng):
    out = []
    for _ in range(rng.randint(1, 4)):
        t = rng.random()
        k = rng.randint(-4, 4)
        if t < 0.45:
            out.append((k, k, _orc_b(rng), _orc_b(rng)))
        elif t < 0.65:
            out.append((k, k - rng.randint(1, 3), _orc_b(rng), _orc_b(rng)))
        else:
            out.append((k, k + rng.randint(1, 3), _orc_b(rng), _orc_b(rng)))
    return out


def _orc_gen_touch(rng):
    k = rng.randint(-4, 4)
    a = k - rng.randint(1, 3)
    b = k + rng.randint(1, 3)
    out = [(a, k, _orc_b(rng), _orc_b(rng)), (k, b, _orc_b(rng), _orc_b(rng))]
    if rng.random() < 0.5:
        out.append((b, b + rng.randint(1, 3), _orc_b(rng), _orc_b(rng)))
    rng.shuffle(out)
    return out


def _orc_gen_inf(rng):
    out = []
    for _ in range(rng.randint(1, 3)):
        t = rng.random()
        k = rng.randint(-6, 6)
        if t < 0.35:
            out.append((None, k, _orc_b(rng), _orc_b(rng)))
        elif t < 0.7:
            out.append((k, None, _orc_b(rng), _orc_b(rng)))
        elif t < 0.8:
            out.append((None, None, _orc_b(rng), _orc_b(rng)))
        else:
            out.append((k, k + rng.randint(1, 3), _orc_b(rng), _orc_b(rng)))
    return out


_rng = random.Random(20260903)
POOL = {}
for _name, _fn in (("plain", _orc_gen_plain), ("degen", _orc_gen_degen),
                   ("touch", _orc_gen_touch), ("inf", _orc_gen_inf)):
    POOL[_name] = [_fn(_rng) for _ in range(80)]
MIX = POOL["plain"] + POOL["degen"] + POOL["touch"] + POOL["inf"]
_rng.shuffle(MIX)
PAIRS = {"plain": [_orc_gen_plain_pair(_rng) for _ in range(60)]}
for _name in ("degen", "touch", "inf", "mix"):
    _src = MIX if _name == "mix" else POOL[_name]
    PAIRS[_name] = [(_rng.choice(_src), _rng.choice(_src)) for _ in range(60)]


# --------------------------------------------------------------------------
# Comparison helpers
# --------------------------------------------------------------------------
def _norm(out):
    """Normalise a candidate intervals() result for comparison."""
    res = []
    for iv in out:
        lo, hi, lc, rc = iv[0], iv[1], iv[2], iv[3]
        if isinstance(lo, float) and lo == float("-inf"):
            lo = None
        if isinstance(hi, float) and hi == float("inf"):
            hi = None
        res.append((lo, hi, bool(lc), bool(rc)))
    return res


def canon_bucket(cases):
    def run():
        for ivl in cases:
            if _norm(RS(list(ivl)).intervals()) != _orc_canon(_orc_set(ivl)):
                return False
        return True
    return run


def op_bucket(op, pairs, mutation=False):
    def run():
        for A, B in pairs:
            ca, cb = RS(list(A)), RS(list(B))
            before_a, before_b = _norm(ca.intervals()), _norm(cb.intervals())
            got = getattr(ca, op)(cb)
            want = _orc_canon(_orc_op(op, _orc_set(A), _orc_set(B)))
            if _norm(got.intervals()) != want:
                return False
            if mutation and (_norm(ca.intervals()) != before_a
                             or _norm(cb.intervals()) != before_b):
                return False
        return True
    return run


# --------------------------------------------------------------------------
# 1. basics
# --------------------------------------------------------------------------
def _basics():
    try:
        src = inspect.getsource(ranges)
    except Exception:
        src = ""
    if re.search(r"^\s*(import|from)\s+(portion|intervaltree|sympy|numpy|pandas)\b",
                 src, re.M):
        return False
    e = RS()
    if e.intervals() != [] or not e.is_empty() or e.to_string() != "{}":
        return False
    if e.measure() != 0 or e.contains(0):
        return False
    if RS([(3, 3, True, True)]).is_empty() or not RS([(3, 3, False, True)]).is_empty():
        return False
    # lists are acceptable in place of tuples
    if _norm(RS([[1, 4, True, False]]).intervals()) != [(1, 4, True, False)]:
        return False
    if (RS([(1, 4, True, False)]) == 7) is not False:
        return False
    if not (RS([(1, 2, True, False), (2, 3, True, True)]) == RS([(1, 3, True, True)])):
        return False
    return True


check("basics: empty set, point vs empty degenerate, no third-party imports", _basics)

check("canonical form: plain interval lists", canon_bucket(POOL["plain"]))
check("canonical form: degenerate and reversed intervals", canon_bucket(POOL["degen"]))
check("canonical form: intervals touching at a shared endpoint",
      canon_bucket(POOL["touch"]))
check("canonical form: infinite endpoints", canon_bucket(POOL["inf"]))
check("canonical form: mixed pool", canon_bucket(MIX[:80]))

check("union: plain (and operands not mutated)",
      op_bucket("union", PAIRS["plain"], mutation=True))
check("union: touching endpoints", op_bucket("union", PAIRS["touch"]))
check("union: degenerate and infinite",
      op_bucket("union", PAIRS["degen"] + PAIRS["inf"]))

check("intersect: plain", op_bucket("intersect", PAIRS["plain"]))
check("intersect: touching and degenerate",
      op_bucket("intersect", PAIRS["touch"] + PAIRS["degen"]))
check("intersect: infinite and mixed",
      op_bucket("intersect", PAIRS["inf"] + PAIRS["mix"]))

check("difference: plain", op_bucket("difference", PAIRS["plain"]))
check("difference: touching and degenerate",
      op_bucket("difference", PAIRS["touch"] + PAIRS["degen"]))
check("difference: infinite and mixed",
      op_bucket("difference", PAIRS["inf"] + PAIRS["mix"]))

check("symmetric_difference: plain and touching",
      op_bucket("symmetric_difference", PAIRS["plain"] + PAIRS["touch"]))
check("symmetric_difference: degenerate, infinite and mixed",
      op_bucket("symmetric_difference",
                PAIRS["degen"] + PAIRS["inf"] + PAIRS["mix"]))


def _complement():
    for ivl in MIX:
        got = _norm(RS(list(ivl)).complement().intervals())
        if got != _orc_canon(_ORC_FULL - _orc_set(ivl)):
            return False
    return True


def _complement_laws():
    univ = _orc_canon(_ORC_FULL)
    for ivl in MIX[:120]:
        r = RS(list(ivl))
        c = r.complement()
        if _norm(c.complement().intervals()) != _norm(r.intervals()):
            return False
        if _norm(r.union(c).intervals()) != univ:
            return False
        if not r.intersect(c).is_empty():
            return False
    return True


check("complement: all flavours", _complement)
check("complement: double complement, A|~A universe, A&~A empty", _complement_laws)


def _contains(xs):
    def run():
        for ivl in MIX[:120]:
            r = RS(list(ivl))
            atoms = _orc_set(ivl)
            for x in xs:
                if bool(r.contains(x)) != _orc_contains(atoms, x):
                    return False
        return True
    return run


check("contains: integer arguments",
      _contains([-11, -9, -6, -4, -2, -1, 0, 1, 2, 3, 4, 6, 9, 11]))
check("contains: non-integer arguments",
      _contains([-11.5, -8.5, -4.5, -2.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 8.5, 11.5]))


def _is_empty():
    for ivl in MIX:
        if bool(RS(list(ivl)).is_empty()) != (not _orc_set(ivl)):
            return False
    return True


def _issubset():
    for A, B in PAIRS["mix"] + PAIRS["touch"] + PAIRS["degen"]:
        sa, sb = _orc_set(A), _orc_set(B)
        if bool(RS(list(A)).issubset(RS(list(B)))) != sa.issubset(sb):
            return False
        if bool(RS(list(B)).issubset(RS(list(A)))) != sb.issubset(sa):
            return False
    return True


def _measure():
    for ivl in MIX:
        if RS(list(ivl)).measure() != _orc_measure(_orc_set(ivl)):
            return False
    return True


def _to_string():
    for ivl in MIX:
        if RS(list(ivl)).to_string() != _orc_to_string(_orc_set(ivl)):
            return False
    return True


def _equality():
    for A, B in PAIRS["mix"] + PAIRS["touch"]:
        ra, rb = RS(list(A)), RS(list(B))
        if bool(ra == rb) != (_orc_set(A) == _orc_set(B)):
            return False
        if bool(ra != rb) != (_orc_set(A) != _orc_set(B)):
            return False
    return True


check("is_empty across all flavours", _is_empty)
check("issubset", _issubset)
check("measure: bounded and unbounded sets", _measure)
check("to_string formatting", _to_string)
check("__eq__ / __ne__ agree with set equality", _equality)

_t.cancel()
report()
