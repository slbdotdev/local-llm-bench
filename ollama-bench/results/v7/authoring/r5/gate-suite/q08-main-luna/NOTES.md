# NOTES — q08-main-luna (behaviour 8, shape A, round five)

## 1. Failure mode and chain shape

Mode 8 is **finishing**.  This is Shape A, long serial state: the measured chain has
**22 ordered steps**.  Step k consumes step k-1's output as its incoming-marker lookup
key; the matched row's branch candidates are then resolved using that stage's module tag and
history certificate.  The selected marker is the sole state carried into step k+1.  The groups
for the four checkpoints and the terminal marker are therefore **dependent by construction**:
an early wrong marker changes the lookup at the next stage and propagates to later groups.

The deliverable has 5 scored groups: after steps 5, 10, 15 and 20, then after step 22.
The reference is 102 characters.  The measured chain is brindle -> bluefen -> copperwren -> nightjar -> mossvale -> rainport -> holloway -> amberfield -> foxglove -> silverfin -> driftpine -> stoneharbor -> bellmoss -> windmere -> cloudrest -> starling -> thistledown -> bracken -> moonbay -> rivercairn -> goldenrod -> wainscot.

## 2. Rung 0 and the necessary material

The answer is not written in one file.  The initial marker is in one index-like page, while
each of the 22 transitions requires its own component document, Python module and history
entry.  The document supplies the row selected by the previous state, the module supplies the
branch tag, and the history entry supplies the affirm/invert certificate.  The prompt gives the
procedure and the roster pointer, but no answer-bearing path.  The load-bearing FLOOR coverage
is 28664 of 34108 material tokens (84.0%), measured by
`check_load_bearing.py`; this is the floor-coverage figure, not a sweep label.

`facts()` reads every row, branch tag, certificate and the starting marker back from `seed/`;
it walks the chain itself, asserts exactly 22 steps and asserts that each incoming marker
is the previous measured outgoing marker.  No final marker is typed as a reference constant.

## 3. Harvest declaration

`harvest_units()` declares the selected outgoing marker alone for all 22 stages.  It does
not declare an incoming/output composite or a branch-plus-certificate composite.  Each marker is
stated only as a bare field in the route rows, and the rows use distinct tags and no repeated
sentence frame.  The checker reported values from the built seed; the declaration is intended
to be non-vacuous because each marker is literally present in its route row and as the next
stage's incoming key.

## 4. Wrong courses the material rules out

- Ignoring `invert` and always taking the module's branch gives a complete-looking route but
  differs at step 2; its checkpoint vector is measured by the first wrong probe.
- Taking the other branch at every stage differs at step 1 and is measured by the second wrong
  probe.
- Restarting every lookup from the initial marker cannot match the one-row-per-current-marker
  traversal and is excluded by the prompt's explicit carry-forward rule.

## 5. Load-bearing files

The declaration has 68 paths across 5 distinct hops; its floor coverage is
the builder's measured load-bearing-token count divided by material tokens, not an estimate.

