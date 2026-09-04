This candidate makes completeness hard through a late import cycle, a default callable,
an indirect `getattr` lookup, a comprehension, and an executed doctest. The tempting
wrong answer updates direct calls and the definition but leaves the reflected string;
the supplied fallback keeps that mistake runnable and plausible.
The checker scans only the three named application modules, so unrelated padding cannot
be a false straggler.

Reference size: 56 lines across `ref/`, about 230 lexical/output tokens. Self-check:
reference -> `SCORE 12/12`, `PASS`, `VERDICT correct`; near-miss (only the getattr
string reverted; fallback keeps it runnable) -> `VERDICT confidently_wrong`; empty sandbox -> `SCORE 0/12`,
`VERDICT visibly_failed`. All came out as intended; no known uncertainty.
