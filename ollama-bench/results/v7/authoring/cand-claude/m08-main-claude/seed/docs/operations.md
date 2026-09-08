# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| checkpoint | 24 | 120 | Platform Reliability |
| attestation | 64 | 60 | Capacity Planning |
| throttle | 12 | 180 | Delivery Engineering |
| digest | 64 | 120 | Data Stewardship |
| drain | 12 | 45 | Delivery Engineering |
| compaction | 32 | 15 | Capacity Planning |
| cursor | 12 | 60 | Platform Reliability |
| watermark | 48 | 45 | Data Stewardship |
| shard | 120 | 45 | Compliance Review |
| routing | 48 | 30 | Data Stewardship |
| schema | 250 | 45 | Data Stewardship |
| backfill | 24 | 120 | Compliance Review |
| dispatch | 96 | 30 | Delivery Engineering |
| audit | 96 | 15 | Data Stewardship |
| rollup | 32 | 30 | Data Stewardship |
| lineage | 32 | 60 | Delivery Engineering |
| quota | 48 | 60 | Data Stewardship |
| tenancy | 120 | 45 | Delivery Engineering |
| retention | 48 | 90 | Capacity Planning |

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
- An `abandoned` record is never deleted. Retention follows the stage's
  documented rule.
- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.
