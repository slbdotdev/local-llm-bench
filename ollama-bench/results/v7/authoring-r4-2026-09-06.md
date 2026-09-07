# v7 round four — tasks whose facts a grep cannot harvest, and the measurement that says the coverage gate is pointed the wrong way, 2026-09-09
*Renamed 2026-09-06 from `v7/authoring-r4-2026-09-09.md`: the campaign labelled rounds by planned campaign day, not by the calendar date they were written.*

*Written by the round-four manager. Round three's record is `authoring-r3-2026-09-06.md`; the
plan of record is `plan-r3-2026-09-06.md`; the round's instrument finding has its own file,
`coverage-instrument-2026-09-06.md`, and is summarised in section 7 here.*

## 1. The brief, and the answer to it

Round three's ten tasks were hard to traverse and easy to harvest: a model that never read the
material could still `grep -rn` a distinctive token and collect the decisive fact for every unit
in one screen. Round four's question was how to stop that **without** making anything hard to
understand — the campaign's standing rule that a task may be hard to DO and never hard to
UNDERSTAND.

One Luna run answered it in `research-r4-2026-09-06.md` (4,524 words, sourced). Its finding, and
the round's design rule:

> A fact that is **derived** — that occurs nowhere in `seed/` as a literal string, because it is
> the result of replaying that unit's own records against a rule the material states in plain
> words — is immune to a token attack, a frame attack and a shape attack at once, and it adds
> work without adding obfuscation.

The research also **demoted the round's presumed exemplar**. `n09-cheap-luna`, round three's one
gate-passing task, was read as the anti-harvest model; the research showed
`grep -rn release_status seed/` reaches all eight of its component documents, so n09 is not an
anti-harvest exemplar at all. That reading was checked against the tree and held: rebuilt as a
probe fixture it measures H1 = 1.000.

## 2. The instrument: `r4/check_harvest.py`

The round's new check, designed here and documented in `r4/SPEC.md`. A candidate declares
`harvest_units()`: for each unit, the decisive datum, that unit's identifier, and the path the
datum is stated at. The check then runs four attacks against the giveaway vocabulary *G* — the
distinctive tokens of `prompt.md`, of any load-bearing file the prompt names, of the deliverable
name and of the scored keys.

| measure | attack | limit |
| --- | --- | ---: |
| H1 | the largest fraction of units one giveaway token harvests at `grep -C2` | < 1/4 |
| H2 | a roster-alternation regex over the unit identifiers | < 2/5 |
| H3 | H1 again at `grep -C5` | < 1/3 |
| H4 | frame harvest: a 2-6 word run shared by the value-bearing lines | < 1/4 |
| P2 | the best two-token union | reported, not gated |

A unit is *harvested* when a giveaway token's match window contains the value **and** the
attribution — either the file is the unit's own, or the identifier is in the same window.
`probe_harvest.py` is the check's own probe: two synthetic trees differing only in the property
under test, and the check must reject the harvestable one (H1 = 1.000) and accept the derived one
(H1 = H2 = 0.000).

**The campaign's law, restated.** Five defects in this instrument were found in round four. Every
one was found by a blind cross-reviewer of a candidate, and **none** by any checker, including
this one: the unit-name join, the key-value join, one constant word standing for all units, frame
harvest through blank-line padding, and a splitter that did not break on `/`, `-` or `.`. Each was
reproduced by the manager before it was closed. A checker states a property; only a reader finds
the property you did not think to state.

## 3. What was authored

Ten slots across three families, authored blind, two cross-family reviews each, one revision.

| slot | family | mode | band | outcome |
| --- | --- | ---: | --- | --- |
| p01-main-glm | glm | 1 | main | revised once (fairness + H4 = 1.000) |
| p02-main-claude | claude | 2 | main | accepted, one PASS |
| p03-main-luna | luna | 3 | main | **dropped** after two revisions |
| p04-main-glm | glm | 4 | main | revised once (rung-0 one-file shortcut) |
| p05-main-claude | claude | 5 | main | accepted, one PASS |
| p06-cheap-luna | luna | 6 | cheap24 | **dropped** after one revision |
| p07-cheap-glm | glm | 7 | cheap24 | **withdrawn**, unauthored (lane budget) |
| p08-cheap-claude | claude | 8 | cheap24 | accepted; one fairness fix |
| p09-main-luna | luna | 9 | main | revised twice (H4, then floor) |
| p10-cheap-glm | glm | 10 | cheap24 | **withdrawn**, unauthored (lane budget) |

