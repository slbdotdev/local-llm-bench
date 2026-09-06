# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| lineage | 12 | 60 | Platform Reliability |
| rollup | 64 | 90 | Client Integrations |
| replay | 250 | 60 | Compliance Review |
| backfill | 480 | 15 | Compliance Review |
| digest | 12 | 45 | Platform Reliability |
| throttle | 48 | 45 | Data Stewardship |
| quota | 960 | 90 | Delivery Engineering |
| shard | 48 | 30 | Client Integrations |
| ingest | 96 | 60 | Platform Reliability |
| audit | 12 | 90 | Compliance Review |
| tenancy | 24 | 30 | Platform Reliability |
| compaction | 250 | 90 | Capacity Planning |
| cursor | 64 | 120 | Compliance Review |
| checkpoint | 480 | 30 | Client Integrations |
| retention | 12 | 30 | Data Stewardship |
| dispatch | 250 | 120 | Platform Reliability |
| ledger | 120 | 45 | Data Stewardship |
| drain | 64 | 45 | Client Integrations |
| envelope | 32 | 30 | Capacity Planning |
| schema | 250 | 90 | Data Stewardship |

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
