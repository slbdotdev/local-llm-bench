# The large band, round 3: the suite finally discriminates

*2026-09-05, Opus manager session. Evidence: `authoring/round3/`, `authoring/tally_all.py`,
`authoring/bands-2026-09-05.json`, `results/bend-small-24k.json`, `results/bend-large-64k.json`.*

## The question this answers

Plan section 2.1 sets the target: **Haiku near 80%, Sonnet at or above 90%.** Round 2, on the
suite as it existed, gave **Haiku 21/24 = 87.5%** and **Sonnet 24/24 = 100%**. Sonnet was fine;
Haiku was too high, the candidate space was exhausted, and the handoff's open question — author
harder variants, or accept saturation — had already been answered by the owner: *sharpen*.

Section 3 supplied the lever. Synthetic context fill was withdrawn in favour of material a task
genuinely requires, and re-banding measured what the suite actually held.

## What re-banding found, and why it made authoring the critical path

Every candidate's `seed/` was counted at the measured 4.664 chars per token
(`authoring/measure_material.py`). Across all 31 pre-existing candidates the range was **149 to
7,637 tokens**. Only `t03/cand-1..3` reached even the bottom of the small band. **The medium and
large bands were empty**, and what `schedule.md` had been calling "small" was tiny.

That is the finding that reorganised the night: the campaign could not measure context behaviour
because it had no context to measure. Eight new `cand-5` tasks were authored against
`authoring/CONTRACT-2026-09-05.md`, one per family, each posing the *same kind of question* over
real material:

| task | seed files | material chars | material tokens | band |
| --- | ---: | ---: | ---: | --- |
| g01/cand-5 | — | — | — | large |
| g02/cand-5 | — | — | — | large |
| g03/cand-5 | 177 | 140,004 | 30,018 | large |
| g04/cand-5 | 28 | 198,546 | 42,570 | large |
| t01/cand-5 | 26 | 170,904 | 36,643 | large |
| t02/cand-5 | 37 | 145,058 | 31,102 | large |
| t03/cand-5 | 37 | 142,739 | 30,604 | large |
| t04/cand-5 | 50 | 191,868 | 41,138 | large |

Holding the **family** fixed across the two bands is deliberate: it measures context *within* a
task and removes the confound section 3.4 concedes when different tasks stand in for different
bands.

## The result

Reference arms, three Haiku trials and two Sonnet trials over all eight large-band tasks:

| task | Haiku (3 trials) | Sonnet (2 trials) |
| --- | --- | --- |
| g01 | 3/3 | 2/2 |
| g02 | 3/3 | 2/2 |
| g03 | **1/3**, 2 confidently_wrong | 2/2 |
| g04 | **0/3**, 3 confidently_wrong | 2/2 |
| t01 | **1/3**, 2 confidently_wrong | 2/2 |
| t02 | 3/3 | 2/2 |
| t03 | 3/3 | 2/2 |
| t04 | 3/3 | 2/2 |
| **total** | **17/24 = 70.8%**, confidently-wrong rate **29.2%** | **16/16 = 100%**, confidently-wrong rate **0%** |

And the two bands side by side, which is the number the campaign was after:

| band | window | Haiku | Sonnet | Haiku confidently-wrong |
| --- | --- | --- | --- | --- |
| tiny (round 2, `cand-1..4`, 149-770 tok of material; t03 6,235) | 24k | 21/24 = 87.5% | 24/24 = 100% | 12.5% |
| large (round 3, `cand-5`, 30,018-42,570 tok) | 64k | 17/24 = 70.8% | 16/16 = 100% | 29.2% |
| **both bands** | — | **38/48 = 79.2%** | **40/40 = 100%** | **20.8%** |

**The target is met.** Section 2.1 asked for Haiku near 80% with Sonnet at or above 90%: the suite
taken whole gives Haiku **79.2%** and Sonnet **100%**.

