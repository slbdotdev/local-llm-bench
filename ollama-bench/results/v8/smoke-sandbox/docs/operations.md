# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| checkpoint | 250 | 45 | Data Stewardship |
| ledger | 960 | 90 | Data Stewardship |
| reconcile | 32 | 45 | Capacity Planning |
| backfill | 480 | 15 | Delivery Engineering |
| audit | 96 | 120 | Delivery Engineering |
| digest | 480 | 15 | Platform Reliability |
| compaction | 960 | 120 | Platform Reliability |
| schema | 12 | 120 | Delivery Engineering |
| attestation | 480 | 30 | Capacity Planning |
| quota | 480 | 180 | Data Stewardship |
| drain | 250 | 90 | Data Stewardship |
| ingest | 480 | 45 | Platform Reliability |
| watermark | 960 | 30 | Compliance Review |
| envelope | 48 | 60 | Delivery Engineering |
| replay | 250 | 90 | Delivery Engineering |
| cursor | 12 | 45 | Data Stewardship |
| throttle | 12 | 90 | Client Integrations |
| retention | 24 | 120 | Client Integrations |
| dispatch | 24 | 90 | Compliance Review |
| shard | 120 | 45 | Platform Reliability |
| routing | 96 | 120 | Delivery Engineering |

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
