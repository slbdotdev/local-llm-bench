# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| quota | 96 | 180 | Data Stewardship |
| tenancy | 120 | 30 | Compliance Review |
| dispatch | 96 | 45 | Delivery Engineering |
| attestation | 96 | 180 | Data Stewardship |
| compaction | 24 | 90 | Delivery Engineering |
| ledger | 48 | 30 | Data Stewardship |
| cursor | 12 | 60 | Platform Reliability |
| lineage | 480 | 30 | Compliance Review |
| retention | 120 | 30 | Compliance Review |
| throttle | 64 | 45 | Compliance Review |
| checkpoint | 96 | 45 | Data Stewardship |
| reconcile | 48 | 180 | Data Stewardship |
| shard | 250 | 180 | Compliance Review |
| backfill | 24 | 15 | Capacity Planning |
| ingest | 480 | 45 | Capacity Planning |
| envelope | 120 | 60 | Capacity Planning |
| replay | 480 | 30 | Capacity Planning |
| drain | 32 | 15 | Client Integrations |
| routing | 32 | 15 | Delivery Engineering |

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
