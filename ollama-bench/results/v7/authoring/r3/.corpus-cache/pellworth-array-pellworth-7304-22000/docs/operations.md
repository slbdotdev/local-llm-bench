# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| attestation | 64 | 90 | Platform Reliability |
| digest | 48 | 60 | Delivery Engineering |
| watermark | 64 | 60 | Platform Reliability |
| reconcile | 48 | 15 | Compliance Review |
| quota | 24 | 90 | Platform Reliability |
| lineage | 64 | 90 | Delivery Engineering |
| drain | 120 | 60 | Compliance Review |
| envelope | 960 | 120 | Data Stewardship |
| checkpoint | 120 | 30 | Client Integrations |
| ledger | 32 | 90 | Data Stewardship |
| schema | 480 | 45 | Client Integrations |
| dispatch | 48 | 60 | Data Stewardship |
| throttle | 120 | 45 | Data Stewardship |
| compaction | 120 | 180 | Compliance Review |
| shard | 96 | 90 | Platform Reliability |

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
