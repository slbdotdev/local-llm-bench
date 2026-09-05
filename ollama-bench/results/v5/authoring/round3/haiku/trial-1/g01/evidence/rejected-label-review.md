# Rejected-label review

The operations exporter attaches labels before it knows whether an action will
be accepted. The adapter must not copy those labels merely because they are
present in a valid change dictionary. Acceptance is the gate for all key state:
entry creation, amount, occurrences, and labels.

Case R-1 sends void error delta 7 with labels `Escalate` and `Owner`, then add
error delta 1 with labels `Owner` and `Triage`. The result is one error entry,
total 1, occurrence 1, labels `["owner", "triage"]`. Escalate is absent and
Owner appears from the accepted change, not from the void.

Case R-2 sends ignore cfg delta 4 with label `Config`, then hold cfg delta -9
with a space-only label. The result has config total 0, occurrence 1, and an
empty labels list. The ignored label is absent, while the hold is accepted even
with a label list that canonicalizes to empty.

Case R-3 sends a void key that would be a source-local alias, followed by an
accepted raw alias for another key. The void does not reserve inner order. This
is why policy must precede key canonicalization, even though source
canonicalization already happened for bucket lifecycle.

No action-specific labels are emitted. The public entry has only its canonical
key, weighted total, accepted count, and accepted canonical labels.
