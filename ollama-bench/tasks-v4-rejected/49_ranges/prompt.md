Create `ranges.py` in the current directory implementing `RangeSet`, an immutable set of
REAL NUMBERS built out of intervals whose endpoints may be open or closed, or infinite.
Use only the Python standard library (do not import `portion`, `intervaltree`, `sympy`,
`numpy` or any other third-party package).

## The interval representation

An interval is a 4-tuple `(lo, hi, lc, rc)`:

- `lo` is an `int`, or `None` meaning minus infinity.
- `hi` is an `int`, or `None` meaning plus infinity.
- `lc` is a bool: `True` if `lo` is INCLUDED (a `[` bracket), `False` if excluded (`(`).
- `rc` is a bool: `True` if `hi` is INCLUDED (`]`), `False` if excluded (`)`).

The tuple denotes the set of real numbers `x` with `lo < x < hi`, plus `lo` itself if
`lc`, plus `hi` itself if `rc`.  Real numbers, not integers: `(1, 2, False, False)`
denotes the open interval `(1,2)`, which is NOT empty -- it contains `1.5`.

An interval may be EMPTY, and an empty interval simply contributes nothing:

- `(5, 3, True, True)` is empty because `lo > hi`.
- `(2, 2, True, True)` is `[2,2]`, the single point `2` -- NOT empty.
- `(2, 2, True, False)`, `(2, 2, False, True)` and `(2, 2, False, False)` are all empty.

An infinite endpoint is never a member of the set, so when `lo is None` the `lc` flag is
ignored (treat it as `False`), and likewise `rc` when `hi is None`.

## API

```python
class RangeSet:
    def __init__(self, intervals=()) -> None    # the UNION of the given intervals
    def intervals(self) -> list[tuple]          # canonical form (see below)
    def is_empty(self) -> bool
    def contains(self, x) -> bool               # x is an int or a float
    def union(self, other: "RangeSet") -> "RangeSet"
    def intersect(self, other: "RangeSet") -> "RangeSet"
    def difference(self, other: "RangeSet") -> "RangeSet"
    def symmetric_difference(self, other: "RangeSet") -> "RangeSet"
    def complement(self) -> "RangeSet"          # within the universe of ALL reals
    def issubset(self, other: "RangeSet") -> bool
    def measure(self) -> int | float
    def to_string(self) -> str
    def __eq__(self, other) -> bool
```

`__init__` takes any iterable of 4-tuples (lists of 4 items are also acceptable); they may
be given in any order and may overlap, touch, nest or be empty.  The five set operations
return NEW `RangeSet` objects and never mutate their operands.  Every operation is the
ordinary set operation on the underlying sets of reals: `union` is `A | B`, `intersect` is
`A & B`, `difference` is `A - B`, `symmetric_difference` is `(A - B) | (B - A)`, and
`complement` is the set of all reals not in `A`.  `issubset(other)` is `True` iff every
real in `A` is also in `other` (so the empty set is a subset of everything, and every set
is a subset of itself).  `contains(x)` is `True` iff the real number `x` is in the set.

## Canonical form

`intervals()` returns the UNIQUE minimal representation of the underlying set of reals:
a list of non-empty intervals, sorted by position, pairwise disjoint, and such that no two
of them could be replaced by a single interval.  Two intervals must therefore be combined
whenever their union is itself an interval -- not only when they overlap, but also when
one ends exactly where the other begins with the shared endpoint belonging to at least one
of them.  A gap of even a single missing point keeps them apart.  The empty set gives `[]`.

Because the form is canonical, two `RangeSet`s are `==` exactly when they denote the same
set of reals, i.e. exactly when their `intervals()` lists are equal.  Comparing a
`RangeSet` with a non-`RangeSet` must return `NotImplemented` (so that `==` against, say,
an `int` evaluates to `False` rather than raising).

`measure()` is the total length: the sum of `hi - lo` over the canonical intervals,
returned as an `int` if the set is bounded, or `float('inf')` if it is unbounded.  Whether
endpoints are open or closed does not change the length.

`to_string()` renders the canonical form as `"{}"` for the empty set, otherwise as the
interval strings joined by `" U "` (space, capital U, space).  Each interval is
`"[lo,hi]"` with `[`/`(` and `]`/`)` chosen by `lc`/`rc`, no spaces, and with the literal
text `-inf` / `+inf` for infinite endpoints (always with a round bracket), e.g.
`"(-inf,3]"`, `"[0,0]"`, `"(2,+inf)"`.

## Examples

```python
RangeSet([(1, 5, True, False)]).intervals() == [(1, 5, True, False)]

a = RangeSet([(0, 3, True, True), (5, 7, True, False)])
a.to_string() == "[0,3] U [5,7)"
a.measure() == 5

b = RangeSet([(0, 10, True, True)])
b.intersect(RangeSet([(4, 20, True, False)])).to_string() == "[4,10]"
b.difference(RangeSet([(3, 5, True, True)])).to_string() == "[0,3) U (5,10]"
b.complement().to_string() == "(-inf,0) U (10,+inf)"
b.contains(10) and not b.contains(10.5)

RangeSet([(0, None, True, True)]).to_string() == "[0,+inf)"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
