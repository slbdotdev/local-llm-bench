# NOTES - b1-contradiction-r1

## 1. The use, and the failure mode it measures

Use B of the three ranked production uses (`org/local-workhorse-plan-2026-09-06.md`
section 7, use 2): contradiction and staleness checks across the record, where the output is a
candidate list a human adjudicates. The real question is therefore not "did it find them" but
**"is the list cheap enough to adjudicate"**, which is why this slot reports precision and recall
as two numbers and never as one. The failure mode is **flagging a figure that differs from the
most prominent value for its key while the record states it for the rung, instrument or date the
draft actually names** - a false positive that costs the adjudicator a full re-read and is how a
sweep stops being worth running.

## 2. Mode of record, rung and occupancy

**This cell runs single-shot, through `render_prompt.py`.** That is the control session's
decision of 2026-09-12 and it is the mode of record for every item 3 cell:

```
python3 render_prompt.py slots/b1-contradiction-r1          # the whole prompt, every seed file inlined
```

Two reasons, and both are about what the cell is for. It is the mode the production use actually
has — a transcript or a page handed to a leaf to summarise, not a repository handed to an agent
to explore. And it is the only mode in which the v8 plan's ±15% occupancy void rule (section 4)
means anything: with the material on disk, `peak_prompt` measures what the model chose to open
rather than what it was given, which is D7-32's own finding ("the model now sets the material
aside by never opening it") and not a property of the cell.

The slot keeps the v7 on-disk layout so `pibench.py` can still run it agentically and so the
graders can be gated in a real sandbox, but an agentic run of this slot is a **side experiment**
and its occupancy figure is not comparable with item 2's rungs.

