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

