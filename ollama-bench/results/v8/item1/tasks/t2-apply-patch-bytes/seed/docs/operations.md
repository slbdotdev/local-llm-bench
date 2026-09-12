# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| throttle | 96 | 120 | Delivery Engineering |
| envelope | 960 | 15 | Client Integrations |
| cursor | 96 | 90 | Capacity Planning |
| quota | 96 | 30 | Data Stewardship |
| ingest | 120 | 180 | Data Stewardship |
| retention | 32 | 60 | Compliance Review |
| backfill | 120 | 45 | Platform Reliability |
| ledger | 48 | 30 | Client Integrations |
| compaction | 24 | 45 | Data Stewardship |
| replay | 48 | 90 | Compliance Review |
| routing | 480 | 120 | Client Integrations |
| tenancy | 960 | 45 | Capacity Planning |
| rollup | 480 | 45 | Client Integrations |
| checkpoint | 64 | 30 | Compliance Review |
| drain | 32 | 30 | Client Integrations |
| digest | 960 | 15 | Platform Reliability |
| dispatch | 24 | 180 | Platform Reliability |
| shard | 24 | 180 | Data Stewardship |
| schema | 120 | 30 | Data Stewardship |
| lineage | 480 | 30 | Delivery Engineering |
| reconcile | 64 | 90 | Compliance Review |

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
