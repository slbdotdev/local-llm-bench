"""Mini SQL-ish query engine over in-memory rows."""
from functools import cmp_to_key

UNKNOWN = ("UNKNOWN",)


def _pred(p, row):
    op = p["op"]
    if op == "and":
        res = True
        for a in p["args"]:
            v = _pred(a, row)
            if v is False:
                return False
            if v is UNKNOWN:
                res = UNKNOWN
        return res
    if op == "or":
        res = False
        for a in p["args"]:
            v = _pred(a, row)
            if v is True:
                return True
            if v is UNKNOWN:
                res = UNKNOWN
        return res
    if op == "not":
        v = _pred(p["arg"], row)
        if v is UNKNOWN:
            return UNKNOWN
        return not v
    v = row.get(p["col"])
    if op == "is_null":
        return v is None
    if v is None:
        return UNKNOWN
    c = p["value"]
    if op == "eq":
        return v == c
    if op == "ne":
        return v != c
    try:
        if op == "lt":
            return v < c
        if op == "le":
            return v <= c
        if op == "gt":
            return v > c
        if op == "ge":
            return v >= c
    except TypeError:
        return UNKNOWN
    raise ValueError("bad op: %r" % (op,))


def _agg_name(s):
    if s["fn"] == "count_star":
        return "count(*)"
    return "%s(%s)" % (s["fn"], s["col"])


def _agg(s, grows):
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
    raise ValueError("bad fn: %r" % (fn,))


def _sort(out, order_by):
    def cmp(ra, rb):
        for col, direction, nulls in order_by:
            va, vb = ra.get(col), rb.get(col)
            an, bn = va is None, vb is None
            if an and bn:
                continue
            if an or bn:
                first = nulls == "nulls_first"
                if an:
                    return -1 if first else 1
                return 1 if first else -1
            if va == vb:
                continue
            r = -1 if va < vb else 1
            return r if direction == "asc" else -r
        return 0
    return sorted(out, key=cmp_to_key(cmp))


def run(rows, spec):
    where = spec.get("where")
    if where is None:
        kept = list(rows)
    else:
        kept = [r for r in rows if _pred(where, r) is True]

    select = spec.get("select")
    group_by = spec.get("group_by")
    has_agg = select is not None and any("fn" in s for s in select)

    if group_by is not None or has_agg:
        if group_by is not None:
            buckets, keys = {}, []
            for r in kept:
                k = tuple(r.get(c) for c in group_by)
                if k not in buckets:
                    buckets[k] = []
                    keys.append(k)
                buckets[k].append(r)
            groups = [(buckets[k]) for k in keys]
        else:
            groups = [kept]
        out = []
        for grows in groups:
            d = {}
            specs = select if select is not None else [{"col": c} for c in group_by]
            for s in specs:
                if "fn" in s:
                    d[_agg_name(s)] = _agg(s, grows)
                else:
                    d[s["col"]] = grows[0].get(s["col"]) if grows else None
            out.append(d)
    elif select is not None:
        out = [{s["col"]: r.get(s["col"]) for s in select} for r in kept]
    else:
        out = [dict(r) for r in kept]

    order_by = spec.get("order_by")
    if order_by:
        out = _sort(out, order_by)
    off = spec.get("offset", 0)
    if off:
        out = out[off:]
    lim = spec.get("limit")
    if lim is not None:
        out = out[:lim]
    return out