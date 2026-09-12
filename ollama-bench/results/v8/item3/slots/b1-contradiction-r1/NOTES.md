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

## 2. Rung and occupancy

Rung **r1**, target 12000 tokens of material, measured **10703** tokens
(49920 chars at the suite's own 4.664 chars per token), inside the +/-15% tolerance.

Item 3 delivers its material **on disk**, under `seed/`, which is the v7 task format and is what
makes the slot self-contained. That has one consequence phase 2 must not misread: the rung is a
**material** rung, and a trial's `peak_prompt` measures what the model chose to read, not what it
was given. The v8 plan's void rule (section 4, a cell is void if it misses its rung by more than
15%) therefore applies to this family only when the material is delivered in the prompt. Use
`render_prompt.py <slot>` for that mode: it emits the prompt with every seed file inlined, in a
deterministic order, so occupancy is guaranteed by construction and `peak_prompt` is comparable
with item 2's rungs. `batch_cell.py` and `escalate.py` both use it for exactly that reason.

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

## 6. Near-miss table

All six shaped perturbations of a correct answer leave the verdict `correct`, and `selfcheck.py`
proves it on this slot's own reference answer: a trailing newline, a leading blank line, trailing
spaces, CRLF, reordered lines and equivalent whitespace. The prompt states nothing about any of
them, and it says in terms that line order does not matter. Nothing here is adjudicated as a
legitimate failure.

## 7. Derivability

Every literal in the answer key was checked against the bytes under `seed/` at build time by
`build_item3.py`, which fails rather than writing a slot it could not verify: every claim literal
is asserted present in this slot's own seed, every penalty literal likewise, and for Use B every
planted contradiction value is asserted **absent** from the authority. Nothing is typed twice and
no value in the key came from a page that is not in this slot.

## 8. Material

- `seed/authority/local-workhorse-plan-2026-09-06.md` ← org/local-workhorse-plan-2026-09-06.md (`ansible-slb/org`), 48675 chars, verbatim