Reasons are in `results/v7/decisions-r4-2026-09-06.md` and summarised: p03 was reproduced by a reviewer
**with zero files opened**, in three greps, and no longer exercised its mode at all; p06 hit mode
6's known structural property — the traceback names the file holding the defect, and no rung
reaches around that (D7-34) — at full score from two files; p07 and p10 were withdrawn for
scheduling, since the Z.ai plan allows this manager one concurrent GLM run and four authoring runs
plus six reviews on one lane would have consumed the GPU window the reference arms and the
calibration needed. An unfilled slot costs the suite nothing: admission only ever replaces an
incumbent.

## 4. Four candidates were dropped, and every one by a reader

The round's central result is not a number. Ten slots were opened, two were withdrawn unauthored
for lane budget, and **four of the eight authored were dropped after review** — p01, p03, p06 and
p09. In each case the blind cross-reviewer did what no checker in the pipeline does: it tried to
answer the task without doing the work, and succeeded.

| slot | what the reviewer did | files opened |
| --- | --- | ---: |
| p03-main-luna | three greps, byte-identical output, `test.py` 8/8 `correct` | **0** |
| p09-main-luna | ran `tools/retention_audit.py`, which `README.md` tells the solver to run and which prints `verified_on` and `declared=/effective=` for all 19 regions, plus two greps | **0** |
| p01-main-glm | one file for the promise, then `grep -rnE -C2 'DLV-\|through:' seed/` driven into a script, reproducing `ref/` byte for byte, 8/8 `correct` | **2** |
| p04-main-glm (first build) | imported the seed's own `tools/run_checks.py` and called its two functions in one command | **1** |

`r4/BRIEF.md` section 6 states the rule those four broke: **no tool in the seed may print the
answer**, and a shortcut under five files is a rung-0 failure. Every one of the four cleared
`check_harvest.py`, `check_rung0.py`, `check_index_leak.py`, `check_load_bearing.py`,
`selfcheck.py` and `probe_candidate.py` first.

**So the round's method finding is this.** Making a value *derived* does defeat the token, frame
and shape attacks the new instrument measures — four candidates reached H1 = H2 = H3 = H4 = 0.000
and the measures are honest. It does not defeat the two attacks that actually decide a benchmark:
**a tool in the material that does the derivation**, and **a grep that harvests the inputs rather
than the answer**. A checker can be told to look for a token near a value. Neither of those two is
a property of a line, so neither is reachable by a check of the kind this round built, and both
were found every time by a person reading with intent to cheat.

That is the same law round four began with, now stated from the other side: the instrument found
zero of the six rung-0 failures in this round; blind cross-review found all six.

## 5. What the workhorse says about the accepted suite

Every accepted task, **five** workhorse trials, both bands; then the two calibration neighbours at
one trial each. Tags `v7r4cal-*`, twenty tasks, one hundred and forty rows. The same tags also carry the parked
candidates' rows (p04, p05, p08, p09), which are **not** part of these totals: the table below is
the twenty accepted tasks only.

| cell | model | rows | correct |
| --- | --- | ---: | ---: |
| main | q27-IQ2_M-64k (workhorse) | 50 | **48 (96%)** |
| cheap | q27-IQ2_M-24k (workhorse) | 50 | **48 (96%)** |
| main | q27-UDQ3KXL-48k | 10 | 10 |
| cheap | q27-UDQ3KXL-24k | 10 | 10 |
| main | q27-Q2_K-64k | 10 | 10 |
| cheap | q27-Q2_K-24k | 10 | 9 |

**The accepted suite is 96 of 100 on the workhorse at five trials — 96.0%.** Not one of the four
non-`correct` rows is *wrong*: two are `unsafe` and two are `visibly_failed`. `unsafe` is in the
denominator and never in the numerator — a trial can be unsafe at a full score — and no task in the
accepted suite produced a single `confidently_wrong` row in a hundred trials. Four tasks are 4/5
(`m03-cheap-claude`, `m06-cheap-claude`, `m07-main-claude`, `p02-main-claude`) and the other
sixteen are 5/5. Trials four and five were run precisely because this round's own finding is that a
small trial count is luck; they moved the figure by 0.7 points and changed no task's character. Both neighbours are
at or above it. The 50% target is not close, and the suite does not separate the three quants at
all. That is the measurement round four was commissioned by, and it is worse than round three's
record implied, because round three's numbers were single-trial.

Round four's own candidates, same cell, three trials each: p02 3/3, p05 **1/3**, p08 3/3, p09 2/3
— 9 of 12. Only p05 is hard for the workhorse, and p05's two failures are a `stop=length` and a
`visibly_failed`, i.e. the model ran out of room rather than answering wrongly.

## 6. Step 7: round three at three trials, and the gate's sign

`coverage-instrument-2026-09-06.md` is the full record; the two results the plan asked for:

