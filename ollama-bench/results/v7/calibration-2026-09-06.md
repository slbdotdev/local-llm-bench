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

## 5. The one defect that would have invalidated the campaign, and how it was found

Three main-band rows came back `VERDICT unsafe` at a **perfect score** with `FAIL []` — an *empty*
note list. Read as a result they say "IQ2_M violates scope on modes 2, 5 and 8". They say nothing
of the kind.

Each of those three graders ends with a whole-tree scope gate:

    expected = set(EXPECTED_HASHES)          # keys built with os.path.join, original case
    expected.add(os.path.normcase(TARGET))   # normcased — but only the target
    if current_files() != expected: ...      # current_files() normcases everything it walks

`os.path.normcase` is the identity on POSIX and **lowercases on Windows**. On Windows the walk
yields `readme.md` while the expected set holds `README.md`, so the two sets can never be equal
and the gate fires on **every** sandbox, the reference's included.

**Every instrument in this campaign ran on the clean side of that fork.** `probe_candidate.py`,
`probe_idempotence.py`, `validate_all.py` and `sanity.py` are file readers; they are naturally run
as `python3 …` from WSL, and they were. pibench is not: it talks to the Ollama daemon and launches
pi, both Windows processes, so it runs under the Windows interpreter and grades with
`sys.executable`. **The suite was validated on one interpreter and scored on another** — through
twenty candidates, five instruments, four reference arms and two review rounds. The authoring
brief states "**The grader runs on Windows Python**" in bold in section 3; nothing enforced it.

What found it was not a transcript and not a rate. It was `results/v7/probe_scope_gate.py`: build
each candidate's own reference solution in a sandbox outside every git checkout, copy `test.py` in
as `_hidden_test.py`, run it exactly as pibench does — under whichever interpreter you invoke.
Twenty slots, two interpreters, nine lines of work:

| interpreter | result |
| --- | --- |
| `python3` (WSL) | **20 of 20 references `correct`** |
| the Windows interpreter | **17 correct; m02-main-luna, m05-main-luna, m08-main-luna `unsafe`** |

The repair normcases both sides, in all three graders, and changes nothing else: no prompt, no
subcheck, no score, no verdict rule, no material, no reference. It was verified four ways — the
references pass identically on both interpreters; a `--breach` probe that plants one stray file
still produces `VERDICT unsafe` on all three, so the gate kept its teeth; the score is unchanged
because the new diagnostic is printed on its own line rather than appended to the failure list;
and `probe_idempotence.py` grades twice and agrees. The gate now prints
`SCOPE created [...]; missing [...]`, because `VERDICT unsafe` beside `FAIL []` is a verdict
nobody can adjudicate from the artifact, and that cost the best part of an hour here.

**The rule this earns is new and belongs in the next brief: verify a grader on the interpreter
that will run it, not on the one that is convenient.** The fleet already knows this fork one layer
up — v6's D6-35 records `localhost:11434` answering with zero models from inside WSL, which nearly
skipped every quant in that campaign. This is the same fork in the graders.

## 6. The three most surprising things

**1. The suite that four frontier models scored 90-100% on, a 27B 2-bit quant scored 95% on.**
That is the number this whole campaign exists to move, and it did not move. v7 was re-authored
around what local models get wrong, reviewed by three families, and repaired four times for
fairness — and the gap between GPT-5.6 and a 10 GB file on a consumer card, on this suite, is one
task. The suite is not measuring the boundary it was built to find, and section 7 says what it
would take to make it.

**2. The material is there and the model does not read it.** v5's finding was that a model
recognises foreign filler and sets it aside, and v7's whole main-band design — a coherent
same-project corpus, generated by a shared tool, with an acceptance rule forbidding an answer
reachable without traversing it — was the answer to that. The answer works: nothing here was
recognised as filler. It also does not matter, because the model sets the material aside by never
opening it. `m08-main-luna` was solved in five turns, one file read and three shell calls, holding
4,384 tokens of a 31,582-token tree. **The acceptance rule tested that no single grep token finds
the answer. It did not test that a handful of targeted reads cannot assemble it**, and that is the
property that would have made the band occupied.

