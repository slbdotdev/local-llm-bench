This variant tests resisting the reflex to find a discrepancy: the ASCII/type checks and both
inclusive numeric endpoints really do implement the docstring. The tempting wrong answer is no,
because boundary-validation code often hides an off-by-one error and the target is surrounded by
other helpers with different contracts.

Reference solution: 2 lines, roughly 16 output tokens. Self-verification: reference ->
`SCORE 3/3`, `VERDICT correct`; near-miss (no with the oracle citation) -> `SCORE 2/3`,
`VERDICT confidently_wrong`; empty sandbox -> `SCORE 0/3`, `VERDICT visibly_failed`. All three
were intended. No task uncertainty. The local environment has no `python` alias; checks were run
with `python3`.