1. **Round three's 10 of 10 was luck.** Thirty trials of the same ten candidates give **21 of 30
   (70%)** — main 13/21, cheap24 8/9 — and six of the ten tasks are not deterministic. No
   single-trial pass rate in this campaign is a property of a task.
2. **Coverage and the pass rate correlate with the wrong sign: Pearson r = +0.471.** The five
   lowest-coverage rows score 9 of 15; the five highest score 12 of 15. A task the model can
   traverse completely is one it can solve; a task it fails is one it got lost in, and getting
   lost reads as *low* coverage. Admitting on coverage pushes the pass rate **up**, away from the
   50% target the same plan sets.

Round four's own rows say it again from inside a single task. `p02-main-claude` was answered
`correct` on all three trials at coverage **44.4%, 12.1% and 10.0%** — a factor of four apart, same
task, same model, same verdict. Coverage is a property of a trial's reading style, not of the task.

Every calibration row was gated. **0 of 140 rows pass**; the twenty accepted tasks fail the
load-bearing half automatically, because `LOAD_BEARING` is a round-four instrument and no incumbent
`test.py` declares it.

## 7. The reference arms

One trial per candidate, per arm, in a sandbox outside every git checkout (D7-18), graded by
`authoring/sanity.py` with the same prep and the same grader as every other arm.

| arm | p01 | p02 | p04 | p05 | p08 | p09 | correct |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| Sonnet 5 | **cw** | correct | correct | correct | correct | correct | 5/6 |
| Haiku 4.5 | **cw** | correct | correct | correct | correct | correct | 5/6 |
| Luna (gpt-5.6) | **cw** | correct | **cw** | correct | correct | correct | 4/6 |
| GLM 5.3 Flash | — | correct | correct | correct | correct | — | 4/4 |

Two things the arms decided, not merely reported.

**p08's Sonnet failure was a fairness defect and was believed only after it was re-read.** Sonnet
answered `authorising_record: history/0211` where the reference wants `QC-1204`. Both forms are in
the material and `history/CHANGELOG.md` itself cites entries as `history/0000`, so the prompt's
"the identifier of the dated entry … exactly as it is written in the material" had two defensible
readings and Sonnet took the one the corpus's own convention supports. That is round three's n05
defect, not difficulty. The prompt was reworded to name the **form** and never the value, nothing
in `seed/`, `test.py` or the expected values moved, and the rebuilt row was identical. Sonnet then
scored 7/7 `correct`, and the workhorse row was re-measured and unchanged.

**p01's Sonnet failure was believed, and it cost the candidate.** Its blind re-reviewer, reading
independently, returned `fair: no` on the same tree for a different reason — README and all
eighteen component pages state the log convention as "oldest signature last" while the rows run
oldest-first — so an honest reader lands in the author's own listed wrong course. Sonnet, Haiku
and Luna all failed it 6/8 `confidently_wrong`. A task all three reference arms get wrong is not a
hard task; it is an unclear one.

GLM 5.3 Flash, run on the four candidates that were still live when the Z.ai window
refilled, passed all four. Haiku 4.5 passed five of six. The round-three tier assumption — that Haiku fails and Sonnet passes
— did not hold for any surviving round-four candidate.

## 8. Admission

The plan admits a candidate on **two cross-family PASSes**, and `assemble_suite.py` refuses a
suite in which one family authors **more than** 40% of the accepted tasks. With p01, p03, p06 and
p09 dropped, the three remaining candidates with a route to admission were all authored by claude,
and the only candidate that would have moved a slot *away* from claude — p04 — spent its one
revision and came back with one PASS and one REVISE. So the cap allowed exactly one.

**Admitted: `p02-main-claude`, replacing `m02-main-luna`.** Two cross-family PASSes (luna, glm),
both with `fix: none`, both `hard_to_do: yes`. It carries the round's highest floor coverage,
74.8% — thirty-eight load-bearing paths over four hops, the largest causally-necessary set any
candidate in this campaign has declared — and its glm reviewer re-verified by hand that an
exhaustive digit-run search over the whole tree finds none of the eighteen decisive values, so
H1 = H2 = H3 = H4 = 0.000 is a measurement rather than a vacuous zero. That is the ground it was
chosen on: a build-time property of the material, decided before any verdict was read.

**Parked, in the register, admissible without further work when the cap allows:**

* `p05-main-claude` — two cross-family PASSes, `fix: none` from both. Blocked only by the 40% cap.
* `p04-main-glm` — one PASS (luna) and one REVISE (claude) after its revision. The revision did
  close what it was sent back for: the seed's verifier now validates a solver-supplied line
  instead of computing the comparison (a reviewer confirmed that importing it yields nothing), and
  the shared preamble is gone. What the re-review found instead is new and smaller: the six failing
  stages, and only those, carry post-close journal rows dated `2034-07`, so `grep -rl '2034-07'
  data/intake/` returns exactly the `failed_stages` line. Rung 0 is cleared — sixteen files, above
  the five-file floor — but two `NOTES.md` claims are false of the built tree, and one command
  hands over the answer's central group. One revision is the rule.
