# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| drain | 24 | 60 | Compliance Review |
| quota | 24 | 15 | Delivery Engineering |
| ingest | 64 | 120 | Compliance Review |
| backfill | 12 | 90 | Capacity Planning |
| attestation | 120 | 120 | Platform Reliability |
| checkpoint | 480 | 120 | Compliance Review |

## Restart procedure

1. Seal in reverse manifest order (`docs/architecture.md`).
2. Take a `snapshot()` of every stage and write it to the evidence store **before**
   anything is restarted. A snapshot taken afterwards is not evidence.
3. Restart the assembler, not the individual stages.
4. Compare the new snapshot against the old one. Any record that changed state without
   passing through `pending` is a defect and is reported rather than corrected.

## What never happens in flight

- A limit is never changed while the pipeline is running. It is changed in the
  manifest and takes effect on the next assembly.
- An `abandoned` record is never deleted. Retention is governed by `docs/standards/`.
- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.

## Working through a batch of refusals

On-call works a batch **by stage, in the order the pipeline assembles them**, because that is
the order a record actually met the stages in and because a stage's owner wants that stage's
refusals together in front of them. Every record that raises a refusal is worked once, and a
record that raises three is worked three times.

That is a triage order. It is not the order the quarterly refusal report puts its findings in,
and the two have been confused at least once. The report's order is settled by the reporting
standard under `docs/standards/`, which outranks this page; the revision of it that is in
force is the one to apply, and superseded and withdrawn revisions are kept on that page as
evidence rather than as instructions.
