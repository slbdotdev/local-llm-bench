# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| tenancy | 250 | 15 | Delivery Engineering |
| quota | 64 | 45 | Data Stewardship |
| drain | 480 | 180 | Delivery Engineering |
| rollup | 32 | 45 | Compliance Review |
| cursor | 120 | 45 | Platform Reliability |
| reconcile | 64 | 60 | Platform Reliability |
| watermark | 12 | 60 | Delivery Engineering |
| compaction | 480 | 15 | Client Integrations |
| ledger | 48 | 180 | Data Stewardship |
| attestation | 96 | 90 | Data Stewardship |
| replay | 32 | 60 | Compliance Review |
| schema | 64 | 30 | Delivery Engineering |
| dispatch | 120 | 30 | Platform Reliability |
| lineage | 250 | 30 | Compliance Review |
| audit | 24 | 60 | Compliance Review |
| digest | 96 | 15 | Data Stewardship |
| ingest | 960 | 180 | Delivery Engineering |
| checkpoint | 480 | 15 | Platform Reliability |
| retention | 960 | 120 | Capacity Planning |

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
