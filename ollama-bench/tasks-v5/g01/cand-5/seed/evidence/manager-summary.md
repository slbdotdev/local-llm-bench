# Manager summary of the 3.2 adapter

The benchmark variant uses Relay Ledger because the public computation is
small but the evidence is distributed across a substantial real-shaped code
and review tree. The solver must hold source aliases, source-local key aliases,
action policy, signed arithmetic, label state, position state, and ownership
requirements together. The current answer is a left-to-right fold with five
dependent stages.

The outer result is a list of fresh buckets. A record first canonicalizes its
source using ASCII-space trimming and exact one-step source alias lookup. That
bucket exists even if no change is accepted. For each change, policy accepts
add, remove, adjust, and hold, with multipliers 1, -1, 1, and 0. Ignore and
void are rejected. Rejection occurs before key or label state.

An accepted key is trimmed of ASCII edge spaces, case-folded, mapped once by
the global key table, and mapped once by the table for the canonical source.
It creates or updates an entry in first accepted identity order. Total receives
signed delta times multiplier and occurrences increases once for every accepted
change, including zero contribution. Labels are trimmed of ASCII edge spaces,
case-folded, empty values are discarded, and new canonical values append in
first-seen order. Rejected labels are absent.

The result exposes exactly source and entries at bucket level, and key, total,
occurrences, and labels at entry level. No raw fields or private state appears.
All mutable containers are fresh and the input is unchanged. Outer, inner, and
label order are temporal first-seen order, not lexical order.

The historical sources describe the old sort, broad-whitespace, raw-sum,
all-action-count, label-dropping, and empty-dropping behaviors so that a
plausible implementation can be confidently wrong. The current sources repeat
the corrected behavior from independent importer and reviewer perspectives.
The task has no malformed-input or runtime-file requirement; a short standard
library implementation is the intended reference.
