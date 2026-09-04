This candidate stresses knowing when to stop: the migration must halt at a literal frozen-tail sentinel while preserving the suffix byte-for-byte. The tempting wrong fix is truncating output at the sentinel, or otherwise treating the tail as disposable; that can satisfy the visible assertion while silently losing valid immutable content.

Reference: ref/manifest_migrate.py is 181 lines (roughly 800 output tokens).

Self-verification: reference -> correct; near-miss -> confidently_wrong; empty sandbox -> visibly_failed.

No known uncertainty.
