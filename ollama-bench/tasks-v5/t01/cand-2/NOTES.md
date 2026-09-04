This candidate makes precise mechanical execution hard: nested paths must be sorted correctly,
and near-match filenames and directories are decoys. The tempting wrong answer is a global text
replacement, which treats the two archived records as stale code references.

Reference solution: 9 lines, roughly 120 output tokens (including the short Python writer).

Self-verification:

- format example: PASS
- reference -> correct: PASS (`SCORE 8/8`, `PASS`, `VERDICT correct`)
- near-miss -> confidently_wrong: PASS (`VERDICT confidently_wrong`)
- empty sandbox -> visibly_failed: PASS (`VERDICT visibly_failed`)

Uncertainty: none known; the strict parser intentionally makes wrong coordinates or malformed
fields a visible failure, while a complete all-UPDATE audit is scored as confidently wrong.
