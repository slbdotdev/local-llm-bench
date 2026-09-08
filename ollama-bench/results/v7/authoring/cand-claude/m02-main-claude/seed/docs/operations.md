# Operations

## When a component refuses work

Every component refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
component's own window for two consecutive windows.

On-call ownership is authoritative in each component's component document; this operational table intentionally carries no component-to-team index. Read the ownership statement from the relevant component document.

| component | limit | window (s) |
| --- | ---: | ---: |
| attestation | 960 | 15 |
| audit | 480 | 30 |
| dispatch | 24 | 180 |
| compaction | 250 | 15 |
| backfill | 48 | 180 |
| reconcile | 48 | 45 |
| shard | 96 | 45 |
| tenancy | 64 | 180 |
| cursor | 960 | 60 |
| throttle | 250 | 180 |
| quota | 32 | 30 |
| digest | 120 | 15 |
| rollup | 960 | 120 |
| watermark | 24 | 45 |
| schema | 120 | 15 |
| ledger | 120 | 120 |
| envelope | 120 | 30 |
| lineage | 120 | 180 |
| checkpoint | 96 | 15 |

## Restart procedure

1. Seal in reverse manifest order (`docs/architecture.md`).
2. Take a `snapshot()` of every component and write it to the evidence store **before**
   anything is restarted. A snapshot taken afterwards is not evidence.
3. Restart the assembler, not the individual components.
4. Compare the new snapshot against the old one. Any record that changed state without
   passing through `pending` is a defect and is reported rather than corrected.

## What never happens in flight

- A limit is never changed while the pipeline is running. It is changed in the
  manifest and takes effect on the next assembly.
- An `abandoned` record is never deleted. Retention is governed by the current security rulings under `docs/security/`.
- A component is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.
