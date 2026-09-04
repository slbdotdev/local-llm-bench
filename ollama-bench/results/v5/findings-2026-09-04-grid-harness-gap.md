# The grid cannot run on today's harness — three gaps, found 2026-09-04

Found by the Opus manager session while the authoring runs were in flight, by reading
`pibench.py` against what plan section 6 and `schedule.md` actually ask the bend-finding pass to
do. **None of these are in `org/pending.md` and none were named as preconditions.** The KV-probe
lifecycle faults were the one precondition the handoff listed; these are three more, and they
block the grid rather than the KV probe.

Stated plainly up front: **nothing here changes what the suite measures.** These are harness
capabilities the plan already requires and the code does not have. Fixing them is not a
section 4a hazard.

## Gap 1 — the context axis is not wired up at all (the serious one)

The grid's whole point is "how does each quant's quality hold as its context fills, from 24k to
64k", and `schedule.md` states the rule: *"`num_ctx` allocates KV up front; a short prompt in a
64k cell measures 64k of nothing."*

`pibench.py` does not pad anything. `run_pi()` creates a sandbox, copies `seed/` in, and runs the
model on `prompt.md`. There is a `FILLER` constant and a `tps_curve()` that pads prompts — but
those exist only to measure **throughput against fill**, and are never used on a task trial.

So today, a "64k cell" and a "24k cell" would hand the model the identical few-thousand-token
prompt and differ only in how much KV was allocated. **Every cell in the fifteen-cell grid would
produce the same number, the curve would be flat by construction, and the flatness would look
like a finding.** This is the single most expensive defect available in this plan: it does not
fail, it produces a confident wrong answer — the exact failure mode the benchmark exists to
measure, committed by the benchmark itself.

The fix is padding the **sandbox**, not the prompt: write realistic irrelevant files into the
sandbox until the material the model must read reaches the cell's token budget. The authoring
contract already requires that the answer live in `seed/` files rather than in `prompt.md`, and
that checkers tolerate extra files, precisely so this is possible.

## Gap 2 — thirteen of the fifteen cells have no model tag, and the failure is silent

`pibench.py` drives pi, which reaches Ollama over the OpenAI-compatible API and **passes no
options**. So `num_ctx` and `num_gpu` can only reach the server if they are baked into the model
tag — which is what `make_model.sh`'s comment means, and why `q27-Q3_K_S-64k` exists as a
separate tag at all. `pibench.py --num-ctx` does **not** set the trial's context; it is used only
by the throughput probe.

Before today only two grid tags existed, `q27-Q3_K_S-64k` and `q27-IQ3_M-64k`. The base tags bake
`num_ctx 32768` and **no `num_gpu`**, so:

- a "48k cell" run against `q27-Q3_K_S` would have silently run at 32768, and
- every cell would have run without the forced full offload that `results/gpu-tune/summary.md`
  measured as worth up to **2.3x** throughput, because Ollama's scheduler parks 2-7 layers on the
  CPU while leaving ~600 MiB of VRAM unused.

Both failures are silent. Neither raises an error; the run just measures the wrong thing.

**Script written, but the run did NOT finish — see the correction at the end of this page.**
`ollama-bench/make_grid_models.sh` builds one tag per cell — `q27-<QUANT>-<N>k` with
`num_ctx` and `PARAMETER num_gpu 66` — for the fifteen cells in the capacity map (Q2_K_L, Q3_K_S
and IQ3_M at 24k/32k/48k/64k; Q3_K_M at 24k/32k/48k; Q3_K_L excluded by the 32k floor). Each tag
reuses a blob already on disk, so this is a metadata operation with no download and no meaningful
disk cost.

### A trap worth writing down: Windows `ollama.exe` cannot read a WSL `/tmp` path

The first attempt failed on all four tags with

    Error: no Modelfile or safetensors files found

