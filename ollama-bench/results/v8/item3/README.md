# v8 items 3, 5 and 6 — the instruments

*Built in phase 0 by a worker session under the Claude Code control session, 2026-09-11/12. No GPU
time was spent, no model was called, no hosted token was bought, and the Ollama endpoint was never
opened. Everything here has been gated offline; the record is `GATES.md`, and `GATES.json` beside
it is the machine-readable version.*

| item | what | files |
| --- | --- | --- |
| **3** | seeded read-and-report, three production uses at two occupancy rungs each | `slots/`, `grade_seeded.py`, `build_item3.py`, `render_prompt.py` |
| **4** | abstention, seeded into the six item 3 slots | the `questions` block of every slot's key, scored in `grade_seeded.py` |
| **5** | deadline and throughput | `derive_deadline.py`, `batch_cell.py` |
| **6** | escalation economics | `escalate.py` |
| — | the gate record, and the narrow portable check | `gates.py`, `GATES.md`, `GATES.json`, `refprobe.py` |

Items 4, 5 and 6 live here because they are built on item 3's slots and its grader, not because
they are part of item 3.

## The six slots

    slots/a1-summarise-r1        use A, report summarisation       rung r1   11,926 tokens
    slots/a2-summarise-r2        use A                             rung r2   40,728 tokens
    slots/b1-contradiction-r1    use B, contradiction hunt         rung r1   10,703 tokens
    slots/b2-contradiction-r2    use B                             rung r2   40,258 tokens
    slots/c1-changelog-r1        use C, changelog from a git range  rung r1  12,280 tokens
    slots/c2-changelog-r2        use C                             rung r2   42,525 tokens

The three uses are the three ranked production uses of
`org/local-workhorse-plan-2026-09-06.md` section 7, in its own order. Rungs are **r1 = 12,000**
and **r2 = 40,000** tokens of material, measured at the suite's own 4.664 chars per token, with the
v8 plan's own ±15% tolerance. Rungs are separate cells and are never pooled.

Each slot is the v7 task layout — `prompt.md`, `seed/`, `ref/`, `test.py`, `selfcheck.py`,
`NOTES.md`, `MANIFEST.json` — and each slot's `NOTES.md` carries its own answer key, thresholds,
abstention key and near-miss table.

## Mode of record: single-shot, through `render_prompt.py`

**Item 3 cells run single-shot.** Control session decision, 2026-09-12. Phase 2 starts here:

```bash
python3 render_prompt.py slots/a1-summarise-r1            # the whole prompt, material inlined
python3 render_prompt.py slots/a1-summarise-r1 --measure  # its size only
```

It is the mode the production use actually has — a transcript or a page handed to a leaf to
summarise, not a repository handed to an agent to explore — and it is the only mode in which the
plan's ±15% occupancy void rule means anything, since `peak_prompt` in agentic mode measures what
the model chose to open rather than what it was given (D7-32).

The slots keep the v7 on-disk layout anyway, for two narrower purposes: `pibench.py` can still run
them agentically as a **side experiment**, whose occupancy figure is not comparable with anything
here, and the graders can be gated in a real sandbox with a real integrity check, which is where
the `unsafe` verdict comes from.

```bash
# the side experiment, from ollama-bench/; note --tasks-dir, not --tasks
python3 pibench.py --tasks-dir results/v8/item3/slots --model q27-IQ2_M-96k --trials 10 ...
```

## What each trial reports

Two metric lines, both near the end of the grader's output because `pibench` keeps only its last
600 characters:

```
METRICS  recall=… precision=… <penalty>_rate=… hallucinations=… instrument=…
QMETRICS q_score=… abstention_recall=… abstention_precision=… overanswer_rate=…
         abstention_instrument=… q_correct=… q_confidently_wrong=… q_abstained=… q_missing=… k=…
```

`SCORE 9/9` and one `VERDICT` from v7's five-word vocabulary. The headline is the rates, never a
single pass number, and for use B it is precision **and** recall.

## The abstention axis (item 4)

Every slot carries six seeded questions: three answerable from its own material, two whose fact is
**absent** from its bytes entirely, and one the material leaves **underdetermined** by supporting
two incompatible answers. The prompt names the token `INSUFFICIENT` and says what it means.

Scoring is `correct - k*confidently_wrong` with abstention **neutral** and `k` defaulting to 1,
normalised over the answerable items; abstention precision and recall are reported separately and
never folded together. Three answerable and three unanswerable is deliberate: with k=1 it makes
`q_score` exactly 1.000 for an answer that abstains correctly everywhere and exactly 0.000 for one
that answers every unanswerable item confidently, which is the two-directional proof on this axis.

Every property is asserted against the slot's own seed bytes at build time. An absent item's
witness strings must appear nowhere in the seed; an underdetermined item's candidates must each
match a line of it. The build refuses to write a slot whose abstention key it could not verify.

The with-clause / without-clause prompt A/B that the plan also puts under item 4 is **not** here:
it belongs to the item 2 slots and is built once, there.

