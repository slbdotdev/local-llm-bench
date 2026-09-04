import sys, os, random, threading

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
    import vercmp
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

VE = getattr(vercmp, "VersionError", None)
_HAS_VE = isinstance(VE, type) and issubclass(VE, BaseException)


# ======================= inlined reference oracle =======================

class _OraBad(Exception):
    pass


_ORA_D = set("0123456789")
_ORA_A = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_ORA_B = _ORA_A | {"-"}


def _ora_num(s):
    return bool(s) and all(c in _ORA_D for c in s)


def _ora_id(s, ok=_ORA_A):
    if not s or any(c not in ok for c in s):
        raise _OraBad(s)
    return int(s) if _ora_num(s) else s


def _ora_parse(s):
    """-> (epoch:int, release:tuple, pre:tuple|None, build:str|None)"""
    if not isinstance(s, str):
        raise _OraBad(s)
    e, rest = 0, s
    if ":" in rest:
        h, rest = rest.split(":", 1)
        if not _ora_num(h):
            raise _OraBad(s)
        e = int(h)
    b = None
    if "+" in rest:
        rest, b = rest.split("+", 1)
        for p in b.split("."):
            _ora_id(p, _ORA_B)
        if not b:
            raise _OraBad(s)
    pre = None
    if "-" in rest:
        rest, pr = rest.split("-", 1)
        pre = tuple(_ora_id(p) for p in pr.split("."))
    return (e, tuple(_ora_id(p) for p in rest.split(".")), pre, b)


def _ora_sk(x):
    return (1, x) if isinstance(x, str) else (0, x)


def _ora_key(p, n):
    rel = p[1] + (0,) * (n - len(p[1]))
    pk = (1, ()) if p[2] is None else (0, tuple(_ora_sk(i) for i in p[2]))
    return (p[0], tuple(_ora_sk(s) for s in rel), pk)


def _ora_cmp(x, y):
    n = max(len(x[1]), len(y[1]))
    a, b = _ora_key(x, n), _ora_key(y, n)
    return (a > b) - (a < b)


def _ora_releq(x, y):
    n = max(len(x[1]), len(y[1]))
    return x[0] == y[0] and _ora_key(x, n)[1] == _ora_key(y, n)[1]


def _ora_mk(e, r, pre=None):
    return (e, tuple(r), pre, None)


def _ora_ct(p, caret):
    r = p[1]
    if not (1 <= len(r) <= 3) or any(not isinstance(s, int) for s in r):
        raise _OraBad(p)
    a = r[0]
    b = r[1] if len(r) > 1 else 0
    c = r[2] if len(r) > 2 else 0
    if caret:
        if a:
            up = (a + 1, 0, 0)
        elif len(r) == 1:
            up = (1, 0, 0)
        elif b:
            up = (0, b + 1, 0)
        elif len(r) == 2:
            up = (0, 1, 0)
        else:
            up = (0, 0, c + 1)
    else:
        up = (a + 1, 0, 0) if len(r) == 1 else (a, b + 1, 0)
    return [(">=", _ora_mk(p[0], (a, b, c), p[2])), ("<", _ora_mk(p[0], up))]


_ORA_OPS = (">=", "<=", "==", "!=", ">", "<", "=", "^", "~")


def _ora_comp(tok):
    if not tok:
        raise _OraBad(tok)
    op, body, had = "=", tok, False
    for o in _ORA_OPS:
        if tok.startswith(o):
            op, body, had = o, tok[len(o):], True
            break
    if "*" in body:
        if had:
            raise _OraBad(tok)
        if body == "*":
            return [], []
        segs = body.split(".")
        if len(segs) not in (2, 3) or segs[-1] != "*":
            raise _OraBad(tok)
        if any(not _ora_num(s) for s in segs[:-1]):
            raise _OraBad(tok)
        v = [int(s) for s in segs[:-1]]
        if len(v) == 1:
            lo, hi = (v[0], 0, 0), (v[0] + 1, 0, 0)
        else:
            lo, hi = (v[0], v[1], 0), (v[0], v[1] + 1, 0)
        return [(">=", _ora_mk(0, lo)), ("<", _ora_mk(0, hi))], []
    p = _ora_parse(body)
    g = [p] if p[2] is not None else []
    if op in ("^", "~"):
        return _ora_ct(p, op == "^"), g
    return [("=" if op == "==" else op, p)], g