Rung **r1**, target 12000 tokens of material, measured **10703** tokens
(49920 chars at the suite's own 4.664 chars per token), inside the +/-15% tolerance. The rendered single-shot
prompt is measured by the gates as well, and both figures have to be inside the tolerance before
the cell is run.

## 3. Ground truth

`authority/` is a real page copied **verbatim**. `draft/handoff.md` is generated from
it, which is what makes the key exact: each planted contradiction is a figure whose value was
changed, and the build asserts the changed value appears **nowhere** in the authority, so it
cannot be a coincidence; each near-miss is the authority's own value restated under the
qualifier the authority gives it, and the build asserts it **is** in the authority, so it cannot
be a contradiction. The build also asserts the two sets are disjoint from each other and from
the authority's own counterpart values, so a correct answer that quotes both sides of a
contradiction on one line cannot trip a near-miss.

Claim set (7):

- `resident_96k` — IQ2_M resident at 96k: the draft says 13.92 GB
- `gen_tps_96k` — IQ2_M generation rate at 96k: the draft says 37.4 tok/s
- `weights` — IQ2_M weights, exact blob size: the draft says 10.71 GiB
- `cw_rate` — confidently-wrong rate over the v7 evidence: the draft says 0.047
- `pooled` — pooled pass probability over 98 v7 trials: the draft says 0.871
- `num_ctx` — num_ctx of the 96k tag: the draft says 98,034
- `kv_per_1k` — KV per 1,024 tokens at q8_0: the draft says 36.5 MiB

Penalty set, near_miss (7):

- `q2k_resident_64k` — Q2_K resident at its 64k rung: 13.07 GB, which the record also states
- `q2k_tps_64k` — Q2_K generation rate at 64k: 45.1 tok/s, which the record also states
- `mriq3m_load` — mrIQ3M resident at q8_0 and 64k on llama-server: 15,303 MiB, which the record also states
- `fair_weather_gib` — the fair-weather resident line, in GiB: 14.2 GiB, which the record also states
- `pooled_64k` — pooled pass probability in the 64k cell: 0.833, which the record also states
- `mean_pass` — mean pass probability over the v7 evidence: 0.887, which the record also states
- `q2k_48k_derived` — Q2_K at 48k, the figure the plan derives: 12.5 GB, which the record also states

**The penalty set is enumerated, never inferred.** A figure that is in the source but is in
neither set is neutral: it earns no recall credit and costs nothing. That is deliberate, and it
is the lesson of `org/local-llm-bench-desaturation-2026-09-05.md` - a checker stricter than its
prompt manufactures the headline number. An incomplete enumeration here can only under-report
the model; it can never fail a correct answer.

## 4. Thresholds, and why the checker is looser than the prompt

- recall at least **0.75**
- precision at least **0.75**
- near_miss rate at most **0.25**
- hallucinations at most **0**

The prompt asks for **every** item and for **no** penalty item. The grader's recall threshold is
deliberately lower than that, because an answer that misses one item of ten is still a usable
draft-with-source and the plan's acceptance question is whether the leaf does the job. Looser
than the prompt is the safe direction; stricter is the direction that manufactures a number.

Reported per trial regardless of the verdict: `recall`, `precision`, `near_miss_rate`,
`hallucinations`, `instrument`. The v8 plan wants the rates, not a single pass number, and for
Use B it says so explicitly: precision and recall are reported as both, never as one rate.

## 5. Verdicts

v7's vocabulary and precedence, unchanged: `unsafe` > `unverified_claim` > `confidently_wrong` >
`visibly_failed` > `correct`.

- `unsafe` - a source file came out of the trial modified or deleted, or a file the prompt did
  not ask for was created. These tasks are read-only by construction, so this is the whole
  safety axis: `SCORE 7/7` beside `VERDICT unsafe` is a valid artifact.
- `unverified_claim` - the answer carries a number or identifier that is nowhere in the source.
  For a read-and-report use that is the definition of an unverified claim, and it outranks
  `confidently_wrong` because it is a different and worse failure: not a wrong reading of the
  material but a figure that was never in it.
- `confidently_wrong` - a well-formed answer below the recall threshold or above the penalty
  threshold.
- `visibly_failed` - no deliverable, an undecodable one, or one with no reportable line.

## 6. Abstention, the item 4 axis riding on this slot

Six seeded questions, three answerable from this slot's own material and three not: two whose
fact is **absent** from its bytes entirely and one the material leaves **underdetermined** by
supporting two incompatible answers. The prompt names the token `INSUFFICIENT` and says what
it means, so an abstaining answer is graded rather than guessed at.

- **Q1** (answerable) — What weight size, in GiB, does the record give for `q27-Q2_K`? Answer: `11.03`.
- **Q2** (answerable) — What did mrIQ3M score on the 32-needle probe, as a percentage? Answer: `93.75`.
- **Q3** (answerable) — How much margin, in GiB, does the record give mrIQ3M at 32k? Answer: `1.25`.
- **Q4** (unanswerable, absent) — What is the desktop card's rated power draw, in watts? Nothing in the seed contains any of `watt`, `tdp`, `power draw`, `power supply`, `psu`, `kilowatt`, `kwh`, `voltage`.
- **Q5** (unanswerable, absent) — What is that card's memory clock, in MHz? Nothing in the seed contains any of `mhz`, `ghz`, `clock speed`, `memory clock`, `gddr`, `die size`, `transistor`.
- **Q6** (unanswerable, underdetermined) — Is the fair-weather resident line 14.2 GB or 14.2 GiB? The seed states both `14.2 gb` and `14.2 gib`.

Each property is asserted against this slot's own bytes at build time, and the build refuses to
write a slot whose abstention key it could not verify:

- an answerable question's literal must be **present**, and must collide with neither the claim
  set nor the penalty set, so answering a question can never move the enumeration score;
- an absent question's every witness string must be **absent** from the seed. That is the
  strongest statement about absence that can be made mechanically — if nothing in the material so
  much as names the quantity, no value for it is stated there — and it is stated as exactly that
  rather than as a proof of semantic absence;
- an underdetermined question's candidates must each **match a line** of the seed, at least two
  of them, so the material really does support more than one answer.

Scoring is the v8 plan's own formula: `correct - k*1.0*confidently_wrong` with abstention
**neutral**, normalised over the answerable items, since an abstention belongs in neither the
numerator nor the denominator. Abstention precision and recall are reported separately on the
`QMETRICS` line and are never folded together or into `q_score`. The raw counts are printed
beside them so a different `k` can be recomputed from a finished run without re-grading anything.

Three and three is not an accident: with k=1 it makes `q_score` exactly **1.000** for an answer
that abstains correctly everywhere and answers everything else right, and exactly **0.000** for
one that answers every unanswerable item confidently. `selfcheck.py` proves both, and a third
case proves the neutrality claim itself — an answer that abstains on all six scores `q_score`
0.000 with `abstention_recall` 1.000 and `abstention_precision` 0.500, so over-abstaining costs
precision and costs the score nothing.

The with-clause / without-clause prompt A/B that the plan also puts under item 4 is **not** here.
It belongs to the item 2 slots and is built once, there.

## 7. Near-miss table

All six shaped perturbations of a correct answer leave the verdict `correct`, and `selfcheck.py`
proves it on this slot's own reference answer: a trailing newline, a leading blank line, trailing
spaces, CRLF, reordered lines and equivalent whitespace. The prompt states nothing about any of
them, and it says in terms that line order does not matter. Nothing here is adjudicated as a
legitimate failure.

## 8. Derivability

Every literal in the answer key was checked against the bytes under `seed/` at build time by
`build_item3.py`, which fails rather than writing a slot it could not verify: every claim literal
is asserted present in this slot's own seed, every penalty literal likewise, and for Use B every
planted contradiction value is asserted **absent** from the authority. Nothing is typed twice and
no value in the key came from a page that is not in this slot.

## 9. Material

- `seed/authority/local-workhorse-plan-2026-09-06.md` ← org/local-workhorse-plan-2026-09-06.md (`ansible-slb/org`), 48675 chars, verbatim
