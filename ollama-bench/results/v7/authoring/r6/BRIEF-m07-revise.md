# Revise `m07-main-glm` — close the recovery-word index and repair paths

Family: glm (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench/results/v7/authoring`. Candidate:
`cand-glm/m07-main-glm/`. Generator: `r2/specs/m07_main_glm.py`.

## Change list — every round-two review finding

1. **Rung-0 grep leak.** `bound_module` is answerable by `grep recovery`: the unique `(recovery)`
   architecture entry and replay self-descriptions point at replay, while the other report fields
   need no traversal. The shortcut reaches `9/9` from `1,237/29,624` tokens.
   (`cand-glm/m07-main-glm/reviews/opus-2026-09-07.md:67-123`.) Break this pointer: move the
   architecture role tag to excluded `audit`, reword replay's recovery descriptions so no
   material statement identifies the bound stage by its own noun, and add a scored arithmetic
   field if needed so the qualification traversal is itself required. Do not replace it with a
   new one-token pointer.
2. **Contradictory module paths.** Every README table row and every stage-doc module path omits
   `ember/`, but `bound_module` is graded against `src/ember/replay_view.py`; a faithful reader
   can score `8/9` for the wrong path. (`cand-glm/m07-main-glm/reviews/opus-2026-09-07.md:136-162`.) Rewrite
   all 19 README rows and 19 stage-doc lines to `src/ember/<module>.py` in the generator and
   assert those paths exist.

The Luna review contains no actionable finding: it reports the rung-0 traversal as genuine, the
grader as sound, and only static execution uncertainty (`cand-glm/m07-main-glm/reviews/luna-2026-09-07.md:3-14`).
The Opus review has the two actionable findings above, so this candidate still requires revision.

## Binding revision bars

Preserve the six exact edits, exclusions, and reference answer while making `bound_module` and
any added arithmetic key derivable only by reconciling distributed material. Add build-time
assertions for the unique qualifying stage, all six editable sites, path existence, and every
NOTES/MANIFEST number. No graded-surface shortcut may solve the task from the prompt, an index,
one helper, a single token, or a label fragment.

Explicitly test label-fragment isolation: prompt terms such as `recovery`, `handle`, `op`, and
`support` must hit excluded and included units without identifying the answer. Vary frame shapes,
line offsets, and final-line placement across stage docs/modules; no fixed-frame or last-line
sweep may collect stated figures. Carry the q09/m08 bars: no un-derivable key, no claimed
property without a build-time assertion, and no single-token/fixed-frame harvest. NOTES claims
must be measured from the rebuilt tree, not asserted from intent; retain the 29,000–36,000 band.

## Rebuild and drift check

Edit only `r2/specs/m07_main_glm.py`, then run exactly:

    cp -r cand-glm/m07-main-glm /tmp/m07-pre-rev
    python3 r2/build.py m07-main-glm
    diff -r /tmp/m07-pre-rev cand-glm/m07-main-glm | head -100

The seeded rebuild must be deterministic. The diff may contain only explained `seed/`, `ref/`,
`test.py`, `selfcheck.py`, `NOTES.md`, and `MANIFEST.json` surfaces. If any other surface drifts,
restore the backup, record the drift, and finish by hand without shipping unexplained changes.

## Exact checker battery

Run once each from this directory. Use the Windows interpreter for every grader verdict and
`python3` for the checkers/build artifacts.

    python3 cand-glm/m07-main-glm/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-glm/m07-main-glm/selfcheck.py
    python3 probe_candidate.py cand-glm/m07-main-glm
    python3 probe_idempotence.py cand-glm/m07-main-glm
    python3 r5/check_rung0.py cand-glm/m07-main-glm
    python3 r2/check_index_leak.py m07-main-glm
    python3 r2/check_load_bearing.py cand-glm/m07-main-glm
    python3 r5/check_tools.py cand-glm/m07-main-glm --verbose

In scratch, grade the reference, untouched sandbox, one wrong plausible report, the two-file
`handle_bridge.py`/`op_table.py` attack, the `recovery` grep attack, the wrong path, and naive
whole-tree rename. The shortcut attacks must not reach full score; report exact Windows scores,
minimum files, and the best token/frame attack.
