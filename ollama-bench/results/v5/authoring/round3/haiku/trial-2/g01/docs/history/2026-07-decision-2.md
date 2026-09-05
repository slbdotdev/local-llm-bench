# 2026-07 decision record: first-seen positions

Decision D-42: preserve first-seen order independently at source, key, and
label levels.

Context: operators review a live feed, so later pages must not cause an earlier
row to move. Source aliases are common, and duplicate keys arrive on separate
pages. The order chosen for a new identity is the moment the canonical identity
is first accepted, not the moment its final total is known.

Consequences: a source position map identifies canonical source buckets; each
bucket has its own key position map; each entry owns a label list and membership
set. Updates modify the entry at its existing position. Output construction must
not sort maps or recreate an entry during update. Labels are appended only when
their canonical value is new.

Rejected alternatives: lexical ordering, insertion order of raw names before
aliasing, and a global key map. They each fail when aliases merge, when two
sources use the same key, or when an update arrives after a new key.

This decision does not require preserving raw spellings. The emitted source and
key are canonical values, and label values are canonical case-folded strings.
Temporal order and canonical spelling are separate dimensions of the result.
