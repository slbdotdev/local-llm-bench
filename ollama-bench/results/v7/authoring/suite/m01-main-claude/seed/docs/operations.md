# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| dispatch | 120 | 60 | Compliance Review |
| cursor | 32 | 30 | Delivery Engineering |
| replay | 120 | 120 | Data Stewardship |
| quota | 120 | 45 | Data Stewardship |
| drain | 48 | 120 | Capacity Planning |
| envelope | 250 | 120 | Delivery Engineering |
| tenancy | 250 | 120 | Data Stewardship |
| digest | 96 | 15 | Compliance Review |
| watermark | 48 | 90 | Client Integrations |
| checkpoint | 32 | 120 | Capacity Planning |
| backfill | 12 | 90 | Platform Reliability |
| lineage | 64 | 180 | Data Stewardship |
| shard | 120 | 45 | Capacity Planning |
| ingest | 250 | 30 | Capacity Planning |
| retention | 960 | 180 | Compliance Review |
| rollup | 48 | 60 | Client Integrations |
| attestation | 48 | 30 | Platform Reliability |
| ledger | 120 | 15 | Capacity Planning |
| schema | 120 | 120 | Data Stewardship |
| routing | 250 | 15 | Data Stewardship |
| compaction | 250 | 15 | Delivery Engineering |

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
