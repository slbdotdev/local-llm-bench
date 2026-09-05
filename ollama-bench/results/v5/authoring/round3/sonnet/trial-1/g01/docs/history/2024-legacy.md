# 2024 adapter notes (2.x)

The first Relay importer treated source and key names as opaque strings. It
grouped by the spelling in each record and sorted both the outer groups and
inner keys before emitting JSON. That was convenient for snapshot diffs but
made a stream's arrival order disappear. It also used `str.strip()` for all
fields, which made tabs and newlines impossible to preserve.

The old implementation counted every change, including the two administrative
actions that were then called `ignore` and `void`. It summed raw deltas and
discarded labels as an import-time optimization. Empty source records were
dropped because the old output represented only nonempty counters.

This file is retained because several migration fixtures use old source names
and because a straightforward rewrite from the 2.x snapshot code looks very
reasonable on ordinary data. None of its sort, broad-whitespace, raw-sum, or
empty-bucket rules are current. The compatibility layer translates names only;
it does not restore the old semantics.

The 2.x examples were useful for identifying accidental behavior:

* `core` and `platform` appeared as separate groups in a legacy snapshot.
* `WARN` and `warn` were separate keys.
* a `void` change still increased the old count.
* a source containing only rejected changes did not appear at all.

Release 3.0 began the correction, and release 3.2 completed it. When this
history conflicts with a current module or release configuration, this history
is the superseded side of the conflict.
