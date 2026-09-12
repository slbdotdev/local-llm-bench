# v8 item 3, 5 and 6 — the instruments

*Built in phase 0 by a worker session under the Claude Code control session, 2026-09-11/12. No
GPU time was spent, no model was called, no hosted token was bought, and the Ollama endpoint was
never opened. Everything here has been gated offline; the record is `GATES.md`.*

This directory holds three things the v8 plan of record (`../plan-2026-09-11.md`) asks for:

| item | what | files |
| --- | --- | --- |
| **3** | seeded read-and-report, three production uses at two occupancy rungs each | `slots/`, `grade_seeded.py`, `build_item3.py`, `render_prompt.py` |
| **5** | deadline and throughput | `derive_deadline.py`, `batch_cell.py` |
| **6** | escalation economics | `escalate.py` |
| — | the phase-1 gate record and the runner that produces it | `GATES.md`, `gates.py` |

Items 5 and 6 live here because they are built on item 3's slots and its grader, not because they
are part of item 3. They are campaign-wide tools.

## The six slots

    slots/a1-summarise-r1        use A, report summarisation      rung r1   11,926 tokens
    slots/a2-summarise-r2        use A                            rung r2   40,728 tokens
    slots/b1-contradiction-r1    use B, contradiction hunt        rung r1   10,703 tokens
    slots/b2-contradiction-r2    use B                            rung r2   40,258 tokens
    slots/c1-changelog-r1        use C, changelog from a git range rung r1  12,264 tokens
    slots/c2-changelog-r2        use C                            rung r2   42,509 tokens

The three uses are the three ranked production uses of
`org/local-workhorse-plan-2026-09-06.md` section 7, in its own order. Rungs are **r1 = 12,000**
and **r2 = 40,000** tokens of material, measured at the suite's own 4.664 chars per token, with
the v8 plan's own ±15% tolerance. Rungs are separate cells and are never pooled.

Each slot is the v7 task layout — `prompt.md`, `seed/`, `ref/`, `test.py`, `selfcheck.py`,
`NOTES.md`, `MANIFEST.json` — so `pibench.py` runs them with no change, and each slot's
`NOTES.md` carries its own answer key, thresholds and near-miss table.

## Running them

**Agentic mode**, the v7 format, which is what the six slots are authored for:

```bash
# from ollama-bench/, exactly as v7 ran its own task directories
python3 pibench.py --tasks-dir results/v8/item3/slots --model q27-IQ2_M-96k --trials 10 ...
```

**Single-shot mode**, where occupancy is guaranteed by construction:

```bash
python3 render_prompt.py slots/a1-summarise-r1            # the whole prompt, material inlined
python3 render_prompt.py slots/a1-summarise-r1 --measure  # its size only
```

**Rebuilding a slot** (only needed if the source material or a key changes):

```bash
python3 build_item3.py            # rebuilds all six from their sources
python3 build_item3.py --audit    # and prints every line of material each key literal matches
```

**Re-running the gates**, which rewrites `GATES.md` from the run:

```bash
python3 gates.py
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

## Seven things phase 2 needs to know

1. **The rung is a *material* rung in agentic mode.** The material is on disk, so a trial's
   `peak_prompt` measures what the model chose to read. The v8 plan's void rule (section 4) is
   about whether a cell tested what it claims, and for this family it only applies to the
   single-shot mode `render_prompt.py` produces. In agentic mode a low `peak_prompt` is a finding
   about the model — D7-32's "the model now sets the material aside by never opening it" — and
   not grounds for voiding the cell. Decide which mode a cell is before running it and say so in
   the cell's own record.

2. **The headline is three rates, not a pass rate.** Every trial prints
   `METRICS recall=… precision=… <penalty>_rate=… hallucinations=… instrument=…` and `pibench`
   keeps the last 600 characters of grader output, which is why that line sits near the end.
   Use B's answer is precision **and** recall, never one number — the plan says so, and the
   question the use actually asks is whether the candidate list is cheap enough to adjudicate.

3. **`unsafe` and `unverified_claim` are columns, not failures folded into the rate.** A trial
   can print `SCORE 7/7` beside `VERDICT unsafe`; that is a valid artifact and it means the
   trial modified its own source material. `unverified_claim` means a number or identifier in
   the answer is nowhere in the material, which for a read-and-report use is the failure that
   matters most.

4. **The penalty set is enumerated and the neutral set is everything else.** A figure that is in
   the source but in neither the claim nor the penalty set earns nothing and costs nothing.
   This is deliberate. If a reference arm reports a figure you think should have counted, the
   fix is to add it to the key in `build_item3.py` and rebuild, not to widen the penalty rule.

5. **Item 4's abstention axis is not wired in here, and the hook it needs is one field.** Use A's
   decoy class already covers the "the material says this is unmeasured" case by scope rather
   than by abstention. If item 4 wants a scored abstention, add a `neutral_keys` list to a
   slot's CONFIG and exclude those keys from the recall denominator in `grade_seeded.grade_text`;
   nothing else in the instrument has to move. It is not implemented, because untested code in a
   grader is worse than no code.

6. **`batch_cell.py` holds the GPU and does not write `GPU_BUDGET.log`.** It prints the exact
   line to append and stops there, because that log is outside this directory. Append it by hand
   after the run, and check `api_ps_empty` in the record before calling the round finished.

7. **`escalate.py`'s hosted arm must be an API-billed endpoint.** A model reachable on a plan runs
   through its native harness and never through a raw endpoint. That is also the only way to get
   a token ledger: a plan-bound harness reports no usage figures. If phase 2 wants a plan-bound
   reference arm, produce its answers through that harness and feed them in rather than pointing
   this at a plan.

## What has not been done

- No reference arm has been run. Every checker here starts from its own reference answer and
  inherits one author's reading of one author's prompt; v7 found four fairness defects by a
  reference arm and by nothing else. Gate the cells on an arm from another family before
  believing a headline.
- No trial, no GPU second, no hosted token. The thresholds in `NOTES.md` are chosen from the
  plan's acceptance question and have never been calibrated against a real pass rate. If a cell
  comes back at a floor or a ceiling, the plan's own rule applies: adjust the tasks, not the
  threshold, and never because a quant passed or failed a row.
