Create `spanmap.py` implementing an interval "paint" map: a class `SpanMap` plus an
exception `class SpanError(ValueError)`.

All coordinates are integers (negatives allowed) and every interval is half-open:
`[lo, hi)` covers the positions `lo, lo+1, ..., hi-1`.

```python
class SpanError(ValueError): ...        # has an attribute .kind (a str)

class SpanMap:
    def __init__(self) -> None: ...                     # empty map
    def paint(self, lo: int, hi: int, label: str) -> None
    def erase(self, lo: int, hi: int) -> None
    def at(self, pos: int) -> str | None
    def spans(self) -> list[tuple[int, int, str]]
    def slice(self, lo: int, hi: int) -> list[tuple[int, int, str]]
    def labels(self) -> dict[str, int]
    def covered(self) -> int
    def checkpoint(self) -> None
    def rollback(self) -> None
    def commit(self) -> None
```

Model rules:
1. Think of the map as an (infinite) array of positions, each holding a label or nothing.
   `paint(lo, hi, label)` sets every position in `[lo, hi)` to `label`, overwriting whatever
   was there: a later paint always wins over an earlier one everywhere the two overlap.
   `erase(lo, hi)` clears every position in `[lo, hi)`.
2. `at(pos)` returns the label at `pos`, or `None` if that position is not covered.
   Because intervals are half-open, after `paint(0, 10, "a")` we have `at(9) == "a"` and
   `at(10) is None`.
3. `spans()` returns the CANONICAL list of spans as `(lo, hi, label)` tuples:
   sorted by `lo` ascending, no zero-length span, no two spans overlapping, and no two
   ADJACENT spans (where the `hi` of one equals the `lo` of the next) carrying the same
   label -- those must be merged into a single span. The canonical form is unique, so
   two maps holding the same positions/labels always give the same `spans()` list.
4. `slice(lo, hi)` returns the canonical spans clipped to `[lo, hi)`: only the parts that
   fall inside the window, with the same guarantees as rule 3. It returns `[]` if the
   window is empty or covers nothing. It does not modify the map.
5. `labels()` returns a dict mapping each label to the total number of positions it covers.
   Labels covering nothing are not in the dict; `{}` for an empty map. Key order does not
   matter. `covered()` returns the total number of covered positions (an int).
6. `checkpoint()` pushes a snapshot of the current state on a stack. `rollback()` pops the
   most recent snapshot and restores the state exactly as it was when that `checkpoint()`
   was called. `commit()` pops the most recent snapshot WITHOUT restoring, so the work done
   since that checkpoint becomes permanent. Checkpoints nest arbitrarily deep: after a
   `rollback()` or `commit()`, the next one applies to the next-outer checkpoint. The map
   must keep working normally after a rollback (further paints/erases behave as if the
   restored state had been built directly).
7. `hi == lo` is NOT an error: `paint(lo, lo, label)` and `erase(lo, lo)` are no-ops and
   must never create a zero-length span; `slice(lo, lo)` returns `[]`.

Errors -- every failure raises `SpanError` with `.kind` set to one of the strings below.
The checks are made in exactly this order and the FIRST one that fails decides the kind:
1. `"type"`  -- any of `lo`, `hi`, `pos` is not an `int`, or is a `bool` (`bool` is a
   subclass of `int` and must be REJECTED), or `label` is not a `str`.
2. `"label"` -- `label` is the empty string `""`.
3. `"order"` -- `hi < lo`.
4. `"no_checkpoint"` -- `rollback()` or `commit()` called with no checkpoint outstanding.
Because of the stated order, `paint(5, 1, "")` raises kind `"label"` (not `"order"`), and
`paint("a", 1, "")` raises kind `"type"`. `paint` checks all of `lo`, `hi` and `label` at
step 1 before moving on. `at`, `erase` and `slice` have no `label` argument, so they skip
step 2. No other operation raises.

Performance requirement: 200,000 `paint` calls followed by one `spans()` call must finish
in well under 5 seconds, for a map that grows to well over 100,000 spans. Rescanning or
rebuilding the whole span list on every operation is too slow; keep the spans sorted and
locate the affected range with `bisect`. Per-position storage (one entry per integer
coordinate) is also too slow -- coordinates can be spread over hundreds of millions.

Worked examples (shown as Python literals):
```python
m = SpanMap()
m.paint(0, 10, "a"); m.paint(3, 5, "b")
m.spans() == [(0, 3, "a"), (3, 5, "b"), (5, 10, "a")]   # painting inside SPLITS a span
m.paint(3, 5, "a")
m.spans() == [(0, 10, "a")]                             # the three pieces re-MERGE
m.erase(4, 6)
m.spans() == [(0, 4, "a"), (6, 10, "a")]                # erasing inside splits too
m.slice(3, 7) == [(3, 4, "a"), (6, 7, "a")]
m.labels() == {"a": 8}
m.covered() == 8

n = SpanMap()
n.paint(0, 5, "a"); n.paint(5, 10, "a")
n.spans() == [(0, 10, "a")]                             # adjacent equal labels merge
n.paint(2, 8, "b"); n.paint(4, 12, "c")
n.spans() == [(0, 2, "a"), (2, 4, "b"), (4, 12, "c")]
n.slice(3, 5) == [(3, 4, "b"), (4, 5, "c")]
n.at(1) == "a" and n.at(12) is None

k = SpanMap(); k.paint(0, 10, "a")
k.checkpoint(); k.paint(2, 4, "b")
k.checkpoint(); k.erase(0, 10)
k.spans() == []
k.rollback(); k.spans() == [(0, 2, "a"), (2, 4, "b"), (4, 10, "a")]
k.rollback(); k.spans() == [(0, 10, "a")]

c = SpanMap(); c.paint(0, 4, "a")
c.checkpoint(); c.paint(4, 8, "b"); c.commit()
c.spans() == [(0, 4, "a"), (4, 8, "b")]                 # commit keeps the change
```

Write a few quick checks of your own and run them with `python`, then reply "done".
