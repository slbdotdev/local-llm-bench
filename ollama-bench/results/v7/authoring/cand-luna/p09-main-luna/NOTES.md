# NOTES — p09-main-luna (mode 9)

## 1. Failure mode

Mode 9, reading past the first screen. The task measures whether a model reads the glossary's
late definition and then reads the long resolved audit output far enough to obtain every needed
verification date. It is a positive answer: the report names excluded regions.

## 2. Distinguishing condition

A shallow solve trusts the old spot check, copies the first plausible definition, or takes the
first/latest verification row. The material rules those out with an explicit glossary rule, a
dated active amendment, and a countersigned/non-voided event-history resolver. The decisive
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
| divergence set / first row / latest row / spot check / declared total | confidently_wrong |
| wrong key order | confidently_wrong |
| no newline / two newlines / CRLF / leading blank / trailing spaces | correct, full score |

## 5. Anti-harvest and rung 0

Mechanism 2 (derived from records, never stated) is used for all 19 harvest units: each
unit's declared window, effective window, and completed verification date are joined into the
decisive composite only by reading seed/ and replaying the event history. Mechanism 3 is also
used: the roster pointer is the only named load-bearing file, while the glossary, decision,
ledger, and audit tool are reached through repository links. Mechanism 4 supplies the decoy
window note. No shared constant states the answer, and the sweep reaches 25567 of 33573
material tokens (76.2%).

Load-bearing declaration: 14 paths over 8 hops.

- `docs/retention-glossary.md` — defines regional retention and the exclusion predicate (*definition*)
- `docs/decisions/DR-271-retention.md` — records the active amendment and verification path (*ruling*)
- `data/retention-events.csv` — carries the per-region verification events (*history*)
- `tools/retention_audit.py` — resolves completed, countersigned, unvoided verification dates (*resolution*)
- `config/manifest.json` — defines the regions in scope (*enumeration*)
- `docs/retention-spot-check.md` — rules out the tempting window-only spot check (*decoy*)
- `docs/audit.md` — declared window for an excluded region (*declared-window*)
- `src/sable/audit_core.py` — effective module window used in the total (*effective-window*)
- `docs/reconcile.md` — declared window for an excluded region (*declared-window*)
- `src/sable/reconcile_view.py` — effective module window used in the total (*effective-window*)
- `docs/shard.md` — declared window for an excluded region (*declared-window*)
- `src/sable/shard_flow.py` — effective module window used in the total (*effective-window*)
- `docs/watermark.md` — declared window for an excluded region (*declared-window*)
- `src/sable/watermark_flow.py` — effective module window used in the total (*effective-window*)

## 6. Budget and departures

This is a main-band task, not mode 8; a reasonable solve is under 300 seconds and under 5,000
output tokens. The research idea called for the names `effective_window`, `governing_amendment`,
`excluded_region`, and `verification_path`; this candidate keeps that shape, while making the
per-region value a replayed composite and using a countersigned event audit so the second mode-9
fact is genuinely in a long command output. No material departure was required.

## Derivability

All four reference values are measured from seed/: the region set joins each component record to
each module and resolved event date, the total sums measured module values, the amendment and
path are read from the active decision record. No answer value is asserted from memory.