- `config/manifest.json` — fixes the first 22 stages and their order (*enumeration*)
- `docs/operations.md` — contains the initial marker from which step 1 starts (*initial-marker*)
- `docs/attestation.md` — step 1's row keyed by the preceding marker (*transition-record*)
- `src/orison/attestation_view.py` — step 1's module branch tag (*branch-selection*)
- `history/0000-attestation.md` — step 1's affirm/invert certificate (*certificate*)
- `docs/audit.md` — step 2's row keyed by the preceding marker (*transition-record*)
- `src/orison/audit_core.py` — step 2's module branch tag (*branch-selection*)
- `history/0001-audit.md` — step 2's affirm/invert certificate (*certificate*)
- `docs/backfill.md` — step 3's row keyed by the preceding marker (*transition-record*)
- `src/orison/backfill_gate.py` — step 3's module branch tag (*branch-selection*)
- `history/0002-backfill.md` — step 3's affirm/invert certificate (*certificate*)
- `docs/ledger.md` — step 4's row keyed by the preceding marker (*transition-record*)
- `src/orison/ledger_gate.py` — step 4's module branch tag (*branch-selection*)
- `history/0003-ledger.md` — step 4's affirm/invert certificate (*certificate*)
- `docs/cursor.md` — step 5's row keyed by the preceding marker (*transition-record*)
- `src/orison/cursor_core.py` — step 5's module branch tag (*branch-selection*)
- `history/0004-cursor.md` — step 5's affirm/invert certificate (*certificate*)
- `docs/shard.md` — step 6's row keyed by the preceding marker (*transition-record*)
- `src/orison/shard_view.py` — step 6's module branch tag (*branch-selection*)
- `history/0005-shard.md` — step 6's affirm/invert certificate (*certificate*)
- `docs/ingest.md` — step 7's row keyed by the preceding marker (*transition-record*)
- `src/orison/ingest_flow.py` — step 7's module branch tag (*branch-selection*)
- `history/0006-ingest.md` — step 7's affirm/invert certificate (*certificate*)
- `docs/compaction.md` — step 8's row keyed by the preceding marker (*transition-record*)
- `src/orison/compaction_view.py` — step 8's module branch tag (*branch-selection*)
- `history/0007-compaction.md` — step 8's affirm/invert certificate (*certificate*)
- `docs/drain.md` — step 9's row keyed by the preceding marker (*transition-record*)
- `src/orison/drain_core.py` — step 9's module branch tag (*branch-selection*)
- `history/0008-drain.md` — step 9's affirm/invert certificate (*certificate*)
- `docs/envelope.md` — step 10's row keyed by the preceding marker (*transition-record*)
- `src/orison/envelope_gate.py` — step 10's module branch tag (*branch-selection*)
- `history/0009-envelope.md` — step 10's affirm/invert certificate (*certificate*)
- `docs/lineage.md` — step 11's row keyed by the preceding marker (*transition-record*)
- `src/orison/lineage_core.py` — step 11's module branch tag (*branch-selection*)
- `history/0010-lineage.md` — step 11's affirm/invert certificate (*certificate*)
- `docs/quota.md` — step 12's row keyed by the preceding marker (*transition-record*)
- `src/orison/quota_core.py` — step 12's module branch tag (*branch-selection*)
- `history/0011-quota.md` — step 12's affirm/invert certificate (*certificate*)
- `docs/throttle.md` — step 13's row keyed by the preceding marker (*transition-record*)
- `src/orison/throttle_flow.py` — step 13's module branch tag (*branch-selection*)
- `history/0012-throttle.md` — step 13's affirm/invert certificate (*certificate*)
- `docs/dispatch.md` — step 14's row keyed by the preceding marker (*transition-record*)
- `src/orison/dispatch_core.py` — step 14's module branch tag (*branch-selection*)
- `history/0013-dispatch.md` — step 14's affirm/invert certificate (*certificate*)
- `docs/schema.md` — step 15's row keyed by the preceding marker (*transition-record*)
- `src/orison/schema_store.py` — step 15's module branch tag (*branch-selection*)
- `history/0014-schema.md` — step 15's affirm/invert certificate (*certificate*)
- `docs/routing.md` — step 16's row keyed by the preceding marker (*transition-record*)
- `src/orison/routing_view.py` — step 16's module branch tag (*branch-selection*)
- `history/0015-routing.md` — step 16's affirm/invert certificate (*certificate*)
- `docs/rollup.md` — step 17's row keyed by the preceding marker (*transition-record*)
- `src/orison/rollup_gate.py` — step 17's module branch tag (*branch-selection*)
- `history/0016-rollup.md` — step 17's affirm/invert certificate (*certificate*)
- `docs/checkpoint.md` — step 18's row keyed by the preceding marker (*transition-record*)
- `src/orison/checkpoint_core.py` — step 18's module branch tag (*branch-selection*)
- `history/0017-checkpoint.md` — step 18's affirm/invert certificate (*certificate*)
- `docs/retention.md` — step 19's row keyed by the preceding marker (*transition-record*)
- `src/orison/retention_flow.py` — step 19's module branch tag (*branch-selection*)
- `history/0018-retention.md` — step 19's affirm/invert certificate (*certificate*)
- `docs/watermark.md` — step 20's row keyed by the preceding marker (*transition-record*)
- `src/orison/watermark_view.py` — step 20's module branch tag (*branch-selection*)
- `history/0019-watermark.md` — step 20's affirm/invert certificate (*certificate*)
- `docs/tenancy.md` — step 21's row keyed by the preceding marker (*transition-record*)
- `src/orison/tenancy_core.py` — step 21's module branch tag (*branch-selection*)
- `history/0020-tenancy.md` — step 21's affirm/invert certificate (*certificate*)
- `docs/reconcile.md` — step 22's row keyed by the preceding marker (*transition-record*)
- `src/orison/reconcile_store.py` — step 22's module branch tag (*branch-selection*)
- `history/0021-reconcile.md` — step 22's affirm/invert certificate (*certificate*)

## 6. Measured documents-only attack

The smallest documents-only attempt that completed a full 22-step graph walk used 23 files:
the start page and the 22 route documents.  It opened no manifest, module, or history file.
The best of its two consistent slot choices scored 4/9 and was `confidently_wrong`; therefore
the measured shortcut did not reconstruct the five checkpoints.  The 68 declared load-bearing
paths are the full-procedure declaration, while this attack demonstrates that the documents
alone do not supply a passing answer.

## 7. Grader and perturbations

The grader scores the five keys independently and also checks the exact key order, UTF-8
readability, and scope/integrity.  It reads no tools and runs no seed helper.  All five
unspecified formatting perturbations — no trailing newline, two trailing newlines, CRLF, one
leading blank line, and trailing spaces — remain correct at full score; no editable file exists.

## 8. Departure from the brief and uncertainty

There is no departure from the specified Shape A requirement.  The chain uses plainly stated
row lookup and conditional selection, not an encoding or judgement call.  The only assumption
made by the spec is the generated corpus contract that the first 22 manifest stages have
history entries; `_assert_layout()` fails the build if that measured premise is false.  The
measured budget is **2 turns** and **256 output tokens**: the deliverable is five lines, while
the extra output allowance covers the ordered replay bookkeeping.
