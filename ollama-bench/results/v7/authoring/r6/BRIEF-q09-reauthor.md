# Re-author `q09-main-glm` from its own spec — the three-item fix list

Family: luna (worker). Effort: high. One candidate, one job. This is the round's biggest
authoring task; take it slowly and verify everything.

Working directory: `/home/slb/local-llm-bench/ollama-bench` (the repo root). The dropped
candidate is `results/v7/authoring/cand-glm/q09-main-glm/`, its generator is
`results/v7/authoring/r5/specs/q09_main_glm.py`, the build is
`cd results/v7/authoring && python3 r5/build.py q09-main-glm` (corpus cache exists under
`r5/.corpus-cache/`).

Read, whole, before anything else:

- `results/v7/decisions-r5-2026-09-06.md`, the section "`q09-main-glm` — DROPPED after one
  revision and four blind reviews" — the measurements and the three-item fix list.
- `results/v7/authoring/r5/reviews/q09-main-glm--claude-2.md` — the review whose `fix:` field
  is the authoritative form of the three items.
- `results/v7/handoff-r5-2026-09-06.md` pickups 1, 3 and 4 (why it is worth re-authoring, what
  "shape enforced by the material" means, what the frame measure misses).

Do not open any other candidate, any review record of another candidate, or anything under
`suite/`.

## The three items, verbatim from the review's `fix:` field

> rewrite `data/settlement-log.csv` and the two figure frames together. (a) Permute the log's
> **rows** with a real shuffle and assert at build that no affine or stride map from row index
> reproduces the chain — the current layout is a stride-3 reverse traversal and is the whole
> order for free. (b) Delete the second `rebase` and make the order genuinely load-bearing by
> giving one kind an applied figure that is a function of the running figure — e.g. a `clamp`
> entry that sets the figure to `min(figure, stage basis)`, or a `relief` that subtracts
> `min(take-back, figure)` — so that no segment is a commutative sum and `probes()` can assert
> that a shuffle of any segment misses; a `rebase` can never do this, because a set truncates
> the chain rather than extending it. (c) Break the frame: put each stage's balance and
> constant at a different line offset in its file, never last, with no sentence, heading or
> comment shared by more than about four stages, and draw the 38 figures independently at
> random rather than from two regularly-stepped bands indexed by a prime stride.

The dropped build's defects being repaired: chain order = stride-3 reverse traversal of file
position (deleting the `previous` column and ordering rows by position scored 12/12); the
mid-chain `rebase` truncated the chain so `figure_final` depended on 19 of 40 entries and every
key was (rebase basis) + an order-free sum (2,000/2,000 shuffled-entry replays hit the graded
figure); every balance sat on line 42 as its page's last line and every take-back on line 90 as
its module's last line inside byte-identical frames on 19 of 19 files, so
`tail -n1 docs/*.md src/kestrel/*.py` harvested 38 of 40; and the figures were a closed form
(sorted balances step by a repeating (64,24,64,24,24) cycle, take-backs by (28,16,16), ranks =
`5i mod 19` / `7i mod 19`).

## What the rebuilt candidate must assert at build time

The spec must fail the build, not ship a lie:

1. No single-field sort, no `position mod k` (k = 2..8), and no affine map `a*i+b` over
   `a` in a plausible range reproduces the chain walk from row index — tested against the
   built log, for all entries.
2. Per-entry perturbation: changing any single entry's applied figure changes `figure_final`;
   and for **every contiguous segment** of the chain, replaying that segment's entries in
   shuffled order (assert on many shuffles, seeded) misses the segment's exit figure — no
   segment is a commutative sum. `probes()` carries at least one such shuffled-segment case
   and asserts it grades `confidently_wrong`.
3. Frame break: no value-bearing line is the last line of its file; the line offsets of the 38
   stated figures are distinct across units (or at minimum never constant across more than
   four); no sentence, heading or comment is byte-identical across more than about four units;
   and the sorted figure sequences have no repeating step cycle and no rank map
   affine-in-`i`-mod-prime from manifest order.
4. The harvest declaration stays on the figure each entry *applies* (the first review's
   wrong-quantity defect), is non-vacuous, and `check_harvest.py` passes with real numbers.

## Keep what made it the round's best material

- The reviewer solved it from `prompt.md` alone and matched `ref/` exactly: every rule stated
  plainly, nothing a puzzle or a judgement call. Do not buy difficulty with comprehension.
- All rules still stated in the procedure document, including the `rebase`-sets-not-adds rule
  and whatever replaces it for the new entry kind; the "assembler's numbers are ruled out"
  clause; the sealed-log reading order.
- Mode 9 fit (reading past the first screen), main band 29,000–36,000 material tokens, the
  `config/manifest.json` exclusion rule, and the reference arms' solvability.
- Fix the false `NOTES.md` claims the second review listed (§2's "previous is the only
  artifact of order", §9's "five files opened", "the greps' yield still has to be walked in
  the chain's own order", §4's widest-token claim) — replace each with the measured truth of
  the rebuilt candidate.
- `tools/settlement_status.py` was flagged for printing all 43 rows (the whole selection half)
  in one bare invocation. `check_tools.py` passes it because it prints no figure. Trim what it
  prints if you can do so without breaking the seed's own contract; if you leave it, say why
  in your report.

## Verify, and put the outputs in your report

From `results/v7/authoring/`, once each, after the rebuild:

    python3 cand-glm/q09-main-glm/selfcheck.py                      # must be all-pass
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-glm/q09-main-glm/selfcheck.py
    python3 probe_candidate.py cand-glm/q09-main-glm                # CLEAN
    python3 probe_idempotence.py cand-glm/q09-main-glm
    python3 r5/check_rung0.py cand-glm/q09-main-glm
    python3 r5/check_index_leak.py q09-main-glm
    python3 r5/check_load_bearing.py cand-glm/q09-main-glm
    python3 r5/check_harvest.py cand-glm/q09-main-glm --verbose     # real numbers, not vacuous
    python3 r5/check_tools.py cand-glm/q09-main-glm --verbose

Then attack your own build by hand and report the numbers: `tail -n1` over the figure-bearing
files (must harvest nothing now), the best single grep you can find against the new frames, a
sorted-by-position replay with the `previous` column deleted (must miss), and a shuffled-segment
replay (must miss). Grade the reference deliverable once under the Windows interpreter
(`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`, per plan-r3 4.1): full score,
`correct`.

## Boundaries

- Touch only: `cand-glm/q09-main-glm/`, `r5/specs/q09_main_glm.py`, and your one report file.
- No `git` commands. No GPU, no pibench, no Ollama. No network.
- Effort: high. The build-time assertions are the point of this re-author; a rebuild without
  them is a failure of the task even if every check passes.

## Report

Write exactly one file, `results/v7/authoring/r6/q09-reauthor-report.md`: what changed in the
spec and the built candidate, the new chain shape in one paragraph, every build assertion with
its outcome, every command above with its numbers, your own attack results, and anything you
could not verify.
