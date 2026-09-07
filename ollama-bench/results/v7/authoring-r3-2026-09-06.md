# v7 round three — ten tasks tuned for difficulty, and the first GPU acceptance sweep, 2026-09-08
*Renamed 2026-09-06 from `v7/authoring-r3-2026-09-08.md`: the campaign labelled rounds by planned campaign day, not by the calendar date they were written.*

*Written by the Fable control session in WSL. Read after `authoring-2026-09-06.md` (round two)
and `calibration-2026-09-06.md`. The register rows are in `authoring/roundtable.md` under
"Difficulty round (v7r3)". Campaign dates are used for the round; wall-clock dates on this
host read 2026-09-05/06.*

## 1. The brief, and the answer to it

The owner's brief: round two came back saturated, so author ten more tasks tuned for
difficulty with one more round of research and one more roundtable, bring the whole suite up
to thirty tasks with a baseline on the four reference arms, and spend at most $1 on a
27B fp8 endpoint to gauge the unquantised model. The requirement was precise: **most of the
new tasks should fail at least Haiku 4.5**, while Sonnet 5 passes them. Late in the night the
owner released the GPU, so the workhorse quant ran too.

**The answer is no, and the numbers below say why.** Ten tasks were authored with real family
provenance, reviewed blind, and accepted with two passes each. Sonnet 5 passes all ten. Haiku
4.5 fails two (n02, n09). Luna fails one (n01). GLM 5.3 Flash fails none. The fp8 27B fails
two (n03, n04), and the 2-bit IQ2_M workhorse, the model the whole bench is for, passes all
ten round-three tasks. The tasks are harder than round two by every static measure the
toolchain has (load-bearing paths, hops, sweep coverage, rung 0), and they are still not hard
enough to separate a Claude Code subagent with `grep` from a careful reader.

Round two, on the other hand, is the first authored set the workhorse has ever failed:
**7 of 9** on IQ2_M at 64k, with m01-main-glm running its context out after 39 file reads and
m10-main-glm confidently wrong on the corrected-stage set. Those nine were authored for
*material necessity* (rung 0), not for a trap, and they are the evidence the calibration
report asked for: the coverage gate is what moves the workhorse, not the cleverness of the
wrong course.

## 2. What was authored

| slot | family | band | idea | reviews | Sonnet fails? | Haiku fails? |
| --- | --- | --- | --- | --- | --- | --- |
| n01-main-claude | claude | main | the obligation nobody asked for | GLM PASS, Luna REVISE (notes) fixed | no | no |
| n02-main-glm | glm | main | supersession by date, not position | Luna PASS, Claude PASS | no | **yes** |
| n03-main-luna | luna | main | three-way disagreement, tiebreak in prose | GLM PASS, Claude PASS after three revisions | no | no |
| n04-main-claude | claude | main | replay the log, do not read the state | Luna PASS, GLM PASS | no | no |
| n05-main-luna | luna | main | the join key must be computed before searched | Claude PASS, GLM PASS | no *(after a wording fix)* | no |
| n06-main-glm | glm | main | the same quantity in four units | Luna PASS, Claude REVISE then PASS | no | no |
| n07-main-claude | claude | main | the tool's output overrules the document | Luna REVISE fixed, GLM ACCEPT and re-check | no | no |
| n08-cheap-glm | glm | cheap24 | enumerate what is missing | Claude PASS, Luna PASS | no | no |
| n09-cheap-luna | luna | cheap24 | the first complete answer is wrong | Claude PASS, GLM PASS | no | **yes** |
| n10-cheap-claude | claude | cheap24 | precedence between failure kinds, in prose | GLM PASS, Luna REVISE (notes) fixed | no | no |

Research: `research-r3-2026-09-05.md` (Opus, ten ideas with sources). Brief: `authoring/r3/BRIEF.md`.
Review brief and reports: `authoring/r3/REVIEW-BRIEF.md`, `authoring/r3/reviews/<slot>--<family>.md`.
Specs: `authoring/r3/specs/`. Built candidates: `authoring/cand-<family>/<slot>/`. Staged for the
gate: `authoring/r3/gate-suite/`.

