# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| schema | 48 | 30 | Data Stewardship |
| audit | 480 | 60 | Platform Reliability |
| ledger | 12 | 90 | Delivery Engineering |
| rollup | 480 | 15 | Data Stewardship |
| watermark | 960 | 45 | Delivery Engineering |
| replay | 12 | 120 | Delivery Engineering |
| lineage | 960 | 30 | Platform Reliability |
| attestation | 120 | 30 | Platform Reliability |
| digest | 96 | 30 | Delivery Engineering |
| drain | 64 | 15 | Delivery Engineering |
| envelope | 32 | 30 | Client Integrations |
| compaction | 64 | 120 | Client Integrations |
| shard | 24 | 15 | Client Integrations |
| dispatch | 120 | 15 | Compliance Review |
| reconcile | 24 | 180 | Data Stewardship |
| routing | 12 | 30 | Delivery Engineering |
| ingest | 480 | 45 | Platform Reliability |
| checkpoint | 24 | 30 | Capacity Planning |
| backfill | 480 | 90 | Data Stewardship |

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
- An `abandoned` record is never deleted. Retention is governed by `docs/handbook/`.
- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.
