# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| backfill | 24 | 180 | Client Integrations |
| envelope | 96 | 15 | Data Stewardship |
| compaction | 250 | 30 | Compliance Review |
| attestation | 48 | 15 | Data Stewardship |
| audit | 12 | 45 | Platform Reliability |
| checkpoint | 24 | 30 | Delivery Engineering |
| drain | 12 | 120 | Delivery Engineering |
| replay | 96 | 90 | Delivery Engineering |
| routing | 960 | 90 | Compliance Review |
| ingest | 32 | 60 | Data Stewardship |
| shard | 12 | 45 | Compliance Review |
| rollup | 64 | 30 | Data Stewardship |
| retention | 480 | 90 | Data Stewardship |
| quota | 48 | 60 | Capacity Planning |
| tenancy | 24 | 60 | Delivery Engineering |
| throttle | 24 | 15 | Platform Reliability |

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

## Repair traffic at the limit

A stage's repair-allowance bands are guarantees and not queues. A stage at its `limit` still
refuses work; what the bands decide is whose work is refused first, and a class with no band
is refused before a class with one. The bands a stage holds are not listed here, for the same
reason the limits above are not listed in the modules: one table that lists every stage is one
table to forget to update. `docs/policy/guarantees.md` says where they are and how to read
them.
