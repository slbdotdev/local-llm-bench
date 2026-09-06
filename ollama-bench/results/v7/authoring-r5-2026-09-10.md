# v7 round five — admit what discriminates, and report a statistic with variance in it, 2026-09-10

*Written by the round-five manager, an Opus subagent of the Fable control session. Read after
`authoring-r4-2026-09-09.md` and `handoff-2026-09-09.md`. Decisions and their reasons:
`decisions-r5-2026-09-10.md`. Plan of record: `plan-2026-09-07.md`, section 2.1 amended today.
Campaign dates continue the convention; the host clock reads 2026-09-06.*

## 1. The owner's ruling, and what this round did with it

The material lever was exhausted at 96%. The ruling opened five lines in priority order: admit
what already discriminates, report a statistic with variance in it, measure context pressure,
and author new tasks on two shapes. `decisions-r5-2026-09-10.md` records it verbatim as its first
entry, committed before anything else.

**The headline is the second item, not the first.** The suite statistic is now pass probability
with a Wilson 95% interval over at least three trials, with the confidently-wrong rate beside it,
and `results/v7/tally_trials.py` computes it. Three admissions moved that number. The authoring
half of the round produced no admission at all, and the reason it did not is the round's most
useful finding.

## 2. The statistic, before and after

`python3 results/v7/tally_trials.py`. Twenty tasks, every counted workhorse trial, coverage and
peak input beside every row as diagnostics that gate nothing.

| | tasks | trials | passes | **mean pass probability** | pooled, Wilson 95% | **confidently-wrong rate**, Wilson 95% | vf | unsafe |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: |
| **before** | 20 | 101 | 97 | **0.962** | 0.960 [0.903, 0.984] | **0.000** [0.000, 0.037] | 2 | 2 |
| **after** | 20 | 98 | 88 | **0.887** | 0.898 [0.822, 0.944] | **0.031** [0.010, 0.086] | 5 | 2 |

The old headline, 96/100 at five trials, is the "before" row's pooled rate. The new number is the
mean of the twenty per-task probabilities, because a task measured nine times is not worth three
tasks measured three times.

**What the interval buys, and it is the point of the exercise.** A row at 5 of 5 reads
`1.000 [0.566, 1.000]`: five trials cannot tell a perfect task from a 60% one, and the old `k/n`
said they could. The suite's own interval, [0.822, 0.944], is what a next round has to move
outside of before it can claim to have moved anything. And the confidently-wrong rate is no longer
structurally zero: three of the ninety-eight trials are now wrong answers delivered with
confidence, which is the failure this benchmark exists to find.

### After, per task

| task | trials | passes | p | Wilson 95% | cw | vf | unsafe | cover% | cov+x% | peak |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m01-cheap-luna | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 44.7 | 84.9 | 6279 |
| m02-cheap-glm | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 13.3 | 15.8 | 4238 |
| m03-cheap-claude | 5 | 4 | 0.800 | [0.376, 0.964] | 0 | 0 | 1 | 16.5 | 50.0 | 5036 |
| m03-main-glm | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 2.7 | 29.5 | 4337 |
| m04-cheap-luna | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 29.3 | 96.4 | 4861 |
| m04-main-claude | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 18.0 | 89.3 | 11503 |
| m05-cheap-glm | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 40.6 | 66.1 | 10173 |
| m06-cheap-claude | 5 | 4 | 0.800 | [0.376, 0.964] | 0 | 0 | 1 | 12.3 | 62.3 | 3727 |
| m06-main-glm | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 9.6 | 78.0 | 9123 |
| m07-cheap-luna | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 35.8 | 95.1 | 5449 |
| m07-main-claude | 5 | 4 | 0.800 | [0.376, 0.964] | 0 | 1 | 0 | 10.1 | 80.0 | 10941 |
| m08-cheap-glm | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 22.4 | 37.8 | 5038 |
| m08-main-luna | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 1.9 | 43.4 | 4341 |
| m09-cheap-claude | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 100.0 | 100.0 | 9860 |
| m10-cheap-luna | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 0.5 | 20.9 | 3637 |
| m10-main-claude | 5 | 5 | 1.000 | [0.566, 1.000] | 0 | 0 | 0 | 6.3 | 56.1 | 9945 |
| **n02-main-glm** | 4 | 2 | **0.500** | [0.150, 0.850] | 2 | 0 | 0 | 12.4 | 83.7 | 15798 |
| **n05-main-luna** | 4 | 3 | **0.750** | [0.301, 0.954] | 1 | 0 | 0 | 5.3 | 86.8 | 7204 |
| p02-main-claude | 6 | 5 | 0.833 | [0.436, 0.970] | 0 | 1 | 0 | 21.3 | 91.5 | 14256 |
| **p05-main-claude** | 4 | 1 | **0.250** | [0.046, 0.699] | 0 | 3 | 0 | 24.4 | 98.0 | 24318 |

