# 2026 policy correction (3.2)

The 3.2 policy review separated acceptance from arithmetic. `ignore` and
`void` are administrative changes and are rejected before key or label
processing. `hold` is different: it is accepted, counts as an occurrence, and
has multiplier zero. This means a hold can create an entry with total zero and
can add labels. A negative raw delta is still a valid signed input; it is not a
signal that an action should be rejected.

Before this correction, the reducer used a truthiness check on the multiplier.
That accidentally discarded holds. A second draft used `if not delta`, which
discarded zero-valued adds and removes. Both bugs are represented in regression
fixtures because they pass common positive-number examples.

Labels are now part of the entry state. They are normalized only after action
acceptance, with ASCII edge-space removal followed by case folding. Empty
canonical labels do not appear. The first canonical spelling wins, and labels
from a later accepted duplicate are appended in their first-seen order. A
rejected change cannot seed or extend an entry's label list.

The policy module returns acceptance and multiplier as separate facts. The
reducer must check acceptance explicitly, then multiply the signed delta. It
must not derive occurrence count from the resulting sum: `hold`, zero deltas,
and cancelling positive/negative contributions all remain countable.

The release team intentionally kept the public shape small: `total`,
`occurrences`, and `labels` are the complete per-key state. No action, raw key,
or source alias is emitted in the result.