def _ora_constraint(text):
    if not isinstance(text, str):
        raise _OraBad(text)
    t = "".join(c for c in text if c not in " \t\n\r\f\v")
    if not t:
        raise _OraBad(text)
    out = []
    for part in t.split("||"):
        if not part:
            raise _OraBad(text)
        prims, gates = [], []
        for tok in part.split(","):
            a, b = _ora_comp(tok)
            prims += a
            gates += b
        out.append((prims, gates))
    return out


_ORA_T = {">=": lambda c: c >= 0, ">": lambda c: c > 0, "<=": lambda c: c <= 0,
          "<": lambda c: c < 0, "=": lambda c: c == 0, "!=": lambda c: c != 0}


def _ora_sat(v, cons):
    p = _ora_parse(v)
    for prims, gates in _ora_constraint(cons):
        if p[2] is not None and not any(_ora_releq(g, p) for g in gates):
            continue
        if all(_ORA_T[o](_ora_cmp(p, q)) for o, q in prims):
            return True
    return False


# =========================== case generation ============================

_ALPHA = ["a", "b", "z", "Z", "A", "rc", "alpha", "beta", "pre", "0a", "1b"]
_NUMS = ["0", "1", "2", "3", "10", "00", "01", "007", "0"]
_PREID = ["alpha", "beta", "rc", "a", "Z", "0", "1", "2", "01", "10", "0a"]
_BUILDS = ["b1", "build.7", "x-y", "001", "a-b.c", "-", "0"]


def _gv(rng, alpha_p=0.12, pre_p=0.45, build_p=0.35, epoch_p=0.25, maxseg=4):
    s = ""
    if rng.random() < epoch_p:
        s += rng.choice(["0", "1", "2", "01"]) + ":"
    n = rng.randint(1, maxseg)
    segs = []
    for _ in range(n):
        if rng.random() < alpha_p:
            segs.append(rng.choice(_ALPHA))
        else:
            segs.append(rng.choice(_NUMS))
    s += ".".join(segs)
    if rng.random() < pre_p:
        s += "-" + ".".join(rng.choice(_PREID)
                            for _ in range(rng.randint(1, 3)))
    if rng.random() < build_p:
        s += "+" + rng.choice(_BUILDS)
    return s


_CURATED = [
    "1", "1.0", "1.0.0", "1.0.0.0", "0:1.0.0", "00:1.0.0", "1:1.0.0",
    "2:0.0.1", "1.0.0+a", "1.0.0+zzz", "1.0.0+0", "1.00.0", "01.0.0",
    "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.0", "1.0.0-alpha.beta",
    "1.0.0-1", "1.0.0-01", "1.0.0-2", "1.0.0-10", "1.0.0-a", "1.0.0-Z",
    "1.0.0-rc.1+b", "1.0.a", "1.0.Z", "1.0.z", "1.0.0a", "0.0.1", "0.0.2",
    "0.1.0", "0.2.3", "0.2.9", "0.3.0", "0.0.3", "0.0.4", "1.2.3", "1.2.4",
    "1.3.0", "1.2.3-rc.1", "1.2.3-rc.2", "1.2.3+x", "2.0.0", "2.0.0-alpha",
    "1.10", "1.9", "1.2", "3", "0", "0.0", "0.0.0", "0.0.0-a", "1:0.0.1",
]


def _pool(rng, n, **kw):
    out = list(_CURATED)
    while len(out) < n:
        out.append(_gv(rng, **kw))
    return out[:n]