* `p08-cheap-claude` — a glm **PASS** with `fix: none`, `hard_to_do: yes` and a nine-file shortcut
  floor, plus a luna REVISE on a `NOTES.md` claim that was corrected and verified, and the fairness
  fix its Sonnet arm forced. Its glm review was run after admission closed, on the lane's last hour,
  precisely because the cap could not admit it whatever the review said — but the next round will
  not have to run it.

**The suite after admission.** Twenty tasks; family share claude 8 (40%), glm 6 (30%), luna 6
(30%); all ten failure modes covered twice, once per band. Every one of the twenty references
grades `correct` under the Windows interpreter pibench grades with (`probe_scope_gate_suite.sh`,
20/20), which is the check calibration section 5 exists for.

## 9. What is open

**The owner's decision, stated plainly.** Plan section 2.2 makes material coverage an admission
gate at 50%, and plan section 2.1 sets a 50% workhorse pass rate as the suite's target. This
round measured the relation between them and it is **positive**: r = +0.471 over round three's ten
tasks at three trials each, and within a single round-four task coverage moved from 44.4% to 10.0%
across three trials that were all `correct`. Coverage measures how a trial read, not how much
material the task requires; admitting on it raises the pass rate and moves the suite away from the
50% target. The two instruments the plan asks the manager to read together pull in opposite
directions, and the plan must say which one yields.

Three courses are set out in `coverage-instrument-2026-09-06.md` section "What this leaves for the
owner". **The manager's recommendation is course 2: demote coverage to a diagnostic** reported
beside every row exactly as peak input is today, and admit on the reference arms and the
cross-review alone — which is, in fact, what this round had to do, because no row of the campaign
has ever passed the gate and admitting on it would have admitted nothing.

**Everything downstream of that decision was still done.** One task was admitted, the suite was
reassembled and re-probed, and every calibration row was gated and is reported below the gate with
its number, so whichever course the owner takes, the rows are already measured.

**What the round could not do, and why.**

* **Seven of ten slots produced no admitted task.** Four were dropped for rung-0 failures found by
  reviewers, two were withdrawn unauthored for lane budget, and one was parked by the family cap.
* **The 40% family cap is now the binding constraint on this campaign, not authoring capacity.**
  Three candidates hold two cross-family PASSes or are one review from them, and only one could be
  admitted, because every one of them is claude-authored — which is itself forced by the
  provenance rule, since a re-authored slot may go to only one family. If the next round is to
  admit more than one task, either the cap moves or the slots re-opened must be ones whose only
  legal family is not claude.
* **The Z.ai plan hit its five-hour limit** (error 1308) part-way through p04's first revision,
  which cost that run and about thirty-five minutes of lane time; the plan is `lite` and was shared
  with another manager. It was **not** `quota_exhausted`: the window refilled at 12:40:25Z and the
  lane ran p04's revision, the batched review and the GLM arm inside it. Weekly usage ended at 58%.
* **No OpenRouter spend of any kind.**

## 10. Where everything is

| what | where |
| --- | --- |
| the round's research | `results/v7/research-r4-2026-09-06.md` |
| the instrument, its spec and its probe | `authoring/r4/check_harvest.py`, `r4/SPEC.md`, `r4/probe_harvest.py` |
| author and review briefs | `authoring/r4/BRIEF.md`, `r4/REVIEW-BRIEF.md` |
| every review report | `authoring/r4/reviews/` |
| the candidates | `authoring/cand-{claude,glm,luna}/p0*`, staged at `authoring/r4/gate-suite/` |
| the register | `authoring/roundtable.md`, "The register" and "Harvest round (v7r4)" |
| drop and park decisions, with reasons | `results/v7/decisions-r4-2026-09-06.md` |
| acceptance cells | `results/v7r4-gate-*.json` |
| the calibration | `results/v7r4cal-{IQ2_M,UDQ3KXL,Q2_K}-{main,cheap}.json` |
| the coverage gate on every calibration row | `results/v7/coverage-r4-suite.json` |
| round three at three trials | `results/v7r3-rep-{main,cheap}.json`, `results/v7/r3repeat.log` |
| the instrument finding, in full | `results/v7/coverage-instrument-2026-09-06.md` |
| the reference arms | `authoring/sanity/{sonnet,haiku,luna,glm}/trial-r4/results.json` |
| the handoff | `results/v7/handoff-r4-2026-09-06.md` |
