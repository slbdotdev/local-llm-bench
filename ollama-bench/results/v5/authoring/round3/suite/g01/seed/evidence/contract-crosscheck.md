# Contract cross-check across project sources

The release manager compared the project sources by concern. This record is a
map for the reviewer who must reconcile them.

Source identity is stated by the source stage, JSON source table, importer
notes, and compatibility matrix. All agree on ASCII-space edge removal, exact
lookup, six aliases, and one-step behavior. The old history is the only source
that says to sort or case-fold sources; it is explicitly superseded.

Key identity is stated by the key stage, JSON key table, frontend/platform
reviews, and regression ledger. All agree on ASCII spaces, casefold, global
lookup, canonical-source lookup, and no recursive lookup. The ordering of
source-specific lookup is repeated because it matters for alias targets.

Policy is stated by the action table, policy stage, replay notes, and numeric
review. All agree on four accepted actions, two rejected actions, signed
multiplication, and accepted zero contributions. The 2024 history is the only
source that counts administrative changes; it describes the old adapter.

Labels are stated by the label stage, label review, callers, and freshness
review. All agree on accepted-only processing, ASCII-space trim, casefold,
empty discard, first-seen uniqueness, and fresh output lists.

Shape and order are stated by models, output stage, UI caller notes, and the
long mixed replay. All agree on exact field sets, first-seen bucket order,
first-accepted key order, in-place conceptual updates, and no private fields.
This cross-check is why the task requires reading the complete supplied tree:
the current answer is the intersection of these sources, not a historical
snippet selected by filename.
