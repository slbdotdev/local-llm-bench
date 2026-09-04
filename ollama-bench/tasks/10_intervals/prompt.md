Create `intervals.py` in the current directory. Intervals are closed integer ranges given as `(start, end)` tuples with `start <= end`.

- `merge(intervals) -> list[tuple[int, int]]`: return the minimal sorted list of disjoint intervals covering the same integers. Overlapping AND adjacent intervals merge: `(1, 3)` and `(4, 6)` become `(1, 6)` because 3 and 4 are consecutive integers, but `(1, 3)` and `(5, 6)` stay separate. Input may be unsorted and must not be mutated. Empty input -> `[]`.
- `insert(intervals, new) -> list[tuple[int, int]]`: `intervals` is already merged and sorted; return the merged result after adding `new`.
- `total_length(intervals) -> int`: number of distinct integers covered, e.g. `total_length([(1, 3), (3, 4), (10, 10)]) == 5`.
- Raise `ValueError` for any interval with `start > end`.

Write a few quick checks of your own and run them with `python`, then reply "done".
