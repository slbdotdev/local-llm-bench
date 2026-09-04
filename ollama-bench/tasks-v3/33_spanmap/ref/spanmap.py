"""An interval "paint" map: overlapping spans, canonical output, checkpoints."""
from bisect import bisect_right


class SpanError(ValueError):
    def __init__(self, kind, msg=None):
        super().__init__(msg or kind)
        self.kind = kind


def _check_ints(*vals):
    for v in vals:
        if isinstance(v, bool) or not isinstance(v, int):
            raise SpanError("type", "coordinates must be plain ints")


class SpanMap:
    def __init__(self):
        self._s = []    # list of (lo, hi, label), sorted, disjoint, canonical
        self._h = []    # parallel list of hi values (for bisect)
        self._stack = []

    # ---------------- internals ----------------
    def _replace(self, i, j, rep):
        """Replace self._s[i:j] with the spans in rep, merging equal neighbours."""
        s = self._s
        # merge inside rep
        merged = []
        for sp in rep:
            if merged and merged[-1][1] == sp[0] and merged[-1][2] == sp[2]:
                merged[-1] = (merged[-1][0], sp[1], sp[2])
            else:
                merged.append(sp)
        rep = merged
        if rep and i > 0 and s[i - 1][1] == rep[0][0] and s[i - 1][2] == rep[0][2]:
            rep[0] = (s[i - 1][0], rep[0][1], rep[0][2])
            i -= 1
        if rep and j < len(s) and s[j][0] == rep[-1][1] and s[j][2] == rep[-1][2]:
            rep[-1] = (rep[-1][0], s[j][1], rep[-1][2])
            j += 1
        self._s[i:j] = rep
        self._h[i:j] = [sp[1] for sp in rep]

    def _apply(self, lo, hi, label):
        """Clear [lo, hi) and, if label is not None, paint it."""
        s = self._s
        i = bisect_right(self._h, lo)         # first span with hi > lo
        j = i
        n = len(s)
        while j < n and s[j][0] < hi:
            j += 1
        rep = []
        if i < j and s[i][0] < lo:
            rep.append((s[i][0], lo, s[i][2]))
        if label is not None:
            rep.append((lo, hi, label))
        if i < j and s[j - 1][1] > hi:
            rep.append((hi, s[j - 1][1], s[j - 1][2]))
        self._replace(i, j, rep)

    # ---------------- public API ----------------
    def paint(self, lo, hi, label):
        _check_ints(lo, hi)
        if not isinstance(label, str):
            raise SpanError("type", "label must be a str")
        if label == "":
            raise SpanError("label", "label must not be empty")
        if hi < lo:
            raise SpanError("order", "hi must be >= lo")
        if hi == lo:
            return
        self._apply(lo, hi, label)

    def erase(self, lo, hi):
        _check_ints(lo, hi)
        if hi < lo:
            raise SpanError("order", "hi must be >= lo")
        if hi == lo:
            return
        self._apply(lo, hi, None)

    def at(self, pos):
        _check_ints(pos)
        i = bisect_right(self._h, pos)
        if i < len(self._s) and self._s[i][0] <= pos:
            return self._s[i][2]
        return None

    def spans(self):
        return list(self._s)

    def slice(self, lo, hi):
        _check_ints(lo, hi)
        if hi < lo:
            raise SpanError("order", "hi must be >= lo")
        if hi == lo:
            return []
        out = []
        i = bisect_right(self._h, lo)
        while i < len(self._s) and self._s[i][0] < hi:
            a, b, lab = self._s[i]
            out.append((max(a, lo), min(b, hi), lab))
            i += 1
        return out

    def labels(self):
        out = {}
        for a, b, lab in self._s:
            out[lab] = out.get(lab, 0) + (b - a)
        return out

    def covered(self):
        return sum(b - a for a, b, _lab in self._s)

    def checkpoint(self):
        self._stack.append((list(self._s), list(self._h)))

    def rollback(self):
        if not self._stack:
            raise SpanError("no_checkpoint", "no checkpoint outstanding")
        self._s, self._h = self._stack.pop()

    def commit(self):
        if not self._stack:
            raise SpanError("no_checkpoint", "no checkpoint outstanding")
        self._stack.pop()
