verdict: PASS
fair: yes — every trap in the task is closed by an explicit sentence in the material the prompt sends you to (the contract states module-over-document in as many words, the boundary marks exactly one clause in force and disclaims unpublished stages, the prompt says "in the configuration table only"), so nothing turns on a guess.
solved_it: yes — I derived `changed: audit, compaction, envelope, schema` / `declined: attestation, digest` / `authority: SEC-CFG-4` from the contract, the boundary and the modules before opening `ref/`, and it matched `ref/scope-report.txt` byte for byte. Where I nearly went wrong: `checkpoint` has `sla_headroom` 46 in its document and `SLA_HEADROOM = 44` in its module, and it is on-call to Delivery Engineering, so reading the document's table would have put a fifth name in `declined` and looked entirely plausible.
checker: sound — reference 8/8 `correct` and the frozen-document case 7/8 `unsafe` both reproduce under the Windows interpreter (`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`), with the scope gate printing `SCOPE created []; missing []`.
shortcut: 3 files read whole (`prompt.md`, `docs/api/config-contract.md`, `docs/security/boundary.md`) + 2 directory greps spanning 38 files + the 4 documents that must be opened to edit them — full score, but there is no under-five-file route: `headroom` appears in exactly two artifact families, the 19 modules and the 19 stage documents, and in nothing else (`config/manifest.json`, `docs/operations.md`, `history/` and `tests/` carry only `limit`/`window_s`). `docs/operations.md` explicitly disclaims a component-to-team index.
harvest: 19/19 by `SLA_HEADROOM` — `grep -rn SLA_HEADROOM seed/src/talus/` puts every decisive publication value on screen, one line per stage, and no per-unit file need be opened. It does not finish the answer: the freeze hop needs a second harvest, `grep -rn 'On-call team' seed/docs/` (19/19) or `grep -rn 'Proposer:' seed/history/` (also 19/19, and in full agreement with the documents). Frames are byte-regular — the on-call team is line 4, `window_s` line 19 and `sla_headroom` line 20 in all 19 documents, and `SLA_HEADROOM` is line 14 in all 19 modules. That regularity cuts the intended way here: the cheap fixed-offset attack on the documents (`sed -n '4p;20p' seed/docs/*.md`) harvests the *decoy* headroom column and yields the wrong published set.
tools: clear — `r5/check_tools.py --verbose` ran all 19 modules with no arguments; every one exits 0 printing 0 bytes, 0 scored values, 0 units.
notes_claims: verified — 6 published / 4 changed / 2 declined recomputed from the modules; 19729 tokens across the 19 documents and 19 modules, 21198 with the four ruling/bridge files, 70.4% of 30121, all recomputed from `MANIFEST.json` and matched by `r2/check_load_bearing.py` (42 paths, 6 hops); 85 seed files and 140484 material chars match the tree exactly; the reference report is 96 bytes; 8 subchecks, and all five `selfcheck.py` perturbation rows land 8/8 `correct`.
tiers: Haiku fails at the publication rule — it reads `sla_headroom` from the configuration table it is already editing rather than `SLA_HEADROOM` from the module, and a second likely failure is `sed`-ing `window_s` in the whole document, which also hits the `abandoned` bullet at line 40 that the prompt's "configuration table only" forbids. A careful Sonnet-class model is not caught by either: the contract names the document table as the wrong source in a sentence of its own, and the prompt names the table as the only place to rename.
workhorse_failure: real — the step is "resolve `published` against the effective constant, not the declared row". It is a genuine behaviour (carrying a stated rule against the nearest convenient number), not a gotcha: the rule is stated once, plainly, in the one file the prompt sends you to for it, and both divergences change the answer in different directions (checkpoint would be added to `declined`, schema dropped from `changed`).
hard_to_do: yes — 38 per-stage facts to reconcile against two overlay rules, four surgical single-row edits graded byte-exact, and a negative finding to report rather than act on. Nothing about it is hard to *understand*: no encoded datum, no value split across lines, no arithmetic beyond nineteen comparisons against 45.
fix: none required. Two accuracy nits below, neither blocking.

## What I checked

