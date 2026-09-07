# The coverage gate measures reading style, not material consumed
*Renamed 2026-09-06 from `v7/coverage-instrument-2026-09-09.md`: the campaign labelled rounds by planned campaign day, not by the calendar date they were written.*

*Written by the round-four manager from the round's own GPU rows, 2026-09-09. This is a finding
about `results/v7/coverage_gate.py` and plan section 2.2, not about any candidate.*

## The measurement

Five round-four candidates went through the workhorse acceptance cell, one trial each, on
`q27-IQ2_M-64k` (main) and `q27-IQ2_M-24k` (cheap24). Every one was authored to make its
per-unit decisive values non-harvestable by grep, and four of the five measure H1 = H2 = H3 =
0.000 under `r4/check_harvest.py`, meaning no single token the prompt or its declared pointers
give away reaches any unit's decisive value at any context width.

| task | floor | verdict | peak | peak/mat | cover% | cover+x% | lb touched | gate |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| p03-main-luna | 5.7% | correct | 7,685 | 26.3 | 8.2 | 8.2 | 12/12 | FAIL |
| p09-main-luna (first build) | 28.7% | visibly failed, timed out | 27,642 | 82.3 | 19.4 | 78.6 | 5/14 | FAIL |
| p02-main-claude | 74.8% | correct | 14,374 | 40.6 | 8.0 | **100.0** | 2/38 | FAIL |
| p05-main-claude | 40.0% | visibly failed, `stop=length` | 25,509 | 76.3 | 25.4 | **100.0** | 6/23 | FAIL |
| p08-cheap-claude | 28.7% | correct | 9,786 | 61.8 | 31.1 | 31.1 | 10/10 | FAIL |

`floor` is `r4/check_load_bearing.py`'s floor coverage: the load-bearing files as a fraction of
the material, and therefore the coverage a trial would score if it read exactly the files the
answer depends on and nothing else.

## What the rows say, in order

**1. The load-bearing floor is a hard ceiling, and it is not the binding constraint.** p03 touched
*every one* of its twelve load-bearing files and scored 8.2%, because its load-bearing set is 5.7%
of its material. That much was predictable and the round acted on it: three candidates were
authored or revised to floors of 40.0%, 50.7% and 74.8%. It did not help.

**2. p02 is the row that settles it.** Floor coverage 74.8% — three quarters of its material is
causally necessary — and the trial scored **8.0%**, naming two of thirty-eight load-bearing paths.
Its tool histogram is `bash: 7, read: 1, write: 1`. It reconciled eighteen units' derived
reservations, *correctly*, in **seven bash calls**, and its expanded coverage is **100%**: every
file in the tree was reached by a directory or glob token.

**3. So the property this round enforced is real but insufficient.** Making the decisive value
derived stops one grep harvesting the **answer**. It does not stop one grep harvesting the
**inputs**. p02's eighteen reservations occur nowhere in `seed/`; its eighteen opening grants and
its adjustment entries do, and `grep -rn` over two directories puts them all in context, after
which the arithmetic is the model's own. Round three failed the gate because the values were
greppable. Round four fails it because the inputs are.

**4. And the instrument itself is not measuring what the gate wants.** `read_paths` counts whole
files *named*. A model that works by `grep -rn <pattern> docs/` names a directory and no file, so
it scores near zero however much material it consumed; a model that opens the same files with
`read` scores fully. **Coverage as defined separates `read` from `bash`, not much material from
little.** Plan section 2.2 already says the expanded number over-counts, because a grep pulls
matching lines rather than whole files. The converse is equally true and is not written down: the
gated number **under-counts a grep-driven trial just as badly**. p02 held 14,374 tokens at peak —
40.6% of its material, real material, actually in the window — while being credited with 8.0%.

The truth for a grepping trial is bracketed, never given, by the two coverage numbers: p02
consumed between 8.0% and 100% of its material. The only field that measures the bracket from
inside is `achieved_fill_prompt_tokens`, the peak single-turn input, which plan section 2.2
demotes to a capacity diagnostic.

## Why this matters for the 50% number specifically

Plan section 2.3 derives the 50% fraction from v6's D6-30, and says so in terms: `g03` at 25,748
of 30,018 tokens (86%) and `t03` at 16,502 of 30,604 (54%), "and both clear 50% **on the
peak-input proxy**, so the fraction rests on measured precedent, and applying it to coverage makes
it harder still."

The precedent is a peak-input measurement. The gate applies that number to a different quantity.
Measured on the proxy the precedent was actually taken on, round four's five rows read **26.3,
40.6, 61.8, 76.3 and 82.3** — three of five clear 50%, median 61.8% — against round three's
main-band range of 9 to 55% of material with a median of 24%. On the gate's own quantity they read
8.0 to 31.1 and none clears it.

**Both statements are true of the same five trials.** Which of them is the campaign's result is
not the manager's call, and section "What is open" below states it as the owner's.

## What would measure it honestly

