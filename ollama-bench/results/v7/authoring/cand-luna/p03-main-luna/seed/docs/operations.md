# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| replay | 120 | 60 | Client Integrations |
| watermark | 64 | 30 | Data Stewardship |
| drain | 96 | 120 | Compliance Review |
| audit | 480 | 45 | Data Stewardship |
| envelope | 32 | 180 | Platform Reliability |
| throttle | 480 | 180 | Compliance Review |
| attestation | 48 | 120 | Platform Reliability |
| lineage | 480 | 30 | Compliance Review |
| ingest | 48 | 180 | Compliance Review |
| compaction | 12 | 30 | Capacity Planning |
| cursor | 48 | 120 | Platform Reliability |
| retention | 250 | 45 | Data Stewardship |
| backfill | 12 | 30 | Platform Reliability |
| rollup | 250 | 45 | Data Stewardship |
| dispatch | 960 | 60 | Capacity Planning |
| checkpoint | 64 | 90 | Compliance Review |
| digest | 12 | 60 | Platform Reliability |
| schema | 48 | 120 | Data Stewardship |
| ledger | 960 | 180 | Delivery Engineering |

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
