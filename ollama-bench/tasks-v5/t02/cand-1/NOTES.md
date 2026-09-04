This variant tests careful boundary reading and exact evidence: `stop` is documented as
exclusive, but the loop uses `stop + 1`. The tempting wrong answer is yes because the docstring
states a familiar half-open range and the rest of the filtering logic looks correct.

Reference solution: 2 lines, roughly 15 output tokens. Self-verification: reference ->
`SCORE 3/3`, `VERDICT correct`; near-miss (yes with the oracle citation) -> `SCORE 2/3`,
`VERDICT confidently_wrong`; empty sandbox -> `SCORE 0/3`, `VERDICT visibly_failed`. All three
were intended. No task uncertainty. The local environment has no `python` alias; checks were run
with `python3`.
