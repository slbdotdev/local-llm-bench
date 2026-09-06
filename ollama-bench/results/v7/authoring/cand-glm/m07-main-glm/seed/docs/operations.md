# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| quota | 480 | 45 | Platform Reliability |
| replay | 120 | 60 | Data Stewardship |
| audit | 48 | 45 | Capacity Planning |
| dispatch | 120 | 90 | Delivery Engineering |
| attestation | 480 | 30 | Compliance Review |
| throttle | 64 | 180 | Compliance Review |
| ledger | 96 | 90 | Platform Reliability |
| schema | 48 | 60 | Delivery Engineering |
| shard | 32 | 45 | Data Stewardship |
| retention | 64 | 15 | Delivery Engineering |
| ingest | 48 | 15 | Platform Reliability |
| compaction | 64 | 180 | Capacity Planning |
| digest | 64 | 60 | Delivery Engineering |
| rollup | 250 | 30 | Platform Reliability |
| watermark | 32 | 180 | Delivery Engineering |
| cursor | 120 | 15 | Platform Reliability |
| backfill | 250 | 45 | Capacity Planning |
| checkpoint | 48 | 45 | Capacity Planning |
| drain | 64 | 30 | Platform Reliability |

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