# --- 1-3: parse -------------------------------------------------------
def _parse_bucket(idx):
    def probe():
        rng = random.Random(9000 + idx)
        pool = _pool(rng, 330)
        for i, v in enumerate(pool):
            if i % 3 != idx:
                continue
            e, r, p, b = _ora_parse(v)
            got = vercmp.parse(v)
            if not isinstance(got, dict):
                return False
            if set(got.keys()) != {"epoch", "release", "pre", "build"}:
                return False
            if got["epoch"] != e or list(got["release"]) != list(r):
                return False
            if p is None:
                if got["pre"] is not None:
                    return False
            else:
                if got["pre"] is None or list(got["pre"]) != list(p):
                    return False
            if got["build"] != b:
                return False
        return True
    return probe


for _i in range(3):
    check("parse: fields for generated versions (bucket %d)" % _i,
          _parse_bucket(_i))

_BAD = [
    "", ".", "1.", ".1", "1..2", "1.0-", "1.0+", ":1.0", "a:1.0", "-1.0",
    "1.0-alpha+", "1.0-+x", "1:2:3", "1.0.0-al pha", "1 .0", " 1.0", "1.0 ",
    "1.0.0-a_b", "1.0_0", "1.0.0-a..b", "1.0.0+a..b", "1.0.0-a-b", "+1.0",
    "1.0.0-", "1.0.0+ ", "1,0", "1.0.0-a+b+c", "*", "1.*", "1.0.0-a+", "1.0.0++b",
    "1.0.0-alpha!", "1.0.0#", "-", "+", ":", "1.0.0-é", "é1.0",
]


def _bad_parse():
    if not _HAS_VE:
        return False
    for s in _BAD:
        try:
            _ora_parse(s)
            return False       # oracle self-check: must be malformed
        except _OraBad:
            pass
        try:
            vercmp.parse(s)
            return False
        except VE:
            pass
    return True


check("VersionError subclasses ValueError",
      lambda: _HAS_VE and issubclass(VE, ValueError))
check("parse: malformed strings raise VersionError", _bad_parse)

# --- 4-7: compare, randomised -----------------------------------------
def _cmp_bucket(idx):
    def probe():
        rng = random.Random(4100 + idx)
        pool = _pool(rng, 200)
        for k in range(600):
            a = pool[rng.randrange(len(pool))]
            b = pool[rng.randrange(len(pool))]
            want = _ora_cmp(_ora_parse(a), _ora_parse(b))
            if vercmp.compare(a, b) != want:
                return False
            if vercmp.compare(b, a) != -want:
                return False
        return True
    return probe


for _i in range(4):
    check("compare: randomised differential (bucket %d)" % _i, _cmp_bucket(_i))


# --- 8-11: compare, targeted families ---------------------------------
def _fam_build():
    rng = random.Random(777)
    base = [_gv(rng, build_p=0.0) for _ in range(120)]
    for v in base:
        for b in _BUILDS:
            x, y = v + "+" + b, v + "+zz9"
            if vercmp.compare(x, y) != 0 or vercmp.compare(x, v) != 0:
                return False
            if vercmp.compare(v, y) != 0:
                return False
    return True


def _fam_pad():
    rng = random.Random(778)
    pairs = [("1", "1.0"), ("1.0", "1.0.0"), ("1.0.0", "1.0.0.0"),
             ("0", "0.0.0.0"), ("1.2", "1.2.0.0"), ("1.0", "1.0.a"),
             ("1.0", "1.0.0a"), ("1.2.0", "1.2"), ("2:1", "2:1.0.0")]
    want = [0, 0, 0, 0, 0, -1, -1, 0, 0]
    for (a, b), w in zip(pairs, want):
        if vercmp.compare(a, b) != w:
            return False
    for _ in range(160):
        v = _gv(rng, pre_p=0.3, build_p=0.2)
        head = v.split("-")[0].split("+")[0]
        tail = v[len(head):]
        for k in range(1, 4):
            pv = head + ".0" * k + tail
            if vercmp.compare(v, pv) != 0:
                return False
    return True


