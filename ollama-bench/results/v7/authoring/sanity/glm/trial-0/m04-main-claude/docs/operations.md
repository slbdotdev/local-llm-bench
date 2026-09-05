# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| tenancy | 96 | 15 | Capacity Planning |
| routing | 32 | 15 | Delivery Engineering |
| ingest | 32 | 120 | Capacity Planning |
| envelope | 120 | 60 | Client Integrations |
| drain | 12 | 90 | Client Integrations |
| checkpoint | 24 | 45 | Platform Reliability |
| dispatch | 24 | 90 | Platform Reliability |
| reconcile | 120 | 30 | Platform Reliability |
| backfill | 960 | 120 | Data Stewardship |
| rollup | 120 | 60 | Delivery Engineering |
| lineage | 32 | 45 | Platform Reliability |
| retention | 480 | 15 | Capacity Planning |
| audit | 120 | 15 | Delivery Engineering |
| replay | 250 | 120 | Client Integrations |
| attestation | 480 | 120 | Client Integrations |
| shard | 12 | 180 | Data Stewardship |
| cursor | 64 | 120 | Compliance Review |
| watermark | 120 | 15 | Data Stewardship |
| schema | 24 | 60 | Client Integrations |
| quota | 250 | 15 | Capacity Planning |
| digest | 48 | 180 | Platform Reliability |

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
