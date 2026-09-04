This candidate stresses mechanical precision in a token-preserving source transformation. The visible failure is a `from ... import ...` rewrite; a global string replacement is tempting because it fixes that line, but corrupts comments and strings and rewrites prefix lookalikes.

Reference: ref/imports.py is 216 lines (roughly 1,150 output tokens).

Self-verification: reference -> correct; near-miss -> confidently_wrong; empty sandbox -> visibly_failed.

No known uncertainty.
