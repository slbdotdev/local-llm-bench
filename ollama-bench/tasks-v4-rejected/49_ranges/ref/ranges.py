"""Sets of real numbers built from intervals with open/closed endpoints."""

NEG = float("-inf")
POS = float("inf")


def _start_key(lo, lc):
    """Sort key for a lower endpoint.  (v, -1) < (v, 0) < (v, 1)."""
    if lo is None:
        return (NEG, 1)
    return (lo, 0 if lc else 1)


def _end_key(hi, rc):
    if hi is None:
        return (POS, -1)
    return (hi, 0 if rc else -1)


def _succ(key):
    v, d = key
    return (v, d + 1)


def _pred(key):
    v, d = key
    return (v, d - 1)


def _to_interval(s, e):
    lo = None if s[0] == NEG else s[0]
    hi = None if e[0] == POS else e[0]
    lc = False if lo is None else (s[1] == 0)
    rc = False if hi is None else (e[1] == 0)
    return (lo, hi, lc, rc)


def _normalize(pairs):
    """Sort/merge a list of (start_key, end_key) pairs into canonical order."""
    pairs = [p for p in pairs if p[0] <= p[1]]
    pairs.sort()
    out = []
    for s, e in pairs:
        if out and s <= _succ(out[-1][1]):
            if e > out[-1][1]:
                out[-1] = (out[-1][0], e)
        else:
            out.append((s, e))
    return out


class RangeSet(object):
    def __init__(self, intervals=()):
        pairs = []
        for iv in intervals:
            lo, hi, lc, rc = iv[0], iv[1], iv[2], iv[3]
            pairs.append((_start_key(lo, bool(lc)), _end_key(hi, bool(rc))))
        self._p = _normalize(pairs)

    @classmethod
    def _from_pairs(cls, pairs):
        r = cls()
        r._p = _normalize(pairs)
        return r

    def intervals(self):
        return [_to_interval(s, e) for s, e in self._p]

    def is_empty(self):
        return not self._p

    def contains(self, x):
        k = (x, 0)
        for s, e in self._p:
            if s <= k <= e:
                return True
            if s > k:
                break
        return False

    def union(self, other):
        return RangeSet._from_pairs(self._p + other._p)

    def intersect(self, other):
        out = []
        for s1, e1 in self._p:
            for s2, e2 in other._p:
                s = s1 if s1 > s2 else s2
                e = e1 if e1 < e2 else e2
                if s <= e:
                    out.append((s, e))
        return RangeSet._from_pairs(out)

    def complement(self):
        out = []
        cur = (NEG, 1)
        for s, e in self._p:
            stop = _pred(s)
            if cur <= stop:
                out.append((cur, stop))
            cur = _succ(e)
        end = (POS, -1)
        if cur <= end:
            out.append((cur, end))
        return RangeSet._from_pairs(out)

    def difference(self, other):
        return self.intersect(other.complement())

    def symmetric_difference(self, other):
        return self.difference(other).union(other.difference(self))

    def issubset(self, other):
        return self.difference(other).is_empty()

    def measure(self):
        total = 0
        for s, e in self._p:
            if s[0] == NEG or e[0] == POS:
                return POS
            total += e[0] - s[0]
        return total

    def to_string(self):
        if not self._p:
            return "{}"
        parts = []
        for lo, hi, lc, rc in self.intervals():
            a = "-inf" if lo is None else str(lo)
            b = "+inf" if hi is None else str(hi)
            parts.append(("[" if lc else "(") + a + "," + b + ("]" if rc else ")"))
        return " U ".join(parts)

    def __eq__(self, other):
        if not isinstance(other, RangeSet):
            return NotImplemented
        return self._p == other._p

    def __ne__(self, other):
        r = self.__eq__(other)
        if r is NotImplemented:
            return r
        return not r

    def __repr__(self):
        return "RangeSet(%s)" % (self.to_string(),)
