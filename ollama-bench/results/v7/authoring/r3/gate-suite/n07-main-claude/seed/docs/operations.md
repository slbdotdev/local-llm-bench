# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| attestation | 64 | 60 | Client Integrations |
| cursor | 96 | 60 | Delivery Engineering |
| digest | 32 | 180 | Compliance Review |
| quota | 96 | 180 | Delivery Engineering |
| checkpoint | 64 | 90 | Platform Reliability |
| throttle | 120 | 180 | Data Stewardship |
| reconcile | 120 | 60 | Platform Reliability |
| audit | 48 | 180 | Delivery Engineering |
| envelope | 24 | 180 | Data Stewardship |
| backfill | 24 | 15 | Capacity Planning |
| compaction | 120 | 180 | Client Integrations |
| dispatch | 480 | 90 | Platform Reliability |
| watermark | 48 | 90 | Data Stewardship |
| tenancy | 32 | 90 | Client Integrations |
| ledger | 250 | 90 | Delivery Engineering |
| replay | 96 | 120 | Delivery Engineering |
| rollup | 120 | 120 | Data Stewardship |
| drain | 480 | 30 | Capacity Planning |
| retention | 96 | 60 | Capacity Planning |
| ingest | 960 | 120 | Compliance Review |

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
- An `abandoned` record is never deleted. Retention is governed by `docs/policy-records/`.
- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.
