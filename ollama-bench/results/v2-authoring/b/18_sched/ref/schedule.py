"""Reference: weighted interval scheduling on half-open intervals with exact
tie-breaking (max weight, then fewest jobs, then lexicographically smallest
sorted id list)."""
from bisect import bisect_right, insort


def select(jobs):
    # Jobs with weight <= 0 are never part of any answer: the empty schedule is
    # always feasible, a weight-0 job adds nothing while increasing the count,
    # and a negative-weight job strictly lowers the total.
    # A zero-length job (start == end) conflicts with nothing, so every
    # zero-length job with positive weight is always chosen.
    forced = sorted(j[0] for j in jobs if j[1] == j[2] and j[3] > 0)
    cands = sorted(
        (j for j in jobs if j[1] < j[2] and j[3] > 0),
        key=lambda j: (j[2], j[0]),
    )
    ends = [j[2] for j in cands]
    # best[i] = optimal (weight, count, sorted_id_tuple) using only the first i
    # candidates, compared by (-weight, count, ids).
    best = [(0, 0, ())]
    for i, (jid, s, e, w) in enumerate(cands):
        p = bisect_right(ends, s, 0, i)  # jobs among the first i with end <= s
        w0, c0, ids0 = best[p]
        take = (w0 + w, c0 + 1, _insert(ids0, jid))
        skip = best[i]
        best.append(min(take, skip, key=lambda t: (-t[0], t[1], t[2])))
    chosen = list(best[-1][2])
    for jid in forced:
        insort(chosen, jid)
    return chosen


def _insert(ids, x):
    i = bisect_right(ids, x)
    return ids[:i] + (x,) + ids[i:]