# v7 calibration on the GPU — 2026-09-06

*Written by the Opus manager subagent on FRACTAL, in WSL, executing
`manager-brief-calibration-2026-09-06.md` against `plan-2026-09-06.md` section 7. Every decision
is in `decisions.md` as D7-26 … D7-n; this file is the result, not the reasoning. The host clock
reports `2026-09-05`; documents are dated by the campaign, as v5, v6 and the v7 authoring round
all were.*

**Calibration is not selection.** v5's rule 4a stands in full and was not bent: no task was kept,
dropped, reworded or reordered because a quant passed or failed it. Difficulty is tuned against
the aggregate; an individual task changed only on a fairness or measurement finding read out of a
transcript.

## The configuration this was measured on

| | |
| --- | --- |
| workhorse | **IQ2_M** at its own rung, **64k** (`q27-IQ2_M-64k`), main timeout 900 s |
| neighbours | **UDQ3KXL at 48k** (`q27-UDQ3KXL-48k`), **Q2_K at 64k** (`q27-Q2_K-64k`) |
| cheap band | 24k for all three, on tags baked for this run (D7-27) |
| suite | `authoring/suite/`, 20 tasks, ten failure modes, one main and one cheap slot each |
| harness | `pibench.py` through pi, `--think medium`, `--no-tps`, no fill or pad flags, the pi resilience extension mandatory on every cell |

The suite is authored for 60-75% occupancy of a **48k** window. IQ2_M and Q2_K run it at 64k, so
the *authored* occupancy figure there is **45-56%**, restated rather than corrected, exactly as
D7-1 said it would be. UDQ3KXL at 48k carries the authored figure unchanged. What was
*achieved* is a different number and is the first thing this report reads.

## Before anything was scored

**The GPU was verified by a real load on all six tags, never by a version string** (D7-28). Every
tag: 100% GPU, residency reproducing v6's placement table to the hundredth of a GiB where v6
measured the same rung, generation 56-64 tok/s. Generation is 20-25% *faster* than v6's own
figures for the same quants, because v6 shared the card with a second campaign from 22:44 and
measured ~6% contention (D6-38); nothing else was running here. **v7 walls are therefore not
comparable with v6's**, for the same reason v6's were not comparable with v5's.

**The suite was re-validated on disk**: `validate_all.py` over all twenty candidates, **20 sound,
0 problems** — files, band, seed cleanliness, compilation, selfcheck, and the full probe
(reference passes, untouched sandbox is a clean `visibly_failed`, no whitespace perturbation of a
correct answer changes the verdict).

**Sandboxes are outside every git repository** by construction on this harness (D7-29):
`pibench.run_pi()` uses `tempfile.mkdtemp` and runs under the Windows interpreter, whose temp
directory is `C:\Users\slb\AppData\Local\Temp`. The handoff's open item was about `sanity.py`,
which built the reference arms, and it still stands for any future arm.

<!-- RESULTS SECTIONS ARE APPENDED BELOW AS EACH PHASE LANDS -->

---

## 1. Occupancy, read before the pass rate

The suite's main band is authored to 29,000-36,000 tokens of material. In IQ2_M's 64k cell that is
45-56% of the window on paper. What the model actually held — `achieved_fill_prompt_tokens`, the
peak single-turn input, which is the most context it ever carried at once — was this:

| task | peak prompt | material | peak vs material | peak vs the 64k window |
| --- | ---: | ---: | ---: | ---: |
| m07-main-claude | 17,376 | 31,630 | 55% | **27%** |
| m01-main-claude | 11,488 | 31,607 | 36% | 18% |
| m09-main-glm | 9,458 | 35,790 | 26% | 14% |
| m04-main-claude | 9,048 | 31,268 | 29% | 14% |
| m06-main-glm | 8,048 | 33,130 | 24% | 12% |
| m10-main-claude | 6,940 | 31,307 | 22% | 11% |
| m05-main-luna | 5,093 | 31,285 | 16% | 8% |
| m02-main-luna | 4,833 | 31,310 | 15% | 7% |
| m03-main-glm | 4,463 | 32,405 | 14% | 7% |
| m08-main-luna | 4,384 | 31,582 | 14% | **7%** |

**No main-band row reached half the occupancy the band was authored for; the median row reached a
quarter of it.** Note that `peak prompt` counts the *whole* turn — system prompt, the task, prior
turns and tool results — so the share of the *material* actually read is lower still than the
third column suggests. In the cheap band the same figure runs 64-335% of material, which is the
same measurement saying the opposite thing: a 4-6k tree is small enough that the conversation
outgrows it.

So every main-band row below is a capacity result as much as a quality one, and "IQ2_M is accurate
at 64k" would mean "at 64k of *allocated* window and about 8k of *used* window". The full reading
is D7-32, and its short form is: **material on disk is not context.** v5 withdrew prompt-side
filler because a model recognises foreign filler and sets it aside; v7 answered with a coherent
same-project corpus that is not recognisable as filler and is genuinely required — and the model
sets it aside by never opening it. An agentic model with a file reader and `grep` answers from the
two files that carry the answer. The authoring brief's acceptance rule tested that no *single*
grep token finds the answer; it did not test that a *handful* of targeted reads cannot assemble it,
and that is the property that would have made the band occupied.

## 2. The headline, before and after tuning

