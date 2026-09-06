# v7 round four — tasks whose facts a grep cannot harvest, and the measurement that says the coverage gate is pointed the wrong way, 2026-09-09

*Written by the round-four manager. Round three's record is `authoring-r3-2026-09-08.md`; the
plan of record is `plan-2026-09-07.md`; the round's instrument finding has its own file,
`coverage-instrument-2026-09-09.md`, and is summarised in section 7 here.*

## 1. The brief, and the answer to it

Round three's ten tasks were hard to traverse and easy to harvest: a model that never read the
material could still `grep -rn` a distinctive token and collect the decisive fact for every unit
in one screen. Round four's question was how to stop that **without** making anything hard to
understand — the campaign's standing rule that a task may be hard to DO and never hard to
UNDERSTAND.

One Luna run answered it in `research-r4-2026-09-09.md` (4,524 words, sourced). Its finding, and
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

Reasons are in `/home/slb/v7r4/DECISIONS.md` and summarised: p03 was reproduced by a reviewer
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

Every accepted task, three workhorse trials, both bands; then the two calibration neighbours at
one trial each. Tags `v7r4cal-*`, twenty tasks, one hundred and four rows.

| cell | model | rows | correct |
| --- | --- | ---: | ---: |
| main | q27-IQ2_M-64k (workhorse) | 30 | **30 (100%)** |
| cheap | q27-IQ2_M-24k (workhorse) | 30 | **28 (93%)** |
| main | q27-UDQ3KXL-48k | 10 | 10 |
| cheap | q27-UDQ3KXL-24k | 10 | 10 |
| main | q27-Q2_K-64k | 10 | 10 |
| cheap | q27-Q2_K-24k | 10 | 9 |

**The accepted suite is 58 of 60 on the workhorse at three trials — 96.7%.** Both neighbours are
at or above it. The 50% target is not close, and the suite does not separate the three quants at
all. That is the measurement round four was commissioned by, and it is worse than round three's
record implied, because round three's numbers were single-trial.

Round four's own candidates, same cell, three trials each: p02 3/3, p05 **1/3**, p08 3/3, p09 2/3
— 9 of 12. Only p05 is hard for the workhorse, and p05's two failures are a `stop=length` and a
`visibly_failed`, i.e. the model ran out of room rather than answering wrongly.

## 6. Step 7: round three at three trials, and the gate's sign

`coverage-instrument-2026-09-09.md` is the full record; the two results the plan asked for:

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

Every calibration row was gated. **0 of 72 rows pass**; the twenty accepted tasks fail the
load-bearing half automatically, because `LOAD_BEARING` is a round-four instrument and no incumbent
`test.py` declares it.