Sixteen of twenty rows are still at 1.000 or 0.800 with an interval that reaches 1.000. The three
admitted rows are the only ones that separate anything, and `p05-main-claude` at 0.250 is the
hardest task the campaign has ever admitted.

### Which trials count, and which do not

`tally_trials.py` reads every workhorse results JSON under `results/` and keeps the tags that were
run against the *current build* of each task. `v7cal-*` and `v7cal2-*` (round two's calibration,
one and three trials against an earlier suite) are excluded by default, because every task they
cover already has five or more trials from `v7r4cal-*` and mixing them would silently mingle two
builds; `v7r4-early-*` is excluded because it ran against candidates later revised; and `v7r5-48k`
is held separate by construction and never merged. The exclusion list is in the file with a reason
per entry, printed by `--list-tags` and reversible with `--tag`. **No fill trials were needed:**
every admitted row already carried four or more.

The three admitted tasks' suite copies were verified byte-identical (seed, `prompt.md`, `test.py`)
to the builds their trials ran against, so folding those trials in is legitimate rather than
assumed.

## 3. The admission pass

`decisions-r5-2026-09-10.md` has the full table and the reasoning. Three slots changed:

| mode / band | out | out p | in | in p | why |
| --- | --- | ---: | --- | ---: | --- |
| 1, main | `m01-main-claude` | 1.000 (5/5) | **`n02-main-glm`** | 0.500 (2/4) | the most discriminating candidate with two genuine PASSes for the slot, and the only move that frees a claude slot |
| 5, main | `m05-main-luna` | 1.000 (5/5) | **`p05-main-claude`** | 0.250 (1/4) | two cross-family PASSes with `fix: none` since round four, parked then only by the cap; the strongest measured discrimination in the staged set |
| 9, main | `m09-main-glm` | 1.000 (5/5) | **`n05-main-luna`** | 0.750 (3/4) | two PASSes, and the only candidate for the slot |

Family share **claude 8 (40%), glm 6 (30%), luna 6 (30%)**, claude exactly on the cap; the two
slots of every mode still in different families. `assemble_suite.py` wrote the suite,
`stamp_manifests.py suite/*` restamped all sixteen manifests that needed it (handoff pickup 4),
and `probe_scope_gate_suite.sh` graded **all twenty references `correct`** under the Windows
interpreter.

### Two findings that shrank the pass from eight rows to three

1. **The brief's premise did not hold.** It said the nineteen staged candidates "hold two
   cross-family reviews". `authoring-2026-09-06.md` section 8.2 records that round two's nine got
   **one** round of review, by clean-context agents rather than by the other two families, and
   section 8.1 records that their family labels are "the plan's slot assignments and not a claim
   about which model wrote the prose" — all nine were drafted by clean-context Sonnet subagents.
   `plan-2026-09-07.md` section 3.1 requires two blind cross-family reviews, both passing. So the
   nine were one review short and their family labels, which is what the 40% cap is computed from,
   are nominal. **This is the round's one open question for the owner.**
2. **Round three's slot numbers are its ten ideas, not the ten failure modes.** Read from each
   candidate's own `MANIFEST.json`, `n01`, `n02`, `n04`, `n06` and `n10` are all mode 1 and
   compete for one slot between them. A candidate replaces the incumbent of the same mode *and*
   band, so nineteen candidates contest eleven distinct slots, not nineteen.

