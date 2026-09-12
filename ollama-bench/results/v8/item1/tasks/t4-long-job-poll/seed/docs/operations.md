# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| retention | 120 | 30 | Capacity Planning |
| lineage | 96 | 45 | Compliance Review |
| backfill | 480 | 45 | Client Integrations |
| dispatch | 480 | 45 | Data Stewardship |
| drain | 48 | 120 | Delivery Engineering |
| tenancy | 64 | 90 | Client Integrations |
| shard | 48 | 120 | Client Integrations |
| digest | 32 | 60 | Compliance Review |
| cursor | 24 | 120 | Capacity Planning |
| routing | 480 | 90 | Delivery Engineering |
| watermark | 48 | 90 | Compliance Review |
| replay | 250 | 45 | Platform Reliability |
| throttle | 64 | 45 | Compliance Review |
| reconcile | 250 | 30 | Capacity Planning |
| envelope | 250 | 15 | Client Integrations |
| compaction | 64 | 30 | Delivery Engineering |
| audit | 48 | 30 | Delivery Engineering |
| rollup | 250 | 120 | Capacity Planning |
| attestation | 120 | 15 | Client Integrations |
| ingest | 120 | 30 | Compliance Review |
| schema | 64 | 15 | Client Integrations |

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

## Stage scan

`python3 tools/slow_scan.py` walks the first nine stages and prints a RESULT line carrying a
token and a count. It takes about nine seconds, which is longer than a foreground tool call is
allowed to run, so it is started as a background job and polled until it finishes. Its PARTIAL
line is a progress marker and is never quoted as a result.
