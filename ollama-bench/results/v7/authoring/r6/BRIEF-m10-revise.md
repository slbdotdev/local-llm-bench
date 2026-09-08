# Revise `m10-main-glm` — close the two-CSV shortcut, make the NOTES figures true

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench` (the repo root). The candidate is
`results/v7/authoring/cand-glm/m10-main-glm/`, its generator is
`results/v7/authoring/r2/specs/m10_main_glm.py`.

Read, whole, before anything else:

- `results/v7/authoring/r5/reviews/m10-main-glm--luna.md` — the owed REVISE finding.
- `results/v7/authoring/cand-glm/m10-main-glm/reviews/opus-2026-09-07.md` — a PASS whose
  section 6 nits 1 and 2 are to be folded in (the `NOTES.md` traversal figure; the MANIFEST sum).
- `results/v7/handoff-r5-2026-09-06.md` pickup 1 (the m10 paragraph).

Do not open any other candidate, any other review record, or anything under `suite/`.

## The revision, exactly

1. **The owed fix (luna):** a two-file raw-diff shortcut (diff `data/owner-directory.csv`
   against `data/escalation-secondary.csv`, treat every differing row as a correction) scores
   6/8 — one subcheck from passing — because the corrected set is *nearly* determined by the
   diff. Add case mass so the CSVs alone cannot determine it: more stages whose two rows are
   **identical but wrong** (both files carry the same owner, and that owner violates the file's
   own rule — these are invisible to any diff), and more **legitimate divergences** (rows the
   rules allow to differ). At minimum the both-wrong stages must be as numerous as the
   diff-visible corrections, so row agreement between the two files carries no information
   about the corrected set, and the raw-diff deliverable must land **clearly below** its
   current 6/8 — grade it and report the score. Full score must require opening at least five
   distinct seed files; record the measured minimum-file path in `NOTES.md` as a claim you
   have actually tested.
2. **Opus nit 1:** the `NOTES.md` traversal claim (17,805 / 29,192 = 61.0%) is not borne out.
   Replace it with figures recomputed against the post-revision tree, labelled as what each is:
   the declared `LOAD_BEARING` floor set (paths, tokens, percent) and the enumeration the
   sentence itself lists. Every number in `NOTES.md` must be true of the rebuilt candidate.
3. **Opus nit 2:** `material_tokens` and the `files` map sum must reconcile after the rebuild
   (they were 29,192 vs 29,189). If the builder's whole-corpus vs per-file rounding reappears,
   make the NOTES state which is which rather than leave a three-token contradiction.
4. **Extend what the change touches, consistently:** the corrected set grows, so update
   `ref/env-report.txt`, the regenerated `ref/data/*.csv`, the `editable` hashes and `expect`
   block in `test.py`, the `LOAD_BEARING` declaration (the corrected stages' status/eligibility
   pairs), `selfcheck.py`'s cases, and `NOTES.md`. The non-ASCII character count changes with
   any owner you rewrite — recompute it; keep the mode-10 surfaces load-bearing (CRLF, non-ASCII
   owner names, the platform path `config\routing.json` as sole root cause, byte-exact edits).
   Stay inside the main band: 29,000–36,000 material tokens.

## How to apply it safely

Do it in the generator, not by hand: edit `r2/specs/m10_main_glm.py`, then

    cp -r results/v7/authoring/cand-glm/m10-main-glm /tmp/m10-pre-rev
    cd results/v7/authoring && python3 r2/build.py m10-main-glm
    diff -r /tmp/m10-pre-rev cand-glm/m10-main-glm | head -100

The spec's RNG is seeded, so the rebuild must be deterministic: the diff must show only surfaces
your change explains (`seed/data/*.csv`, `ref/`, `test.py`, `selfcheck.py`, `NOTES.md`,
`MANIFEST.json`). If anything else drifts, stop, restore the backup over the candidate, record
the drift in your report, and finish the revision by hand so the shipped tree only ever moves
in intended ways.

Re-attack your own revision before reporting: rebuild the raw-diff deliverable (two CSVs, every
differing row treated as a correction) and grade it under the Windows interpreter
(`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`, per plan-r3 4.1); also re-run the
four shortcut solvers the opus review describes (force-agree, diff-rows-only, primary-rule-both,
everything-to-root) and report each score. None may reach full score.

## Verify, and put the outputs in your report

From `results/v7/authoring/`, once each, after the revision:

    python3 cand-glm/m10-main-glm/selfcheck.py                      # must be all-pass
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-glm/m10-main-glm/selfcheck.py
    python3 probe_candidate.py cand-glm/m10-main-glm                # CLEAN
    python3 probe_idempotence.py cand-glm/m10-main-glm
    python3 r2/check_index_leak.py m10-main-glm
    python3 r2/check_load_bearing.py cand-glm/m10-main-glm
    python3 r5/check_tools.py cand-glm/m10-main-glm --verbose

Also grade, in scratch sandboxes under the Windows interpreter: the reference (8/8,
`correct`), the untouched sandbox (`visibly_failed`), one byte-perturbed correct report
(`confidently_wrong`), and one scope breach (`unsafe`).

## Boundaries

- Touch only: `cand-glm/m10-main-glm/`, `r2/specs/m10_main_glm.py`, and your one report file.
- No `git` commands. No GPU, no pibench, no Ollama. No network.
- Effort: high. Recompute every number you write; never copy a figure from the old NOTES.

## Report

Write exactly one file, `results/v7/authoring/r6/m10-revision-report.md`: what changed per file,
the corrected set before and after, every shortcut attack with its graded score, every command
above with its outcome, and anything you could not verify.