The two most discriminating candidates in the campaign, `m10-main-glm` (**0 of 4**) and
`m01-main-glm` (**1 of 4**), were sent to the blind Luna cross-family review their admission
needed. **Both came back REVISE**, before their second review was even run. `m10`'s is a rung-0
failure — a two-file shortcut at 6/8 — plus a `NOTES.md` claim of 61.0% traversal that measures
22.9%, and its reviewer judges both tiers saturated. `m01`'s is one narrow defect: the required
output key `authority` is a one-file locator, while its best shortcut needed **18 files at 7/7**
and its reviewer judges the workhorse failure **real**. Both are parked with one revision owed;
`m01` is the cheapest discrimination available and is pickup 1 of the handoff.

## 4. The four new candidates, on the two shapes

Four authored blind under `authoring/r5/BRIEF.md`, two shapes, families forced by the provenance
rule and the cap. **None was admitted.**

| slot | family | band | mode | shape | Sonnet | Haiku | Luna | GLM | workhorse | reviews | fate |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| `q08-main-luna` | luna | main | 8 | A, long serial state | correct | correct | correct | — | not run | claude REVISE → revised → **REVISE** | **dropped** |
| `q06-main-luna` | luna | main | 6 | B, large correct output | cw 37/40 | cw 37/40 | cw 38/40 | — | 2/3 pre-revision | claude REVISE → revised → **REVISE** | **dropped** |
| `q09-main-glm` | glm | main | 9 | A, long serial state | **correct** 12/12 | **correct** 12/12 | **correct** 12/12 | **correct** 12/12 | **1/3, two `confidently_wrong`** | claude+luna **REVISE** → revised → claude+luna **REVISE** | **dropped** |
| `q08-cheap-glm` | glm | cheap24 | 8 | B, large correct output | — | — | — | — | — | — | **withdrawn**, unauthored (Z.ai lane) |

Arms before `q06`'s revision were three of three `correct` (Sonnet, Haiku, Luna); the three re-run
after it are the three `confidently_wrong` rows above, every one of them having satisfied the
specification the prompt names. `q08-main-luna`'s three arms all answered its pre-revision build
`correct`. The GLM arm ran on `q09-main-glm` only — the single Z.ai lane spent the rest of the
round on authoring and revision, and its two failed authoring runs are why.

**Both candidates that reached a second review were dropped for the same reason, and it is the
round's finding: the shape was asserted in the prompt and not enforced by the material.**
`q08`'s twenty-two-step chain could be read off one grep, at full score with zero files opened,
because the live route row was identifiable without the previous step — first by row position and
a name prefix, and after the revision by a new `qNN0M` tag class that isolated it at 22 of 22.
`q06`'s thirty-two-file deliverable could be written from one file, because each unit's answer was
printed inside that unit, and its 32 files stayed one subcheck so a truncated deliverable scored
the same as doing nothing. Every mechanical check passed on both, both times. A blind reader found
it, four times out of four. That is the third round running in which every instrument defect was
found by a reader and none by a probe.

**`q09-main-glm` is the round's best material and it was dropped too.** All four reference arms
answered it `correct` at 12/12 and the workhorse scored **1 of 3 with the other two
`confidently_wrong`** — four arms right and the 2-bit model confidently wrong twice is exactly the
discrimination the suite lacks, and it is the first candidate this campaign has built that shows
it. Both reviewers called it **fair** and **hard to do**, and one solved it from the prompt alone
and matched `ref/` exactly. Both nonetheless returned REVISE on a two-file shortcut at 12/12; one
revision was granted as a **recorded deviation**, as rounds three and four each did once. The
revision closed both attacks it was sent back for — 0 of 2,000 shuffles reach the graded figure,
0 of 8 keys from an identifier-sorted replay — and opened two more of the same class: two
**byte-identical frames at two fixed line numbers** (every balance the last line of its page,
every take-back the last line of its module) so `tail -n1 docs/*.md src/kestrel/*.py` harvests 38
of 40 with no token at all; and a second `rebase` that **cut the chain instead of lengthening it**,
because a rebase *sets*, leaving `figure_final` dependent on 19 of 40 entries and each key an
order-free sum after the nearest rebase. Two misses is a drop.
`decisions-r5-2026-09-10.md` has the measurements and the three-item fix list. **Do not throw the
spec away**: it is pickup 1 of the handoff.

### The pipeline, and the two pickups it closed

`authoring/r5/` is round four's, copied and amended. Two of the handoff's five pickups are closed
in it:

