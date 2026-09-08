# Revise `m04-main-glm` — remove the checker/tool oracles and make the contract exact

Family: glm (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench/results/v7/authoring`. Candidate:
`cand-glm/m04-main-glm/`. Generator: `r2/specs/m04_main_glm.py`.

## Change list — every round-two review finding

1. **Blank-line checker defect.** `test.py:345–348` drops blank lines, while the prompt says
   exactly three lines and no other lines; `selfcheck.py` nevertheless marks a leading blank and
   extra trailing blanks `correct`. (`cand-glm/m04-main-glm/reviews/luna-2026-09-07.md:11-16`.)
   Make the parser and near-miss expectations agree with the explicit contract.
2. **One-file answer oracle.** `tools/run_checks.py` computes the entire answer; importing
   `compute()` and writing the permitted fixture yields `7/7` from one 591-token file.
   (`cand-glm/m04-main-glm/reviews/opus-2026-09-07.md:40-66`.) Remove the sweep from the tool. It may verify a
   supplied fixture only against a digest and print `OK`/`FAIL`, never stage names or the rule.
3. **Nineteen-trial workflow oracle.** The documented `build_fixture.py`/`run_checks.py` loop
   finds `dispatch` without reading a stage source file, in 19 trials and 1,877 tokens.
   (`cand-glm/m04-main-glm/reviews/opus-2026-09-07.md:68-85`.) Widen the fixture to all 19 rows with both dates
   and an inclusion field, and make the full 19×2 material traversal the only way to construct
   its digest; assert that the tool itself cannot reconstruct the answer.
4. **Non-load-bearing review date and false documentation.** `build_fixture.py` uses only
   `date >= CUTOVER`; arbitrary dates, omitted rows, and decoy rows still pass, contradicting
   the release-checks prose. (`cand-glm/m04-main-glm/reviews/opus-2026-09-07.md:87-102`.) Make both date columns
   load-bearing and rewrite the documentation to state the actual check.
5. **Broken policy links and paths.** README/operations point to nonexistent `docs/policy/`,
   and README lists `src/<module>.py` although the files are under `src/vantage/`.
   (`cand-glm/m04-main-glm/reviews/opus-2026-09-07.md:137-148`.) Correct the material and assert every referenced
   path exists.
6. **TESTS case handling.** `TESTS` is exact-compared while the prompt is silent on case and
   the tree uses `PASS`; a genuine `TESTS: PASS` gets `6/7` and `confidently_wrong`.
   (`cand-glm/m04-main-glm/reviews/opus-2026-09-07.md:150-157`.) Use `kinds['TESTS'] = 'ci'` or explicitly state
   and consistently enforce case; the recommended fix is `ci`.
7. **Unverified coverage claim.** The structural docs/modules figure is measured, but the
   `24,160/31,024 (77.9%)` acceptance-trial claim has no supplied trial record.
   (`cand-glm/m04-main-glm/reviews/luna-2026-09-07.md:6-9,15-17`.) Recompute and label structural versus trial
   measurements; never present an unrun trial as fact.
8. **MANIFEST rounding.** Per-file values sum to `31,027` versus `material_tokens 31,024`.
   (`cand-glm/m04-main-glm/reviews/luna-2026-09-07.md:8`; `cand-glm/m04-main-glm/reviews/opus-2026-09-07.md:194-197`.) Reconcile
   the aggregate/map or identify their distinct rounding bases in NOTES.

The Luna review has one actionable finding; the Opus review has the three oracle findings plus
the material, grader, and measurement defects above. No candidate has both reviews free of an
actionable finding; this slot is not re-verification-only.

## Binding revision bars

The reference keys must remain derivable from distributed seed facts, with `facts()` assertions
for every row count, date relationship, digest input, and measured token/coverage figure. No key
may be copied from a helper, checker, manifest, or label fragment. A helper may validate a
solver-created artifact but must not enumerate or print the answer.

No graded-surface shortcut is allowed: no single-token grep, fixed-frame/line-offset sweep,
last-line harvest, or label-fragment isolation may collect the figures across units. Vary where
the decisive fields occur and their surrounding labels across the 19 units. Keep NOTES measured,
keep the checker battery and scope/integrity semantics honest, and preserve the 29,000–36,000
main band. Carry the q09/m08 bars explicitly: every key derivable from material, build-time
assertions for claimed properties, and no single-token/fixed-frame sweep.

## Rebuild and drift check

Edit only `r2/specs/m04_main_glm.py`, then run exactly:

    cp -r cand-glm/m04-main-glm /tmp/m04-pre-rev
    python3 r2/build.py m04-main-glm
    diff -r /tmp/m04-pre-rev cand-glm/m04-main-glm | head -100

The seeded rebuild must be deterministic. Only explained `seed/`, `ref/`, `test.py`,
`selfcheck.py`, `NOTES.md`, and `MANIFEST.json` surfaces may drift. On any unexplained drift,
restore the backup, record it, and finish by hand without shipping unrelated generated changes.

## Exact checker battery

Run once each from this directory. Verdicts, including all scratch attack grades, come from the
Windows interpreter; `python3` runs the checkers.

    python3 cand-glm/m04-main-glm/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-glm/m04-main-glm/selfcheck.py
    python3 probe_candidate.py cand-glm/m04-main-glm
    python3 probe_idempotence.py cand-glm/m04-main-glm
    python3 r5/check_rung0.py cand-glm/m04-main-glm
    python3 r2/check_index_leak.py m04-main-glm
    python3 r2/check_load_bearing.py cand-glm/m04-main-glm
    python3 r5/check_tools.py cand-glm/m04-main-glm --verbose

In scratch sandboxes, grade the one-file helper oracle, the 19-trial documented workflow, the
reference, untouched sandbox, byte-perturbed correct report, scope breach, wrong date, wrong
fixture row, and both blank-line cases. The oracle/workflow attacks must fail to reach full score;
report exact Windows scores and the measured minimum-file path.
