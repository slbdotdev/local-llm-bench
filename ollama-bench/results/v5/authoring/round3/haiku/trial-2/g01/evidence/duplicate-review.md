# Duplicate update review

Duplicates are identified by canonical source and canonical key. The first
accepted occurrence creates the entry and fixes its position. Every later
accepted occurrence for that identity updates total and occurrences and merges
labels in place. It does not create another entry or move the original.

For source `web`, accepted raw keys arrive as paint, render, DRAW, and
` render `. They all identify frontend/render. If their signed contributions
are 1, 2, -3, and 0, the one entry total is zero and occurrence count is four.
Its labels are the first-seen canonical union across the four changes. An
ignore of paint between any two does not count or add labels.

For source `core`, accepted raw keys compile and build identify platform/build;
an accepted error creates a separate second entry. The later build update stays
ahead of error even if its final total is smaller or zero. A dictionary keyed by
key can hold state, but output must be created at first insertion order or via
an explicit position list.

Duplicate identity is source-local. A service requests entry and a worker jobs
entry are separate even if their raw input keys or labels match. Alias expansion
must happen before the source-local key lookup and before the position lookup.