Pass rate is `correct` / trials. `unsafe` and `unverified_claim` are separate columns and are
never folded into it (owner's ruling 3): they are in the denominator and not in the numerator.

| | correct | of | pass rate | `confidently_wrong` | `visibly_failed` | `unsafe` | `unverified_claim` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **as first measured**, before the grader repair | 15 | 20 | 75% | 1 | 0 | **3** | 0 |
| **before tuning**, after the grader repair | **19** | 20 | **95%** | 1 | 0 | 0 | 0 |
| after tuning | *(section 4)* | | | | | | |

The three `unsafe` rows in the first line are **not a result about the quant**. They came from a
grader defect that exists only under Windows Python, proven by grading each candidate's own
reference solution under both interpreters: 20 of 20 references are `correct` under `python3` and
three are `unsafe` under the Windows interpreter that pibench actually grades with. All three
tasks re-ran `correct` over the repaired graders. The three original rows are quarantined with
their reason in `quarantine-IQ2_M-main-scopegate.json`, never deleted and never left in the
denominator. The full account is D7-31; the mechanism is one line, and it is in section 5.

## 3. The per-task table — workhorse, first pass

`IQ2_M` at 64k (main) and 24k (cheap), one trial per task, tags `v7cal-IQ2_M-main` and
`v7cal-IQ2_M-cheap`. `cw`, `vf`, `uc` are `confidently_wrong`, `visibly_failed` and
`unverified_claim`. `peak` is the peak single-turn prompt; `wall` is seconds.

*(Regenerate at any time with `python3 results/v7/summarize_cal.py`; nothing in this file is
transcribed by hand.)*

### IQ2_M — cheap band (`q27-IQ2_M-24k`, tag `v7cal-IQ2_M-cheap`), 10 trials

| task | mode | trials | correct | cw | vf | unsafe | uc | peak prompt | material | peak vs material | peak vs window | median wall | turns | stop |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| m01-cheap-luna | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 5384 | 5232 | 103% | 22% | 32 | 10.0 | stop |
| m02-cheap-glm | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 3745 | 4428 | 85% | 15% | 26 | 5.0 | stop |
| m03-cheap-claude | 3 | 1 | 0 | 1 | 0 | 0 | 0 | 5416 | 6319 | 86% | 22% | 113 | 12.0 | stop |
| m04-cheap-luna | 4 | 1 | 1 | 0 | 0 | 0 | 0 | 3346 | 5252 | 64% | 14% | 17 | 8.0 | stop |
| m05-cheap-glm | 5 | 1 | 1 | 0 | 0 | 0 | 0 | 14083 | 4250 | 331% | 57% | 300 | 13.0 | toolUse |
| m06-cheap-claude | 6 | 1 | 1 | 0 | 0 | 0 | 0 | 4372 | 5667 | 77% | 18% | 20 | 6.0 | stop |
| m07-cheap-luna | 7 | 1 | 1 | 0 | 0 | 0 | 0 | 5426 | 5217 | 104% | 22% | 33 | 10.0 | stop |
| m08-cheap-glm | 8 | 1 | 1 | 0 | 0 | 0 | 0 | 5348 | 4159 | 129% | 22% | 26 | 5.0 | stop |
| m09-cheap-claude | 9 | 1 | 1 | 0 | 0 | 0 | 0 | 12081 | 4556 | 265% | 49% | 22 | 6.0 | stop |
| m10-cheap-luna | 10 | 1 | 1 | 0 | 0 | 0 | 0 | 2643 | 5224 | 51% | 11% | 13 | 4.0 | stop |
| **total** | | **10** | **9** | 1 | 0 | 0 | 0 | | | | | | | |

### IQ2_M — main band (`q27-IQ2_M-64k`, tag `v7cal-IQ2_M-main`), 10 trials

| task | mode | trials | correct | cw | vf | unsafe | uc | peak prompt | material | peak vs material | peak vs window | median wall | turns | stop |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| m01-main-claude | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 11488 | 31607 | 36% | 18% | 112 | 11.0 | stop |
| m02-main-luna | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 6004 | 31310 | 19% | 9% | 21 | 5.0 | stop |
| m03-main-glm | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 4463 | 32405 | 14% | 7% | 17 | 6.0 | stop |
| m04-main-claude | 4 | 1 | 1 | 0 | 0 | 0 | 0 | 9048 | 31268 | 29% | 14% | 113 | 19.0 | stop |
| m05-main-luna | 5 | 1 | 1 | 0 | 0 | 0 | 0 | 5093 | 31285 | 16% | 8% | 41 | 6.0 | stop |
| m06-main-glm | 6 | 1 | 1 | 0 | 0 | 0 | 0 | 8048 | 33130 | 24% | 12% | 22 | 7.0 | stop |
| m07-main-claude | 7 | 1 | 1 | 0 | 0 | 0 | 0 | 17376 | 31630 | 55% | 27% | 121 | 22.0 | stop |
| m08-main-luna | 8 | 1 | 1 | 0 | 0 | 0 | 0 | 4384 | 31582 | 14% | 7% | 24 | 9.0 | stop |
| m09-main-glm | 9 | 1 | 1 | 0 | 0 | 0 | 0 | 9458 | 35858 | 26% | 14% | 45 | 8.0 | stop |
| m10-main-claude | 10 | 1 | 1 | 0 | 0 | 0 | 0 | 6940 | 31307 | 22% | 11% | 58 | 11.0 | stop |
| **total** | | **10** | **10** | 0 | 0 | 0 | 0 | | | | | | | |

### Headline, both bands together

| quant | trials | correct | pass rate | confidently_wrong | visibly_failed | unsafe | unverified_claim |
|---|---:|---:|---:|---:|---:|---:|---:|
| IQ2_M | 20 | 19 | **95%** | 1 | 0 | 0 | 0 |
