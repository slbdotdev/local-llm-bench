# 2026-07 decision record: labels as ordered metadata

Decision D-46: labels are per-entry ordered metadata, merged only for accepted
changes and deduplicated after canonicalization.

The first accepted occurrence creates an output-owned label list. Each later
accepted occurrence scans its labels left to right, removes ASCII edge spaces,
case-folds, discards empty values, and appends only values not already present.
The existing list prefix never moves. A temporary set is permitted for
membership; set iteration is not a permitted output order.

Context: labels were previously thrown away, then a set was proposed as a cheap
replacement. The UI requires stable first-observed ordering and sees labels as
review evidence. Administrative labels must not leak into accepted entries.

Consequences: policy rejection precedes all label work; label lists are copied
into fresh output entries; labels from duplicate accepted keys merge into the
existing entry. Empty labels do not remove an entry or an occurrence.

The label rule is intentionally not the source rule. A tab is preserved in a
label after edge-space removal, while source aliases are exact and sources are
not case-folded. A shared broad-normalization helper is incorrect.
