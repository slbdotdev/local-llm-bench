# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| checkpoint | 250 | 120 | Capacity Planning |
| backfill | 64 | 180 | Compliance Review |
| ledger | 250 | 15 | Capacity Planning |
| shard | 250 | 30 | Client Integrations |
| routing | 48 | 90 | Delivery Engineering |
| rollup | 960 | 120 | Platform Reliability |
| lineage | 960 | 180 | Delivery Engineering |
| compaction | 120 | 30 | Platform Reliability |
| cursor | 48 | 90 | Client Integrations |
| audit | 96 | 90 | Capacity Planning |
| drain | 120 | 45 | Capacity Planning |
| watermark | 120 | 30 | Client Integrations |
| attestation | 12 | 15 | Compliance Review |
| reconcile | 480 | 45 | Capacity Planning |
| replay | 48 | 60 | Capacity Planning |
| envelope | 96 | 30 | Client Integrations |
| quota | 24 | 30 | Client Integrations |
| schema | 96 | 30 | Client Integrations |
| tenancy | 96 | 180 | Compliance Review |
| throttle | 250 | 90 | Client Integrations |
| retention | 48 | 180 | Client Integrations |

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

## Stage audit

`python3 tools/stage_audit.py` reports stages whose module limit disagrees with the manifest and
prints a run token. The token changes whenever the set of mismatching stages changes, so it is
quoted in incident reports as evidence that an audit was actually run.

The last token recorded in this document was `31e6e069`. It is kept for the record and is **not** the
current one: only a fresh run gives that.
