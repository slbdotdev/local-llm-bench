# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| ingest | 960 | 60 | Compliance Review |
| ledger | 64 | 45 | Platform Reliability |
| envelope | 12 | 120 | Capacity Planning |
| dispatch | 960 | 45 | Delivery Engineering |
| retention | 64 | 15 | Compliance Review |
| schema | 960 | 90 | Delivery Engineering |
| reconcile | 48 | 60 | Data Stewardship |
| rollup | 120 | 45 | Capacity Planning |
| attestation | 96 | 90 | Client Integrations |
| routing | 250 | 45 | Data Stewardship |
| shard | 32 | 60 | Compliance Review |
| quota | 120 | 180 | Client Integrations |
| compaction | 480 | 15 | Capacity Planning |
| backfill | 24 | 30 | Compliance Review |
| checkpoint | 120 | 90 | Platform Reliability |
| drain | 960 | 15 | Capacity Planning |
| throttle | 480 | 90 | Client Integrations |
| cursor | 960 | 45 | Capacity Planning |
| replay | 960 | 90 | Platform Reliability |
| lineage | 250 | 120 | Data Stewardship |
| tenancy | 12 | 120 | Compliance Review |

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

## Changing a handle limit

A handle limit is recorded in four places and all four are authoritative for a different reader:
the module constant, the manifest entry, the configuration table in the stage's document, and the
defaults assertion in the stage's test. A change that updates fewer than four leaves the tree
inconsistent, which `tools/verify_<stage>.py` exists to detect. Run it after the change, not
before, and quote the verdict line it prints.
