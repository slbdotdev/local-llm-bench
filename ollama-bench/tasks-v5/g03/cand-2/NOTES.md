This candidate makes the semantic argument-order migration hard: the renamed callable
flows through a default argument, a comprehension, a reflective lookup, and two wrapper
layers. The wrong answer is tempting because a renamed function with the old order still
runs and produces plausible-looking brackets until asymmetric cases are checked; the
fallback keeps a stale reflection runnable.

Reference size: 56 lines across `ref/`, about 270 lexical/output tokens. Self-check:
reference -> `SCORE 12/12`, `PASS`, `VERDICT correct`; near-miss (only the getattr
string reverted; fallback keeps it runnable) -> `VERDICT confidently_wrong`; empty sandbox -> `SCORE 0/12`,
`VERDICT visibly_failed`. All came out as intended; no known uncertainty.
