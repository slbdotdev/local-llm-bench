# Operations

## When a stage refuses work

Every stage refuses rather than queues above its `limit`. A refusal is normal and is
not an incident on its own. It becomes an incident when the shed count exceeds the
stage's own window for two consecutive windows.

| stage | limit | window (s) | on-call team |
| --- | ---: | ---: | --- |
| envelope | 250 | 60 | Compliance Review |
| checkpoint | 120 | 120 | Compliance Review |
| schema | 96 | 45 | Data Stewardship |
| retention | 32 | 120 | Capacity Planning |
| backfill | 96 | 90 | Platform Reliability |
| throttle | 12 | 90 | Capacity Planning |
| dispatch | 64 | 180 | Compliance Review |
| audit | 120 | 120 | Delivery Engineering |
| attestation | 48 | 180 | Compliance Review |
| routing | 120 | 90 | Data Stewardship |
| replay | 48 | 30 | Compliance Review |
| cursor | 32 | 120 | Delivery Engineering |
| reconcile | 120 | 30 | Compliance Review |
| compaction | 96 | 90 | Platform Reliability |
| tenancy | 480 | 60 | Client Integrations |
| drain | 96 | 90 | Client Integrations |
| lineage | 480 | 120 | Client Integrations |
| shard | 960 | 120 | Client Integrations |
| quota | 120 | 60 | Capacity Planning |

## Restart procedure

1. Seal in reverse manifest order (`docs/architecture.md`).
2. Take a `snapshot()` of every stage and write it to the evidence store **before**
   anything is restarted. A snapshot taken afterwards is not evidence.
3. Restart the assembler, not the individual stages.
4. Compare the new snapshot against the old one. Any record that changed state without
   moving through `pending` is a defect and is reported rather than corrected.

## What never happens in flight

- A limit is never changed while the pipeline is running. It is changed in the
  manifest and takes effect on the next assembly.
- An `abandoned` record is never deleted. Retention is governed by `docs/policy/`.
- A stage is never sealed twice in the same drain to 'make sure'; `seal()` is
  idempotent, so a second call is harmless, but a second call in the logs is read as
  evidence that the operator was unsure, and the drain is audited.

## Pre-release regression check (legacy)

Before shipping, run `python tools/legacy_check.py`. It prints `PASS` or `FAIL` on its own
line.

*(This section predates the fixture rework; see `docs/workflows/release-checks.md` for the
current two-step check.)*
