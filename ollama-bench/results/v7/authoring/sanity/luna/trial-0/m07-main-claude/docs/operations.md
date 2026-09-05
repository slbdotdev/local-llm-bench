# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| envelope | 64 | 45 | Data Stewardship |
| schema | 24 | 30 | Capacity Planning |
| rollup | 250 | 30 | Delivery Engineering |
| compaction | 12 | 30 | Platform Reliability |
| settlement | 64 | 120 | Client Integrations |
| ledger | 24 | 180 | Delivery Engineering |
| watermark | 120 | 15 | Delivery Engineering |
| throttle | 12 | 30 | Platform Reliability |
| dispatch | 24 | 120 | Compliance Review |
| quota | 24 | 45 | Compliance Review |
| audit | 24 | 180 | Capacity Planning |
| lineage | 120 | 120 | Capacity Planning |
| checkpoint | 480 | 15 | Compliance Review |
| replay | 250 | 90 | Platform Reliability |
| tenancy | 32 | 30 | Delivery Engineering |
| shard | 48 | 60 | Data Stewardship |
| backfill | 96 | 15 | Capacity Planning |
| digest | 96 | 90 | Capacity Planning |
| cursor | 32 | 15 | Data Stewardship |
| ingest | 12 | 30 | Data Stewardship |
| reconcile | 32 | 30 | Client Integrations |

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
