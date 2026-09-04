import sys, os, random, threading

TOTAL = 20
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
    import nullagg
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


class _Missing(object):
    def __init__(self, *a, **k):
        raise AttributeError("attribute missing from nullagg")


CT = getattr(nullagg, "Table", _Missing)


def _cand(name):
    f = getattr(nullagg, name, None)
    if f is None:
        def boom(*a, **k):
            raise AttributeError("nullagg.%s missing" % name)
        return boom
    return f


# ======================================================================
# Inlined naive oracle (independent slow reference for the same spec).
# ======================================================================

def _ora_tgroup(v):
    return 1 if isinstance(v, str) else 0


def _ora_cmpv(a, b):
    ga, gb = _ora_tgroup(a), _ora_tgroup(b)
    if ga != gb:
        return -1 if ga < gb else 1
    if a < b:
        return -1
    if b < a:
        return 1
    return 0


def _ora_normkey(k):
    if isinstance(k, str):
        col, direction, nulls = k, "asc", None
    else:
        col = k[0]
        direction = k[1] if len(k) > 1 else "asc"
        nulls = k[2] if len(k) > 2 else None
    if nulls is None:
        nulls = "last" if direction == "asc" else "first"
    return (col, direction, nulls)


def _ora_rowcmp(ra, rb, keys):
    for col, direction, nulls in keys:
        a = ra.get(col)
        b = rb.get(col)
        if a is None and b is None:
            continue
        if a is None:
            return -1 if nulls == "first" else 1
        if b is None:
            return 1 if nulls == "first" else -1
        c = _ora_cmpv(a, b)
        if c:
            return c if direction == "asc" else -c
    return 0


def _ora_order(rows, keys):
    ks = [_ora_normkey(k) for k in keys]
    out = [dict(r) for r in rows]
    if not ks:
        return out
    # stable insertion sort
    for i in range(1, len(out)):
        item = out[i]
        j = i - 1
        while j >= 0 and _ora_rowcmp(out[j], item, ks) > 0:
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = item
    return out


