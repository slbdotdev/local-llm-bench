# Sequence review: why each stage feeds the next

This review uses one canonical source and one key so that ordering mistakes
cannot hide behind aliasing. Start with a record for ` core ` containing a void
` compile ` change with label `Old`; then an empty `platform` record; then a
record containing a hold `compile` delta 0 with label `New`; then an add
`build` delta 4 with label ` new `; then a remove `compilation` delta -2 with
label `Done`.

The first record ensures platform but its void is rejected before key and label
work. The empty record finds platform and changes nothing. The hold is the
first accepted key after canonicalization, so it creates build with total zero,
occurrence one, and label new. The add is the second accepted occurrence and
raises total to four, occurrence two; its canonical label is already present.
The remove is the third occurrence and contributes +2, raising total to six and
appending done.

The final result has one platform bucket, one build entry, total six,
occurrences three, and labels `["new", "done"]`. It has no old label from the
void. This is a compact example of all stage dependencies: lifecycle before
policy, policy before identity, source before local alias, arithmetic before
count/merge, and stable positions throughout.

Changing any one stage can produce a plausible tree. Sorting might preserve
the single-key result here but fails when a second key is inserted. Counting
nonzero amounts fails the hold. Normalizing labels before policy exposes old.
Using raw source for local lookup fails when the source alias is used. The
cross-source reviews provide the corresponding multi-bucket cases.