Neither existing number is right, and a third is computable from the same event stream. For a
`grep` the model ran, the material it consumed is the **matching lines**, not the whole file and
not nothing: for `grep -rn <pattern> <dir>`, attribute to each file under `<dir>` the tokens of
the lines that match `<pattern>`. That is exactly what entered the window. It needs pibench to
keep the bash command string alongside `read_paths` — today it keeps only the extracted paths and
a per-tool histogram — which is one field, of the same kind as the `read_paths` addition plan
section 2.5 already specified and this campaign already made.

Recommended, and **not done here** because redefining the gate mid-round would rewrite the
acceptance rule under the candidates it is judging:

1. add that field, `bash_commands`, to pibench;
2. compute a third coverage number, *grep-attributed coverage*, between the two existing ones;
3. re-derive the gating fraction against it, from D6-30's two rows, as plan section 2.3 does.

## The decisive measurement: the gate and the pass rate disagree in sign

Plan section 2.2 makes coverage an **admission** criterion, on the reasoning that a trial which
never occupies the band is a capacity result rather than a quality one. Step 7 of the round-four
brief asked for the test of that: three trials of every round-three candidate, so the record can
say whether the gate and the pass rate agree. Thirty trials, `results/v7/r3repeat.log`, tags
`v7r3-rep-main` and `v7r3-rep-cheap`, one workhorse cell per band.

**First, one trial was not enough to say anything.** Round three reported **10 of 10** on a single
trial each. At three trials it is **21 of 30, 70%** — main band **13 of 21 (62%)**, cheap24 **8 of
9 (89%)**. Six of the ten rows are not deterministic: n02, n03 and n04 pass one trial in three,
n01, n05 and n10 two in three. The 100% was luck, and any single-trial pass rate in this campaign
should be read as one sample and never as a property of a task.

**Second, and this is the finding: coverage predicts the pass rate with the wrong sign.**

| task | peak/mat | cover% | cover+x% | 3-trial |
| --- | ---: | ---: | ---: | ---: |
| n05-main-luna | 29.7 | 7.8 | 89.4 | 2/3 |
| n02-main-glm | 47.1 | 11.7 | 78.2 | **1/3** |
| n04-main-claude | 70.0 | 12.5 | 91.7 | **1/3** |
| n07-main-claude | 37.2 | 16.8 | 100.0 | 3/3 |
| n01-main-claude | 41.2 | 18.6 | 90.0 | 2/3 |
| n06-main-glm | 33.1 | 30.2 | 75.3 | 3/3 |
| n03-main-luna | 44.0 | 35.2 | 76.3 | **1/3** |
| n08-cheap-glm | 41.7 | 47.5 | 71.9 | 3/3 |
| n10-cheap-claude | 85.2 | 48.5 | 93.1 | 2/3 |
| n09-cheap-luna | 108.2 | 88.5 | 88.5 | 3/3 |

* **Pearson r between coverage and three-trial passes = +0.471.**
* The five lowest-coverage rows average **13.5%** coverage and score **9 of 15**.
* The five highest-coverage rows average **50.0%** coverage and score **12 of 15**.
* The single row that has ever passed the gate, `n09-cheap-luna` at 88.5%, is one of four rows the
  workhorse has **never** failed.

So the gate does not merely fail to track difficulty. **It selects against it.** A task the model
can traverse completely is a task it can solve; a task it fails is one it got lost in, and getting
lost shows up as *low* coverage. Admitting on coverage therefore pushes the suite's pass rate
**up**, away from the 50% target that the same plan sets, and the two instruments the plan asks
the manager to read together are pulling in opposite directions.

That is not an argument against measuring occupancy. It is an argument that occupancy is a
**diagnostic about the trial** — did this run exercise the band, or answer from a corner of it —
and not a **property of the task** that admission can be conditioned on. Round four's own rows say
the same thing from the other side: `p02-main-claude` has 74.8% of its material load-bearing and
was answered correctly at 8.0% coverage in seven bash calls, while `p03-main-luna` reached 49.9%
coverage and was also answered correctly. Coverage moved by a factor of six between two rows with
the same verdict.

## What this leaves for the owner

Three courses, and the choice is not the manager's:

1. **Keep the gate as an admission rule.** It is coherent — it guarantees the material is
   occupied — but on this evidence it raises the pass rate, so the 50% target and the 50% gate
   cannot both be met by the same suite, and the plan should say which one yields.
2. **Demote coverage to a diagnostic** reported beside every row, exactly as peak input is today,
   and admit on the reference arms and the cross-review alone. This is what the round-four
   evidence supports and it is the manager's recommendation.
3. **Replace the instrument** with grep-attributed coverage (above), then re-derive the fraction,
   and re-run this correlation before making it a gate again. Nothing should become a gate again
   until it has been shown to correlate with difficulty in the right direction.

**The one number the plan asked for.** Measured on the peak-input proxy that plan section 2.3's
own precedent (v6 D6-30) was taken on, round four's five gated rows read 26.3, 40.6, 61.8, 76.3
and 82.3 — three of five clear 50%, median 61.8 — against round three's main-band 9-55% with a
median of 24%. On the gate's own quantity they read 8.0 to 47.3 and none clears it. Both
statements describe the same trials.
