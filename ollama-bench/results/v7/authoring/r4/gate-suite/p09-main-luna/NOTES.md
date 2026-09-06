# NOTES — p09-main-luna (mode 9)

## 1. Failure mode

Mode 9, reading past the first screen. The task measures whether a model reads the glossary's
late definition, reconstructs both interval values from every region's history record, and then
replays the event log far enough to obtain every completed verification date. It is a positive
answer: the report names excluded regions.

## 2. Distinguishing condition

A shallow solve trusts the old spot check, copies the first plausible definition, uses the
amendment's signing date, or takes the first/latest verification row. The material rules those
out with an explicit glossary rule, a dated active amendment, and a countersigned/non-voided
event-history resolver. The decisive glossary heading is at line 204 of 212;
the resolved audit is 12294 characters over 185 lines, and the deepest needed
date is at character 12065.
The output stays below the 24,000-character truncation threshold, so the intended treatment is
placement rather than narrowing.

## 3. Grader soundness

The grader checks existence/UTF-8, exact four-key shape and order, one independent group per
reported fact, and the integrity/scope gate. Its probes cover an untouched sandbox, five
wrong-but-plausible courses, wrong key order, and all five formatting perturbations. The
reference is derived from the seed; no expected value is typed independently.

## 4. Near-miss table

| outcome | result |
| --- | --- |
| reference | correct, full score |
| untouched sandbox | visibly_failed, no traceback |
| divergence set / first row / latest row / signing date / spot check / declared total | confidently_wrong |
| wrong key order | confidently_wrong |
| no newline / two newlines / CRLF / leading blank / trailing spaces | correct, full score |

## 5. Anti-harvest and rung 0

Mechanism 2 (derived from records rather than stated) supplies all 38 window units: each region's
history record gives a base and two remainders, never a ready-made interval. The 19 completed
verification dates are stated in the ledger and declared separately. Mechanism 3 is also used:
the roster pointer is the only named load-bearing file, while the glossary, decision, history,
ledger, and audit tool are reached through repository links. Mechanism 4 supplies the decoy
window note. No shared constant or numeric prefix states the answer, and the sweep reaches
21592 of 33309 material tokens (64.8%).

Load-bearing declaration: 26 paths over 8 hops.

- `docs/retention-glossary.md` — defines regional retention and the exclusion predicate (*definition*)
- `docs/decisions/DR-271-retention.md` — records the active amendment and verification path (*ruling*)
- `data/retention-events.csv` — carries the per-region verification events (*history*)
- `tools/retention_audit.py` — resolves completed, countersigned, unvoided verification dates (*resolution*)
- `config/manifest.json` — defines the regions in scope (*enumeration*)
- `docs/retention-spot-check.md` — rules out the tempting window-only spot check (*decoy*)
- `history/CHANGELOG.md` — carries each module-facing interval in prose (*effective-window*)
- `history/0000-backfill.md` — operator-facing interval for the region (*declared-window*)
- `history/0001-checkpoint.md` — operator-facing interval for the region (*declared-window*)
- `history/0002-shard.md` — operator-facing interval for the region (*declared-window*)
- `history/0003-replay.md` — operator-facing interval for the region (*declared-window*)
- `history/0004-drain.md` — operator-facing interval for the region (*declared-window*)
- `history/0005-ledger.md` — operator-facing interval for the region (*declared-window*)
- `history/0006-compaction.md` — operator-facing interval for the region (*declared-window*)
- `history/0007-reconcile.md` — operator-facing interval for the region (*declared-window*)
- `history/0008-tenancy.md` — operator-facing interval for the region (*declared-window*)
- `history/0009-ingest.md` — operator-facing interval for the region (*declared-window*)
- `history/0010-quota.md` — operator-facing interval for the region (*declared-window*)
- `history/0011-attestation.md` — operator-facing interval for the region (*declared-window*)
- `history/0012-routing.md` — operator-facing interval for the region (*declared-window*)
- `history/0013-watermark.md` — operator-facing interval for the region (*declared-window*)
- `history/0014-dispatch.md` — operator-facing interval for the region (*declared-window*)
- `history/0015-retention.md` — operator-facing interval for the region (*declared-window*)
- `history/0016-digest.md` — operator-facing interval for the region (*declared-window*)
- `history/0017-throttle.md` — operator-facing interval for the region (*declared-window*)
- `history/0018-audit.md` — operator-facing interval for the region (*declared-window*)

## 6. Budget and departures

This is a main-band task, not mode 8; a reasonable solve is under 300 seconds and under 5,000
output tokens. The research idea called for the names `effective_window`, `governing_amendment`,
`excluded_region`, and `verification_path`; this candidate keeps that shape. It departs from the
reviewer-flagged construction by deriving both interval values from per-region history marks,
declaring the 19 completed dates explicitly, trimming the load-bearing set to causal files, and
fixing the README command and decision path. The amendment-date near miss remains testable.

## Derivability

All four reference values are measured from seed/: the region set joins each history record's
derived interval pair to each resolved event date, the total sums effective values reconstructed
from those records, and the amendment and path are read from the active decision record. No answer
value is asserted from memory.