* **Pickup 2 — `r5/check_tools.py`, new.** It copies `seed/` to scratch, runs every `*.py` and
  `*.sh` under it with **no arguments**, and fails the candidate if any prints a value the grader
  compares, or the decisive datum of more than a quarter of the declared units. It reproduces the
  defect that dropped `p09-main-luna` — `tools/retention_audit.py`, four scored values and **57 of
  57 units** in 12,294 bytes from one bare invocation — and clears `p02-main-claude` and
  `p04-main-glm`. It ran clean on all three round-five candidates.
* **Pickup 3 — `vacuous` rather than `0.000`.** `check_harvest.py` now prints
  `H1=vacuous H2=vacuous H3=vacuous H4=vacuous` when every declared unit is derived, with a note
  saying the claim is the declaration's own and a reviewer must verify it by hand. **It paid for
  itself the same day.** `q09-main-glm` read vacuous on all four measures; its reviewer, told
  explicitly that verifying it was theirs, found that `harvest_units()` declared the post-entry
  *running figure* — which cannot occur under `seed/` by construction — while the decisive datum
  is the figure each entry *applies*, and that declaring it honestly would read H1 at or near
  1.000. That is the same wrong-quantity error the checker missed twice on `q08-main-luna`, caught
  this time because the word `vacuous` told a reader where to look.

## 5. The context-pressure cell, `v7r5-48k`

Ten main-band tasks, three trials each on `q27-IQ2_M-48k` at `--num-ctx 49152`, reported beside
the 64k number and never merged into it. It admits nothing.

| | tasks | trials | passes | mean p | pooled, Wilson 95% | cw | `stop=length` |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 64k, same ten tasks | 10 | 48 | 40 | 0.813 | 0.833 [0.704, 0.913] | 3 | 0 |
| **48k** | 10 | 30 | 27 | **0.900** | 0.900 [0.744, 0.965] | **0** | 3 in 2 runs |

**Occupancy does not move the pass rate measurably, and what movement there is runs the wrong way
for the hypothesis.** The intervals overlap over almost their whole length. `n02-main-glm` went
2/4 to 3/3 and `n05-main-luna` 3/4 to 3/3, taking both confidently-wrong verdicts with them;
`p05-main-claude` stayed hard at both windows. The failure *shape* did change: all three 48k
misses are `visibly_failed` and two carry `STOP=length`, against zero length stops in 48 trials at
64k. A narrower window converts a wrong answer into a truncated one.

## 6. The 64k KV-cache rerun

Run last, on the owner's instruction, to the method in `results/v5/kv-probe-plan-2026-09-03.md`.
Full record and the org recommendation: **`results/v5/kv-64k-2026-09-10.md`**. In one line: **q8_0
KV is not measurably better than q4_0 at 64k** — 120/128 against 118/128 on the one model where
both cells completed, intervals overlapping — while on the other model q8_0 loaded to 15,315 MiB
of a 16,303 MiB card and answered 1 of 32 needles before the 600 s cap, which is the plan's
predicted spill. The recommendation is a single global `OLLAMA_KV_CACHE_TYPE=q4_0`.

## 7. Plans and the GPU

* **GPU:** RTX 5080, one cell at a time throughout. The workhorse cells and the 48k cell ran
  through Ollama; the four KV cells ran on the vendored `llama-server.exe` directly with Ollama
  stopped and the drain verified, and Ollama was restored afterwards.
* **ChatGPT plan (Codex/Luna):** about eleven runs — two authoring, two round-two reviews, two
  revisions, one candidate review, and the reference-arm runs. No run reported `quota_exhausted`
  and none was rate-limited. Per-run plan percentages are not reported by the wrapper and are not
  claimed here.
* **Z.ai GLM Coding Plan:** three runs, and it was the round's binding constraint. Two of the
  three hit repeated upstream `Request timed out` provider errors after the resilience extension
  truncated their large tool outputs; the first died on them outright having written nothing, the
  second wrote its spec and seed but never completed `overlay()`. **Not `quota_exhausted`** — an
  upstream failure, not an exhausted plan. It cost the round one candidate (`q08-cheap-glm`,
  withdrawn) and every GLM cross-review and the GLM reference arm.
* **Claude plan:** about eleven subagents — five blind reviews, six reference-arm trials, and the
  KV harness rebuild.
* **OpenRouter: no spend of any kind.** The fp8 arm was not run.
