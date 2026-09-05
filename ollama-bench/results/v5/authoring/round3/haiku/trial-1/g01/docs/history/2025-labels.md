# 2025-07 label design

Labels were added after operators asked why two occurrences of one key could
not be distinguished in a review. They are metadata on the canonical key, not
independent output entries. Labels from the first accepted occurrence seed the
list. A later accepted occurrence can append new canonical labels, but cannot
reorder labels already present.

Canonicalization happens before membership testing. Thus `Owner`, ` owner `,
and `owner` are one label, and the first one contributes `owner` at its first
position. An edge-only-space label becomes empty and disappears. A tab is not
an edge space; a label containing a tab can remain a nonempty canonical value.

The policy gate precedes this operation. A rejected change's labels are not
observed, even if a later accepted occurrence uses the same key. This prevents
administrative annotations from becoming visible as operational evidence.

The label list is ordered data. A set can be used temporarily for membership,
but its iteration order must never determine the result. The output list is
fresh, and the input `labels` list is never modified.
