Purpose: stresses following a request through session lookup and distinguishing the real response branch from a similarly named authentication helper and a malformed-cookie cleanup path.

Trap: `auth.py` has an expiry-related helper and `cookies.py` emits the same cookie-clearing header, so a plausible wrong citation can combine or select those near-misses.

Self-verification: reference -> correct; near-miss (`auth.py`, lines 1-3) -> confidently_wrong; empty sandbox -> visibly_failed. All three were observed with the checker.

Reference size: 3 lines, roughly 27 output tokens.

Uncertainty: none known.
