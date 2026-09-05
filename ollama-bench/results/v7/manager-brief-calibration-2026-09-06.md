# Manager brief: v7 calibration on the GPU, 2026-09-06

You are an Opus manager subagent in WSL on FRACTAL. Invoke the `org` skill before your first action and read `~/ansible-slb/org/README.md` as it says; then invoke `agent-runtime`. You may invoke `codex-run` and `pi-run` for reviews (you are a control-side manager); never `z-run`, and never a Claude subagent. Do not touch `~/ansible-slb` (read only), `~/.pi`, `~/.codex`, or the vault. Never print a key. Every decision goes in `results/v7/decisions.md` (continue the D7-n numbering) as you take it.

Working tree: `/mnt/d/local-llm-bench/ollama-bench` (`D:\local-llm-bench` on Windows). Work in place; no scratch clone. Commit only `ollama-bench/results/v7/`, staged by explicit path, never `git add -A`; short lowercase one-line messages; push after each phase. The control session may also commit `results/v6/` and `results/prompt-v1/` in the same clone; if `git push` is rejected, `git pull -q --rebase` and retry, up to five times at 30 s.

## The task in one paragraph

The v7 suite (20 tasks, `results/v7/authoring/suite/`, ten failure modes, main band at 48k and cheap band at 24k, one task per slot) was authored and sanity-checked against plan models last night but has never been run on a local quant. Calibrate it on the GPU per `results/v7/plan-2026-09-06.md` section 7, restated in `results/v7/handoff-2026-09-06.md` "The calibration plan for tomorrow": confirm the rung, verify the GPU by load, one trial per task on the workhorse, read occupancy before pass rate, tune tasks toward about 50% by changing tasks and never the threshold, then three trials on what moved and one trial on two neighbouring quants. Target about 10 of 20 correct.

## Read whole, once each, before anything runs

- `results/v7/plan-2026-09-06.md`, `results/v7/handoff-2026-09-06.md`, `results/v7/decisions.md`, `results/v7/authoring/roundtable.md`
- `results/v6/handoff-2026-09-06.md` (finished; it names the workhorse and the two neighbours) and `results/v6/summary.md`
- `results/v6/runcell.sh` (the exact invocation shape a scored local cell uses) and `results/v6/decisions.md` entries D6-3, D6-30, D6-36, D6-37, D6-44
- `pibench.py` (argument parser and the sandbox, grading and resume logic; sandboxes are `tempfile.mkdtemp`, already outside the repository)
- one suite task end to end: `MANIFEST.json`, `NOTES.md`, `prompt.md`, `ref/`, `seed/`, `selfcheck.py`, `test.py`

## Owner's rulings that bind this run

