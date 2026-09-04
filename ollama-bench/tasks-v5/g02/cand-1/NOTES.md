This candidate stresses careful reading of scoped, case-insensitive names while preserving value text and layout. The tempting wrong fix is to lowercase the whole document (or to special-case the seeded spelling), which makes the visible assertion pass but corrupts case-sensitive values or misses hidden name variants.

Reference: ref/manifest.py is 220 lines (roughly 1,000 output tokens).

Self-verification: reference -> correct; near-miss -> confidently_wrong; empty sandbox -> visibly_failed.

No known uncertainty.
