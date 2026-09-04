"""NULL-tolerant sorting and aggregation over a tiny in-memory table."""

import functools


# ---------------------------------------------------------------- ordering

def _tgroup(v):
    """Type group used by the total order: numbers before strings."""
    return 1 if isinstance(v, str) else 0


def _cmp_vals(a, b):
    """Compare two non-None values under the ascending total order."""
    ga, gb = _tgroup(a), _tgroup(b)
    if ga != gb:
        return -1 if ga < gb else 1
    if a < b:
        return -1
    if b < a:
        return 1
    return 0


def _norm_key(k):
    if isinstance(k, str):
        col, direction, nulls = k, "asc", None
    else:
        t = tuple(k)
        col = t[0]
        direction = t[1] if len(t) > 1 else "asc"
        nulls = t[2] if len(t) > 2 else None
    if nulls is None:
        nulls = "last" if direction == "asc" else "first"
    return (col, direction, nulls)


def _row_cmp(keys):
    def cmp(ra, rb):
        for col, direction, nulls in keys:
            a = ra.get(col)
            b = rb.get(col)
            if a is None and b is None:
                continue
            if a is None:
                return -1 if nulls == "first" else 1
            if b is None:
                return 1 if nulls == "first" else -1
            c = _cmp_vals(a, b)
            if c:
                return c if direction == "asc" else -c
        return 0
    return cmp


# ---------------------------------------------------------------- table

class Table(object):
    def __init__(self, rows=()):
        self._rows = [dict(r) for r in rows]

    def rows(self):
        return [dict(r) for r in self._rows]

    def order_by(self, *keys):
        ks = [_norm_key(k) for k in keys]
        if not ks:
            return Table(self._rows)
        srt = sorted(self._rows, key=functools.cmp_to_key(_row_cmp(ks)))
        return Table(srt)

    def distinct(self, *cols):
        seen = set()
        out = []
        for r in self._rows:
            k = tuple(r.get(c) for c in cols)
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        return Table(out)

    def having(self, pred):
        return Table([r for r in self._rows if pred(r) is True])

    def group_by(self, cols, **aggs):
        cols = list(cols)
        order = []
        buckets = {}
        for r in self._rows:
            k = tuple(r.get(c) for c in cols)
            if k not in buckets:
                buckets[k] = []
                order.append(k)
            buckets[k].append(r)
        if not cols:
            order = [()]
            buckets.setdefault((), [])
        out = []
        for k in order:
            grp = buckets[k]
            row = {}
            for i, c in enumerate(cols):
                row[c] = k[i]
            for name, agg in aggs.items():
                row[name] = agg(grp)
            out.append(row)
        return Table(out)


# ---------------------------------------------------------------- aggregates

def _vals(rows, col):
    return [r.get(col) for r in rows if r.get(col) is not None]


def count_star():
    return lambda rows: len(rows)


def count(col):
    return lambda rows: len(_vals(rows, col))


def sum_(col):
    def f(rows):
        vs = _vals(rows, col)
        return sum(vs) if vs else None
    return f


def avg(col):
    def f(rows):
        vs = _vals(rows, col)
        return (sum(vs) / len(vs)) if vs else None
    return f


def min_(col):
    def f(rows):
        best = None
        for v in _vals(rows, col):
            if best is None or _cmp_vals(v, best) < 0:
                best = v
        return best
    return f


def max_(col):
    def f(rows):
        best = None
        for v in _vals(rows, col):
            if best is None or _cmp_vals(v, best) > 0:
                best = v
        return best
    return f


def any_(col):
    def f(rows):
        vs = [r.get(col) for r in rows]
        if any(v is True for v in vs):
            return True
        if any(v is None for v in vs):
            return None
        return False
    return f


def every(col):
    def f(rows):
        vs = [r.get(col) for r in rows]
        if any(v is False for v in vs):
            return False
        if any(v is None for v in vs):
            return None
        return True
    return f


# ---------------------------------------------------------------- predicates

def _mk(col, value, op):
    def p(row):
        a = row.get(col)
        if op == "eq":
            return None if a is None else (a == value)
        if op == "ne":
            return None if a is None else (a != value)
        if a is None or value is None:
            return None
        if _tgroup(a) != _tgroup(value):
            return None
        if op == "lt":
            return a < value
        if op == "le":
            return a <= value
        if op == "gt":
            return a > value
        return a >= value
    return p


def eq(col, value):
    return _mk(col, value, "eq")


def ne(col, value):
    return _mk(col, value, "ne")


def lt(col, value):
    return _mk(col, value, "lt")


def le(col, value):
    return _mk(col, value, "le")


def gt(col, value):
    return _mk(col, value, "gt")


def ge(col, value):
    return _mk(col, value, "ge")


def is_null(col):
    return lambda row: row.get(col) is None


def and_(*preds):
    def p(row):
        unk = False
        for q in preds:
            v = q(row)
            if v is False:
                return False
            if v is None:
                unk = True
        return None if unk else True
    return p


def or_(*preds):
    def p(row):
        unk = False
        for q in preds:
            v = q(row)
            if v is True:
                return True
            if v is None:
                unk = True
        return None if unk else False
    return p


def not_(pred):
    def p(row):
        v = pred(row)
        return None if v is None else (not v)
    return p