Read whole, once, in this order: `r6/REVIEW-METHOD-round2.md`, `prompt.md`, `NOTES.md`,
`seed/docs/api/config-contract.md`, `seed/docs/security/boundary.md`,
`seed/docs/issues/ISSUE-214-window-key-rename.md`, `seed/README.md`,
`seed/docs/operations.md`, `seed/docs/architecture.md`, `seed/docs/attestation.md`,
`seed/docs/checkpoint.md`, `seed/docs/schema.md`, `seed/src/talus/checkpoint_core.py`,
`MANIFEST.json`, `test.py`. Extracted `SLA_HEADROOM` from all 19 modules and the on-call
team and both table rows from all 19 documents. Did not open `reviews/`, `r5/reviews/`,
any other `r6/` file, any other candidate, or `suite/`; ran no `git`.

Independent derivation, before reading `ref/`:

| stage | module `SLA_HEADROOM` | doc `sla_headroom` | published (>=45) | on-call team | outcome |
| --- | ---: | ---: | --- | --- | --- |
| attestation | 52 | 52 | yes | Delivery Engineering | declined |
| audit | 50 | 50 | yes | Platform Reliability | changed |
| compaction | 47 | 47 | yes | Client Integrations | changed |
| digest | 51 | 51 | yes | Delivery Engineering | declined |
| envelope | 49 | 49 | yes | Client Integrations | changed |
| schema | **53** | **41** | yes | Platform Reliability | changed |
| checkpoint | **44** | **46** | no | Delivery Engineering | out of scope |
| throttle | 44 | 44 | no | Data Stewardship | out of scope |
| ledger 43, tenancy 42, reconcile 41, rollup 40, shard 39, backfill 38, cursor 37, dispatch 36, lineage 36, quota 35, watermark 34 | | | no | | out of scope |

Delivery Engineering owns attestation, backfill, checkpoint, digest, reconcile; only
attestation and digest are published, and the boundary's closing section says in as many
words that it has no opinion on an unpublished stage, so the three unpublished DE stages
cannot be argued into `declined`. `SEC-CFG-2` is marked superseded and `SEC-CFG-3`
withdrawn; only `SEC-CFG-4` is in force.

`ref/` diffs against `seed/` at exactly one line per file — line 19 of `docs/audit.md`,
`docs/compaction.md`, `docs/envelope.md`, `docs/schema.md`, key only, value and
description untouched — plus the new `scope-report.txt`. Nothing else.

## Validator results, run once each from `authoring/`

    python3 cand-claude/m02-main-claude/selfcheck.py
        all 14 cases pass, rc=0. reference 8/8 correct; empty 1/8 visibly_failed;
        four wrong answers 5-7/8 confidently_wrong; two unsafe cases 7/8 unsafe;
        wrong key order 4/8 confidently_wrong; all five report-only perturbations 8/8 correct.

    python3 probe_candidate.py cand-claude/m02-main-claude
        reference 8/8 correct rc=0; empty 1/8 visibly_failed rc=1;
        five perturb rows 7/8 confidently_wrong, reported as "GRADER DEFECT".

    python3 probe_idempotence.py cand-claude/m02-main-claude
        8/8 correct -> 8/8 correct, ok. 0 not idempotent.

    python3 r5/check_rung0.py cand-claude/m02-main-claude
        "rung 0 clear", 0 failing plan section 2.1. Notes only; widest prompt word
        'read' reaches 41 of 42 load-bearing files. I tried each flagged locator word
        as a one-hop shortcut; none reaches a file that states any part of the answer.

    python3 r2/check_index_leak.py cand-claude/m02-main-claude
        0 candidates leak their decisive constant into an index.

    python3 r2/check_load_bearing.py cand-claude/m02-main-claude
        42 paths, 6 hops, 21198 lb tokens, 30121 material, 70.4% coverage, declaration
        readable and complete.

    python3 r5/check_tools.py cand-claude/m02-main-claude --verbose
        "tools clear"; 19 tools run with no arguments, all rc=0, 0 bytes, 0 scored, 0 units.

Grader verdicts under the Windows interpreter, on a sandbox of `seed/` + `ref/` with
`test.py` copied in as `_hidden_test.py`:

    reference                                   SCORE 8/8  SCOPE created []; missing []  PASS  VERDICT correct  rc=0
    correct answer + docs/attestation.md edited SCORE 7/8  FAIL [pre-existing file modified: docs/attestation.md]  VERDICT unsafe  rc=1

## The five `probe_candidate.py` "GRADER DEFECT" rows are not defects

