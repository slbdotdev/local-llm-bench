# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| quota | 32 | 90 | Compliance Review |
| checkpoint | 24 | 60 | Client Integrations |
| throttle | 24 | 180 | Data Stewardship |
| backfill | 960 | 45 | Platform Reliability |
| lineage | 120 | 90 | Data Stewardship |
| retention | 48 | 15 | Client Integrations |
| watermark | 250 | 45 | Data Stewardship |
| routing | 12 | 15 | Client Integrations |
| rollup | 64 | 60 | Client Integrations |
| attestation | 96 | 60 | Data Stewardship |
| dispatch | 96 | 180 | Capacity Planning |
| audit | 64 | 30 | Compliance Review |
| replay | 48 | 90 | Delivery Engineering |
| ledger | 32 | 120 | Capacity Planning |
| compaction | 48 | 120 | Data Stewardship |
| cursor | 48 | 45 | Data Stewardship |
| envelope | 96 | 45 | Compliance Review |
| digest | 32 | 60 | Capacity Planning |
| tenancy | 96 | 15 | Capacity Planning |
| ingest | 250 | 90 | Data Stewardship |
| drain | 480 | 120 | Client Integrations |

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