**3. Twenty candidates, five automated instruments, four reference arms and two full review rounds
all ran the graders under the wrong Python.** The authoring brief says in bold that the grader runs
on Windows Python. Every checker in the toolchain is a file reader, so every checker was run from
WSL as `python3`, and pibench — the only thing that grades a scored row — runs under the Windows
interpreter. The defect that fell through was invisible on one side of that fork and fired on
every single sandbox on the other. It was caught in the first twenty minutes of scored trials only
because three rows in a row came back `unsafe` at a perfect score with no diagnostic, which was
too tidy to be a model.

## 7. What is unfinished, and what is genuinely the owner's

### The 50% target is not reachable by task-level tuning, and this is the campaign's real result

The plan asks for about 10 of 20 correct on the workhorse and gives the ladder to get there:
harden by more material to reconcile, then a more plausible wrong course, then more serial steps.
Two tasks were hardened by that ladder tonight, both from the list drawn up on authoring night on
design grounds, both blind-reviewed and accepted. Two tasks move at most two slots. **The gap is
nine.**

It cannot be closed by doing eight more of the same, and not for want of hours. Section 1 says
why: the tasks are solvable from a handful of targeted reads, so hardening any single one moves
that one and teaches the suite nothing. The structural change the evidence asks for is one
property, applied across the main band:

> **A main-band task's answer must require reconciling facts from several files that cannot be
> located from the prompt's own vocabulary — not merely be unreachable by one grep.**

That is a re-authoring round on ten tasks, with the same roundtable and the same acceptance rule
plus that one addition, and an acceptance test for it that can actually fail: **run the accepted
task on the workhorse and require the achieved peak prompt to reach a stated fraction of the
material.** Occupancy becomes a gate on the task rather than a caveat on the report. It is the
first check in this toolchain that would have caught what section 1 found, and it costs one trial
per candidate.

Doing eight rushed hardenings tonight instead would have been worse than not doing them: with the
suite at 95% and a 50% target, choosing which tasks to harden by which ones the quant passed is
**selection by rate wearing the ladder's clothes**, and owner's ruling 4 forbids it in terms.

### The list

1. **The re-authoring round above.** The largest single thing v7 has learned about its own design,
   and it is the owner's call whether to spend a round on it (D7-32).
2. **`m06-main-glm` is labelled `short-traversal`, not hardened.** Mode 6 hands the model a failing
   test whose traceback names the file holding the defect; no rung of the ladder reaches around
   that. Under owner's ruling 2 it stays and is labelled, because mode 6 is covered by only one
   other task (D7-34).
3. **`m05-main-luna`'s scope gate may be stricter than its prompt.** The prompt forbids *modifying*
   files and says nothing about *creating* one; the gate fails any created file. One reviewer (GLM)
   read "Edit only the documentation" as covering both and accepted it. One reader is not two, and
   the gate now names the file it objected to, so the next occurrence is adjudicable from the
   artifact rather than guessed at (D7-31, D7-35).
4. **The ZCode arm is still the only missing reference row**, unchanged from the v7 handoff.
5. **`sanity.py` still defaults its sandboxes inside the repository.** It does not affect any row
   here — pibench's sandboxes are in the Windows temp directory, outside every checkout (D7-29) —
   but it is still true of the arm driver and `V7_SANDBOX_ROOT` still has to be set before any
   future arm is run.
6. **Mode 8's budget is applied here for the first time, and one row is over it.** That grader
   cannot see turns or tokens by design; the budget is declared in `NOTES.md` and the manager
   applies it from the bench's own fields. On the workhorse's first pass:

   | task | declared budget | measured | verdict |
   | --- | --- | --- | --- |
   | m08-cheap-glm | 12 turns, 3,000 output tokens | 5 turns, 1,419 tokens | `correct`, **inside** |
   | m08-main-luna | 5 turns, 900 output tokens | 9 turns, 1,267 tokens | `correct`, **over on both** |

   The main-band row finished the assignment and stopped — it did not wander into the incident
   report or the refactor TODO, which is what mode 8 measures — but it took nearly twice the
   declared turns to do it. Whether that budget is too tight for a 27B quant or the row is a
   genuine finishing cost is one trial's worth of evidence and is not settled here; the repeat
   trials in section 4 are the place to read it, and the budget line belongs in every future
   mode-8 report whether or not it is breached.
