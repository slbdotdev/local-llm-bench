# Final audit before the 3.2 benchmark handoff

The final audit re-ran the complete release material as a checklist rather than
adding new behavior. It first compared source identity across the importer
reviews, then key and label identity across the normalization records, then
policy and arithmetic across replay records, and finally order, shape, and
ownership across UI and serialization reviews.

The audit's source questions were: are ordinary edge spaces removed; are tabs
retained; are aliases exact, case-sensitive, and one-step; do aliases merge
positions; and does an empty or rejected-only record create a bucket? Its key
questions were: is casefold after edge-space trim; is global lookup before local
lookup; is the local table selected by canonical source; and is a rejected key
ignored before identity?

Its policy questions were: are exactly four actions accepted; are ignore and
void absent; does hold count despite zero multiplier; are signed deltas
multiplied; and are zero deltas counted? Its label questions were: are labels
accepted-only; are empty canonical labels discarded; is first canonical
appearance retained; and are lists output-owned?

Its output questions were: are source, entry, and label orders first-seen; are
updates in place; are exact field sets emitted; are empty values retained; are
integers preserved; and is the input unchanged? All answers are fixed by the
current package and release evidence. The old historical behavior is included
only as a clearly marked explanation of plausible failures.

The audit found no malformed-input requirement, no runtime file dependency, and
no nondeterministic step. A short standard-library implementation can therefore
inline the current tables and ordered fold while the model must still read and
reconcile the full material to avoid the adjacent historical answers.
