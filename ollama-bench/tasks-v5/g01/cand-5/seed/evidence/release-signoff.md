# Release sign-off record

Release 3.2 was signed off by the importer, operations replay, UI, and data
ownership reviewers. The importer reviewer confirmed that source aliases and
field normalization are exact and field-specific. The replay reviewer
confirmed that rejection occurs before key and label state while source bucket
lifecycle occurs before rejection. The UI reviewer confirmed first-seen order,
zero-total visibility, canonical labels, and exact public fields. The ownership
reviewer confirmed fresh nested containers and unchanged inputs.

The sign-off batch begins with an empty service record, follows with a rejected
platform record, then accepted aliases for service, platform, frontend, and
worker, with duplicates and source-only pages interspersed. It includes an
empty source, empty key, empty labels, tabs, signed removes, holds, zero adds,
and large integer totals. The batch was also replayed with page boundaries at
every possible position; flattening before the fold did not change the result.

The release manager rejected a final cleanup that would sort output keys and a
final optimization that would discard empty buckets. Both would preserve some
totals while violating live-review semantics. The manager also rejected using
the old 2.x broad-strip and raw-count behavior for compatibility. Compatibility
means accepting old names under current aliases, not restoring old output.

The final implementation target remains deliberately compact. The extensive
material documents independent evidence and historical traps; it does not add
runtime dependencies. A solver should derive the tables and five-stage order,
then implement the fresh public tree with standard Python only.
