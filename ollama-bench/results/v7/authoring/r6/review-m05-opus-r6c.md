verdict: PASS
fair: yes — I solved it blind from the prompt alone and my checklist is byte-identical to `ref/doc-checklist.txt`; the prompt states the rule, the direction and the output format without ambiguity.
solved_it: yes — matched `ref/` exactly (all 20 rows, `corrected_count: 4`, `authoritative_source: DR-0091`); the one place I nearly went wrong was reading "the value the code actually uses in the stage's own module" as `window_s` (what the class actually reads) rather than `ACTIVE_WINDOW_S` (a constant no code path touches) — DR-0091 names the constant explicitly and closes it, but only because that record is mandatory reading anyway.
checker: sound — 8 subchecks, atomic groups (16 MATCHES rows / 4 CORRECTED rows / count / authority); I ran `selfcheck.py` under both `python3` and `/mnt/c/Users/slb/scoop/apps/python/current/python.exe` and all 13 cases agree, including the two `unsafe` cases (seed document repaired; scratch file left behind).
shortcut: 45 files (5 hand-opened + 2 tree-wide greps over the other 40), score 8/8 — open `docs/design/DR-0091-window-authority.md`, `docs/migrations/MIG-0014-window-rebase.md`, `docs/design/DR-0055-window-consistency.md` (which hands you both grep tokens), `tests/test_window_migration_coverage.py` and `config/manifest.json`, then grep the 40 numbers off screen. Well above the five-file rung-0 bar; no route under five files exists, because no index repeats either constant.
harvest: 20/20 by `enforced_window_s`, and a second 20/20 by `ACTIVE_WINDOW_S` — neither finishes alone, both together finish it without opening a single per-stage file. Frames: the value-bearing lines are byte-identical apart from the integer, but line offsets are shuffled across all 40 files (docs 17–36, modules 14–33), so `tail -n1` and any fixed offset fail.
tools: clear — 20 seed modules run with no arguments, all rc=0, 0 bytes printed, 0 scored values.
notes_claims: **one claim failed** — NOTES.md:43 "the current rule and the superseded one share almost every word (only 'in force' versus 'superseded' tells them apart)". Measured word-set Jaccard between the two records is 0.263 (41 shared of 156 union), and `grep -rln governs seed/` returns DR-0091 and nothing else. Every other number in NOTES verifies (see evidence below).
tiers: Haiku fails at the exemption hop — MIG-0014 names no stages, points at a test file, and the exempt set is a Python list literal whose 5 stages all have visibly disagreeing numbers that must be suppressed; a careful Sonnet follows the pointer and is not caught.
workhorse_failure: real — the failure is the two-hop indirection plus suppressing 5 visible disagreements, a reasoning step, not transcription volume; volume (40 values under atomic grading) is a secondary contributor, not the discriminator.
hard_to_do: yes — 44 files must be reconciled, and the prompt's vocabulary locates none of the 40 that carry the numbers.
fix: reword `prompt.md:8` so it does not reuse DR-0091's own wording — drop "governs" and the verbatim clause "the document is what an operator was told and the module is what the code does", and state the direction in neutral terms ("the module's value is the correct one"). At present `grep -rln governs` lands on the in-force record alone and the DR-0055 decoy is never encountered, so one of the two declared wrong courses is not actually exercised.

---

## What I checked

Read in this order, each whole and once: `prompt.md`; then my own solution from the tree
(`config/manifest.json`, all 20 `docs/*.md`, all 20 `src/hearth/*.py`, both design records, the
migration note, the exemption test); then `ref/doc-checklist.txt`; then `NOTES.md`,
`MANIFEST.json`, `test.py`, `selfcheck.py`. Blind rules held: I opened no `reviews/` directory,
no `r5/reviews/`, no other `r6/` file except `REVIEW-METHOD-round2.md`, no other candidate, and
ran no `git`. Nothing under `suite/` was touched. I wrote only this file.

## Findings, most severe first

### 1. Every bridge artifact is reachable by a one-grep prompt word; the DR-0055 decoy is never met

`prompt.md:8` paraphrases `seed/docs/design/DR-0091-window-authority.md:9` almost verbatim —
the clause "the document is what an operator was told and the module is what the code does"
is shared word-for-word, and the prompt's own "**the module governs**" is the record's own
phrase.

    grep -rln governs seed/          -> docs/design/DR-0091-window-authority.md   (1 file)
    grep -rln intentionally seed/    -> docs/migrations/MIG-0014-window-rebase.md
                                        tests/test_window_migration_coverage.py   (2 files)

