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

**Fixed.** `ollama-bench/make_grid_models.sh` builds one tag per cell — `q27-<QUANT>-<N>k` with
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
4. The fifteen tags built (done).

Items 1-3 are one contained change to `pibench.py`. Until they land, **the grid should not be
run**, because it would return a flat curve that looks like a result.
