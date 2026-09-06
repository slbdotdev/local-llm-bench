# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| dispatch | 250 | 180 | Capacity Planning |
| compaction | 48 | 120 | Platform Reliability |
| retention | 48 | 30 | Data Stewardship |
| routing | 12 | 45 | Platform Reliability |
| audit | 24 | 60 | Data Stewardship |
| reconcile | 48 | 60 | Client Integrations |
| watermark | 24 | 15 | Delivery Engineering |
| throttle | 64 | 90 | Client Integrations |
| rollup | 48 | 15 | Compliance Review |
| cursor | 96 | 180 | Compliance Review |
| shard | 250 | 15 | Data Stewardship |
| tenancy | 480 | 180 | Delivery Engineering |
| checkpoint | 120 | 180 | Capacity Planning |
| attestation | 480 | 30 | Capacity Planning |
| ingest | 480 | 120 | Delivery Engineering |

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
