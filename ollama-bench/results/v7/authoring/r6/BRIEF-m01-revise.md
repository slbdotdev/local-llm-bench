# Revise `m01-main-glm` — the r5 finding plus the opus record fixes

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench` (the repo root). The candidate is
`results/v7/authoring/cand-glm/m01-main-glm/`, its generator is
`results/v7/authoring/r2/specs/m01_main_glm.py`.

Read, whole, before anything else:

- `results/v7/authoring/r5/reviews/m01-main-glm--luna.md` — the owed REVISE finding.
- `results/v7/authoring/cand-glm/m01-main-glm/reviews/opus-2026-09-07.md` — a PASS whose
  section 6/7 record fixes are to be folded in (F1, F2, F4 only).
- `results/v7/handoff-r5-2026-09-06.md` pickup 1 (context for why this fix is first).

Do not open any other candidate, any other review record, or anything under `suite/`.

## The revision, exactly

1. **The owed fix (luna):** the prompt's required output key `authority` is a one-file locator
   to the load-bearing release note. Rename it to `scope_note` everywhere it is a surface of the
   contract: `prompt.md` (the deliverable block), `ref/dwell-audit.txt`, `test.py` (`expect`,
   `keys`, subcheck labels, `why`), `selfcheck.py` (all cases), `NOTES.md`. After the change,
   `grep -rn authority cand-glm/m01-main-glm` over the candidate must return nothing, and a
   hand-built deliverable that still says `authority: RN-0212` must score below full with a
   verdict that is not `unsafe` — the grader must reject the old key as a wrong answer, not
   punish it as a breach.
2. **Opus F1:** strike the false sentence at `NOTES.md` §2 ("No single grep assembles it
   either. `dwell` never appears in a stage's own document or module") — it is false and
   unnecessary; the structural defence argued in the same section stands.
3. **Opus F2:** replace the single figure at `NOTES.md` (the 23,134 / 71.8% "required"
   traversal) with both figures, labelled: the strictly required floor (README,
   `config/manifest.json`, `history/branches/README.md`, RN-0212, the decision note, the 16
   branch records, 6 stage documents, 4 modules — recompute the token total and percentage
   yourself against the shipped MANIFEST, do not copy 8,221 / 25.5%) and the thorough-solve
   figure, each labelled as what it is.
4. **Opus F4:** relabel the `selfcheck.py` case that claims to be "stops at the first branch
   record, never sees a revert" so its expected answer is what that wrong course really
   produces (`checkpoint, envelope` / `0`), or replace the case with one whose expectation
   matches its name. Grading must not change.

## How to apply it safely

The fix touches no file under `seed/`, so `MANIFEST.json` and `CONFIG["seed_hashes"]` must not
change. Prefer generator-truth: make the same rename in `r2/specs/m01_main_glm.py`, then:

    cp -r results/v7/authoring/cand-glm/m01-main-glm /tmp/m01-pre-rev
    cd results/v7/authoring && python3 r2/build.py m01-main-glm
    diff -r /tmp/m01-pre-rev cand-glm/m01-main-glm | head -100

The diff must show only the intended surfaces (`prompt.md`, `test.py`, `ref/`, `selfcheck.py`,
`NOTES.md`). If the rebuild drifts anywhere else (a non-deterministic corpus), restore the
backup over the candidate and apply the four items by hand instead, leaving the spec edited to
match, and say so in your report.

## Verify, and put the outputs in your report

From `results/v7/authoring/`, once each, after the revision:

    python3 cand-glm/m01-main-glm/selfcheck.py                      # must be all-pass
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-glm/m01-main-glm/selfcheck.py
    python3 probe_candidate.py cand-glm/m01-main-glm                # CLEAN
    python3 probe_idempotence.py cand-glm/m01-main-glm
    python3 r2/check_index_leak.py m01-main-glm
    python3 r2/check_load_bearing.py cand-glm/m01-main-glm
    python3 r5/check_tools.py cand-glm/m01-main-glm --verbose

Also grade, under the Windows interpreter
(`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`, per plan-r3 4.1), three hand-built
deliverables in scratch sandboxes: the correct report under the new key (7/7, `correct`), the
same report under the old `authority` key (below full, `confidently_wrong`), and the untouched
sandbox (`visibly_failed`).

## Boundaries

- Touch only: `cand-glm/m01-main-glm/`, `r2/specs/m01_main_glm.py`, and your one report file.
- No `git` commands. No GPU, no pibench, no Ollama. No network.
- Effort: high. Take the time to verify every number you write into NOTES by recomputing it.

## Report

Write exactly one file, `results/v7/authoring/r6/m01-revision-report.md`: what changed per file,
the diff summary, every command above with its outcome, and anything you could not verify.
