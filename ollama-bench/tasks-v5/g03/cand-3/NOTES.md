This candidate makes an optional-looking API change hard: the added keyword-only
`urgent` flag must propagate through wrappers, a default sender, a comprehension, a
reflection string, and an executed doctest. The wrong answer is tempting because all
ordinary calls still work when the new default is false, while urgent behavior silently
disappears; the reflective fallback keeps a stale lookup runnable.

Reference size: 57 lines across `ref/`, about 295 lexical/output tokens. Self-check:
reference -> `SCORE 13/13`, `PASS`, `VERDICT correct`; near-miss (only the getattr
string reverted; fallback keeps it runnable) -> `VERDICT confidently_wrong`; empty sandbox -> `SCORE 0/13`,
`VERDICT visibly_failed`. All came out as intended; no known uncertainty.
