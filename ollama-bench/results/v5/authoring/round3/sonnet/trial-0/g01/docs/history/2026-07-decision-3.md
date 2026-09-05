# 2026-07 decision record: policy before identity

Decision D-43: reject administrative changes before canonical key and label
processing.

Context: replay events contain valid but non-observational `ignore` and `void`
changes. Their raw keys may be aliases and their labels may describe internal
workflow. Treating them as zero-valued observations made administrative data
visible and reserved entry positions that should belong to a later accepted
change.

Consequences: action lookup is the first operation inside a change loop. A
rejected result returns immediately. An accepted result carries a multiplier;
the reducer computes signed contribution, canonicalizes the key, and merges
labels. `hold` is accepted with zero multiplier and follows the accepted path.

Rejected alternatives: filter only after key normalization; count all changes
but add zero for rejected actions; and treat all zero contributions as absent.
The first leaks keys or labels, the second changes counts, and the third drops
holds and zero deltas.

The source bucket exception is explicit in decision D-41. The reducer therefore
has one pre-policy operation per record and no pre-policy operation per change.
