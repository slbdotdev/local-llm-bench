# 2025-03 ordering decision

The snapshot group proposed lexical ordering after alias expansion. The import
team rejected it after observing that a later alias could move an already
displayed source and make review notes point at the wrong row. Release 3.0
therefore made first canonical source appearance the outer order and first
accepted canonical key appearance the inner order.

“Accepted” is important in the inner rule. A rejected administrative change
does not reserve a key position. If the same key later arrives as an add, that
add creates the first entry at that later point. In contrast, a record always
reserves a source bucket before its changes are filtered.

Updates are in place conceptually. If keys arrive as `b`, `a`, `b`, the output
is `b`, `a`, with the first total and occurrence count updated. The result must
not be reconstructed by sorting the finished entries or by deleting and
re-inserting a duplicate.

The decision was copied into UI, replay, and export reviews. Those secondary
references are included so that an implementation that reads only the reducer
can still be checked against the behavior users observe.
