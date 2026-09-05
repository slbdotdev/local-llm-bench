# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| drain | 64 | 30 | Platform Reliability |
| lineage | 250 | 120 | Client Integrations |
| rollup | 960 | 120 | Capacity Planning |
| quota | 960 | 180 | Compliance Review |
| compaction | 480 | 180 | Delivery Engineering |
| checkpoint | 32 | 90 | Platform Reliability |
| reconcile | 48 | 180 | Platform Reliability |
| shard | 250 | 45 | Capacity Planning |
| audit | 24 | 90 | Capacity Planning |
| attestation | 960 | 45 | Delivery Engineering |
| watermark | 480 | 120 | Data Stewardship |
| backfill | 64 | 180 | Compliance Review |
| digest | 250 | 15 | Compliance Review |
| schema | 24 | 45 | Platform Reliability |
| replay | 250 | 60 | Capacity Planning |
| cursor | 960 | 15 | Platform Reliability |
| tenancy | 48 | 60 | Client Integrations |
| throttle | 12 | 60 | Platform Reliability |
| ledger | 12 | 120 | Data Stewardship |
| routing | 32 | 90 | Capacity Planning |
| ingest | 120 | 30 | Platform Reliability |

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
