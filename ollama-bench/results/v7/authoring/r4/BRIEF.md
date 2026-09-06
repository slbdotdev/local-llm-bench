# Round-4 authoring brief — ten tasks whose per-unit facts no grep can harvest, 2026-09-09

*Written by the round-four manager. One author per slot, three families, blind. Read this whole,
once.*

## 1. What this round is for, and the measurement that asks for it

Nineteen candidates from rounds two and three were run on the 2-bit workhorse (`q27-IQ2_M-64k`,
driven by an agentic harness with `bash` and a file reader). **Eighteen were answered correctly
while naming 6 to 49% of their material as whole files**, and the coverage gate — 50% of the
material by the files the trial actually named, plus five load-bearing paths touched — admitted
exactly **one of nineteen** (`results/v7/authoring-r3-2026-09-08.md` section 6).

The transcripts say why. The model does not read the tree, **it greps it**. Every per-unit fact
was a named constant on one line; the manifest is a pointer the prompt is allowed to give; so
one `grep -rn <NAME> seed/` puts every unit's value on one screen and the task collapses to
arithmetic. `n02-main-glm` was answered *correctly* having named two of its fifteen load-bearing
files.

Round two made the material impossible to locate from the **prompt's** vocabulary. It did not
make it impossible to locate from the **manifest's**.

> **The property this round exists to enforce: a value that a single grep can harvest across
> units is not material, whatever its token count.**

Difficulty still comes from the amount of real material that must be read and reconciled, from a
plausible wrong course the material itself rules out, and from steps that each depend on the
previous one. It never comes from ambiguity, trick wording, format, or a judgement call.
**A task must be hard to DO and never hard to UNDERSTAND.** A task Sonnet 5 fails is unfair, not
hard, and is re-reviewed before it is believed.

## 2. Read, whole, once, in this order

1. `AUTHORING-BRIEF.md` — the contract every task obeys (sections 2, 8 and 9 especially), and
   the table of the ten failure modes.
2. `r4/SPEC.md` — the spec-module contract. It is round three's plus `harvest_units()` and the
   grep-harvest check; read the last three sections closely, they are new.
3. `r4/specs/EXAMPLE-n09_cheap_luna.py.txt` — a complete worked cheap24 spec, the one row of
   nineteen that passed the coverage gate.
   `r4/specs/EXAMPLE-m09_main_luna.py.txt` — a complete worked main-band spec.
4. `../research-r4-2026-09-09.md` — section 2 (the four anti-harvest mechanisms, which is the
   craft of this round), section 3 (the read of n09, **including why it is not this round's
   exemplar**: one `grep -rn release_status seed/` harvests all eight of its per-stage values),
   section 4 (the thresholds), and **your slot's subsection of section 5**, which is the design
   you are implementing. You
   may depart from it where the material forces you to, and you say so in `NOTES.md`.
5. `../authoring-r3-2026-09-08.md` sections 6 and 8, and `roundtable.md`'s two "What review
   actually caught" sections. Every defect listed there is one your candidate must not have.

## 3. The assignment

Family, band and mode are **fixed**. They are forced by the campaign's provenance rule — a
re-authored slot goes to a family that is neither its current author's nor its mode's other-band
author's — and by the 40% family cap on the finished suite. Nobody chose their own.

| slot | family | band | mode | replaces | idea (research §5) |
| --- | --- | --- | ---: | --- | --- |
| `p01-main-glm` | glm | main | 1 | `m01-main-claude` | §5, p01 |
| `p02-main-claude` | claude | main | 2 | `m02-main-luna` | p02 |
| `p03-main-luna` | luna | main | 3 | `m03-main-glm` | p03 |
| `p04-main-glm` | glm | main | 4 | `m04-main-claude` | p04 |
| `p05-main-claude` | claude | main | 5 | `m05-main-luna` | p05 |
| `p06-cheap-luna` | luna | cheap24 | 6 | `m06-cheap-claude` | p06 |
| `p07-cheap-glm` | glm | cheap24 | 7 | `m07-cheap-luna` | p07 |
| `p08-cheap-claude` | claude | cheap24 | 8 | `m08-cheap-glm` | p08 |
| `p09-main-luna` | luna | main | 9 | `m09-main-glm` | p09 |
| `p10-cheap-glm` | glm | cheap24 | 10 | `m10-cheap-luna` | p10 |

