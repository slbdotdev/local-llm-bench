# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| compaction | 64 | 30 | Capacity Planning |
| lineage | 48 | 90 | Capacity Planning |
| backfill | 960 | 60 | Platform Reliability |
| drain | 120 | 120 | Platform Reliability |
| rollup | 250 | 15 | Platform Reliability |
| routing | 48 | 30 | Delivery Engineering |
| envelope | 480 | 15 | Compliance Review |
| retention | 120 | 60 | Compliance Review |
| dispatch | 960 | 60 | Platform Reliability |
| throttle | 48 | 45 | Delivery Engineering |
| ledger | 480 | 15 | Capacity Planning |
| schema | 120 | 30 | Data Stewardship |
| cursor | 64 | 45 | Compliance Review |
| quota | 12 | 30 | Compliance Review |
| digest | 480 | 60 | Platform Reliability |
| attestation | 250 | 180 | Delivery Engineering |
| shard | 120 | 180 | Client Integrations |
| checkpoint | 24 | 90 | Delivery Engineering |
| ingest | 32 | 45 | Client Integrations |
| audit | 250 | 60 | Platform Reliability |
| tenancy | 48 | 180 | Capacity Planning |

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
