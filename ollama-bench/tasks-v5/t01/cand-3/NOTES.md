This candidate makes knowing when to stop hard: archived quotations and dated move notes are
deliberately readable and look like stale live links, but they are audit evidence. The tempting
wrong answer is to update every occurrence after a successful-looking sweep.

Reference solution: 9 lines, roughly 120 output tokens (including the short Python writer).

Self-verification:

- format example: PASS
- reference -> correct: PASS (`SCORE 8/8`, `PASS`, `VERDICT correct`)
- near-miss -> confidently_wrong: PASS (`VERDICT confidently_wrong`)
- empty sandbox -> visibly_failed: PASS (`VERDICT visibly_failed`)

Uncertainty: none known; the parser accepts the double-slash path as a path value but still
requires exact tab-separated fields and exact source coordinates.
