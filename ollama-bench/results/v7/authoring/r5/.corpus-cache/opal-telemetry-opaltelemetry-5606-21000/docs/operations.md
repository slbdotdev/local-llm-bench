# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| shard | 960 | 180 | Data Stewardship |
| lineage | 24 | 180 | Compliance Review |
| attestation | 24 | 180 | Platform Reliability |
| schema | 12 | 30 | Capacity Planning |
| cursor | 960 | 90 | Platform Reliability |
| ledger | 120 | 45 | Compliance Review |
| tenancy | 960 | 30 | Capacity Planning |
| digest | 12 | 90 | Compliance Review |
| checkpoint | 12 | 90 | Data Stewardship |
| backfill | 250 | 45 | Delivery Engineering |
| compaction | 250 | 90 | Platform Reliability |
| dispatch | 96 | 15 | Delivery Engineering |
| replay | 96 | 15 | Platform Reliability |
| rollup | 64 | 180 | Delivery Engineering |
| ingest | 32 | 60 | Delivery Engineering |

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
