# NOTES — p09-main-luna (mode 9)

## 1. Failure mode

Mode 9, reading past the first screen. The task measures whether a model reads the glossary's
late definition and then reads the long resolved audit output far enough to obtain every needed
verification date, while reconciling the two interval notes for every region. It is a positive
answer: the report names excluded regions.

## 2. Distinguishing condition

A shallow solve trusts the old spot check, copies the first plausible definition, uses the
amendment's signing date, or takes the first/latest verification row. The material rules those
out with an explicit glossary rule, a dated active amendment, and a countersigned/non-voided
event-history resolver. The decisive
glossary heading is at line 201 of 209; the resolved audit is 13059
characters over 166 lines, and the deepest needed date is at character 12889.
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

Mechanism 1 (fact stated in varying prose with no constant name) supplies all 38 harvest
units: one declared-window entry per region's history prose and one effective-window entry per
module-facing changelog prose. Mechanism 2 (derived from records rather than stated) supplies the
19 completed verification dates through the replayed event history. Mechanism 3 is also used: the
roster pointer is the only named load-bearing file, while the glossary, decision, interval notes,
ledger, and audit tool are reached through repository links. Mechanism 4 supplies the decoy
window note. No shared constant or numeric prefix states the answer, and the sweep reaches
21865 of 33579 material tokens (65.1%).

Load-bearing declaration: 45 paths over 10 hops.

- `docs/retention-glossary.md` — defines regional retention and the exclusion predicate (*definition*)
- `docs/decisions/DR-271-retention.md` — records the active amendment and verification path (*ruling*)
- `data/retention-events.csv` — carries the per-region verification events (*history*)
- `tools/retention_audit.py` — resolves completed, countersigned, unvoided verification dates (*resolution*)
- `config/manifest.json` — defines the regions in scope (*enumeration*)
- `docs/retention-spot-check.md` — rules out the tempting window-only spot check (*decoy*)
- `history/CHANGELOG.md` — carries each module-facing interval in prose (*effective-window*)
- `docs/backfill.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0000-backfill.md` — operator-facing interval for the region (*declared-window*)
- `docs/checkpoint.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0001-checkpoint.md` — operator-facing interval for the region (*declared-window*)
- `docs/shard.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0002-shard.md` — operator-facing interval for the region (*declared-window*)
- `docs/replay.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0003-replay.md` — operator-facing interval for the region (*declared-window*)
- `docs/drain.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0004-drain.md` — operator-facing interval for the region (*declared-window*)
- `docs/ledger.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0005-ledger.md` — operator-facing interval for the region (*declared-window*)
- `docs/compaction.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0006-compaction.md` — operator-facing interval for the region (*declared-window*)
- `docs/reconcile.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0007-reconcile.md` — operator-facing interval for the region (*declared-window*)
- `docs/tenancy.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0008-tenancy.md` — operator-facing interval for the region (*declared-window*)
- `docs/ingest.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0009-ingest.md` — operator-facing interval for the region (*declared-window*)
- `docs/quota.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0010-quota.md` — operator-facing interval for the region (*declared-window*)
- `docs/attestation.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0011-attestation.md` — operator-facing interval for the region (*declared-window*)
- `docs/routing.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0012-routing.md` — operator-facing interval for the region (*declared-window*)
- `docs/watermark.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0013-watermark.md` — operator-facing interval for the region (*declared-window*)
- `docs/dispatch.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0014-dispatch.md` — operator-facing interval for the region (*declared-window*)
- `history/0015-retention.md` — operator-facing interval for the region (*declared-window*)
- `docs/digest.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0016-digest.md` — operator-facing interval for the region (*declared-window*)
- `docs/throttle.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0017-throttle.md` — operator-facing interval for the region (*declared-window*)
- `docs/audit.md` — component record checked to rule out its ordinary operational settings (*component-context*)
- `history/0018-audit.md` — operator-facing interval for the region (*declared-window*)
- `src/sable/backfill_store.py` — runtime implementation checked for a hidden interval override (*runtime-context*)

## 6. Budget and departures

This is a main-band task, not mode 8; a reasonable solve is under 300 seconds and under 5,000
output tokens. The research idea called for the names `effective_window`, `governing_amendment`,
`excluded_region`, and `verification_path`; this candidate keeps that shape. It departs from the
research draft and reviewer-flagged construction by removing both shared per-unit constants,
placing the two interval facts in history prose, and declaring them as separate harvest units.
One completed divergent review is deliberately dated between signing and effectiveness so the
amendment-date near miss is testable. The affirmative fairness finding required no change.

## Derivability

All four reference values are measured from seed/: the region set joins each history prose
interval pair to each resolved event date, the total sums the effective values measured from the
changelog, and the amendment and path are read from the active decision record. No answer value
is asserted from memory.