def _ora_keq(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a == b


def _ora_kteq(ka, kb):
    if len(ka) != len(kb):
        return False
    for a, b in zip(ka, kb):
        if not _ora_keq(a, b):
            return False
    return True


def _ora_distinct(rows, cols):
    keys = []
    out = []
    for r in rows:
        k = tuple(r.get(c) for c in cols)
        dup = False
        for k2 in keys:
            if _ora_kteq(k, k2):
                dup = True
                break
        if dup:
            continue
        keys.append(k)
        out.append(dict(r))
    return out


def _ora_inputs(grp, col):
    return [r.get(col) for r in grp if r.get(col) is not None]


def _ora_agg(spec, grp):
    kind = spec[0]
    if kind == "count_star":
        return len(grp)
    col = spec[1]
    if kind == "any":
        vs = [r.get(col) for r in grp]
        for v in vs:
            if v is True:
                return True
        for v in vs:
            if v is None:
                return None
        return False
    if kind == "every":
        vs = [r.get(col) for r in grp]
        for v in vs:
            if v is False:
                return False
        for v in vs:
            if v is None:
                return None
        return True
    vs = _ora_inputs(grp, col)
    if kind == "count":
        return len(vs)
    if not vs:
        return None
    if kind == "sum":
        tot = 0
        for v in vs:
            tot = tot + v
        return tot
    if kind == "avg":
        tot = 0
        for v in vs:
            tot = tot + v
        return tot / len(vs)
    if kind == "min":
        best = vs[0]
        for v in vs[1:]:
            if _ora_cmpv(v, best) < 0:
                best = v
        return best
    if kind == "max":
        best = vs[0]
        for v in vs[1:]:
            if _ora_cmpv(v, best) > 0:
                best = v
        return best
    raise ValueError(kind)


def _ora_group(rows, cols, aggs):
    cols = list(cols)
    keys = []
    groups = []
    for r in rows:
        k = tuple(r.get(c) for c in cols)
        idx = -1
        for i, k2 in enumerate(keys):
            if _ora_kteq(k, k2):
                idx = i
                break
        if idx < 0:
            keys.append(k)
            groups.append([])
            idx = len(keys) - 1
        groups[idx].append(r)
    if not cols:
        keys = [()]
        if not groups:
            groups = [[]]
    out = []
    for k, grp in zip(keys, groups):
        row = {}
        for i, c in enumerate(cols):
            row[c] = k[i]
        for name, spec in aggs:
            row[name] = _ora_agg(spec, grp)
        out.append(row)
    return out


def _ora_pred(node, row):
    op = node[0]
    if op == "is_null":
        return row.get(node[1]) is None
    if op == "not":
        v = _ora_pred(node[1], row)
        return None if v is None else (not v)
    if op == "and":
        unk = False
        for sub in node[1]:
            v = _ora_pred(sub, row)
            if v is False:
                return False
            if v is None:
                unk = True
        return None if unk else True
    if op == "or":
        unk = False
        for sub in node[1]:
            v = _ora_pred(sub, row)
            if v is True:
                return True
            if v is None:
                unk = True
        return None if unk else False
    col, val = node[1], node[2]
    a = row.get(col)
    if op == "eq":
        return None if a is None else (a == val)
    if op == "ne":
        return None if a is None else (a != val)
    if a is None or val is None:
        return None
    if _ora_tgroup(a) != _ora_tgroup(val):
        return None
    if op == "lt":
        return a < val
    if op == "le":
        return a <= val
    if op == "gt":
        return a > val
    if op == "ge":
        return a >= val
    raise ValueError(op)


def _ora_having(rows, node):
    return [dict(r) for r in rows if _ora_pred(node, r) is True]


# ======================================================================
# Bridges into the candidate module
# ======================================================================

_AGG_FN = {"count_star": "count_star", "count": "count", "sum": "sum_",
           "avg": "avg", "min": "min_", "max": "max_", "any": "any_",
           "every": "every"}
_PRED_FN = {"eq": "eq", "ne": "ne", "lt": "lt", "le": "le", "gt": "gt",
            "ge": "ge"}


def _build_agg(spec):
    fn = _cand(_AGG_FN[spec[0]])
    if spec[0] == "count_star":
        return fn()
    return fn(spec[1])


def _build_pred(node):
    op = node[0]
    if op == "is_null":
        return _cand("is_null")(node[1])
    if op == "not":
        return _cand("not_")(_build_pred(node[1]))
    if op == "and":
        return _cand("and_")(*[_build_pred(s) for s in node[1]])
    if op == "or":
        return _cand("or_")(*[_build_pred(s) for s in node[1]])
    return _cand(_PRED_FN[op])(node[1], node[2])


# ======================================================================
# Case generation
# ======================================================================

COLS = ["g", "h", "x", "y", "b1", "b2"]
POOL = {
    "g": ["a", "b", 1, 2],
    "h": ["p", "q"],
    "x": [-2, 0, 1, 2, 3, 1.5, 2.0, 4],
    "y": [1, 2, 10, "a", "b", "z"],
    "b1": [True, False],
    "b2": [True, False],
}


def gen_rows(rng):
    n = rng.choice([0, 1, 1, 2, 3, 3, 4, 5, 6, 7, 8])
    allnull = set(c for c in COLS if rng.random() < 0.15)
    rows = []
    for _i in range(n):
        r = {}
        for c in COLS:
            if c in allnull or rng.random() < 0.35:
                r[c] = None
            else:
                r[c] = rng.choice(POOL[c])
        rows.append(r)
    if rows and rng.random() < 0.4:
        for _k in range(rng.randint(1, 3)):
            rows.append(dict(rng.choice(rows)))
        rng.shuffle(rows)
    return rows


def gen_keys(rng, explicit, pool=None):
    pool = pool or COLS
    ks = []
    for _i in range(rng.randint(1, 3)):
        col = rng.choice(pool)
        d = rng.choice(["asc", "desc"])
        if explicit:
            ks.append((col, d, rng.choice(["first", "last"])))
        else:
            if rng.random() < 0.3:
                ks.append(col)
            else:
                ks.append((col, d))
    return ks


NUM_AGGS = [("count_star",), ("count", "x"), ("sum", "x"), ("avg", "x"),
            ("min", "x"), ("max", "x"), ("count", "y"), ("min", "y"),
            ("max", "y"), ("count", "g")]
BOOL_AGGS = [("any", "b1"), ("every", "b1"), ("any", "b2"), ("every", "b2"),
             ("count_star",), ("count", "b1")]


def gen_aggs(rng, palette, lo=1, hi=4):
    picks = rng.sample(palette, rng.randint(lo, min(hi, len(palette))))
    return [("a%d" % i, s) for i, s in enumerate(picks)]


def gen_gcols(rng, allow_empty=True):
    r = rng.random()
    if allow_empty and r < 0.2:
        return []
    if r < 0.7:
        return [rng.choice(["g", "h", "y", "b1"])]
    return rng.sample(["g", "h", "y", "b1"], 2)


PRED_COLS_VALS = [None, 0, 1, 2, 3, "a", "b", True, False, 2.0]


def gen_pred(rng, cols, depth=0):
    r = rng.random()
    if depth < 2 and r < 0.35:
        op = rng.choice(["and", "or"])
        k = rng.randint(0, 3)
        return (op, [gen_pred(rng, cols, depth + 1) for _i in range(k)])
    if depth < 2 and r < 0.45:
        return ("not", gen_pred(rng, cols, depth + 1))
    if r < 0.58:
        return ("is_null", rng.choice(cols))
    op = rng.choice(["eq", "ne", "lt", "le", "gt", "ge"])
    return (op, rng.choice(cols), rng.choice(PRED_COLS_VALS))


# ======================================================================
# Differential runner
# ======================================================================

def make_bucket(cases, runner):
    def probe():
        for c in cases:
            got = runner(c)
            want = c[-1]
            if got != want:
                return False
            if not _same_shape(got, want):
                return False
        return True
    return probe


def _same_shape(got, want):
    if not isinstance(got, list) or len(got) != len(want):
        return False
    for a, b in zip(got, want):
        if not isinstance(a, dict) or set(a.keys()) != set(b.keys()):
            return False
        for k in b:
            if (a[k] is None) != (b[k] is None):
                return False
            if isinstance(b[k], bool) != isinstance(a[k], bool):
                return False
    return True


def spread(prefix, cases, runner, nbuckets):
    for b in range(nbuckets):
        sl = cases[b::nbuckets]
        check("%s [%d/%d]" % (prefix, b + 1, nbuckets), make_bucket(sl, runner))


# ---- family: order_by, default null placement -------------------------
rng = random.Random(4701)
order_cases = []
for _i in range(90):
    rows = gen_rows(rng)
    keys = gen_keys(rng, False)
    order_cases.append((rows, keys, _ora_order(rows, keys)))


def run_order(c):
    return CT(c[0]).order_by(*c[1]).rows()


spread("order_by default null placement", order_cases, run_order, 3)

# ---- family: order_by, explicit null placement -------------------------
rng = random.Random(4702)
oe_cases = []
for _i in range(60):
    rows = gen_rows(rng)
    keys = gen_keys(rng, True)
    oe_cases.append((rows, keys, _ora_order(rows, keys)))

spread("order_by explicit nulls first/last", oe_cases, run_order, 2)

# ---- family: order_by over mixed-type / tie-heavy columns --------------
rng = random.Random(4703)
om_cases = []
for _i in range(50):
    rows = gen_rows(rng)
    keys = gen_keys(rng, rng.random() < 0.5, ["y", "x", "b1"])
    om_cases.append((rows, keys, _ora_order(rows, keys)))

spread("order_by mixed types and stability", om_cases, run_order, 1)

# ---- family: distinct --------------------------------------------------
rng = random.Random(4704)
d_cases = []
for _i in range(60):
    rows = gen_rows(rng)
    cols = rng.sample(COLS, rng.randint(1, 3))
    d_cases.append((rows, cols, _ora_distinct(rows, cols)))


def run_distinct(c):
    return CT(c[0]).distinct(*c[1]).rows()


spread("distinct with NULLs equal", d_cases, run_distinct, 2)

# ---- family: group_by with numeric aggregates -------------------------
rng = random.Random(4705)
g_cases = []
for _i in range(90):
    rows = gen_rows(rng)
    cols = gen_gcols(rng)
    aggs = gen_aggs(rng, NUM_AGGS)
    g_cases.append((rows, cols, aggs, _ora_group(rows, cols, aggs)))


def run_group(c):
    return CT(c[0]).group_by(c[1], **dict((n, _build_agg(s))
                                          for n, s in c[2])).rows()


spread("group_by numeric aggregates", g_cases, run_group, 3)

# ---- family: group_by with any_/every ---------------------------------
rng = random.Random(4706)
gb_cases = []
for _i in range(60):
    rows = gen_rows(rng)
    cols = gen_gcols(rng)
    aggs = gen_aggs(rng, BOOL_AGGS)
    gb_cases.append((rows, cols, aggs, _ora_group(rows, cols, aggs)))

spread("group_by three-valued any_/every", gb_cases, run_group, 2)

# ---- family: degenerate groups (empty tables, all-NULL columns) --------
rng = random.Random(4707)
deg_cases = []
for _i in range(50):
    if rng.random() < 0.5:
        rows = []
    else:
        n = rng.randint(1, 4)
        rows = []
        for _j in range(n):
            r = dict((c, None) for c in COLS)
            if rng.random() < 0.4:
                r["g"] = rng.choice(POOL["g"])
            rows.append(r)
    cols = gen_gcols(rng)
    aggs = gen_aggs(rng, NUM_AGGS + BOOL_AGGS, 2, 5)
    deg_cases.append((rows, cols, aggs, _ora_group(rows, cols, aggs)))

spread("empty tables and all-NULL groups", deg_cases, run_group, 1)

# ---- family: having over grouped rows ---------------------------------
rng = random.Random(4708)
h_cases = []
for _i in range(90):
    rows = gen_rows(rng)
    cols = gen_gcols(rng)
    aggs = gen_aggs(rng, NUM_AGGS + BOOL_AGGS, 1, 4)
    grouped = _ora_group(rows, cols, aggs)
    names = list(cols) + [n for n, _s in aggs]
    node = gen_pred(rng, names)
    h_cases.append((rows, cols, aggs, node, _ora_having(grouped, node)))


def run_having(c):
    t = CT(c[0]).group_by(c[1], **dict((n, _build_agg(s)) for n, s in c[2]))
    return t.having(_build_pred(c[3])).rows()


spread("having with three-valued logic", h_cases, run_having, 3)

# ---- family: predicate truth tables on raw rows -----------------------
rng = random.Random(4709)
p_cases = []
for _i in range(50):
    rows = gen_rows(rng)
    node = gen_pred(rng, COLS)
    p_cases.append((rows, node, _ora_having(rows, node)))


def run_pred(c):
    return CT(c[0]).having(_build_pred(c[1])).rows()


def pred_bucket():
    for c in p_cases:
        if run_pred(c) != c[-1]:
            return False
    row = {"x": 1, "z": None}
    facts = [
        (("and", []), True),
        (("or", []), False),
        (("is_null", "z"), True),
        (("not", ("is_null", "x")), True),
        (("not", ("is_null", "z")), False),
        (("not", ("eq", "z", 1)), None),
        (("and", [("eq", "x", 1), ("eq", "z", 1)]), None),
        (("and", [("eq", "x", 2), ("eq", "z", 1)]), False),
        (("or", [("eq", "x", 1), ("eq", "z", 1)]), True),
        (("or", [("eq", "x", 2), ("eq", "z", 1)]), None),
        (("eq", "x", None), False),
        (("ne", "x", None), True),
        (("lt", "x", None), None),
        (("lt", "x", "a"), None),
        (("ge", "x", "a"), None),
        (("is_null", "nope"), True),
    ]
    for node, want in facts:
        p = _build_pred(node)
        got = p(row)
        if got is not want:
            return False
    return True


check("predicate three-valued truth tables", pred_bucket)

# ---- family: full chained pipelines -----------------------------------
rng = random.Random(4710)
pipe_cases = []
for _i in range(60):
    rows = gen_rows(rng)
    dcols = rng.sample(COLS, rng.randint(1, 2))
    gcols = gen_gcols(rng)
    aggs = gen_aggs(rng, NUM_AGGS + BOOL_AGGS, 1, 4)
    names = list(gcols) + [n for n, _s in aggs]
    node = gen_pred(rng, names)
    keys = gen_keys(rng, rng.random() < 0.5, names)
    step1 = _ora_distinct(rows, dcols)
    step2 = _ora_group(step1, gcols, aggs)
    step3 = _ora_having(step2, node)
    pipe_cases.append((rows, dcols, gcols, aggs, node, keys,
                       _ora_order(step3, keys)))


def run_pipe(c):
    rows, dcols, gcols, aggs, node, keys = c[0], c[1], c[2], c[3], c[4], c[5]
    t = CT(rows).distinct(*dcols)
    t = t.group_by(gcols, **dict((n, _build_agg(s)) for n, s in aggs))
    t = t.having(_build_pred(node))
    return t.order_by(*keys).rows()


spread("chained distinct/group_by/having/order_by", pipe_cases, run_pipe, 2)

_t.cancel()
report()
