This variant tests following the complete return path and distinguishing deduplication from
ordering. The loop builds first-seen order, but the final set conversion discards that guarantee.
The tempting wrong answer is yes because the loop visibly maintains `seen` and `result`, and a
typical run may appear stable.

Reference solution: 2 lines, roughly 12 output tokens. Self-verification: reference ->
`SCORE 3/3`, `VERDICT correct`; near-miss (yes with the oracle citation) -> `SCORE 2/3`,
`VERDICT confidently_wrong`; empty sandbox -> `SCORE 0/3`, `VERDICT visibly_failed`. All three
were intended. No task uncertainty. The local environment has no `python` alias; checks were run
with `python3`.