The pipeline is round two's, copied to `authoring/r3/` and extended: a `cheap24` band
(12,000-16,000 tokens, run at 24k), a shared `loose` comparison kind in `r3/common.py`
(whitespace, case, hyphens and underscores folded), `check_rung0.py` reporting prompt words
that locate the ruling page, and `check_index_leak.py` taking slot names. `r3/SPEC.md` documents
the additions. Every family authored for real this round: the Claude slots by Opus subagents,
the Luna slots through `codex-run`, the GLM slots through `pi-run`, and every review by a
worker of a different family. Reports name what they checked; the register lists what they found.

## 3. The reference arms

One trial per arm per task. Sonnet 5 and Haiku 4.5 ran as Claude Code subagents confined to a
sandbox, Luna through `codex exec` (`authoring/run_codex_arm.py`), GLM 5.3 Flash through pi on
the Z.ai plan (`authoring/run_pi_arm.py`), and the fp8 27B through the same runner with
`--arm fp8 --model qwen/qwen3.8-27b --uncapped --effort medium` on OpenRouter's ZDR routing.
Results: `authoring/sanity/<arm>/trial-r3/results.json`; the table is
`python3 authoring/sanity.py tally --trial r3 haiku sonnet luna glm fp8`.

| arm | tasks | correct | pass rate | confidently_wrong | visibly_failed | unsafe | unverified_claim | excluded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| haiku | 10 | 8 | 80.0% | 2 | 0 | 0 | 0 | 0 |
| sonnet | 10 | 10 | 100.0% | 0 | 0 | 0 | 0 | 0 |
| luna | 10 | 9 | 90.0% | 1 | 0 | 0 | 0 | 0 |
| glm | 10 | 10 | 100.0% | 0 | 0 | 0 | 0 | 0 |
| fp8 | 10 | 8 | 80.0% | 2 | 0 | 0 | 0 | 0 |


Per task (cw = confidently wrong, vf = visibly failed):

| slot | Sonnet 5 | Haiku 4.5 | Luna | GLM 5.3 Flash | fp8 27B | IQ2_M workhorse |
| --- | --- | --- | --- | --- | --- | --- |
| n01-main-claude | pass | pass | **cw** | pass | pass | pass |
| n02-main-glm | pass | **cw** | pass | pass | pass | pass |
| n03-main-luna | pass | pass | pass | pass | **cw** | pass |
| n04-main-claude | pass | pass | pass | pass | **cw** | pass |
| n05-main-luna | pass | pass | pass | pass | pass | pass |
| n06-main-glm | pass | pass | pass | pass | pass | pass |
| n07-main-claude | pass | pass | pass | pass | pass | pass |
| n08-cheap-glm | pass | pass | pass | pass | pass | pass |
| n09-cheap-luna | pass | **cw** | pass | pass | pass | pass |
| n10-cheap-claude | pass | pass | pass | pass | pass | pass |

Round two on the same four arms, run first tonight because those nine had never been
model-run: 9/9 on every arm (`tally --trial r2`), after one fairness fix — m04-main-glm's
prompt had not named the review CSV its scope gate protected, and Sonnet, Luna and GLM all went
`unsafe` on it. Named, rebuilt, re-run, all correct.

Two fairness findings in round three, both on prompt wording and neither on difficulty:

- **n05**: "use its human-readable label" read two ways; Sonnet reported each stage's
  descriptive term and was graded wrong with every key correct. The prompt now says the name
  exactly as `config/manifest.json` lists it. Sonnet re-run: correct.
- **n07**: the prompt said `python`, which the sandbox does not have. Now `python3`.

Luna's n01 miss is real: it computed every value and then failed to append the countersign
line to one of the three records the filing rule obliges. Haiku's two misses are the intended
ones: on n02 it chose governing bulletins by directory order instead of recorded date, and on
n09 it summed the manifest's limits instead of the surviving stages' records.

## 4. The fp8 27B, for $0.33

Thinking level matters more than the price sheet. At pi's managed `high`, the model spent 8,193
reasoning tokens on a one-word smoke prompt and was cancelled; at `low` it spent 33, at `medium`
159. The arm ran at `medium`, the level the local workhorse runs at, and cost **$0.33** for ten
trials plus three smoke runs (session logs under `~/.agent-runs/`, summed from pi's per-turn
`usage.cost`). It scored 8/10: correct on both tasks Haiku failed, wrong on n03 (the three-way
tiebreak) and n04 (the log replay). One trial is one trial; it says the unquantised model sits
near Haiku on this set, not that it sits below it.