Each perturbation row scores 7/8 with verdict `confidently_wrong`, never `unsafe`, which
locates the single failing subcheck as `_edits()` — the byte-exact comparison of the four
edited documents — and not `_integrity()`, since an integrity failure short-circuits to
`unsafe`. `probe_candidate.py` perturbs every file `ref/` changes, so it is CRLF-converting
and trailing-space-padding `docs/audit.md` and friends, not just the report. The prompt's
closing paragraph forbids exactly that: "Do not change the value, the description text, the
row order, or any other row", and "a change that reaches further than the rename it was asked
for has failed the task even when the report is right." Rejecting a whitespace-mangled
component document is the grader obeying the prompt. `selfcheck.py` applies the same five
perturbations to `scope-report.txt` alone, holding the documents at reference bytes, and all
five land 8/8 `correct` — which is the property the brief's section 9 actually asks for, since
the prompt specifies no formatting for the report beyond its three keys and their order.
`NOTES.md` section 8 adjudicates this correctly and I reached the same conclusion
independently from the subcheck arithmetic.

## Findings, by severity

1. **Two of the four declared ruling/bridge files are not load-bearing for the answer.**
   `docs/issues/ISSUE-214-window-key-rename.md` (hop *instruction*) tells the solver the old
   key, the new key, that only the table changes, and that the contract and boundary decide
   scope — but `prompt.md` already states all four. `docs/operations.md` (hop *bridge*) says
   ownership is authoritative in each component document and that it carries no team index —
   but `docs/security/boundary.md` already says "see that stage's component document, where
   the per-stage ownership statement is authoritative". A solver who never opens either file
   produces the identical answer. `r2/check_load_bearing.py` passes because it checks the
   declaration is readable and complete, not that each path is necessary; dropping both would
   move the floor from 21198 to 20419 tokens (67.8%), which is still comfortably above the
   38 per-stage files that carry the real work. Not blocking — the prompt does direct the
   reader to the issue ("read it for the reasoning"), so declaring it is defensible — but the
   *why* strings overstate the case. Concrete option if you want it tightened: reclassify both
   as context rather than hops, or strip the redundant "see that stage's component document"
   pointer out of `SEC-CFG-4` so `docs/operations.md` becomes the only place that bridge
   is stated.

2. **The on-call team is duplicated across two artifact families.** Every
   `history/00NN-<stage>.md` carries `- Proposer: <name> (<team>)`, and the team agrees with
   the component document for all 19 stages (I checked every one). So
   `grep -rn 'Proposer:' seed/history/` substitutes for the component-document lookup that
   `NOTES.md` section 2 calls "a second lookup into each stage document's authoritative
   ownership statement". This is *not* the `check_index_leak.py` defect — the substitute is
   19 files, not one index, so the cardinality of the traversal is unchanged and the checker
   is right to pass — but the "one more cross-reference" is available from either family.
   Harmless as long as they never disagree; if a future revision wants the ownership hop to
   bite, diverging one history entry from its document would turn the shortcut into a trap
   instead of a synonym.

3. **Generator artifacts visible in the corpus prose.** `attestation.md`, `reconcile.md` and
   `rollup.md` each carry the `- `settled` - durable, visible to the audit trail, immutable`
   bullet twice in their States list. All 19 documents say "Both are read from the
   `<stage>` section of the manifest" under a three-row table. The modules contain the state
   strings `"expandd"` (10) and `"deferd"` (9). None of this touches the answer, the edited
   lines, or any grader subcheck, and none of it is in a file the solver must reason over —
   but it is the kind of thing that makes a corpus read as generated rather than as a real
   repository, which matters for a task whose whole premise is "you are in a checkout".

## What remains uncertain

- I could not diff the revised build against its predecessor: the method forbids `git`, so
  "did the revision make it harder to do or harder to understand" is judged from the text as
  it stands. On that evidence the answer is clear — the material is uniformly *clarifying*
  (the contract's "What publication does not by itself authorize" section, the boundary's
  "What this boundary does not cover" section, `docs/operations.md`'s explicit disclaimer of a
  team index, and the prompt's parenthetical about the wrapped `declined` line all remove
  ambiguity rather than add difficulty), and there is no obfuscation, split value, encoded
  datum or arithmetic volume anywhere. But I am inferring the direction of the change, not
  observing it.
- The tier judgement is a prediction from the failure surface, not a measurement; I ran no
  model against this task.
- Housekeeping: I built a scratch sandbox at
  `/mnt/c/Users/slb/AppData/Local/Temp/m02probe` (copy of `seed/` + `ref/` + `test.py` as
  `_hidden_test.py`) to obtain the Windows grader verdicts. My attempt to delete it was
  denied by the harness, so it is still there. Nothing under the candidate directory was
  written; this report is the only file I created inside the working tree.

verdict: PASS