Bands, measured by `measure_material.py` on the built candidate:

| band | material | runs at | `BAND` | `TARGET_TOKENS` |
| --- | ---: | --- | --- | --- |
| `main` | 29,000-36,000 tokens | 64k | `"main"` | 26,000-27,000 |
| `cheap24` | 12,000-16,000 tokens | 24k | `"cheap24"` | 10,000-11,000 |

The overlay carries you the rest of the way into band.

## 4. The one new thing: `harvest_units()` and the grep-harvest check

Your spec declares `harvest_units(ctx)`: one entry per unit, `{"unit", "value", "path"}`,
**measured from `seed/` on disk** exactly as `facts()` is. At least six units. `r4/SPEC.md` has
the contract; `r4/check_harvest.py`'s docstring has the full statement of the measure. In short:

* **H1** — the largest fraction of your units that any single token of the *giveaway vocabulary*
  can harvest with one `grep -C2`. The giveaway vocabulary is every distinctive word of your
  `prompt.md`, plus every distinctive word of any file you declare `named_in_prompt`, plus your
  deliverable's name and your scored keys' words. **H1 must be under 1/4.**
* **H2** — what one regex alternating over every unit name in the roster harvests, the attack the
  task's own scope hands the solver. **H2 must be under 2/5.**
* **H3** — H1 again with a five-line window, because a token can miss the decisive line under
  ±2 and still catch it inside a record block. **H3 must be under 1/3.**
* *P2*, the best union of two giveaway tokens, is printed and is not gated. Read it anyway:
  it is the number that says how much a second grep buys.

Declaring the units honestly is the whole point. A spec that declares the six units it made hard
and omits the twelve it left as named constants has defeated its own round, and a reviewer who
finds that writes REVISE.

**The four mechanisms that pass this check** (research section 2 develops each, with sources):

1. **the fact stated inside prose that names no constant** — the value is a word in a sentence
   and the sentence's vocabulary varies from unit to unit;
2. **the fact derived from records rather than stated** — no file holds the value at all; the
   unit's own ledger, event log or history has to be replayed to produce it. This is the
   strongest answer: a unit whose value never occurs literally in `seed/` cannot be harvested;
3. **the fact spread across artifacts the manifest does not name** — the pointer the prompt
   legitimately gives names the roster of units, never the artifact carrying the fact;
4. **the table whose deciding column is not the one named** — the obvious column is a decoy and
   the deciding one is reached only by a rule stated elsewhere.

Mixing two of these across your units is fine and usually better than one applied twenty times.
What is **not** allowed: making the value hard to *read*. Obfuscation, encoding, arithmetic
volume, values split across lines to defeat a grep, or a fact whose location is a puzzle. Each
of those makes the task hard to understand, which is the one thing this benchmark never does.

## 5. Method

Work only in `/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring`. It is a slow Windows
mount: read files with `cat` or `sed -n` on a named path, never a recursive `find`, never
`grep -r` over the repository, and **never run `git` at all**.

1. Write `r4/specs/<slot with underscores>.py`, e.g. `r4/specs/p03_main_luna.py`, following
   `r4/SPEC.md` exactly. Module constants first, then the functions in the order the contract
   lists them. `facts()` and `harvest_units()` both compute their values by reading `seed/` back
   from disk and assert their own arithmetic. *A reference that asserts a fact the material does
   not state is this benchmark's most expensive defect and it has happened twice.*
