# 2026-07 decision record: public shape and ownership

Decision D-47: return only the documented JSON-like tree and own its mutable
containers.

Buckets have source and entries. Entries have key, total, occurrences, and
labels. Position maps and policy facts are reducer state, not output fields.
Every returned list and dictionary is new; label lists are copied and then
updated only in output state. Caller input is read-only from the adapter's point
of view even though Python does not enforce that convention.

Context: returning input records was fast and passed equality checks. It failed
when a caller mutated a result after the call. A shallow copy fixed some cases
but still shared the nested changes or labels lists. The release review added
deep ownership probes.

Consequences: empty buckets, empty entries lists, empty labels lists, zero
totals, and zero occurrences are represented by their ordinary fields. No
truthiness shortcut may remove them. Equal results from repeated calls are
independent trees.

The benchmark compares Python values directly, so this decision is about actual
types and nested ownership, not merely JSON serialization output.
