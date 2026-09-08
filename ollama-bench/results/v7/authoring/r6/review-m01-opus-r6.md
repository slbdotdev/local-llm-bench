verdict: PASS
fair: yes — every fact the answer needs is present, dated, and reachable; the prompt names each trap in prose without naming a file, and my blind solve matched `ref/` exactly.
solved_it: yes — I read `prompt.md` first, then the tree, and produced `checkpoint, envelope, replay, shard` / `24` / `RN-0212` before opening `ref/`; I nearly went wrong at `history/branches/README.md:3-5`, which calls `EFFECTIVE_DWELL_S` "the number actually honoured" and then names *that* number "the stage's dwell" — read literally that endorses the doc-versus-module comparison the grader scores `confidently_wrong`, and only the dated decision note plus the prompt's own "a document that still reads the same as always is not proof" sentence pull you off it.
checker: sound — 14/14 selfcheck cases land on their declared verdict *and* score under the Windows interpreter, including `unsafe: correct report, but a seed document repaired` (6/7, `unsafe`) and `shape: keys in the wrong order` (3/7, `confidently_wrong`); 7 subchecks, scope gate on, `stale_dwell` compared as an ordered list so the prompt's stated alphabetical order is enforced and comma/whitespace style is not.
shortcut: 21 files, score 7/7 — the floor is `history/branches/README.md`, the decision note, RN-0212, the 8 branch records of the 6 in-scope stages, those 6 component documents, and the 4 stale stages' modules. Five directory-wide greps reach the same 21 files in five commands but do not reduce the file count, and the grepped numbers *alone*, without the two rule files, yield `replay, retention, shard, throttle` / `42` or the raw `checkpoint, compaction, digest, envelope, replay, shard` / `148` — both graded `confidently_wrong`. Far above the five-file floor.
harvest: 20/20 by `dwell_s` — `grep -rni 'dwell_s' seed/` returns 43 lines and puts all 20 documented dwells and all 20 module constants on one screen. The answer cannot be finished from it: the branch records, the onboarding table and the two rules are all still required, and the harvested numbers on their own give a graded-wrong set. Frames: yes, and this is the one thing I would tighten — every component document is a byte-identical template with the value at line 17, every module has `EFFECTIVE_DWELL_S` at line 14, and the branch records' rationales are three template sentences perfectly correlated with their classification, so `tail -n1 seed/history/branches/*.md` sorts all 17 records into merged-and-documented / merged-and-not-documented / reverted / withdrawn without reading one record whole.
tools: clear — `r5/check_tools.py --verbose`: 20 seed tools run with no arguments, all `rc=0`, 0 bytes, 0 scored values, 0 declared units; no module prints a dwell.
notes_claims: verified — traversal floor 8221/32213 (25.5%) and thorough-solve 23134/32213 (71.8%) both reproduce to the token from `measure_material.per_file` when I rebuild the sets NOTES describes; `material_tokens` 32213 = 150240/4.664; reference answer is exactly 90 characters; 18 LOAD_BEARING paths across 7 hops matches `r2/check_load_bearing.py`; the four wrong-course sums (148 raw, 42 doc-versus-default, the 6-stage raw set) all recompute; `EFFECTIVE_DWELL_S` appears only in each stage's own module and twice in `history/branches/README.md`, never in the decision note.
tiers: Haiku fails at including `checkpoint` and `envelope` — two stages whose document, module constant and every other artifact agree, and which are stale only because an accepted merge in a branch record was never folded in, and which then contribute 0 to `net_dwell_change`; a careful Sonnet is not caught by the same step, because the prompt states that trap outright ("a document that still reads the same as always is not, on its own, proof that nothing changed") and the arithmetic is two additions.
workhorse_failure: real — the failing step is reconciling three independent rulings (replay the whole branch history, apply the 2034-04-01 onboarding cutoff from RN-0212, override README.md's stale "without exception" claim) against 20 stages; nothing is obfuscated, encoded, split across lines, or arithmetically heavy, so a workhorse that fails here failed to reconcile, not to decode.
hard_to_do: yes — the reading is wide and the reconciliation is three-way, but the writing is three lines and 90 characters, and each of the four graded wrong courses is a complete, confident, well-formed answer.
fix: none required for PASS; recommended, in `history/branches/README.md`, replace "the module's `EFFECTIVE_DWELL_S` constant is the number actually honoured. Once a stage enters this workflow this project calls that number the stage's **dwell**" with wording that names the *replayed* value as the dwell (e.g. "the module's `EFFECTIVE_DWELL_S` constant is the value a revert restores to; the number this workflow tracks, replayed by the decision note below, is what this project calls the stage's **dwell**"), so the definition does not read as an endorsement of the doc-versus-module shortcut.

---

## Findings, by severity

**1. `seed/history/branches/README.md:3-5` — the definition sentence can be read as endorsing the graded-wrong shortcut.**
"Every branch under this directory proposes a new value for one stage's `dwell_s` configuration
row - the module's `EFFECTIVE_DWELL_S` constant is the number actually honoured. Once a stage
enters this workflow this project calls that number the stage's **dwell**." Taken literally,
"that number" is `EFFECTIVE_DWELL_S`, which makes *stale* mean "document disagrees with module
constant" — exactly the near-miss `selfcheck.py` grades `confidently_wrong` (`replay, retention,
shard, throttle` / `42`). It is also flatly untrue for `checkpoint`, whose merge (1155) was
accepted and whose `EFFECTIVE_DWELL_S` is 1143. Not a REVISE: the decision note is dated,
"in force", and explicitly governs replay, and the prompt independently warns that an unchanged
document proves nothing. But it is a coin-flip a one-clause edit removes. Fix as above.

**2. `seed/README.md:11`, `seed/README.md:47`, `seed/docs/operations.md:45` — `docs/policy/` is
referenced three times and does not exist.**
The reading order lists it third as "the rules that outrank both of the above", and the
conventions say "a policy under `docs/policy/` outranks everything else". The prompt twice tells
the solver to "find the rule that is currently in force", so this points the solver's first
search at a directory that is not in the tree. It costs tool calls rather than correctness —
the two governing notes that do exist are complementary, not in conflict — but it is a dangling
pointer in the one place the task tells the reader to look. Fix: either add the `docs/policy/`
directory with a note that does not touch dwell, or drop the three references.

**3. Frame uniformity is high enough to make a per-unit read optional for the *values*.**
`seed/docs/<stage>.md:17` and `seed/src/cordage/<module>.py:14` are the decisive lines in
byte-identical templates across all 20 units, and the branch records' closing rationale is one
of three fixed sentences that gives away the classification
("...the component document was never brought in line with it" for the two forgotten merges,
"...folded into the component document the same week it merged" for the two that were, "...asked
for the prior number back" for the four reverts, "...the existing dwell was not the cause" for
the three withdrawals), so `tail -n1 seed/history/branches/*.md` sorts every record without
reading one. This does not reach the answer — the onboarding cutoff and the two rules are still
required, and the file count does not drop below 21 — so it is not a rung-0 failure. Fix, if
wanted: vary the rationale wording per record so the classification is not a template constant.

## What I checked

- `prompt.md` read first and cold; deliverable predicted as three ordered `key: value` lines.
- Blind solve from `seed/` alone, then compared with `ref/dwell-audit.txt` — exact match.
  In-scope (onboarded >= 2034-04-01): checkpoint, envelope, replay, retention, shard, throttle.
  Replayed: checkpoint 1155 vs doc 1143 (stale, +0); envelope 1222 vs doc 1198 (stale, +0);
  replay reverted to 1022 vs doc 1030 (stale, +8); shard reverted to 1077 vs doc 1093
  (stale, +16); retention 1166 = doc (not stale); throttle 1061 = doc (not stale). Sum 24.
  Out of scope and correctly excluded: compaction (+66) and digest (+58), the two largest
  divergences in the tree; audit, ledger, rollup carry withdrawn-only records and are not stale
  under any reading.
- Every `NOTES.md` number recomputed from the tree (see `notes_claims`).
- Harvest attack by hand, per step 5; frames checked at fixed offsets and with `tail -n1`.

## Validator results, run once each from `authoring/`

    /mnt/c/.../python.exe cand-glm/m01-main-glm/selfcheck.py
        14/14 PASS, "all checks pass", rc 0
    python3 probe_candidate.py cand-glm/m01-main-glm
        CLEAN — reference 7/7 correct, empty 1/7 visibly_failed, 5 whitespace perturbations 7/7 correct
    python3 probe_idempotence.py cand-glm/m01-main-glm
        7/7 correct -> 7/7 correct, ok; 0 not idempotent
    python3 r5/check_rung0.py cand-glm/m01-main-glm
        rung 0 clear; narrowest covering prompt word 'dwell' hits 61 of 107 files (threshold 34)
    python3 r2/check_index_leak.py m01-main-glm
        clean — 'EFFECTIVE_DWELL_S' appears only in each stage's own module
    python3 r2/check_load_bearing.py cand-glm/m01-main-glm
        18 paths, 7 hops, 6284 lb tokens / 32213 material, 19.5%; declaration readable and complete
    python3 r5/check_tools.py cand-glm/m01-main-glm --verbose
        tools clear — 20 tools, rc=0, 0 bytes, 0 scored values, 0 declared units

`r5/check_harvest.py` not run: these specs predate `harvest_units()`, per the method.

## What remains uncertain

- I did not run `git`, so I judged only the tree as it stands and cannot say which lines the
  revision changed; my "harder to do, not harder to understand" call is a judgement about the
  present build, not a diff.
- Whether finding 1 is worth a rebuild is the control session's call. It did not change my own
  answer, and the grader punishes the reading it invites, which is the design's intent — but it
  is the single place where a correct solver and a `confidently_wrong` one part on a sentence's
  antecedent rather than on a rule.
- Report path: the cover brief names `r6/review-m01-opus-r6.md`; the method's own Report section
  names `cand-glm/m01-main-glm/reviews/opus-2026-09-08.md`. The brief binds the variables, and
  its blind rules forbid the `reviews/` directory, so I wrote only the brief's path.