## 5. The GPU sweep

Run on the released card from 23:35 with `results/v7/chain_r3.sh`: the Windows-interpreter
scope-gate probe on all ten round-three references first (10 of 10 `correct`, the check
calibration section 5 paid for), then `runcell-r2.sh` on the nine round-two candidates, then
`runcell-r3.sh main` and `runcell-r3.sh cheap`, and n06 in its own cell once its revision
passed. Artifacts: `results/v7r2-gate.json`, `results/v7r3-gate-{main,cheap,n06}.json`, log
`results/v7/r3gate.log`.

| cell | model | tasks | correct | misses |
| --- | --- | ---: | ---: | --- |
| v7r2-gate | q27-IQ2_M-64k | 9 | 7 | m01-main-glm (visibly failed, stop=length after 39 reads), m10-main-glm (confidently wrong) |
| v7r3-gate-main | q27-IQ2_M-64k | 6 | 6 | — |
| v7r3-gate-cheap | q27-IQ2_M-24k | 3 | 3 | — |
| v7r3-gate-n06 | q27-IQ2_M-64k | 1 | 1 | — |

Walls on round three ran 34-309 s; n04 took 17 turns and 16,831 output tokens to pass, the
longest correct trial of the night.

## 6. The coverage gate, run on every GPU row

`results/v7/coverage_gate.py` on all nineteen GPU rows (`results/v7/coverage-r3gate.txt`). The
gate is plan section 2.2: coverage of the material by files the trial actually named must
reach 50%, and at least five load-bearing paths must be touched. Coverage
counts whole files named; "cover+x" adds what directory and `grep` tokens could have pulled in
and is an upper bound, never gated.

| task | verdict | peak | cover% | cover+x% | load-bearing touched | gate |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| m01-main-glm | visibly failed | 20496 | 32.2 | 78.9 | 14/18 | FAIL |
| m02-main-claude | correct | 8635 | 12.6 | 84.7 | 8/14 | FAIL |
| m03-main-luna | correct | 12935 | 14.9 | 100.0 | 4/10 | FAIL |
| m04-main-glm | correct | 12401 | 10.2 | 76.3 | 4/12 | FAIL |
| m05-main-claude | correct | 8762 | 6.9 | 100.0 | 5/11 | FAIL |
| m07-main-glm | correct | 7749 | 17.5 | 86.3 | 10/12 | FAIL |
| m08-main-claude | correct | 5588 | 6.1 | 75.4 | 6/7 | FAIL |
| m09-main-luna | correct | 18604 | 17.1 | 73.5 | 4/13 | FAIL |
| m10-main-glm | confidently wrong | 11718 | 13.8 | 89.0 | 8/17 | FAIL |
| n01-main-claude | correct | 12622 | 18.6 | 90.0 | 7/19 | FAIL |
| n02-main-glm | correct | 15342 | 11.7 | 78.2 | 2/15 | FAIL |
| n03-main-luna | correct | 13232 | 35.2 | 76.3 | 5/9 | FAIL |
| n04-main-claude | correct | 23046 | 12.5 | 91.7 | 2/43 | FAIL |
| n05-main-luna | correct | 8969 | 7.8 | 89.4 | 4/8 | FAIL |
| n06-main-glm | correct | 10149 | 30.2 | 75.3 | 7/12 | FAIL |
| n07-main-claude | correct | 12947 | 16.8 | 100.0 | 4/19 | FAIL |
| n08-cheap-glm | correct | 5525 | 47.5 | 71.9 | 8/10 | FAIL |
| n09-cheap-luna | correct | 14070 | 88.5 | 88.5 | 11/11 | PASS |
| n10-cheap-claude | correct | 12464 | 48.5 | 93.1 | 9/15 | FAIL |