2. Build and check, from the authoring directory, running each of these once when you believe
   the spec is finished, and again only after a fix:

       python3 r4/build.py <slot>
       python3 cand-<family>/<slot>/selfcheck.py
       python3 probe_candidate.py cand-<family>/<slot>
       python3 probe_idempotence.py cand-<family>/<slot>
       python3 measure_material.py cand-<family>/<slot>
       python3 r4/check_rung0.py cand-<family>/<slot>
       python3 r4/check_index_leak.py <slot>
       python3 r4/check_load_bearing.py cand-<family>/<slot>
       python3 r4/check_harvest.py cand-<family>/<slot> --verbose

   All must be clean and the measured material must be in band before you report.
3. Write nothing outside `r4/specs/<your slot>.py`; the builder writes `cand-<family>/<slot>/`
   for you. Never touch another slot, `suite/`, `r2/`, `r3/`, or any file under `results/`
   other than through the builder.

## 6. The traps, as instructions

- **The index leak.** The generated tree writes each stage's `limit` and `window_s` into five
  agreeing artifacts, two of which list every stage in one small file. Your decisive per-unit
  datum is one the generator does not replicate. `check_index_leak.py` enforces this for a spec
  that declares `DECISIVE_CONSTANT`; declare it whenever the decisive fact is a per-unit
  constant, and say in `NOTES.md` why not otherwise.
- **No single word of `prompt.md` may grep to exactly one load-bearing file**, and no decoy may
  carry the deliverable's own key names.
- **The prompt never names the file that holds the answer.** The only `named_in_prompt`
  load-bearing entry is a roster of units, if the task needs one; knowing the scope of a sweep is
  not knowing its answer. Remember that every word of that roster joins the giveaway vocabulary
  the harvest check measures against you.
- **A correction must never state the delta** in units a solver can apply arithmetically to a
  stale total; the corrected value has to be re-derived from the per-unit material.
- **No tool in the seed may print the answer.** A helper validates an input the solver supplies;
  it never computes the result.
- **Every claim in `NOTES.md` is a build-time measurement**, never an estimate. Three pages last
  round stated a line number or a count the built candidate did not bear out.
- **`sweep_paths()` should cover 60-80% of the material**; a sweep of 30% has not cleared rung 0.
  `load_bearing()` needs at least six paths and three distinct hops.
- **The five perturbations of `probes()` case 5 all pass**, or the grader is defective.
- Difficulty is never format, never ambiguity, never a judgement call, and never more than about
  four causal hops: each of those fails Sonnet too and marks the task unfair rather than hard.
- **`python` is not on the sandbox's path. Write `python3`.**

## 6a. The floor-coverage addition, measured tonight

Added after the round's first two candidates were built, and it applies to every slot.
`python3 r4/check_load_bearing.py cand-<family>/<slot>` prints a **floor coverage** column: the
load-bearing files as a fraction of the whole material. One candidate measured 28.7% and one
measured 5.7%. The second is at real risk, because the GPU acceptance gate requires the trial to
**name files totalling 50% of the material**, and a task whose decisive files are 6% of the tree
can be solved perfectly while naming almost nothing.

**Aim for a floor coverage of about 25% or more.** Put the per-unit records, their supporting
ledgers, and the artifacts a reader must open in order to rule them out, *into* the load-bearing
set, and make those files substantial, rather than deriving the answer from a handful of small
ones. This is an addition to the H1/H2/H3 limits and never a replacement for them: the harvest
check and the coverage gate pull in different directions, and a candidate has to satisfy both.

## 7. Report

When the checks are clean, reply with: the slot; the row `build.py` printed (tokens, files,
load-bearing count, hops, sweep tokens, coverage %); the measured band; the H1 and H2 that
`check_harvest.py` printed at C=2 and which token drove H1; one line per check saying it passed;
the floor coverage `check_load_bearing.py` printed; which of section 4's mechanisms you
used and for how many of your units; where your candidate
departs from the research idea and why; and anything you are unsure of. Nothing else.
