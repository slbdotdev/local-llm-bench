# Whole-contract walkthrough

A complete transformation of one valid batch can be reviewed as a fixed walk.
For each record, canonicalize the source and ensure a fresh bucket if needed.
For each change in the given order, check the action table. If rejected, skip
the rest of that change. If accepted, multiply the signed delta, canonicalize
the key using the canonical source, and locate or create the entry. On create,
copy the canonical nonempty labels into a fresh list and set occurrence one.
On update, add the amount, increment occurrence, and append new canonical
labels. Continue without sorting and return only the public tree.

The walk explains why the project has separate modules even though a solution
can inline them. Sources establish outer identity; actions establish whether a
change is observable; keys establish inner identity; arithmetic establishes
total and occurrence; labels establish ordered metadata; output establishes
ownership and shape.

The walk also gives a checklist for combined cases. An empty record stops after
source ensure. A rejected-only record does the same. A hold continues through
all accepted stages even when amount is zero. A negative remove continues with a
positive contribution when multiplication yields one. A duplicate continues
without changing position. A zero label list changes neither acceptance nor
occurrence.

The current release has no hidden exception to this walk. The only historical
exceptions are deliberately marked as old: lexical sorting, broad whitespace,
raw arithmetic, counting administrative changes, dropping empty buckets, and
discarding labels. They are included as plausible implementation traps and are
not part of the answer.
