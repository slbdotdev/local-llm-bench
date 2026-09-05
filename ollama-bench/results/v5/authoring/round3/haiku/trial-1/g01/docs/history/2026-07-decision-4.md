# 2026-07 decision record: canonicalization order

Decision D-44: use field-specific normalization and one-step alias tables.

Source names remove ASCII spaces at both edges and then perform exact alias
lookup. They are not case-folded. Keys remove ASCII spaces, case-fold, perform
one global alias lookup, then perform one lookup in the table belonging to the
canonical source. Labels remove ASCII spaces and case-fold, with no alias table.

Context: broad Python whitespace removal changed identifiers containing tabs,
and recursive alias lookup made a newly configured target unexpectedly redirect
again. The current order is simple enough to test independently and matches all
three importer families.

Consequences: unknown values survive their field-specific normalization. Empty
canonical source and key are valid strings. Empty canonical labels are omitted.
Interior spaces and tabs remain data. The canonical source is used both in the
outer result and as the scope of source-specific key aliases.

Rejected alternatives: a shared `.strip()` helper, lowercasing source names,
and repeated lookup until no alias matches. These are common normalization
conventions but are not Relay 3.2 behavior.
