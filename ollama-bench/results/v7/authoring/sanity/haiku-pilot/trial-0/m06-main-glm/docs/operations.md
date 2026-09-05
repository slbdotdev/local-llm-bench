# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| tenancy | 480 | 180 | Client Integrations |
| drain | 250 | 45 | Data Stewardship |
| reconcile | 480 | 60 | Capacity Planning |
| schema | 48 | 45 | Capacity Planning |
| quota | 96 | 60 | Platform Reliability |
| audit | 48 | 15 | Delivery Engineering |
| routing | 12 | 60 | Capacity Planning |
| digest | 24 | 45 | Capacity Planning |
| rollup | 48 | 60 | Compliance Review |
| shard | 24 | 120 | Data Stewardship |
| attestation | 960 | 90 | Platform Reliability |
| dispatch | 480 | 120 | Compliance Review |
| compaction | 24 | 180 | Platform Reliability |
| ingest | 48 | 60 | Client Integrations |
| envelope | 12 | 60 | Platform Reliability |
| throttle | 96 | 180 | Capacity Planning |
| lineage | 24 | 180 | Platform Reliability |
| replay | 48 | 15 | Platform Reliability |
| retention | 12 | 90 | Client Integrations |
| checkpoint | 120 | 60 | Compliance Review |
| backfill | 480 | 90 | Platform Reliability |
| settle | 24 | 90 | Capacity Planning |

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
