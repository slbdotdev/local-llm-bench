verdict: REVISE
fair: yes — nothing here is unfair to a Sonnet-class model; the defect is the opposite, the task is too easy to shortcut.
solved_it: yes — my independent answer is byte-identical to `ref/doc-checklist.txt`. The one place I nearly went wrong is the intended trap: five of the nine stages whose numbers disagree are exempt and must still read `MATCHES`. I caught it only because the prompt itself told me exempt rows are `MATCHES` regardless.
checker: sound — 8 subchecks (3 shape + 4 groups + integrity); `selfcheck.py` 13/13, `probe_candidate.py` CLEAN, `probe_idempotence.py` ok, and I graded both the reference and my own shortcut answer at 8/8 PASS on `/mnt/c/Users/slb/scoop/apps/python/current/python.exe` per plan-r3 4.1.
shortcut: 1 file, score 8/8 — `config/manifest.json` opened for row order, plus three greps (`enforced_window_s|ACTIVE_WINDOW_S`, `exempt`, `in force`). Verified end to end: reproduces `ref/` exactly, PASS on the Windows interpreter.
harvest: 20/20 by `enforced_window_s`, and 40/40 both sides in one alternation grep — every token the prompt names verbatim.
tools: clear — `r5/check_tools.py` verbose, 20 modules, all rc=0, 0 bytes, no scored or per-unit values.
notes_claims: `NOTES.md` §2 "No single grep assembles it either" — false; one grep puts all 40 decisive values on screen. Every *numeric* claim verified (416 chars, 90 seed files, 143847 chars, 47 LOAD_BEARING paths, 9 hops, 4 corrected, 5 exempt).
tiers: both pass — the only real discriminator is the exemption, and the prompt word `exempt` greps straight to the list that holds it.
workhorse_failure: defect — a Sonnet-class model that failed here would fail by miscomparing 20 pairs, not by lacking the behaviour, because the prompt supplies the governing rule and the exemption semantics itself.
hard_to_do: no — after two greps it is bookkeeping over 20 pairs.
fix: stop the prompt naming both grep tokens verbatim (say "the constant the module actually enforces" without printing `ACTIVE_WINDOW_S`), give each module's constant a stage-specific name so no single token spans stages, and replace the `2000 + 13i` run with unpatterned values.

---

## Findings, by severity

**1. Rung-0 failure: full score from one opened file plus three greps.**
`prompt.md:5-7,17-19` — I built the deliverable from `seed/config/manifest.json` alone (row
order) plus three greps, and it reproduced `ref/doc-checklist.txt` byte for byte and graded
**SCORE 8/8 / PASS / VERDICT correct** on the Windows interpreter. The three greps:

    grep -rnE 'enforced_window_s|ACTIVE_WINDOW_S' docs src   # 40/40 values
    grep -rni exempt tests                                   # the exempt list
    grep -rl 'in force' docs/design                          # DR-0091, from the filename

The method's step 4 threshold is "under five files for full score is a rung-0 failure and a
REVISE". This is one file.

**2. The prompt hands over both harvest tokens verbatim.**
`prompt.md:6-8` names `enforced_window_s` and `ACTIVE_WINDOW_S` in its own text, and both appear
verbatim as file content at fixed offsets: every stage doc carries the row at **line 17**
(`docs/quota.md:17`), every module the constant at **line 14** (`src/hearth/quota_flow.py:14`).
The round-two standard is that a main-band answer must reconcile facts "the prompt's own
vocabulary cannot locate". Here the prompt's vocabulary locates all 40 decisive values, and
`r5/check_rung0.py` independently flags `exempt`, `baseline`, `historical`, `intentionally`,
`matches` and `shows` as one-hop locators for the bridge artifacts.

**3. Module values are an exact arithmetic progression, so the 20 modules need never be read.**
`src/hearth/retention_gate.py:14` through `src/hearth/audit_core.py:14` — every
`ACTIVE_WINDOW_S` is exactly `2000 + 13i` at manifest index `i`, for all 20 stages with no
exception. I generated the whole checklist from that formula having read **zero** module files,
and it reproduced `ref/` exactly. This invalidates 20 of the 47 declared `LOAD_BEARING` paths
(the `effective-value` hop) as genuinely necessary material — roughly 35% of the claimed
traversal — and `NOTES.md` §2's "every component document and every module" is not true of the
modules.

**4. The prompt pre-empts both wrong courses the task's discrimination rests on.**
`NOTES.md` §3 stakes the whole distinguishing condition on two errors, and `prompt.md` rules out
both before the solver opens a file: `prompt.md:7` states **"Where the two disagree, the module
governs"**, which is the entire content of DR-0091, so the DR-0055 decoy cannot catch a solver
who read the prompt — only the *identifier string* remains to be found. `prompt.md:14-15` states
exempt rows are "`MATCHES` regardless of what the numbers say", so the migration-note trap is
likewise pre-announced. What is left is locating two short facts and comparing 20 pairs.

**5. `NOTES.md` §2's single-grep defence is false.**
`NOTES.md` §2, "No single grep assembles it either: ... the per-stage numbers are a markdown
table cell beside a Python constant that no generated index repeats." The second clause is true
(`r2/check_index_leak.py` is clean, and I confirmed no module value appears outside its own
module). The first is not: one alternation grep returns all 40 values. The index-leak fix from
the last revision worked; the claim built on top of it overreaches.

**6. The grader's docstring names a constant that does not exist.**
`test.py:4-9` describes the module constant as `ENFORCED_WINDOW_S` twice; the tree's constant is
`ACTIVE_WINDOW_S`. Stale after the rename this revision performed. Docstring only — no effect on
scoring — but it is the grader's own account of what it grades.

**7. The prompt promises a decoy list that does not exist.**
`prompt.md:15-16` — "find the current, complete list, not a partial or an out-of-date one."
There is no partial or out-of-date exempt list anywhere in `seed/`. I searched `rebase`, `exempt`,
`migrat`, `MIG-0014`, `baseline`, `wave`, `overhaul`, `historical`, `pre-rebase` across every
`.md`, `.py` and `.json`: the only list is `tests/test_window_migration_coverage.py:8`. The
prompt warns against a hazard the tree does not contain.

**8. Three dangling references to a `docs/policy/` that does not exist.**
`README.md:11`, `README.md:47`, `docs/operations.md:45`. `README.md:47` declares "a policy under
`docs/policy/` outranks everything else" — i.e. it asserts an authority above DR-0091, and the
directory is absent. Harmless in practice (nothing suggests a policy speaks to windows) but it
invites a careful solver to treat the authority question as unresolved. Cosmetic sibling:
`src/hearth/quota_flow.py:14` and `docs/quota.md` carry the generated state name `classifyd`.

## What the revision did

It made the task harder to **do**, legitimately, not harder to understand: moving the checked
property off the generator's own indexes closed the route cross-review found, and
`r2/check_index_leak.py` is now clean on `ACTIVE_WINDOW_S`. There is no obfuscation, no split
value, no encoded datum, no arithmetic padding. The problem is that it did not close the grep
route or the arithmetic progression, and the prompt still gives away the tokens and the rule.

## What remains uncertain

I cannot run Haiku 4.5 or Sonnet 5 here, so the tier call is my judgment from the material, not
a measurement. My reading is that the exemption bookkeeping is the only residual failure surface
and that it is thin, but a 20-row comparison with a 16/4 split does retain some carelessness
surface that a trial could still resolve differently.

verdict: REVISE