The guard holds at its ceiling and the discrimination arm has come down off the ceiling. Read per
band, with the count behind each number as section 6 requires, the suite now has one band where
Haiku is saturated and one where it is not — which is exactly the instrument the campaign wanted,
and it is a *better* instrument than a single band tuned to 80% would have been, because the gap
between the two bands is itself the measurement.

## The three tasks that discriminate, and why each is fair

Every Haiku failure was read, not counted.

- **g04** (0/3). Failing checks are `['totals', 'groups', 'report_format']`: the current policy
  memo requires each row to be rounded to two places before summing into account and tax-code
  groups, and Haiku sums unrounded and rounds the totals. The prompt names the policy memo as
  authoritative "including ... how fees and currency conversion are calculated". Sonnet reads the
  identical prompt and gets it 2/2.
- **t01** (1/3). One misclassification out of 55 records, both times on a line whose own sentence
  says so in as many words — *"It describes past state and must remain unchanged"* and *"It is
  historical evidence, not a live pointer."* Not ambiguity; a missed sentence.
- **g03** (1/3). A 177-file rename where the old identifier must not survive anywhere in the
  application source, including reflected strings and doctests.

None of these is a trick, none turns on an unstated convention, and none was chosen because a
model failed it — section 4a holds.

## The defect this round found, and it was in the instrument

`t04/cand-5` scored a **correct** answer `confidently_wrong` on an exact span equality,
`_ora_parsed[1] == (6, 20)`, when the prompt itself invites citing `8-20`. Three Haiku rows and
none of Sonnet's differed *only* in that boundary. Fixed, re-probed, and **every** t04 row
re-graded for both arms; three `confidently_wrong` labels were withdrawn as instrument artifacts.
Full reasoning in `decisions.md`, D-R3-5, and the class in
`findings-2026-09-05-checker-format-bias.md`.

The pattern across this session is worth stating once on its own: **four of the five faults found
today were found by reading a tool's own report of what it could not do, or by reading a single
failing row, and not one of them by looking at a rate.** A rate cannot tell you that the thing
producing it is wrong.

## The local quants, tiny band, 24k, one trial per task

`results/bend-small-24k.json`. All four ran at **100% GPU** with the resident size and generation
throughput on the known curve — verified by real load, not by a version string, as
`ollama-cuda-repair-2026-09-04.md` requires.

| tag | resident | %GPU | gen tok/s | pass | confidently wrong | failed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| q27-Q2_K_L-24k | 11.83 GB | 100 | 58.5 | 7/8 | 1 | t04 |
| q27-Q3_K_S-24k | 13.18 GB | 100 | 52.2 | 7/8 | 1 | g03 |
| q27-Q3_K_M-24k | 14.00 GB | 100 | 50.7 | 6/8 | 2 | g03, g04 |
| q27-IQ3_M-24k | 13.35 GB | 100 | 52.4 | 6/8 | 2 | g03, g04 |

Two things to say about this table and no more, because it is a baseline and not a result:

1. **The band is tiny** — seven of the eight tasks carry under 800 tokens of material — so a 24k
   window is not a constraint and this measures the model, not the context. `decisions.md`, D-R3-8.
2. **Q2_K_L, the 2-bit line, is not last.** It ties the best pass rate at 7/8, carries the lowest
   confidently-wrong count, is the smallest resident at 11.83 GB and the fastest at 58.5 tok/s.
   Plan section 6 says to report the 2-bit line whatever the ranking says; here the ranking says
   it is fine, and the ordering by pass rate is the reverse of the ordering by bits.

The 64k large-band pass over the same eight families is `results/bend-large-64k.json`.

### One thing in that table deserves its own line

**Zero `visibly_failed` verdicts in thirty-two 24k trials.** Every single failure across all four
quants was `confidently_wrong` — a wrong answer delivered as a finished one, with no timeout, no
length stop, and no refusal (`0 in 0/8` length stops on every quant). The confidently-wrong rate
and the failure rate are therefore **the same number** on this band: 12.5% for Q2_K_L and Q3_K_S,
25.0% for Q3_K_M and IQ3_M.

