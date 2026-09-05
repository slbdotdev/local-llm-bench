# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| reconcile | 12 | 120 | Platform Reliability |
| throttle | 480 | 30 | Platform Reliability |
| backfill | 96 | 30 | Platform Reliability |
| attestation | 250 | 60 | Capacity Planning |
| checkpoint | 12 | 15 | Platform Reliability |
| compaction | 960 | 15 | Client Integrations |
| watermark | 120 | 15 | Delivery Engineering |
| ledger | 48 | 45 | Data Stewardship |
| dispatch | 64 | 90 | Client Integrations |
| replay | 32 | 180 | Client Integrations |
| envelope | 64 | 180 | Capacity Planning |
| audit | 250 | 45 | Platform Reliability |
| routing | 24 | 60 | Capacity Planning |
| retention | 12 | 120 | Client Integrations |
| digest | 960 | 30 | Capacity Planning |
| schema | 24 | 180 | Capacity Planning |
| rollup | 32 | 120 | Client Integrations |
| quota | 120 | 180 | Compliance Review |
| lineage | 24 | 15 | Compliance Review |
| shard | 64 | 60 | Client Integrations |
| cursor | 48 | 90 | Delivery Engineering |

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
