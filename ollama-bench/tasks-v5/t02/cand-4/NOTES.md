This variant tests complete branch tracing rather than spotting a simple off-by-one. The
string/string branch correctly uses case-insensitive comparison, but the other branch converts
both values to text even though the docstring requires direct `==` and explicitly forbids
coercion. The tempting wrong answer is yes because the normal string path is correct and the
fallback still looks like a reasonable case-insensitive matcher.

Reference solution: 2 lines, roughly 20 output tokens. Self-verification: reference -> `SCORE
3/3`, `VERDICT correct`; near-miss (yes with the oracle citation) -> `SCORE 2/3`, `VERDICT
confidently_wrong`; empty sandbox -> `SCORE 0/3`, `VERDICT visibly_failed`. All three were
intended. No task uncertainty. The local environment has no `python` alias; checks were run
with `python3`.