Plan section 6 makes the confidently-wrong rate a verdict line of its own that outranks pass rate,
on the reasoning that a model which fails loudly is usable and one which fails quietly is not.
This band says the distinction does not exist for these quants on these tasks: they do not fail
loudly at all. That is the most useful sentence the 24k pass produced, and it is an argument for
the instrument rather than a result about any one quant.

## The local quants at 64k, and the bend is a wall-clock bend

`results/bend-large-64k.json` and `results/bend-large-48k-q3km.json`. One trial per cell, no fill,
`num_ctx` 65536 (48k for Q3_K_M), q8_0 KV, every trial 100% GPU.

| cell | resident | tasks run | pass | confidently wrong | wall range | turns |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| q27-Q2_K_L-64k | 13.35 GB | 8/8 | 7/8 | 1 (g03) | 35.4 - 493.5 s | 7-31 |
| q27-Q3_K_S-64k | 14.70 GB | 3/8 | 3/3 checker, **1/3 on the 900 s wall** | 0 | 498.4 - 1779.7 s | 7-38 |
| q27-IQ3_M-64k | 15.11 GB | 1/8 | 1/1 | 0 | 216.3 s | 8 |
| q27-Q3_K_M-48k | 14.91 GB | 3/3 (the three that fit) | 1/3 | 1 (g03, at the wall) | 475.3 - 900.1 s | 6-11 |

**No trial collapsed to a single turn.** The lowest turn count anywhere in the band is 6 and the
highest is 38, so by plan section 3.3 these are quality results and not capacity results — the
1.6x working-margin rule did its job and the agentic loop had room to work in.

### The finding

The same task, `t03`, 30,604 tokens of material, on four cells:

| cell | resident | wall | slowdown |
| --- | ---: | ---: | ---: |
| q27-Q2_K_L-64k | 13.35 GB | 35.4 s | 1x |
| q27-IQ3_M-64k | 15.11 GB | 216.3 s | 6.1x |
| q27-Q3_K_S-64k | 14.70 GB | 498.4 s | 14.1x |
| q27-Q3_K_M-48k | 14.91 GB | 880.6 s | 24.9x |

Every one of those is 100% GPU with all 66 layers offloaded. The bend on this card is **not a
quality bend and not an offload bend — it is a headroom bend.** Below about 13.5 GB resident the
large band runs at conversational speed; above about 14.7 GB the same work on the same card takes
six to twenty-five times as long, and plan section 6's 900-second verdict wall starts eating rows
whose checkers passed. `Q3_K_S-64k` answered g01 and g02 **correctly**, at 1,456.9 s and 1,779.7 s.
Correct and unusable is a different verdict from wrong, and reporting it as a pass rate would have
lost it entirely.

### What that makes the 2-bit line

Plan section 6 says to report the 2-bit line whatever the ranking says. Here the ranking says
`Q2_K_L` **wins the large band outright** and it is not close:

- the only cell that ran all eight tasks;
- the best pass rate, 7/8;
- every trial inside the 900 s wall, worst 493.5 s;
- the lowest resident size, 13.35 GB, which is the only reason for all of the above.

The ordering by pass rate and by wall time is the **reverse** of the ordering by bits, at both
24k and 64k. On a 16 GB card at 64k with q8_0 KV, the quantisation that leaves headroom beats the
quantisation that spends it on precision, and it is not a marginal call.

### What is not measured, and it is not a small gap

`Q3_K_S` ran three of eight tasks and `IQ3_M` one of eight. The large band therefore has **one
complete quant row**, not three. The pass was stopped deliberately rather than lost — the reasoning
is in `decisions.md` D-R3-11 — but the honest statement is that the 64k quality comparison between
the three quants **has not been made**, and only the wall-clock comparison has. Queue item 1 in
`schedule.md` is what finishes it; the artifact resumes rather than repeats.
