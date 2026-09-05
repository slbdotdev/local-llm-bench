# Zero review

Zero appears in three independent places and each has a different semantic
question. A zero delta is still a valid signed integer. A hold has a zero
multiplier but is still an accepted action. An empty label list is still a
valid label value after all labels are discarded. None of these is a reason to
drop a bucket or entry when the surrounding lifecycle says it exists.

Consider an input whose first source record has an add of delta 0 for key err,
then a hold of delta 50 for key warn, then a remove of delta 0 for key err. The
result has error total 0 occurrence 2 and warning total 0 occurrence 1. The
entry order is error then warning. A remove's multiplier applies even when its
delta is zero.

Now put an ignore of delta 0 for key cfg between those changes. It creates no
entry and contributes no occurrence. Put a void with labels between two
accepted duplicates; its labels do not appear in the duplicate's label list.

These cases defeat checks such as `if not delta`, `if multiplier`,
`if contribution`, and `if labels`. The contract distinguishes acceptance,
occurrence, and arithmetic explicitly. A total of zero can have many accepted
occurrences, and an entry with no labels can still be fully valid.
