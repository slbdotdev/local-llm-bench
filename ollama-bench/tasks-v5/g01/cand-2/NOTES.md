# Candidate 2 notes

This candidate stresses precise mechanical execution: first-seen ordering is
independent of lexical order, duplicate keys merge in place, duplicate values
are counted rather than deduplicated, and empty groups/keys remain meaningful.
The likely trap is using sorted grouping or dropping empty groups, both common
when an implementation reaches for a convenient aggregation pattern.

Validation results:

- `python selfcheck.py`: four examples printed `PASS`; exit 0.
- checker with `ref/solution.py`: `SCORE 24/24`, `PASS`, `VERDICT correct`; exit 0.
- checker with the plausible sorting-and-drop-empty near-miss: `SCORE 16/24`,
  `FAIL ['group first appearance order', 'key first appearance order',
  'empty record retained', 'same key separate groups', 'mixed signs and keys',
  'many group returns', 'all empty records', 'full combination']`,
  `VERDICT confidently_wrong`; exit 1.
- checker with an empty sandbox: `SCORE 0/24`,
  `FAIL ['import failed: ModuleNotFoundError', 'not run', 'not run', 'not run',
  'not run', 'not run', 'not run', 'not run', 'not run', 'not run']`,
  `VERDICT visibly_failed`; exit 1.

The reference is 37 lines and 1,306 bytes, roughly 330 Python tokens. No known
uncertainty at authoring time.
