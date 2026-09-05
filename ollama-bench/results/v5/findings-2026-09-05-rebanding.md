# Re-banding the suite by real material size — the medium and large bands are empty

Measured 2026-09-05 by the Opus manager session, under `plan-2026-09-05.md` section 3.2, which
requires each task's real material size measured and recorded before any GPU cell. No model, no
GPU, no network: this is a character count.

## Method

`results/v5/authoring/measure_material.py` walks every file under each candidate's `seed/`,
skipping `__pycache__` and `.pyc`, sums the characters, and divides by **4.664** — the suite's own
measured chars-per-token constant, not the 5.95 that was 28% wrong. Full output:
`authoring/material-sizes-2026-09-05.json`.

The plan's bands: **small 4,000-8,000 tokens, medium 12,000-20,000, large 30,000-45,000.**

## Result

| task | selected candidate | material tokens | seed files | band |
| --- | --- | --- | --- | --- |
| g01 | cand-2 | 537 | 1 | below small |
| g02 | cand-3 | 1,722 | 2 | below small |
| g03 | cand-1 | 283 | 4 | below small |
| g04 | cand-1 | 367 | 2 | below small |
| t01 | cand-3 | 174 | 4 | below small |
| t02 | cand-2 | 301 | 1 | below small |
| t03 | cand-3 | 6,235 | 1 | **small** |
| t04 | cand-3 | 195 | 5 | below small |

Across all 31 candidates the range is **149 to 7,637 tokens**. Exactly three of the thirty-one —
t03's cand-1 (7,637), cand-2 (6,575) and cand-3 (6,235) — reach the small band.

**Nothing in the suite reaches the medium band. Nothing is within a factor of four of the large
band.** The largest candidate in the suite is smaller than the *floor* of the medium band.

## This corrects the plan, and the correction is load-bearing

`plan-2026-09-05.md` section 3.2 says:

> t03 already belongs to the medium band by construction — eight graded facts out of a 12k-token
> document — and is the model for how the others should be built.

Measured, t03's selected candidate is **6,235 tokens**, about half of 12k, and it is in the small
band. The 12k figure was an estimate that had never been measured. It is measured now.

That matters because t03 was the plan's worked example of a task already in the right shape.
There is no such example. Every task in the suite has to be grown, not merely labelled.

## Consequence: re-banding is not bookkeeping, it is the critical path

The plan schedules re-banding as cheap — "measure each surviving task's real material size, assign
it a band, record the size in its manifest. Cheap, and it must happen before any GPU cell." The
measurement step *is* cheap; it took one script and under a second. What it revealed is not.

**Two of the three bands are empty, so there is no context axis to run.** The grid's whole second
dimension — quant x context band — has one populated band and it is the smallest one. Until
material-heavy tasks exist, a "bend-finding pass" has nothing to find a bend across.

So authoring is the campaign's critical path, and it is the same work as desaturation rather than
a competitor for it: "more material to hold at once" is the first and most preferred lever on the
plan's own difficulty ladder (section 2.3), and it is the only lever that populates a band.

## The design taken in response

Recorded in full in `decisions.md`. In short: **two bands holding the same eight task families,
rather than three bands holding different tasks.**

- **small** — the eight existing families at their measured sizes (174 to 6,235 tokens), run at
  24k;
- **large** — a new `cand-5` per family asking the *same question over 30,000-45,000 tokens of
  real material*, run at 64k.

The reason is a confound the plan concedes in section 3.4 and this shape removes. If a band is
populated by "the tasks that genuinely need it", then a small-band number and a large-band number
are computed over **different tasks**, and any difference between them mixes context with task
identity. Holding the family fixed across both bands measures the context effect *within* a task,
which is the strongest available design and costs nothing extra here, because every existing task
is below the small band anyway and all of them need a larger sibling.

The honest cost: the small band's material sits below the plan's own 4k-8k floor, so "small" here
means "the task's natural size". Every report of it must give the measured token count rather than
the band name.

## What must not be repeated

The suite carried a "medium band by construction" claim for two days without anyone counting the
characters, and it was wrong by roughly 2x. It is the same shape as the fifteen-grid-tags row that
read "done" when three existed. **A size is a measurement only when something measured it**; an
authoring note describing a "12k-token document" is a description of intent, not of the file.
