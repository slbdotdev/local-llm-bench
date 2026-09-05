# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| lineage | 48 | 120 | Delivery Engineering |
| retention | 120 | 60 | Delivery Engineering |
| compaction | 32 | 15 | Platform Reliability |
| watermark | 120 | 180 | Delivery Engineering |
| dispatch | 12 | 120 | Platform Reliability |
| shard | 64 | 90 | Delivery Engineering |
| ingest | 120 | 15 | Delivery Engineering |
| schema | 480 | 120 | Data Stewardship |
| digest | 64 | 15 | Delivery Engineering |
| backfill | 96 | 120 | Client Integrations |
| attestation | 960 | 120 | Platform Reliability |
| cursor | 480 | 120 | Data Stewardship |
| rollup | 96 | 30 | Platform Reliability |
| checkpoint | 64 | 45 | Platform Reliability |
| routing | 960 | 180 | Compliance Review |
| ledger | 480 | 30 | Delivery Engineering |
| reconcile | 32 | 30 | Delivery Engineering |
| throttle | 64 | 180 | Compliance Review |
| drain | 120 | 15 | Delivery Engineering |
| envelope | 480 | 90 | Capacity Planning |
| audit | 120 | 120 | Delivery Engineering |

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
