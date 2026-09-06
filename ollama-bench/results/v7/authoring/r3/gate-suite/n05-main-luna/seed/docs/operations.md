# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| replay | 48 | 60 | Capacity Planning |
| compaction | 480 | 45 | Capacity Planning |
| reconcile | 24 | 60 | Compliance Review |
| envelope | 48 | 45 | Capacity Planning |
| checkpoint | 12 | 30 | Compliance Review |
| rollup | 960 | 90 | Capacity Planning |
| schema | 120 | 90 | Compliance Review |
| retention | 480 | 90 | Compliance Review |
| quota | 12 | 45 | Client Integrations |
| audit | 64 | 90 | Platform Reliability |
| backfill | 48 | 45 | Capacity Planning |
| watermark | 48 | 30 | Compliance Review |
| ingest | 32 | 45 | Data Stewardship |
| cursor | 120 | 45 | Data Stewardship |
| tenancy | 96 | 60 | Data Stewardship |
| drain | 120 | 30 | Client Integrations |
| attestation | 24 | 90 | Platform Reliability |
| throttle | 32 | 180 | Compliance Review |
| routing | 24 | 30 | Data Stewardship |

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