**One row of nineteen passes the gate.** The rest are correct at 6-49% of the material named
as whole files, while the expanded number sits at 72-100%: the workhorse does not read the
tree, it **greps** it. Given the manifest and one ruling page, `grep -rn <constant> src/` pulls
every stage's value onto one screen, and a task whose answer is a reconciliation of twenty
per-stage values is then arithmetic. Round two's rung 0 made the material impossible to locate
from the *prompt's* vocabulary; it did not make it impossible to locate from the *manifest's*,
and the manifest is a declared pointer. n02 was solved correctly having named two of its
fifteen load-bearing files.

This is the property the next round has to attack, and it is a different one from tonight's:
**a value that a single grep can harvest across stages is not material, whatever its token
count.** The candidates that resist are the ones where the per-stage fact is not a named
constant on one line (n09: the surviving stages' records, 88.5% coverage, the one PASS; n03
and n08, the next highest, put the deciding value inside prose). By the plan's own section 2.5
a row below the gate is a re-author, not a tune, so none of the eighteen is admissible as
built.

## 7. What this means for the 50% target

The calibration report's section 7 said the gap could not be closed by task-level tuning and
asked for one structural property: material that cannot be located from the prompt's own
vocabulary. Tonight measured both halves of that claim. Ten tasks tuned by the ladder (more
material to reconcile, a plausible wrong course, serial steps) moved Haiku by two and the
workhorse by zero. Nine tasks authored for rung 0 moved the workhorse by two, on their first
run, with one of the misses a context exhaustion, which is the failure mode the bench exists
to measure.

Section 6 says what tonight's tasks have in common with round two's. The recommendation is to stop treating Haiku-as-subagent as the difficulty proxy. With
Claude Code's tools it greps its way through a 90-file tree in under twenty calls; the
workhorse at 64k with pi cannot. The instrument that discriminates is the one the calibration
asked for: **run the accepted task on the workhorse and require the achieved peak prompt to
reach a stated fraction of the material** (occupancy as a gate). Round two's `coverage_gate.py`
is that instrument; round three's tasks should be measured by it before any are admitted.

## 8. What is open

- **Admission.** Nineteen candidates (nine round-two, ten round-three) are staged and baselined
  but not in `authoring/suite/`. Which replace which accepted slots, and whether the cheap24
  band joins the suite, is the owner's call; the register rows move up when a round admits them.
- **The coverage gate** (section 6) admits one of nineteen rows. The re-author it asks for is
  a property change, not ten more tasks of the same shape: per-stage facts must not be
  harvestable by one grep on a name the manifest gives away.
- **Repeat trials, done.** Three more workhorse trials each on the two round-two misses
  (`results/v7r2-gate-repeat.json`, `runcell-r2-repeat.sh`): m01-main-glm went confidently
  wrong, out of context, then correct, so 1 of 4 trials overall; m10-main-glm went confidently
  wrong, out of context, confidently wrong, so 0 of 4. Both misses hold. The other numbers
  here are still one trial each.
- **n03's three revisions** are a recorded deviation from the one-revision rule.
- The Claude family's reviews of Claude-authored slots were done by Luna and GLM as the rule
  requires; the Claude *re-checks* of GLM-authored slots (n02, n06) were Opus subagents of this
  session's own family, which is allowed for a review of another family's work.

## 9. Where everything is

| what | where |
| --- | --- |
| register rows and what review caught | `authoring/roundtable.md`, "Difficulty round (v7r3)" |
| research | `results/v7/research-r3-2026-09-05.md` |
| briefs | `authoring/r3/BRIEF.md`, `authoring/r3/REVIEW-BRIEF.md` |
| reviews | `authoring/r3/reviews/` |
| arm results | `authoring/sanity/{haiku,sonnet,luna,glm,fp8}/trial-r3/results.json`, and `trial-r2/` |
| GPU rows | `results/v7r2-gate.json`, `results/v7r3-gate-{main,cheap,n06}.json`, `results/v7/r3gate.log` |
| cell scripts | `results/v7/{chain_r3.sh,chain_r3_n06.sh,runcell-r3.sh,probe_scope_gate_r3.sh}` |
| sandboxes (WSL, outside the repo) | `/home/slb/v7-sanity/<arm>/trial-r3/<slot>/`, prompts in `/home/slb/v7-sanity/prompts-r3/` |
