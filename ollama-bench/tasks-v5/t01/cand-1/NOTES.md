This candidate makes careful semantic reading hard: two current pointers look like the two
dated records, and the tempting wrong answer is to replace every old path found by a sweep.
The historical entries explicitly describe the former location, so changing them damages the
record.

Reference solution: 9 lines, roughly 120 output tokens (including the short Python writer).

Self-verification:

- format example: PASS
- reference -> correct: PASS (`SCORE 8/8`, `PASS`, `VERDICT correct`)
- near-miss -> confidently_wrong: PASS (`VERDICT confidently_wrong`)
- empty sandbox -> visibly_failed: PASS (`VERDICT visibly_failed`)

Uncertainty: none known; the checker intentionally treats any complete, syntactically valid but
wrong classification as confidently wrong, while missing or malformed output is visibly failed.
