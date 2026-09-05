# Acceptance matrix with observable state

The action matrix is reviewed not only for arithmetic but for every observable
state column. An accepted add, remove, adjust, or hold can create an entry;
increments occurrences; contributes its signed delta times multiplier; and
merges canonical labels. A rejected ignore or void does none of those things.

For add, delta 4 yields amount 4, count one. For remove, delta 4 yields -4,
count one. For adjust, delta -4 yields -4, count one. For hold, delta 4 yields
0, count one. Repeat each with an empty label list and the count and amount are
unchanged. Repeat each with a zero delta and the action remains accepted.

An action's acceptance is not a property of its resulting amount. Hold and a
zero-valued accepted action have amount zero but are observations. Ignore and
void are absent observations even if a hypothetical multiplier of zero would
make their amount look similar. This is why the reducer receives an explicit
policy decision rather than testing a computed integer.

The matrix also clarifies source lifecycle. The record is ensured before any
row of this matrix is consulted. Thus a source with six rejected actions has a
bucket and no entries, while a source with one hold has a bucket and one zero
entry. A later accepted change uses first accepted position, not first rejected
position.

The output never records the action or multiplier. Those are intermediate facts
used only to update total and occurrences.
