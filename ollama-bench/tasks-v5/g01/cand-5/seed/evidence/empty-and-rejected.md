# Empty and rejected record review

The empty/rejected review isolates lifecycle from accumulation. Every record in
the first sequence has a valid source and a changes list, but not every change
is an observation.

* `{"source": "svc", "changes": []}` creates service with no entries.
* `{"source": "core", "changes": [{"action": "void"}]}` creates platform
  with no entries, assuming the other valid fields are present.
* A later `platform` record with a rejected `ignore` does not create a second
  platform bucket.
* A later `platform` record with an accepted hold creates the first entry at
  that point, even if the hold delta is zero.
* An empty record for a source already present does not reset totals, labels, or
  positions.
* An empty input returns an empty list and does not share that list with a
  later call.

The distinction is visible in operations dashboards: a bucket means the source
was present in the batch, while an entry means at least one accepted change for
that canonical key was observed. An implementation that filters records before
folding cannot preserve the distinction.

Rejected changes are also deliberately interspersed with accepted changes. A
rejected key does not reserve an inner position, and rejected labels do not
enter the label list. Rejection is not a zero contribution: a hold is zero but
accepted, whereas ignore and void are absent observations.
