import sys, random, copy
fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

try:
    # ---------- independent reference implementation (brute force) ----------
    def ref_pred(p, row):
        op = p["op"]
        if op == "and":
            vals = [ref_pred(a, row) for a in p["args"]]
            if "F" in vals:
                return "F"
            if "U" in vals:
                return "U"
            return "T"
        if op == "or":
            vals = [ref_pred(a, row) for a in p["args"]]
            if "T" in vals:
                return "T"
            if "U" in vals:
                return "U"
            return "F"
        if op == "not":
            v = ref_pred(p["arg"], row)
            return {"T": "F", "F": "T", "U": "U"}[v]
        v = row.get(p["col"])
        if op == "is_null":
            return "T" if v is None else "F"
        if v is None:
            return "U"
        c = p["value"]
        if op == "eq":
            return "T" if v == c else "F"
        if op == "ne":
            return "T" if v != c else "F"
        try:
            if op == "lt":
                return "T" if v < c else "F"
            if op == "le":
                return "T" if v <= c else "F"
            if op == "gt":
                return "T" if v > c else "F"
            if op == "ge":
                return "T" if v >= c else "F"
        except TypeError:
            return "U"
        raise ValueError(op)

    def ref_agg(s, grows):
        fn = s["fn"]
        if fn == "count_star":
            return len(grows)
        vals = [r.get(s["col"]) for r in grows]
        vals = [v for v in vals if v is not None]
        if fn == "count":
            return len(vals)
        if not vals:
            return None
        if fn == "sum":
            return sum(vals)
        if fn == "avg":
            return sum(vals) / len(vals)
        if fn == "min":
            return min(vals)
        if fn == "max":
            return max(vals)
        raise ValueError(fn)

    def ref_sort(out, ob):
        res = list(out)
        for col, direction, nulls in reversed(ob):
            eff = nulls
            if direction == "desc":
                eff = "nulls_last" if nulls == "nulls_first" else "nulls_first"
            def key(r, col=col, eff=eff):
                v = r.get(col)
                nf = 0 if eff == "nulls_first" else 1
                if v is None:
                    return (nf, 0)
                return (1 - nf, 1, v)
            res.sort(key=key, reverse=(direction == "desc"))
        return res

    def ref_run(rows, spec):
        w = spec.get("where")
        kept = [r for r in rows if w is None or ref_pred(w, r) == "T"]
        sel = spec.get("select")
        gb = spec.get("group_by")
        has_agg = sel is not None and any("fn" in s for s in sel)
        if gb is not None or has_agg:
            if gb is not None:
                keys, buckets = [], {}
                for r in kept:
                    k = tuple(r.get(c) for c in gb)
                    if k not in buckets:
                        buckets[k] = []
                        keys.append(k)
                    buckets[k].append(r)
                groups = [(k, buckets[k]) for k in keys]
            else:
                groups = [(None, kept)]
            out = []
            for _k, g in groups:
                d = {}
                for s in (sel if sel is not None else [{"col": c} for c in gb]):
                    if "fn" in s:
                        name = "count(*)" if s["fn"] == "count_star" else s["fn"] + "(" + s["col"] + ")"
                        d[name] = ref_agg(s, g)
                    else:
                        d[s["col"]] = g[0].get(s["col"]) if g else None
                out.append(d)
        else:
            if sel is not None:
                out = [{s["col"]: r.get(s["col"]) for s in sel} for r in kept]
            else:
                out = [dict(r) for r in kept]
        ob = spec.get("order_by")
        if ob:
            out = ref_sort(out, ob)
        off = spec.get("offset", 0)
        if off:
            out = out[off:]
        lim = spec.get("limit")
        if lim is not None:
            out = out[:lim]
        return out

    # ---------- fixed cases ----------
    from query import run

    def case(name, rows, spec, want):
        rows_before = copy.deepcopy(rows)
        spec_before = copy.deepcopy(spec)
        got = run(rows, spec)
        check(name, got == want)
        check(name + " no-mut-rows", rows == rows_before)
        check(name + " no-mut-spec", spec == spec_before)

    R1 = [{"a": 1}, {"a": None}, {"a": 2}]
    case("not of UNKNOWN drops", R1,
         {"where": {"op": "not", "arg": {"op": "gt", "col": "a", "value": 1}}}, [{"a": 1}])
    case("or with UNKNOWN keeps TRUE", R1,
         {"where": {"op": "or", "args": [{"op": "is_null", "col": "a"},
                                          {"op": "eq", "col": "a", "value": 2}]}},
         [{"a": None}, {"a": 2}])
    case("and with UNKNOWN drops", R1,
         {"where": {"op": "and", "args": [{"op": "is_null", "col": "a"},
                                           {"op": "eq", "col": "a", "value": 2}]}},
         [])
    case("and zero args true", R1, {"where": {"op": "and", "args": []}}, R1)
    case("or zero args false", R1, {"where": {"op": "or", "args": []}}, [])
    case("eq constant None is UNKNOWN", R1, {"where": {"op": "eq", "col": "a", "value": None}}, [])
    case("ne constant None true", R1, {"where": {"op": "ne", "col": "a", "value": None}},
         [{"a": 1}, {"a": 2}])
    case("lt incomparable is UNKNOWN", [{"s": "x"}, {"s": 3}],
         {"where": {"op": "lt", "col": "s", "value": 3}}, [])
    case("ne incomparable is equality", [{"s": "x"}, {"s": 3}],
         {"where": {"op": "ne", "col": "s", "value": 3}}, [{"s": "x"}])
    case("eq int float", [{"a": 1}, {"a": 1.0}, {"a": 2}],
         {"where": {"op": "eq", "col": "a", "value": 1.0}}, [{"a": 1}, {"a": 1.0}])
    case("missing key is None", [{"a": 1}, {}],
         {"where": {"op": "is_null", "col": "a"}}, [{}])
    case("missing key comparison", [{"a": 1}, {}],
         {"where": {"op": "eq", "col": "a", "value": 1}}, [{"a": 1}])

    G = [{"a": None, "b": 1}, {"a": 1, "b": 2}, {"a": None, "b": 3}, {"a": 1, "b": 4}]
    case("group None keys together", G,
         {"group_by": ["a"],
          "select": [{"col": "a"}, {"fn": "count_star"}, {"fn": "sum", "col": "b"}]},
         [{"a": None, "count(*)": 2, "sum(b)": 4}, {"a": 1, "count(*)": 2, "sum(b)": 6}])
    case("aggregates ignore None", G,
         {"select": [{"fn": "count", "col": "a"}, {"fn": "count_star"},
                      {"fn": "avg", "col": "b"}, {"fn": "min", "col": "b"}, {"fn": "max", "col": "b"}]},
         [{"count(a)": 2, "count(*)": 4, "avg(b)": 2.5, "min(b)": 1, "max(b)": 4}])
    case("all-None aggregates", [{"x": None}, {"x": None}],
         {"select": [{"fn": "sum", "col": "x"}, {"fn": "avg", "col": "x"},
                      {"fn": "min", "col": "x"}, {"fn": "max", "col": "x"}, {"fn": "count", "col": "x"}]},
         [{"sum(x)": None, "avg(x)": None, "min(x)": None, "max(x)": None, "count(x)": 0}])
    case("empty implicit group", [],
         {"select": [{"col": "a"}, {"fn": "count_star"}, {"fn": "sum", "col": "a"}]},
         [{"a": None, "count(*)": 0, "sum(a)": None}])
    case("group_by no select", G, {"group_by": ["a"]}, [{"a": None}, {"a": 1}])
    case("grouped plain col = first row", G,
         {"group_by": ["a"], "select": [{"col": "b"}]}, [{"b": 1}, {"b": 2}])
    case("where then group", G,
         {"where": {"op": "gt", "col": "b", "value": 1}, "group_by": ["a"],
          "select": [{"col": "a"}, {"fn": "count_star"}]},
         [{"a": 1, "count(*)": 2}, {"a": None, "count(*)": 1}])
    case("aggregate order_by + limit", G,
         {"group_by": ["a"], "select": [{"col": "a"}, {"fn": "sum", "col": "b"}],
          "order_by": [("sum(b)", "desc", "nulls_last")], "limit": 1},
         [{"a": 1, "sum(b)": 6}])
    case("projection missing key", [{"a": 1}, {}],
         {"select": [{"col": "a"}, {"col": "z"}]},
         [{"a": 1, "z": None}, {"a": None, "z": None}])
    case("no keys copies rows", [{"a": 1, "b": 2}], {}, [{"a": 1, "b": 2}])

    S = [{"k": 2, "i": 0}, {"k": None, "i": 1}, {"k": 1, "i": 2}, {"k": 2, "i": 3}]
    case("sort asc nulls last", S, {"order_by": [("k", "asc", "nulls_last")]},
         [{"k": 1, "i": 2}, {"k": 2, "i": 0}, {"k": 2, "i": 3}, {"k": None, "i": 1}])
    case("sort desc nulls first", S, {"order_by": [("k", "desc", "nulls_first")]},
         [{"k": None, "i": 1}, {"k": 2, "i": 0}, {"k": 2, "i": 3}, {"k": 1, "i": 2}])
    case("sort desc nulls last", S, {"order_by": [("k", "desc", "nulls_last")]},
         [{"k": 2, "i": 0}, {"k": 2, "i": 3}, {"k": 1, "i": 2}, {"k": None, "i": 1}])
    case("sort stable multi key", S,
         {"order_by": [("k", "asc", "nulls_last"), ("i", "desc", "nulls_first")]},
         [{"k": 1, "i": 2}, {"k": 2, "i": 3}, {"k": 2, "i": 0}, {"k": None, "i": 1}])
    case("offset limit after sort", S,
         {"order_by": [("k", "asc", "nulls_last")], "offset": 1, "limit": 2},
         [{"k": 2, "i": 0}, {"k": 2, "i": 3}])
    case("offset past end", [{"a": 1}], {"offset": 5}, [])
    case("limit zero", [{"a": 1}], {"limit": 0}, [])
    case("limit larger than rows", [{"a": 1}, {"a": 2}], {"limit": 9}, [{"a": 1}, {"a": 2}])

    # ---------- seeded randomised differential test ----------
    random.seed(21)
    COLS = ["name", "cat", "a", "b", "c"]
    POOL = {
        "name": [None, "ann", "bob", "cat", "dot"],
        "cat": [None, "a", "b", "c"],
        "a": [None, 0, 1, 2, 3],
        "b": [None, 0.5, 1.0, 2.5],
        "c": [None, 10, 20],
    }

    def gen_pred(depth=0):
        r = random.random()
        if depth < 2 and r < 0.30:
            return {"op": random.choice(["and", "or"]),
                    "args": [gen_pred(depth + 1) for _ in range(random.randint(0, 3))]}
        if depth < 2 and r < 0.45:
            return {"op": "not", "arg": gen_pred(depth + 1)}
        col = random.choice(COLS)
        op = random.choice(["eq", "ne", "lt", "le", "gt", "ge", "is_null"])
        if op == "is_null":
            return {"op": op, "col": col}
        return {"op": op, "col": col, "value": random.choice(POOL[col])}

    def gen_rows():
        rows = []
        for _ in range(random.randint(5, 40)):
            r = {}
            for c in COLS:
                if random.random() < 0.88:
                    r[c] = random.choice(POOL[c])
            rows.append(r)
        return rows

    def gen_spec():
        spec = {}
        if random.random() < 0.85:
            spec["where"] = gen_pred()
        sel = None
        if random.random() < 0.85:
            sel = []
            for _ in range(random.randint(1, 3)):
                if random.random() < 0.45:
                    sel.append({"col": random.choice(COLS)})
                else:
                    fn = random.choice(["count_star", "count", "sum", "min", "max", "avg"])
                    if fn == "count_star":
                        sel.append({"fn": fn})
                    elif fn in ("sum", "avg"):
                        sel.append({"fn": fn, "col": random.choice(["a", "b", "c"])})
                    else:
                        sel.append({"fn": fn, "col": random.choice(COLS)})
            spec["select"] = sel
        if random.random() < 0.55:
            spec["group_by"] = random.sample(COLS, random.randint(1, 2))
        if sel is not None:
            names = ["count(*)" if s.get("fn") == "count_star"
                     else (s["col"] if "fn" not in s else s["fn"] + "(" + s["col"] + ")")
                     for s in sel]
        elif spec.get("group_by"):
            names = list(spec["group_by"])
        else:
            names = COLS
        if names and random.random() < 0.75:
            spec["order_by"] = [
                (random.choice(names), random.choice(["asc", "desc"]),
                 random.choice(["nulls_first", "nulls_last"]))
                for _ in range(random.randint(1, 2))
            ]
        if random.random() < 0.35:
            spec["offset"] = random.randint(0, 5)
        if random.random() < 0.45:
            spec["limit"] = random.randint(0, 6)
        return spec

    n = 0
    for i in range(250):
        rows = gen_rows()
        spec = gen_spec()
        want = ref_run(copy.deepcopy(rows), copy.deepcopy(spec))
        rows_before = copy.deepcopy(rows)
        spec_before = copy.deepcopy(spec)
        try:
            got = run(rows, spec)
        except Exception as e:
            fails.append(f"rand {i} raised {e!r}")
            continue
        n += 1
        if got != want:
            fails.append(f"rand {i} spec={spec!s:.180} got={str(got)[:180]} want={str(want)[:180]}")
        elif rows != rows_before or spec != spec_before:
            fails.append(f"rand {i} mutated its inputs")
    check("enough random cases", n > 200)

except Exception as e:
    fails.append(f"exception: {e!r}")

if fails:
    print("FAIL", fails[:12])
    sys.exit(1)
print("PASS")