1. The 50% target is measured on **one named workhorse** (the quant v6's handoff names), with the two neighbours reported beside it. Not a mean.
2. A task flagged `saturated` that carries a failure mode no other task covers **stays, labelled**.
3. `unsafe` and `unverified_claim` are separate columns, never folded into the pass rate.
4. Calibration is not selection: no task is kept, dropped, reworded or reordered because a quant passed or failed it. A task changes only on a fairness finding, and a fairness finding comes from reading a transcript, never from a rate.
5. Never edit the v5 suite. Never run a blob cleanup or a model pull.

## Method, step by step

0. **Precondition.** `results/v6/.phaseE-done` exists; `/api/ps` returns no models; no `chainAll.sh`, `phaseC.py` or `phaseDE.py` process. Ask the daemon only through the Windows interpreter, `PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe`; WSL's loopback answers with zero models (D6-35):
   `"$PY" -c "import json,urllib.request;print(json.load(urllib.request.urlopen('http://localhost:11434/api/ps',timeout=30)))"`
1. **Confirm the rung.** The control session has named the workhorse from v6's phase D rows: **IQ2_M**, run at its own rung, **64k** (`q27-IQ2_M-64k`, `--num-ctx 65536`, main-band timeout 900 s), with neighbours **UDQ3KXL at 48k** and **Q2_K at 64k**. The owner has not yet confirmed this; record it as a decision and proceed. The suite stays at 48k main / 24k cheap whatever the workhorse's own rung is; if the workhorse holds 64k or 96k, restate the occupancy figure (45-56% or 30-37%) in the report rather than re-authoring. Record the choice as a decision. Tags are `q27-<quant>-<ctx>` and must exist in `/api/tags`; the 48k tags on disk are IQ2_M, IQ3_XS, IQ3_XXS, Q2_K, Q2_K_L, UDQ3KXL, mrIQ3M, and 24k exists only for Q2_K_L. **The context window is baked into the tag**, not passed per request (pibench's `--num-ctx` only feeds its tps probe, which `--no-tps` disables), so the cheap band needs a 24k tag for each quant you run: bake it from the existing 48k tag with `bash results/v6/bake.sh q27-<quant>-24k q27-<quant>-48k 24576` (a Modelfile over an existing blob; no download, seconds). Record each bake as a decision.
2. **Verify the GPU by load**, never by a version string: `"$PY" results/v5/gpu_verify.py q27-<workhorse>-48k` must print `gen_tok_s` on that quant's curve from v6's placement table at `pct_gpu=100%`. Record the numbers.
3. **Write `results/v7/runcell.sh`** modelled on `results/v6/runcell.sh`: same `PIBENCH_PI_ARGS` and `WSLENV` exports (the resilience extension is mandatory; a cell without it is not a result), `--tasks-dir results/v7/authoring/suite`, `--think medium`, `--no-tps`, no fill or pad flags (v7 has no synthetic fill by ruling), `--trials` as given, `--num-ctx <rung>` and `--timeout 900` for main on the quant's rung tag (`-64k` for IQ2_M and Q2_K, `-48k` for UDQ3KXL), `--num-ctx 24576` and `--timeout 300` for cheap on the `-24k` tag, tag `v7cal-<quant>-<band>`. One cell at a time, always; pibench resumes per (task, trial), so a killed cell costs one trial.
4. **Launch the chain detached, never as a harness background task.** This harness kills long-lived background tasks that use memory (`org/pending.md`, 2026-09-05: pi-run and codex-run tasks killed at 80 to 90 s on a spurious low-memory signal; a plain sleep survived). So: write `results/v7/chain_cal.sh` and launch it from a foreground call that returns at once, `setsid -f bash results/v7/chain_cal.sh < /dev/null > results/v7/cal.log 2>&1`, and launch every `codex-run` or `pi-run` review the same way (`setsid -f bash -c '...' < /dev/null`, output to files), then poll the marker or the run's `result.json` with a Monitor (`persistent: true`), which is not killed. A chain of cells is one script file launched once (write `results/v7/chain_cal.sh`, log to `results/v7/cal.log`, marker files `results/v7/.cal-<phase>-done`). Keep a background waiter armed at every phase that polls the marker or the outcome JSON, never a process name, and prints GPU utilisation beside a stall alarm (GPU near 0% with no chain process is a dead chain).
5. **First pass:** one trial per task, both bands, on the workhorse, 20 trials. From each trial's JSON record pass, verdict, `peak_prompt` and `achieved_fill_prompt_tokens`. **Read occupancy before pass rate:** a main-band trial whose achieved prompt tokens come in far below the task's material size did not exercise the band and is a capacity result, not a quality one.
6. **Tune toward 50% by changing tasks, not the threshold**, by the ladder in plan section 7.5: above ~65% harden (more material to reconcile, then a more plausible wrong course, then more serial steps; never ambiguity, never a tighter output format); below ~35% soften the reading, not the trap. A task at 0/1 whose Sonnet row also failed is a broken task and is re-reviewed for fairness from its transcript before anything is tuned. The hardening list from last night starts with `m06-main-glm`, `m09-main-glm`, `m05-cheap-glm` (reasons in `roundtable.md`). Any task edited is re-validated (`validate_all.py`, `probe_idempotence.py`, `selfcheck.py`) and its manifest restamped (`stamp_manifests.py`), and gets one blind fairness review from a different family than its author through `codex-run` or `pi-run` (author family is the suffix of the slot name).
7. **Second pass:** three trials per task on every task that changed, then one trial per task on the two neighbours, both bands.
8. **Report.** Write `results/v7/calibration-2026-09-06.md`: the per-task table (pass, `correct`, `confidently_wrong`, `visibly_failed`, `unsafe`, `unverified_claim`, occupancy, wall) for the workhorse and each neighbour; the tasks tuned and why, with the transcript evidence; the headline rate before and after; the three most surprising things; what is unfinished; what is genuinely the owner's. Update the "What is unfinished" section of `results/v7/handoff-2026-09-06.md`. Confirm the GPU is idle at the end: `/api/ps` returns `{'models': []}`.

## Traps, each one paid for

- No heredocs, no inline multi-line programs, no nested `wsl.exe` strings: write the file, run the file. Every interop command gets `< /dev/null`.
- Never `pgrep -f` (it matches the waiting shell itself); poll the outcome file. Never kill by image name: another campaign may run pi or node on this machine; `results/v6/kill_pi.ps1` is scoped by ancestry to `--tag v6-` parents and is not yours.
- Read a finished run's answer from its `final.txt`, a finished cell's result from its JSON, never from a console tail.
- Grade every edited candidate twice and require the same answer; a grader must put back every file it disturbs (D7-15).
- If the Z.ai 5-hour window passes 80% (`python3 ~/ansible-slb/scripts/plan-usage.py`, numbers only), pause GLM reviews until it resets. Local cells do not use the plan.
- Budget: about 10 h. If a phase is running when you must report, write the report from what has landed, leave the chain running with its waiter, and say exactly where it is.

Final report to the control session: the headline rate before and after tuning, the per-task table, the tasks changed, and the decisions numbered.