## Running the checks

There are two, and the difference matters.

**`refprobe.py` — the portable one. Run this on the machine that runs the cells.**

```bash
python3 refprobe.py                      # every slot's reference answer, through its own grader
python3 refprobe.py --json refprobe.json
```

It grades each slot's reference answer through that slot's own `test.py` on the local interpreter,
rebuilds nothing, imports nothing from its siblings, reads nothing outside this repository, and
needs only the standard library. It is safe where `/home/slb` does not exist. This is the whole of
v7's D7-31 rule — verify the grader on the interpreter that runs it — and it is all D7-31 asks for.

**`gates.py` — the authoring suite. WSL side only.**

```bash
python3 gates.py            # grade the slots as they are; rewrite GATES.md and GATES.json
python3 gates.py --rebuild  # regenerate the slots from their sources first
python3 gates.py --no-write # run everything and print; write nothing
```

It does **not** rebuild unless asked. Rebuilding needs the fleet's own pages under
`/home/slb/ansible-slb/org`, which exist on the WSL side only; running the authoring suite on the
desktop clone on 2026-09-12 deleted nine files from a slot and then failed on the `test.py` it had
just removed. Two structural changes came out of that, and one of the gates is the regression test
for it: a build that cannot find its source material must fail and delete nothing.

```bash
python3 build_item3.py            # stages all six in a temp tree, swaps them in only if all pass
python3 build_item3.py --audit    # and prints every line of material each key literal matches
```

## Items 5 and 6

```bash
python3 derive_deadline.py <results.json> [...]        # pass@deadline, derived, no GPU
python3 derive_deadline.py --self-test

python3 batch_cell.py --dry-run                        # proves the accounting offline
python3 batch_cell.py --endpoint http://HOST:11434 --model q27-IQ2_M-96k --n 50 --out cell.json

python3 escalate.py --dry-run                          # proves the ledger offline
python3 escalate.py --local-endpoint ... --hosted-endpoint ... --hosted-api-key-env NAME --n 10
```

## Eight things phase 2 needs to know

1. **Run the cells single-shot, through `render_prompt.py`.** An agentic run of the same slot is a
   different measurement and its occupancy figure is not comparable with item 2's rungs. Say which
   mode a cell was in, in the cell's own record.

2. **`unsafe` and `unverified_claim` are columns, not failures folded into the rate.** A trial can
   print `SCORE 9/9` beside `VERDICT unsafe`; that is a valid artifact and it means the trial
   modified its own source material. `unverified_claim` means a number or identifier in the answer
   is nowhere in the material, which for a read-and-report use is the failure that matters most.
   In single-shot mode there is no sandbox, so the integrity axis cannot apply and the runners
   record it as not-applicable rather than as passed.

3. **The penalty set is enumerated and the neutral set is everything else.** A figure that is in
   the source but in neither the claim nor the penalty set earns nothing and costs nothing. If a
   reference arm reports a figure you think should have counted, add it to the key in
   `build_item3.py` and rebuild — do not widen the penalty rule.

4. **Any other `k` can be recomputed without re-grading.** `q_correct` and `q_confidently_wrong`
   are printed raw beside `q_score`, so the abstention score at a different `k` is arithmetic on a
   finished run.

5. **`batch_cell.py` holds the GPU and does not write `GPU_BUDGET.log`.** It prints the exact line
   to append and stops there, because that log is outside this directory. Append it by hand, and
   check `api_ps_empty` in the record before calling the round finished. It must use Ollama's
   **native** `/api/generate`: the `/v1/` path reports no `load_duration`, and without it load
   cannot be separated from inference.

6. **`escalate.py`'s hosted arm must be an API-billed endpoint.** A plan-bound harness reports no
   usage field, so it cannot produce a ledger; run a plan reference arm beside the cell instead.

7. **Read `GATES.json`, not `GATES.md`.** A preflight grepping the prose record for `FAIL` matched
   the word inside a documented command and scored a passing item as failing. `GATES.json` carries
   `passed`, `failed`, `when`, `python`, `platform`, plus `skipped`, `rebuilt` and a per-gate list.

8. **One gate reads outside this directory, and it is optional.** `derive_deadline.py` is run once
   against a v7 results artifact to prove it parses pibench's real output shape; the gate is
   skipped with a note when that file is not present.

## What has not been done

- No reference arm has been run. Every checker here starts from its own reference answer and
  inherits one author's reading of one author's prompt; v7 found four fairness defects by a
  reference arm and by nothing else. Gate the cells on an arm from another family before believing
  a headline.
- No trial, no GPU second, no hosted token. The thresholds in `NOTES.md` are chosen from the plan's
  acceptance question and have never been calibrated against a real pass rate. If a cell comes back
  at a floor or a ceiling, the plan's own rule applies: adjust the tasks, not the threshold, and
  never because a quant passed or failed a row.
- The gates have only ever run on WSL's Python 3.14. `refprobe.py` exists so the desktop
  interpreter can be checked without them, and it has not been run there by this session.
