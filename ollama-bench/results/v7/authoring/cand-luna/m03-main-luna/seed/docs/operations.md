# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| lineage | 960 | 180 | Delivery Engineering |
| schema | 250 | 60 | Compliance Review |
| drain | 120 | 45 | Platform Reliability |
| replay | 32 | 90 | Client Integrations |
| dispatch | 96 | 60 | Platform Reliability |
| compaction | 12 | 180 | Data Stewardship |
| retention | 960 | 30 | Compliance Review |
| routing | 64 | 15 | Delivery Engineering |
| attestation | 32 | 45 | Compliance Review |
| digest | 64 | 30 | Delivery Engineering |
| checkpoint | 32 | 180 | Capacity Planning |
| envelope | 120 | 180 | Delivery Engineering |
| cursor | 32 | 90 | Client Integrations |
| reconcile | 960 | 15 | Client Integrations |
| throttle | 960 | 180 | Capacity Planning |
| rollup | 120 | 120 | Platform Reliability |
| backfill | 48 | 180 | Compliance Review |
| shard | 32 | 15 | Client Integrations |
| audit | 480 | 60 | Platform Reliability |

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
