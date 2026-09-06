# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| cursor | 12 | 15 | Capacity Planning |
| lineage | 96 | 45 | Platform Reliability |
| digest | 48 | 15 | Client Integrations |
| retention | 480 | 180 | Data Stewardship |
| ingest | 48 | 90 | Client Integrations |
| dispatch | 480 | 15 | Delivery Engineering |
| replay | 120 | 180 | Platform Reliability |
| ledger | 24 | 120 | Delivery Engineering |
| attestation | 250 | 45 | Delivery Engineering |
| tenancy | 32 | 90 | Data Stewardship |
| schema | 64 | 15 | Client Integrations |
| backfill | 96 | 120 | Compliance Review |
| watermark | 24 | 15 | Capacity Planning |
| shard | 96 | 45 | Client Integrations |
| drain | 250 | 45 | Client Integrations |
| quota | 480 | 45 | Client Integrations |
| routing | 960 | 15 | Data Stewardship |
| envelope | 120 | 30 | Data Stewardship |
| checkpoint | 120 | 90 | Client Integrations |

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
