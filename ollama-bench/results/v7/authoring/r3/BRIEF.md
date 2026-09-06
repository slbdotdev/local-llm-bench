# Round-3 authoring brief — ten tasks tuned for difficulty, 2026-09-08

*Written by the control session. One author per slot, three families. Read this whole, once.*

## 1. What this round is for

The accepted v7 suite is saturated: Sonnet 5 scored 20/20, GLM 5.3 Flash 20/20, Luna 19/20,
Haiku 4.5 18/20, and a 2-bit 27B local quant 19/20. Ten more tasks are being authored tonight,
and the owner's requirement is precise: **most of them must fail Haiku 4.5 while Sonnet 5 passes
them.** A task Sonnet fails is unfair, not hard, and is re-reviewed; a task Haiku passes easily
is saturated and adds nothing. The eventual target is about 50% on the 2-bit workhorse.

Difficulty comes, in this order, from the amount of real material that must be read and
reconciled, from a plausible wrong course the material itself rules out, and from steps that
each depend on the previous one. It never comes from ambiguity, trick wording, or format.
**A task must be hard to DO and never hard to UNDERSTAND.**

## 2. Read, whole, once, in this order

1. `AUTHORING-BRIEF.md` — the contract every task obeys (sections 2, 8, 9 especially).
2. `r3/SPEC.md` — the spec module contract; the builder writes the candidate from it.
3. `r3/specs/EXAMPLE-m09_main_luna.py.txt` — a complete worked spec from round two.
4. `../research-r3-2026-09-08.md` — section 1, section 3, and **your slot's subsection of
   section 2**, which is the design you are implementing. You may depart from it where the
   material forces you to, and you say so in `NOTES.md`.
5. `../authoring-2026-09-06.md` section 8, items 2-4 only: the three systemic defects the last
   round's review found. Every one of them is a defect your candidate must not have.

## 3. The assignment

| slot | family | band | idea (research §2) | suggested MODE |
| --- | --- | --- | --- | ---: |
| `n01-main-claude` | claude | main | n01, the obligation nobody asked for | 1 |
| `n02-main-glm` | glm | main | n02, supersession ordered by date not position | 9 |
| `n03-main-luna` | luna | main | n03, three-way disagreement, tiebreak in prose | 5 |
| `n04-main-claude` | claude | main | n04, replay the log, do not read the state | 7 |
| `n05-main-luna` | luna | main | n05, the join key must be computed before searched | 9 |
| `n06-main-glm` | glm | main | n06, the same quantity in four units | 1 |
| `n07-main-claude` | claude | main | n07, the tool's output overrules the document | 4 |
| `n08-cheap-glm` | glm | cheap24 | n08, enumerate what is missing | 7 |
| `n09-cheap-luna` | luna | cheap24 | n09, the first complete answer is wrong | 5 |
| `n10-cheap-claude` | claude | cheap24 | n10, precedence between failure kinds, in prose | 9 |

`MODE` is the closest of the ten failure modes in `AUTHORING-BRIEF.md`; if another fits your
task better, use it and say why in `NOTES.md`. Family and band are fixed.

Bands, measured by `measure_material.py` on the built candidate:

| band | material | runs at |
| --- | ---: | --- |
| `main` | 29,000-36,000 tokens | 48k and 64k |
| `cheap24` | 12,000-16,000 tokens | 24k |

`cheap24` is new this round. Set `BAND = "cheap24"` and `TARGET_TOKENS` around 10,000-11,000
in a cheap spec; the main-band default is `BAND = "main"` with `TARGET_TOKENS` 26,000-27,000.

## 4. Method

Work only in `/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring`. It is a slow mount:
read files with `cat` or `sed -n`, never a recursive find, and never run `git` at all.

1. Write `r3/specs/<slot with underscores>.py`, e.g. `r3/specs/n03_main_luna.py`, following
   `r3/SPEC.md` exactly. Module constants first, then the functions in the order the contract
   lists them. `facts()` computes every value by reading `seed/` back from disk and asserts
   its own arithmetic; a reference that asserts a fact the material does not state is this
   benchmark's most expensive defect and has happened twice.
2. Build and check, from the authoring directory, running each of these once when you
   believe the spec is finished, and again only after a fix:

       python3 r3/build.py <slot>
       python3 cand-<family>/<slot>/selfcheck.py
       python3 probe_candidate.py cand-<family>/<slot>
       python3 probe_idempotence.py cand-<family>/<slot>
       python3 measure_material.py cand-<family>/<slot>
       python3 r3/check_rung0.py cand-<family>/<slot>
       python3 r3/check_index_leak.py cand-<family>/<slot>
       python3 r3/check_load_bearing.py cand-<family>/<slot>

   All must be clean and the measured material must be in band before you report.
3. Write nothing outside `r3/specs/<your slot>.py`; the builder writes
   `cand-<family>/<slot>/` for you. Never touch another slot, `suite/`, `r2/`, or any file
   under `results/` other than through the builder.

## 5. The traps, as instructions

- **The index leak.** The generated tree writes each stage's `limit` and `window_s` into five
  agreeing artifacts, two of which list every stage in one small file. Your decisive per-unit
  datum is one the generator does not replicate: written by `overlay()` into exactly one
  artifact per unit, of a kind no summary file carries. `check_index_leak.py` enforces it.
- **The prompt never names the file that holds the answer** and never uses a token that greps
  to it. The only `named_in_prompt` load-bearing entry is a roster of units, if the task needs
  one; knowing the scope of a sweep is not knowing its answer.
- **No tool in the seed may print the answer.** A helper validates an input the solver
  supplies; it never computes the result.
- **Every claim in `NOTES.md` is a build-time measurement**, never an estimate: if you say a
  fact sits past line 200, the spec measures it and fails the build otherwise.
- **`sweep_paths()` should cover 60-80% of the material**; a sweep of 30% has not cleared rung
  0. `load_bearing()` needs at least six paths and three distinct hops.
- **The five perturbations of `probes()` case 5 all pass**, or the grader is defective.
- Difficulty is never format, never ambiguity, never a judgement call, and never more than
  about four causal hops (research §3): each of those fails Sonnet too and marks the task
  unfair rather than hard.

## 6. Report

When the checks are clean, reply with: the slot; the row `build.py` printed (tokens, files,
load-bearing count, hops, sweep tokens, coverage %); the measured band; one line per check
saying it passed; where your candidate departs from the research idea and why; and anything
you are unsure of. Nothing else.
