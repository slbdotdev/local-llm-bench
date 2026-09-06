# The coverage gate measures reading style, not material consumed

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