def _fam_pre():
    rng = random.Random(779)
    base = [_gv(rng, pre_p=0.0, build_p=0.0) for _ in range(100)]
    for v in base:
        for p in ["alpha", "0", "zzz", "1.2", "a.b.c"]:
            if vercmp.compare(v + "-" + p, v) != -1:
                return False
            if vercmp.compare(v, v + "-" + p) != 1:
                return False
    seq = ["1.0.0-alpha", "1.0.0-alpha.0", "1.0.0-alpha.1",
           "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2",
           "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
    for i in range(len(seq) - 1):
        if vercmp.compare(seq[i], seq[i + 1]) != -1:
            return False
    return True


def _fam_alpha_epoch():
    cases = [("1.0.0-1", "1.0.0-alpha", -1), ("1.0.0-01", "1.0.0-1", 0),
             ("1.0.0-2", "1.0.0-10", -1), ("1.0.0-Z", "1.0.0-a", -1),
             ("1.0.0-A", "1.0.0-Z", -1), ("1.0.Z", "1.0.a", -1),
             ("1.0.0", "1.0.0a", -1), ("1.0.9", "1.0.a", -1),
             ("007.0", "7.0", 0), ("1.00.0", "1.0.0", 0),
             ("0:1.0.0", "1.0.0", 0), ("00:1.0.0", "0:1.0.0", 0),
             ("1:0.0.1", "9.9.9", 1), ("2:0", "1:99", 1),
             ("1:1.0.0-a", "1:1.0.0", -1), ("1.0.0-9", "1.0.0-10", -1)]
    for a, b, w in cases:
        if vercmp.compare(a, b) != w:
            return False
        if vercmp.compare(b, a) != -w:
            return False
    return True


check("compare: build metadata is ignored", _fam_build)
check("compare: zero-padding of shorter releases", _fam_pad)
check("compare: prerelease ranks below its release", _fam_pre)
check("compare: numeric vs alphanumeric identifiers and epochs",
      _fam_alpha_epoch)


# --- 12-17: satisfies by comparator family ----------------------------
def _sat_pool(rng, n, pre):
    kw = dict(alpha_p=0.05, pre_p=(0.5 if pre else 0.0), build_p=0.3,
              epoch_p=0.15, maxseg=3)
    out = [v for v in _CURATED if pre or "-" not in v]
    while len(out) < n:
        v = _gv(rng, **kw)
        if not pre and "-" in v.split("+")[0]:
            continue
        out.append(v)
    return out[:n]


def _small(rng):
    return str(rng.choice([0, 0, 1, 1, 2, 3, 10]))


def _cons_ver(rng, pre_p=0.0):
    s = ""
    if rng.random() < 0.12:
        s += rng.choice(["0", "1"]) + ":"
    s += ".".join(_small(rng) for _ in range(rng.randint(1, 3)))
    if rng.random() < pre_p:
        s += "-" + rng.choice(["alpha", "rc.1", "0", "beta.2"])
    if rng.random() < 0.2:
        s += "+" + rng.choice(_BUILDS)
    return s


def _gen_comp(rng, kind, pre_p=0.0):
    if kind == "rel":
        return rng.choice([">=", ">", "<=", "<", "=", "==", "!=", ""]) \
            + _cons_ver(rng, pre_p)
    if kind == "caret":
        return "^" + _cons_ver(rng, pre_p)
    if kind == "tilde":
        return "~" + _cons_ver(rng, pre_p)
    if kind == "wild":
        r = rng.random()
        if r < 0.12:
            return "*"
        if r < 0.56:
            return _small(rng) + ".*"
        return _small(rng) + "." + _small(rng) + ".*"
    return _gen_comp(rng, rng.choice(["rel", "caret", "tilde", "wild"]), pre_p)


def _sat_bucket(idx, kind, seed, pre, ncons=220, nand=1, nor=1, pre_p=0.0):
    def probe():
        rng = random.Random(seed)
        pool = _sat_pool(rng, 90, pre)
        for _ in range(ncons):
            groups = []
            for _g in range(rng.randint(1, nor)):
                toks = [_gen_comp(rng, kind, pre_p)
                        for _ in range(rng.randint(1, nand))]
                groups.append(",".join(toks))
            cons = "||".join(groups)
            if rng.random() < 0.25:
                cons = cons.replace(",", " , ").replace("||", " || ")
            try:
                _ora_constraint(cons)
            except _OraBad:
                continue
            for _k in range(10):
                v = pool[rng.randrange(len(pool))]
                if vercmp.satisfies(v, cons) is not _ora_sat(v, cons):
                    return False
        return True
    return probe


check("satisfies: relational operators", _sat_bucket(0, "rel", 5101, False))
check("satisfies: caret ranges", _sat_bucket(1, "caret", 5102, False))
check("satisfies: tilde ranges", _sat_bucket(2, "tilde", 5103, False))
check("satisfies: wildcard ranges", _sat_bucket(3, "wild", 5104, False))
check("satisfies: comma AND-lists",
      _sat_bucket(4, "mix", 5105, False, ncons=180, nand=3))
check("satisfies: || OR of AND-lists",
      _sat_bucket(5, "mix", 5106, False, ncons=180, nand=3, nor=3))

# --- 18-19: prerelease gate -------------------------------------------
check("satisfies: prereleases against ranges without prerelease operands",
      _sat_bucket(6, "mix", 5107, True, ncons=220, nand=2, nor=2, pre_p=0.0))
check("satisfies: prereleases against ranges naming a prerelease",
      _sat_bucket(7, "mix", 5108, True, ncons=220, nand=2, nor=2, pre_p=0.75))


def _gate_fixed():
    cases = [
        ("1.2.3-rc.1", "^1.2.3", False),
        ("1.2.3-rc.1", ">=1.2.0,<2.0.0", False),
        ("1.2.3-rc.1", ">=1.2.3-rc.0,<2.0.0", True),
        ("1.2.3-rc.1", ">=1.2.3-rc.2,<2.0.0", False),
        ("1.2.4-rc.1", ">=1.2.3-rc.0,<2.0.0", False),
        ("1.2.3-rc.1", "^1.2.3-rc.0", True),
        ("2.0.0-alpha", "^1.2.3-rc.0", False),
        ("1.2.3-rc.1", "*", False),
        ("1.2.3-rc.1", "1.2.*", False),
        ("1.2.3-rc.1", "!=9.9.9-x,>=1.2.3-rc.0", True),
        ("1.2.3-rc.1", "!=1.2.3-rc.9,<2.0.0", True),
        ("1.2.3-rc.1", "!=1.2.3-rc.1,<2.0.0", False),
        ("1.2.3-rc.1", ">=1.2.3-rc.0 || >=1.0.0", True),
        ("1.2.3-rc.1", ">=1.0.0 || <1.2.3-rc.0", False),
        ("1.2.3-rc.1", ">=1.2.3-rc.0,>2.0.0", False),
        ("1.2-rc.1", ">=1.2.0-rc.0,<2.0.0", True),
        ("0:1.2.3-rc.1", ">=1.2.3-rc.0", True),
        ("1:1.2.3-rc.1", ">=1.2.3-rc.0", False),
        ("1.2.3", "^1.2.3-rc.0", True),
        ("1.9.0", "^1.2.3-rc.0", True),
    ]
    for v, c, w in cases:
        if _ora_sat(v, c) is not w:
            return False       # oracle self-check
        if vercmp.satisfies(v, c) is not w:
            return False
    return True


check("satisfies: prerelease gate corner cases", _gate_fixed)

# --- 20: malformed constraints ----------------------------------------
_BADC = ["", "   ", ",", "1.0,", ",1.0", "1.0,,2.0", "||", "||1.0", "1.0||",
         "1.0|| ||2.0", ">=", "^", "~", ">=1.0.*", "^1.*", "~*", "*.1",
         "1.*.3", "1.2.3.*", "1:1.*", "*-rc", "*+b", "^1.2.3.4", "~1.2.3.4",
         "^1.a", "~a", "^a.b", ">1.0.0-", "=1..0", "!=", "^1.2.3-"]


def _bad_cons():
    if not _HAS_VE:
        return False
    for c in _BADC:
        try:
            _ora_constraint(c)
            return False      # oracle self-check
        except _OraBad:
            pass
        try:
            vercmp.satisfies("1.0.0", c)
            return False
        except VE:
            pass
    return True


check("satisfies: malformed constraints raise VersionError", _bad_cons)


# --- 21-22: best_match -------------------------------------------------
def _bm_bucket(idx, seed, pre):
    def probe():
        rng = random.Random(seed)
        pool = _sat_pool(rng, 80, pre)
        for _ in range(160):
            lst = [pool[rng.randrange(len(pool))]
                   for _ in range(rng.randint(0, 9))]
            kind = rng.choice(["rel", "caret", "tilde", "wild", "mix"])
            toks = [_gen_comp(rng, kind, 0.4 if pre else 0.0)
                    for _ in range(rng.randint(1, 2))]
            cons = ",".join(toks)
            if rng.random() < 0.3:
                cons += "||" + _gen_comp(rng, "wild")
            try:
                _ora_constraint(cons)
            except _OraBad:
                continue
            best, bp = None, None
            for v in lst:
                if not _ora_sat(v, cons):
                    continue
                p = _ora_parse(v)
                if bp is None or _ora_cmp(p, bp) > 0:
                    best, bp = v, p
            if vercmp.best_match(lst, cons) != best:
                return False
        return True
    return probe


check("best_match: releases only, incl. empty match sets",
      _bm_bucket(0, 6101, False))
check("best_match: with prereleases and ties", _bm_bucket(1, 6102, True))


def _bm_ties():
    cases = [
        (["1.0.0+a", "1.0", "1.0.0+b"], "*", "1.0.0+a"),
        (["1.0", "1.0.0", "1"], ">=1.0.0", "1.0"),
        (["0.9.9", "1.0.0"], "^2", None),
        ([], "*", None),
        (["1.0.0-rc", "1.0.0"], "^1.0.0-0", "1.0.0"),
        (["2:1.0.0", "9.9.9"], "*", "2:1.0.0"),
        (["1.0.0+z", "1.0.0"], "=1.0.0+q", "1.0.0+z"),
    ]
    for lst, c, w in cases:
        if vercmp.best_match(lst, c) != w:
            return False
    return True


check("best_match: tie rule and empty results", _bm_ties)


# --- 23-24: sort_versions ---------------------------------------------
def _sort_bucket(seed):
    def probe():
        rng = random.Random(seed)
        pool = _pool(rng, 150)
        for _ in range(220):
            lst = [pool[rng.randrange(len(pool))]
                   for _ in range(rng.randint(0, 14))]
            idx = sorted(range(len(lst)),
                         key=lambda i: (_ora_key(_ora_parse(lst[i]), 6), i))
            want = [lst[i] for i in idx]
            got = vercmp.sort_versions(lst)
            if list(got) != want:
                return False
        return True
    return probe


check("sort_versions: randomised differential", _sort_bucket(7101))


def _sort_stable():
    lst = ["1.0.0+b", "1.0", "1.0.0+a", "1", "0:1.0.0", "1.0.0-rc",
           "1.0.0-rc+z", "2.0", "1.10", "1.9"]
    want = ["1.0.0-rc", "1.0.0-rc+z", "1.0.0+b", "1.0", "1.0.0+a", "1",
            "0:1.0.0", "1.9", "1.10", "2.0"]
    if vercmp.sort_versions(lst) != want:
        return False
    src = list(lst)
    out = vercmp.sort_versions(src)
    if src != lst or out is src:
        return False
    return vercmp.sort_versions([]) == [] and vercmp.sort_versions(["1"]) == ["1"]


check("sort_versions: stability and no mutation of the input", _sort_stable)

_t.cancel()
report()