The prompt supplies both words ("the module governs"; "their document intentionally still
shows the number from before the move"). So all three bridge artifacts fall out of two greps,
and a solver who greps never opens `docs/design/DR-0055-window-consistency.md` at all.
NOTES §3 declares "cite the superseded record" as one of the two distinguishing wrong courses;
in practice the task's discrimination rests almost entirely on the other one (the exemption).
`r5/check_rung0.py` flags exactly this and asks a reviewer to try each locator word as a
one-hop shortcut — I did, and they work.

This is a weakening of the design's claim, not a fairness or grading defect: rung 0 still
holds, because no prompt word locates any of the 40 files carrying the numbers (the widest,
`stage`, reaches 45 of 47 load-bearing paths and so discriminates nothing).

### 2. Two greps put all 40 decisive values on screen

    grep -rn 'enforced_window_s' seed/docs/    -> 20/20 documented values
    grep -rn 'ACTIVE_WINDOW_S'   seed/src/     -> 20/20 module values

Both frames are byte-identical apart from the integer, and the stage identity is in the
filename, so the whole comparison is completable without opening one per-stage file. Neither
token is in the prompt, but `seed/docs/migrations/MIG-0014-window-rebase.md:14` explicitly
sends the solver to DR-0055 "for the historical row's exact field name", and
`seed/docs/design/DR-0055-window-consistency.md:7,9` names both `enforced_window_s` and
`ACTIVE_WINDOW_S`. So the tokens are two hops from the prompt, and the declared 74.6%
traversal is reachable as ~5 files plus two greps.

Under the method's stated bars this does not trip a REVISE: step 4 asks for a route under five
files (none exists), and step 5 asks for the best *single* grep (neither one finishes). I record
it as the sharpest remaining attack on this slot.

### 3. 10.2% of the material is content-free filler

    190 lines  `# placement marker NN`                              in 19 of 21 modules
    190 rows   `| \`window_note_NN\` | retained | ... |`            in 19 of 20 component docs
    16,340 chars = 10.2% of the 160,441-char seed = ~3,503 of 34,400 declared tokens

Its only function is to shuffle the line offset of the value-bearing line, and at that it
succeeds (finding 2: no fixed offset, `tail -n1` useless). Two costs. First, it is visible
authoring scaffolding to the model under test:
`seed/src/hearth/retention_gate.py:14-24` is eleven consecutive `# placement marker` comments
and `ACTIVE_WINDOW_S` is line 25 — the filler block *signposts* the planted constant in every
module that has one. Second, it is counted as material against the band
(`MANIFEST.json:11` "hand-overlaid to land inside the 29,000-36,000 main band"). I checked
whether the band depends on it: without the filler the corpus is ~30,900 tokens, still in
band, so the band survives its removal. Not a REVISE — it is padding, not obfuscation; it
hides no value, splits nothing across lines, and costs Sonnet nothing.

### 4. All 20 component documents contradict their own configuration table

Every doc says "Both are read from the `<stage>` section of the manifest by `build_<stage>`"
(`seed/docs/retention.md:19` and 19 others) while its table now lists 3 to 21 keys — e.g.
`seed/docs/checkpoint.md:17-31` is fourteen `window_note_NN` rows plus `enforced_window_s`
between `window_s` and that sentence. A realism defect introduced by the filler of finding 3,
not a fairness one: `prompt.md:4` names the row to use ("an enforced-window setting in its
configuration table") and there is exactly one such row per doc.

### 5. `ACTIVE_WINDOW_S` is dead code

No module reads it — `seed/src/hearth/quota_flow.py:14` defines it and lines 21 and 84 show
the class and builder using `window_s` from the manifest instead. The prompt
(`prompt.md:4`) says to check the document against "the value the code actually uses in the
stage's own module", and the value the code actually uses is `window_s`. The tension is closed
by `seed/docs/design/DR-0091-window-authority.md:9`, which names `ACTIVE_WINDOW_S` explicitly
and which the solver must read anyway for the authority identifier. Fair, but the prompt's
phrase is literally false of the tree; a solver who trusts the prompt over the design record
answers `window_s` and loses everything. I flag it because it is the one place my blind
reading and the reference nearly diverged.

## Exact evidence

Independent recomputation from the tree (docs' `enforced_window_s` vs modules'
`ACTIVE_WINDOW_S`, minus `MIGRATED_STAGES`, in manifest order) reproduces
`ref/doc-checklist.txt` byte for byte.

Nine stages disagree: quota (2020/2013), ledger (2274/2269), backfill (2136/2126),
checkpoint (2077/2091), reconcile (2192/2177), rollup (2177/2156), digest (2042/2022),
drain (2193/2221), audit (2258/2233). Five of the nine are exempt per
`seed/tests/test_window_migration_coverage.py` (audit, backfill, digest, ledger, reconcile),
leaving 4 corrected: quota 2013, checkpoint 2091, rollup 2156, drain 2221. All five exempt
stages do visibly disagree, as NOTES §2 claims.

NOTES numbers, all verified against the tree:

| claim | measured |
| --- | --- |
| 4 corrected: checkpoint, drain, quota, rollup | confirmed |
| 5 exempt: audit, backfill, digest, ledger, reconcile | confirmed |
| LOAD_BEARING 47 paths, 9 hops, 25,653 tokens, 74.6% | 47 unique paths, 9 hops, 25,653, 74.6% |
| trial traversal 25,472 tokens, 74.0% | = 25,653 − `tests/test_audit.py` (163) − `src/hearth/__init__.py` (18); consistent |
| reference answer is 416 characters | `wc -c` = 416 |
| MANIFEST 34,400 tokens / 160,441 chars / 90 files | file-map sums to 34,400 over 90 entries; `find` counts 90 files, 160,441 chars |
| 8 subchecks, 16-row group, 4-row group | confirmed in `test.py` CONFIG |
| `check_index_leak` clean on `ACTIVE_WINDOW_S` | clean; the 2xxx hits elsewhere are CHANGELOG years (2033/2034/2035), none colliding |
| "no single grep assembles it" | true as stated |
| "the two records share almost every word" | **false** — Jaccard 0.263, and `governs` is unique to DR-0091 |

Validators, run once each from `authoring/`:

    python3 cand-claude/m05-main-claude/selfcheck.py        all 13 cases pass ("all checks pass")
    ...same under the Windows interpreter                    identical, all 13 pass
    python3 probe_candidate.py cand-claude/m05-main-claude   CLEAN (ref 8/8 correct; empty 1/8; 5 perturbations 8/8)
    python3 probe_idempotence.py cand-claude/m05-main-claude 8/8 correct -> 8/8 correct, ok
    python3 r5/check_rung0.py cand-claude/m05-main-claude    rung 0 clear (with the locator-word notes acted on above)
    python3 r2/check_index_leak.py m05-main-claude           clean
    python3 r2/check_load_bearing.py cand-claude/m05-main-claude  47 paths, 9 hops, 25,653/34,400, 74.6%
    python3 r5/check_tools.py cand-claude/m05-main-claude --verbose  tools clear, 20 tools rc=0, 0 bytes

## Did the revision make it harder to do, or harder to understand?

Harder to **do**, in the part that counts. Moving the checked property off `window_s` onto a
pair of constants that appear nowhere but the 40 per-stage files is a real fix: `manifest.json`
and `docs/operations.md` still carry every stage's `window_s`, so under the old property the
task was answerable without opening a module, and it no longer is. The offset-shuffling filler
(finding 3) makes it neither harder to do nor harder to understand — it defeats fixed-offset
harvesting and costs 10% of the corpus for that. Nothing was obfuscated, no value is split
across lines, nothing is encoded, and the arithmetic is 20 integer comparisons.

## What remains uncertain

- The 25,472-token trial traversal is a separately measured figure I cannot reproduce from the
  tree; it is arithmetically consistent with LOAD_BEARING minus the two context files, which is
  the only reading under which it checks out.
- Whether the campaign wants the two-grep route of finding 2 treated as a harvest failure is a
  judgment above this seat. Under the method as written it is not one, and I have judged it
  PASS on that basis; if the bar is meant to be "no small number of greps", this slot fails it
  and the fix is to give the two constants different names per stage.
- I did not attempt an execution-based shortcut (importing the modules and reflecting on
  `ACTIVE_WINDOW_S`); it would read the same 20 files and so cannot beat the grep route.

verdict: PASS
