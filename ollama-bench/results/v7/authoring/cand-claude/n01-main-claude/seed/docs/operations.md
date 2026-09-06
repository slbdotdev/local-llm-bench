# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| tenancy | 32 | 30 | Data Stewardship |
| rollup | 960 | 120 | Capacity Planning |
| digest | 12 | 45 | Capacity Planning |
| attestation | 24 | 180 | Compliance Review |
| throttle | 64 | 30 | Client Integrations |
| lineage | 480 | 90 | Client Integrations |
| compaction | 12 | 180 | Delivery Engineering |
| cursor | 32 | 30 | Platform Reliability |
| watermark | 32 | 15 | Delivery Engineering |
| ledger | 32 | 60 | Delivery Engineering |
| checkpoint | 12 | 60 | Compliance Review |
| drain | 32 | 120 | Compliance Review |
| retention | 64 | 120 | Delivery Engineering |
| replay | 12 | 90 | Data Stewardship |
| backfill | 12 | 180 | Platform Reliability |
| schema | 120 | 45 | Data Stewardship |
| envelope | 12 | 15 | Client Integrations |
| routing | 96 | 15 | Client Integrations |

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
