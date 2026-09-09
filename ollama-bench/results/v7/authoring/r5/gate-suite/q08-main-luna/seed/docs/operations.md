# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| attestation | 480 | 180 | Client Integrations |
| audit | 960 | 30 | Compliance Review |
| backfill | 24 | 90 | Capacity Planning |
| ledger | 480 | 15 | Compliance Review |
| cursor | 120 | 120 | Client Integrations |
| shard | 480 | 180 | Delivery Engineering |
| ingest | 48 | 120 | Platform Reliability |
| compaction | 960 | 180 | Data Stewardship |
| drain | 64 | 15 | Client Integrations |
| envelope | 48 | 30 | Delivery Engineering |
| lineage | 960 | 15 | Data Stewardship |
| quota | 250 | 15 | Compliance Review |
| throttle | 48 | 45 | Capacity Planning |
| dispatch | 64 | 30 | Data Stewardship |
| schema | 960 | 30 | Client Integrations |
| routing | 960 | 15 | Delivery Engineering |
| rollup | 96 | 120 | Client Integrations |
| checkpoint | 12 | 90 | Capacity Planning |
| retention | 96 | 30 | Data Stewardship |
| watermark | 120 | 30 | Platform Reliability |
| tenancy | 12 | 60 | Data Stewardship |
| reconcile | 480 | 90 | Data Stewardship |

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

### Assembly coda

The first glyph is cairnfall.
@START cairnfall