and **exit code 1**. (An earlier version of this page said exit code 0, "a failure that reports
success to the shell". That was wrong and was corrected the same day: the misreading came from
taking `$?` after a **pipeline**, which reports the last command's status, not ollama's —
`${PIPESTATUS[0]}` is the fix. The correction is left visible because "distrust this command's
exit code" is exactly the kind of false lesson that outlives the page it is written on.)
The cause is not the Modelfile
content: `ollama create -f /tmp/tmp.XXXX` hands a WSL path to a Windows binary that cannot see
it. The fix is to write the Modelfile inside the Windows-visible tree (anywhere under
`/mnt/d/...`) and pass a **relative** path with the working directory set there. Recorded because
the error message names the file format and not the path, which sends you to the wrong problem,
and because the zero exit code means a script without an explicit check will report success.
`ollama create` for a 13 GB blob takes roughly two minutes, so fifteen tags is about half an hour
of wall clock — schedule it, do not discover it.

## Gap 3 — the headline instrument is not recorded

Section 7 makes the confidently-wrong rate a verdict line of its own and says it outranks pass
rate. `pibench.py` records `pass`, `score`, and the last 600 characters of grader output. There
is no per-trial field distinguishing **correct / visibly failed / confidently wrong**, so the
headline number would have to be reconstructed later by a human reading truncated grader tails —
across 120 trials.

The v5 authoring contract already requires every checker to print a `VERDICT <word>` line and
decide it mechanically. What is missing is the harness parsing that line into its own result
field. That is a small, additive change: one regex, one key in the result dict. It cannot change
any existing number, because `pass` and `score` keep their current definitions.

## What must happen before the first grid cell

1. Sandbox context padding in `pibench.py`, with the achieved fill recorded per trial from the
   model's own reported prompt token count — never assumed from the padding written.
2. `VERDICT` parsed into its own result field.
3. Per-trial residency: `ollama ps` split, `nvidia-smi` peak, and **measured gen tok/s**, per plan
   rule 7, which currently exist only as a per-model probe (`tps()`), not per trial. A trial well
   below its quant's known resident curve is flagged thrashing, and that judgement needs the
   number attached to the trial that produced it.
4. The fifteen tags built (**NOT done** — three of fifteen exist; see the correction at the end).

Items 1-3 are one contained change to `pibench.py`. Until they land, **the grid should not be
run**, because it would return a flat curve that looks like a result.

## Padding measured against a live arm: written material is not context fill

Run 2026-09-04 as the first real exercise of the `--pad-tokens` path against a live model, using
agentic Haiku across all eight tasks at a 48k request. Two rows were run, because the first
revealed a defect in the padding itself.

### Defect: the filler was trivially excludable

The original padding wrote every filler file as `__pibench_pad_NNNN.{py,md}`, flat at the sandbox
root. Two give-aways, either sufficient on its own:

- **By name.** One glob removes the entire fill and leaves exactly the unpadded sandbox.
- **By location.** On t01 the real material lives in `docs/`, `history/` and `quickstart.md` while
  all 41 pad files sat at the root, so even an agent ignoring names could separate them by position.

A grid whose padding can be excluded produces a **flatter curve than reality, and the flatness
looks like a finding** — the confidently-wrong failure mode this page already names as the most
expensive one available in this plan. The first row is therefore recorded as **inconclusive on the
padding axis**: Haiku passed 8/8, but the fill was avoidable, so it largely re-measures the
unpadded condition and must not be cited as having closed the fill question.

**Fix (in `pibench.py`).** Filler is now named like real material (`session_store.py`,
`retention-policy.md`, …) and distributed into the same directories the seed uses, with build and
cache directories excluded from the shape so filler never lands in `__pycache__`. Padding is
identified by a manifest — `pad_files` in the returned info, persisted to `padding.json` — never by
its filenames. Reserved deliverable names are never shadowed. On t01 the filler now interleaves:
`docs/escalation-matrix.md` sits beside the real `docs/escalation.md`.

### The measurement that matters: achieved fill, from reported prompt tokens

Achieved fill is the model's own reported prompt size — `input_tokens + cache_read_input_tokens +
cache_creation_input_tokens`, peak across the run's assistant messages — never the characters
written. `measure_fill.py` and `merge_fill.py` compute it and write it into each row's
`padding.json`; the earlier `est_tokens_after` estimate has been **removed** from those artifacts
rather than left beside the real number, because a `chars/5.95` figure reads like a measurement.

| task | unpadded | 48k, excludable filler | 48k, non-excludable filler |
| --- | --- | --- | --- |
| g01 | 18,605 | 22,794 | 21,985 |
| g02 | 20,750 | 22,735 | 23,924 |
| g03 | 20,109 | 22,064 | 21,816 |
| g04 | 17,747 | 19,504 | 22,648 |
| t01 | 18,601 | 20,479 | 22,691 |
| t02 | 18,205 | 20,426 | 20,847 |
| t03 | 23,604 | 25,555 | 26,988 |
| t04 | 18,115 | 21,223 | **37,555** |
| **median** | **18,603** | **21,643** | **22,669** |

### The finding: a 48k cell is not a 48k cell

**Roughly 48,000 estimated tokens of material were written per task. Median achieved fill was
22,669 — and the unpadded floor is already 18,603, most of which is harness and tool-definition
overhead rather than task material. So the padding contributed about 4,100 tokens of the ~48,000
written: under 10% of it ever reached the context.** Fixing the excludability moved the median by
about 1,000 tokens, which is real but small.

The cause is structural, not a bug: **padding on disk only enters the context if the model reads
it.** An agentic arm greps, opens the two or three files it needs, and never touches the rest. The
one task that behaved differently is instructive — t04 reached 37,555 tokens over 32 tool calls and
103 s, because it is the negative variant and the honest way to answer "is this implemented?" is to
search the tree. Difficulty drove the reading; the padding did not.

**Consequence for the grid, and it is serious.** As specified, the context axis does not vary what
it claims to vary. Cells labelled 24k and 64k would both land near ~20-25k of achieved fill for an
agentic arm, and the resulting curve would be close to flat *for reasons that have nothing to do
with the quants under test*. Any conclusion drawn from "performance holds up at 64k" would be
unfounded.

**What would actually work** — none of it taken here, since this is a design change for the owner:

1. Put the fill in the **prompt** rather than on disk, so occupancy is guaranteed and measurable.
2. Author tasks whose correct answer **requires** reading widely, as t04 incidentally does.
3. Keep padding on disk but **verify per trial** that achieved fill reached the cell's target, and
   discard or re-label any trial that did not — the cheapest option, and it at least stops the
   harness from reporting fills it never achieved.

Whatever is chosen, **every trial must record achieved fill and the grid must be read against that
number, not against the cell label.**


## Correction (2026-09-04): the fifteen tags were recorded as built and were not

This page said "Fixed" and listed "the fifteen tags built (done)". That was wrong, and the claim is
retracted here rather than quietly edited away.

A direct `ollama list` against the Windows daemon returned **three** of the fifteen cell tags —
`q27-Q2_K_L-24k`, `q27-Q3_K_S-64k`, `q27-IQ3_M-64k` — of which the last two already existed before
this session, as recorded earlier on this page. So the `make_grid_models.sh` run produced exactly
**one** new tag before stopping.

The script is not at fault: the one tag it built carries the right `num_ctx 24576` and
`num_gpu 66`. This was an unfinished run written up as a finished one.

**The consequence is the exact hazard this page exists to document.** `ollama list` also shows five
suffix-less base tags (`q27-IQ3_M`, `q27-Q2_K_L`, `q27-Q3_K_S`, `q27-Q3_K_L`, `q27-Q3_K_M`). Run 1
launched against the old "done" line would have had twelve of fifteen cells fail, or silently fall
back to a base tag baking `num_ctx 32768` with no `num_gpu` — gap 1 and gap 2 on this page,
re-entered through a stale checkbox. **Confirm tag existence with `ollama list` immediately before
run 1.**

## Local calibration on the arm the grid actually runs: the context axis is dead

The fill numbers earlier on this page were taken on a **Claude Code subagent arm**, whose unpadded
floor is 18,603 tokens of system prompt and tool definitions. Plan section 4 puts the pi arm's floor
at about **2k** ("pi's system prompt plus AGENTS.md") and rests the 24k-64k sweep on that. The
Claude-arm table therefore could not be carried across, so section 6 step 3 local calibration was
run on the pi/Ollama arm. Calibration only; **no pass/fail is reported or citable from these runs,
per section 4a**.

Setup followed the schedule's rules: `OLLAMA_KV_CACHE_TYPE=q4_0` set with an Ollama restart before
and reverted to `q8_0` with a restart after, one model resident at a time, `--pad-tokens` set to the
cell size, achieved fill taken per trial from the model's own reported prompt tokens.

| cell | task | requested fill | **achieved fill** | wall | tool calls | `ollama ps` split | nvidia-smi peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q2_K_L **24k** | g01 | 24,000 | **4,701** | 33.2 s | 5 | 11.83 GB, **100% GPU** | 13,362 MiB |
| Q2_K_L **24k** | t04 | 24,000 | **10,527** | 25.4 s | 7 | 11.83 GB, **100% GPU** | 13,061 MiB |
| Q2_K_L **64k** | g01 | 64,000 | **3,836** | 25.7 s | 6 | 13.35 GB, **100% GPU** | 14,610 MiB |
| Q2_K_L **64k** | t04 | 64,000 | **9,382** | 19.5 s | 5 | 13.35 GB, **100% GPU** | 14,612 MiB |
| Q3_K_S **64k** | g01 | 64,000 | **7,051** | 101.9 s | 4 | 14.70 GB, **100% GPU** | 15,767 MiB |
| Q3_K_S **64k** | t04 | 64,000 | **12,640** | 193.7 s | 16 | 14.70 GB, **100% GPU** | 15,769 MiB |

Measured gen throughput: Q2_K_L 59.1 / 59.4 tok/s, Q3_K_S 53.3 tok/s, all fully resident with no
CPU spill, so rule 7 is satisfied and none of these trials is a thrashing artefact.

### The result

**Holding the quant fixed and raising the cell from 24k to 64k did not raise achieved fill — it
lowered it slightly.** Q2_K_L g01 went 4,701 → 3,836 and t04 went 10,527 → 9,382, while the padding
written rose by 2.67x. Across all six trials achieved fill sits between 3,836 and 12,640 regardless
of whether the cell is 24k or 64k.

**The context axis as specified does not vary what it claims to vary, on the arm the grid runs.**
This is stronger than the Claude-arm finding, not weaker: there the padding at least moved the
median by ~1,000 tokens, whereas here the cell label and the achieved fill are uncorrelated. A
24k row and a 64k row would be measuring the same thing, and the resulting flat curve would be an
artefact of the harness rather than a property of the quants.

**So option 1 is now the only workable one:** put the fill in the prompt, where occupancy is
guaranteed and measurable, rather than on disk where it only counts if the model chooses to read it.
Option 3 (keep disk padding, verify achieved fill per trial and discard trials that miss) degenerates
here — on this evidence *every* trial would miss, so there would be nothing left to keep.

The variation that does exist tracks the **task**, not the cell: t04 draws roughly 2.5x the fill of
g01 in every cell, because answering its negative question honestly requires searching the tree.
That is the mechanism option 2 would exploit.

### Deviation from the brief, stated plainly

The brief asked for `q27-Q3_K_S-24k` and `q27-Q3_K_S-64k`. **`q27-Q3_K_S-24k` did not exist** and
building it was not this session's to do, so the same-quant 24k-vs-64k comparison was taken on
**Q2_K_L**, whose 24k and 64k tags both existed. `q27-Q3_K_S-64k` was run as asked and is reported
above. Six trials rather than four; the comparison the brief was designed to make is intact,
because the quant is held constant across the two cells that are being compared.

## The fill fix, and its acceptance test — PASSED

The owner decided the mechanism: fill is delivered **in the prompt**, not on disk. Implemented in
`pibench.py` as `--fill-tokens N` (target for the whole prompt), with `--pad-tokens` demoted to
sandbox realism and no longer sized to the cell.

Rules held constant, stated so a later reader knows what was controlled:

- The **instruction is byte-identical across cells**, taken verbatim from the frozen `prompt.md`
  and never regenerated. Only the quantity of extra material differs.
- The **instruction leads; the extra material follows**, identically in every cell and task.
  Position effects are real and are not what this axis measures.
- The extra material is **not labelled as filler**. It is introduced as "further context from this
  project ... judging what matters is part of the job". Anything reading as "ignore the following"
  gets ignored, which is the pad-filename lesson one layer up.

### Two harness faults found while building it

**1. A large prompt cannot be passed as an argv.** Windows caps a command line at 32,767 characters;
a 20k-token fill is ~93,000. The first acceptance attempt failed at spawn with
`WinError 206: The filename or extension is too long`, producing `"runs": []` — **no request ever
reached the model**. That is a harness failure, not a fill number that missed, and the two are worth
distinguishing because an empty result array otherwise reads as "the fix did not work". `pibench.py`
now writes large prompts to a file and passes them with pi's `@file` syntax, which inlines the file
as the message and preserves the order inside it. Small prompts still go inline, so every earlier
run and gate is unaffected.

**2. The chars/token constant was wrong by 28%.** `PAD_CHARS_PER_TOKEN = 5.95` was an estimate.
Measured against q27-Q3_K_S on this filler: 47,635 chars -> 10,213 prompt tokens = **4.664**. Sizing
prompt fill on 5.95 would have overshot `num_ctx` on the 24k cell and been silently truncated.
`FILL_CHARS_PER_TOKEN = 4.664` is now separate from the sandbox constant, with
`results/v5/fill_calibrate.py` to re-measure it if the model or filler style changes.

### Acceptance result

Quant held constant (`q27-Q3_K_S`), one trial per cell, achieved fill from the model's own reported
prompt tokens. Calibration only — **no pass/fail from these trials is citable about any task, per 4a.**

| cell | task | target | **achieved fill** | % of target | wall | turns | residency |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 24k | g01 | 24,000 | **23,427** | **97.6%** | 31.4 s | 5 | 13.18 GB, 100% GPU, peak 14,525 MiB |
| 24k | t04 | 24,000 | **22,383** | **93.3%** | 34.0 s | 6 | 13.18 GB, 100% GPU, peak 14,525 MiB |
| 64k | g01 | 64,000 | **57,871** | **90.4%** | 45.4 s | 1 | 14.70 GB, 100% GPU, peak 15,767 MiB |
| 64k | t04 | 64,000 | **57,857** | **90.4%** | 40.8 s | 1 | 14.70 GB, 100% GPU, peak 15,767 MiB |

**Both criteria pass.** Every trial reached at least 90% of its cell target, and the 64k figure is
far above the 24k figure for the same task — g01 23,427 -> 57,871 and t04 22,383 -> 57,857. Under
the old disk mechanism the same comparison went *down* (4,701 -> 3,836 and 10,527 -> 9,382). The
context axis now varies what it claims to vary.

### Prefill versus generation, and one thing to watch

Measured prefill throughput: **1,612-1,726 tok/s**. At the 64k cell's 57,871 tokens that is about
**36 s of prefill**, which is roughly 79% of the observed 45.4 s wall — prefill dominates the
*shape* of a 64k trial, but the total is nowhere near the 300 s wall, so `CONTRACT.md`'s sizing
limit holds at the 64k end. Budget note for run 1: each 64k trial now costs ~36 s of pure prefill
before any work happens.

**A caveat on how that was measured, because it bit me.** The `/api/generate` probe used for the
prefill split **truncates the prompt to exactly half `num_ctx`** — it reported 12,290 tokens on the
24k cell and 32,770 on the 64k cell, i.e. 24576/2 and 65536/2. Those fill figures are artifacts and
must not be quoted; the *rate* is still valid, and pi's own path did not truncate (it reached
57,871). Anyone calibrating through `/api/generate` should know it silently halves.

**Also worth watching: the agentic loop collapses at 64k.** Both 64k trials ran **1 turn**, against
5-6 turns at 24k. With ~57.9k of a 65,536 window consumed by the prompt, only ~7.6k remains for the
whole tool loop. That is a real property of running a 64k cell on a 64k window and it is not a
defect in the fill fix, but it means the 64k end of the axis measures something qualitatively
different from the 24k end — less room to work, not merely more to read. Flagged for the owner; not
resolved here.
