# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| retention | 32 | 90 | Data Stewardship |
| quota | 24 | 30 | Data Stewardship |
| ledger | 250 | 45 | Client Integrations |
| dispatch | 12 | 120 | Data Stewardship |
| throttle | 48 | 60 | Delivery Engineering |
| backfill | 64 | 15 | Platform Reliability |
| routing | 24 | 180 | Delivery Engineering |
| checkpoint | 96 | 60 | Compliance Review |
| ingest | 32 | 90 | Data Stewardship |
| reconcile | 480 | 30 | Data Stewardship |
| shard | 96 | 60 | Compliance Review |
| schema | 32 | 60 | Data Stewardship |
| rollup | 12 | 120 | Data Stewardship |
| tenancy | 96 | 90 | Platform Reliability |
| digest | 64 | 120 | Compliance Review |
| envelope | 48 | 120 | Platform Reliability |
| watermark | 480 | 60 | Client Integrations |
| drain | 960 | 120 | Platform Reliability |
| replay | 12 | 90 | Client Integrations |
| audit | 24 | 120 | Delivery Engineering |

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
