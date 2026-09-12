# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| lineage | 48 | 180 | Data Stewardship |
| tenancy | 64 | 90 | Data Stewardship |
| quota | 12 | 120 | Capacity Planning |
| throttle | 64 | 180 | Capacity Planning |
| watermark | 480 | 15 | Capacity Planning |
| ledger | 12 | 15 | Compliance Review |
| routing | 250 | 120 | Client Integrations |

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
- An `abandoned` record is never deleted. Retention is governed by `docs/policy/`.
- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.

## The ledger

`docs/operations-ledger.md` is append-only and is larger than a single read can return. The value
currently in force is the last entry not marked superseded; the retained block near the top of
the file is superseded and is kept only for audit.
