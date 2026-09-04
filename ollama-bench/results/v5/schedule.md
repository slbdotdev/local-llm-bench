# v5 GPU schedule

The next GPU runs, each with a one-line reason, rewritten after every result (plan rev 5.8
section 6). Rule for choosing the next run: prefer the run whose result could flip a verdict line
in section 7.

**Status: the GPU is working again; the queue is blocked only on the freeze.** The CPU-only
fault that dominated 2026-09-04 is **repaired** — `cuda_v13` was reinstalled and verified by a
real load (`q27-Q3_K_S`, 100% GPU, 15357 MiB, **52.7 eval tok/s**, on the gpu-tune curve). Fault:
`findings-2026-09-04-gpu-cuda-broken.md`; repair: `ansible-slb/org/ollama-cuda-repair-2026-09-04.md`.

Preconditions for run 1, current state:

| precondition | state |
| --- | --- |
| GPU actually resident | **done**, verified by a real load, not a version string |
| KV-probe lifecycle barrier fixed and proven | **done**, `--lifecycle-selftest` `ok: true` **and `drain_branch_proven: true`** — the artifact records `vram_peak_while_healthy_mib: 14611` per cycle, draining to the 1230 MiB baseline before returning |
| fifteen grid model tags with `num_ctx` + `num_gpu 66` | **NOT done as of 2026-09-04 — script correct, run unfinished; see correction below** |
| `pibench.py` pads the sandbox to the cell context | **done**, `--pad-tokens N`; verified independently (24,000 requested -> 30 files, ~24,173 est. tokens, seed untouched, filler type matched to the seed) |
| `pibench.py` records `VERDICT` per trial | **done**, verified (last line wins, absent -> None) |
| `pibench.py` records per-trial residency + gen tok/s | **written, NOT verified against a live model** — it could not be tested while the GPU was down. Verify before trusting a thrashing flag. |
| suite frozen | **NOT done**, and not the manager session's to take |
| Sonnet 3/3 on all eight | **done** — 3/3 on every task, after replacing g03 and g04 on gate evidence |
| GLM >=2/3 on all eight | **done** — 3/3 on seven, 2/3 on t02 |
| Haiku x3 discrimination check | **done** — and it says **do not freeze**: five tasks saturated at 3/3 against a section 4 limit of three. `findings-2026-09-04-haiku-saturation.md` |
| Haiku x3 prompt-defect read | **done** — t01 flagged by two of three readers, t04 by one; tighten t01 before freezing |
| suite freeze-ready | **NO** — the saturation count must be resolved first, and that decision is structural and was banked, not taken |
| local calibration (section 6 step 3) | **NOT done** — no task has been sized against the local model |

**Before any cell: set `OLLAMA_KV_CACHE_TYPE=q4_0` and revert it to `q8_0` with an Ollama restart
afterwards.** It is still `q8_0` machine-wide; this session never changed it, because no cell ran.

**Unload Ollama before any direct-server (KV probe) run.** Ollama's own model runner is *also*
named `llama-server.exe`, so the KV harness's cleanup barrier cannot tell it from its own child:
with a model resident it will burn its full 180 s and report a misleading "VRAM did not reach
three consecutive quiescent samples", and in the wrong ordering it would `taskkill /T /F` Ollama's
runner. Unloading with `keep_alive: 0` returned the card from 15,357 MiB to 1,230 MiB in about
two seconds.

**Rev 5.8 replaced the queue entirely.** The first probe, the differentiation paths, the context
sweep and the concurrency probe are gone; so is the Unity class, on the capacity measurement in
plan section 9. What remains is one grid.

## Queue

| # | run | config | why this one |
| --- | --- | --- | --- |
| 1 | **Bend-finding pass** | all four quants x their reachable contexts (24k/32k/48k/64k), `num_gpu 66`, `q4_0` KV, thinking medium, all 8 tasks, **1 trial** | Fifteen cells, 120 trials. Finds where quality against context bends before any trial is spent confirming a flat part. This is the run to protect if the night runs short. |
| 2 | **Three-trial passes at the bend** | the cells at and either side of the bend, same config, 3 trials | Turns the bend into a verdict input under section 3 rule 4. Which cells these are is not knowable until run 1 lands, which is why they are not enumerated here. |
| 3 | **Confirming the winner** | best quant on the evidence, at the context it held, 3 trials on every task with fewer than three | The ranking row. |

Capacity map for run 1, from `results/gpu-tune/summary.md` at `q4_0`: Q2_K_L reaches all four
steps comfortably (13.07 GB at 96k); Q3_K_S reaches 64k at 13.70 GB; IQ3_M reaches 64k at 14.11
GB and is **fair-weather**, so flag every IQ3_M 64k trial; Q3_K_M stops at 48k (14.16 GB, also
fair-weather); Q3_K_L is excluded by the 32k floor.

**The whole grid pins `q4_0` and the desktop is on `q8_0`.** Set it, and **revert to `q8_0` and
restart Ollama afterwards**. Results are conditional on `q4_0`, which is stated in the report:
q8_0 is predicted not to fit at 64k at all, so this grid does not answer the cache question for
the machine's live setting. The direct per-server comparison in `kv-probe-plan-2026-09-03.md`
still stands separately.

**Fill the context or the cell is meaningless.** `num_ctx` allocates KV up front; a short prompt
in a 64k cell measures 64k of nothing. Each task is padded to the cell size with realistic
irrelevant material, with the needed material present and required.

## Standing run rules

- One model on the GPU at a time.
- Every local trial logs the `ollama ps` processor split, `nvidia-smi` peak memory **and measured
  gen tok/s**. Residency alone is not trusted: on Windows/WDDM an oversized allocation raises no
  OOM, it spills to system RAM while still reporting `100% GPU` and `offloaded 66/66` (plan
  rule 7). A trial well below its quant's known resident curve is flagged thrashing.
- Configs above ~14.2 GB are fair-weather and are labelled as such if run at all; the desktop's
  idle VRAM drifts 1.0–2.9 GB and reclaims without warning.
- Every pi change stays bench-local through `PI_CODING_AGENT_DIR`; nothing under `~/.pi` or the
  deployed skill roots is touched.
- A timeout is a fail and is recorded as one.

## Log

- 2026-09-03 — file created at plan rev 5.4. Queue seeded, nothing run. GPU idle, no model loaded;
  the last local activity was the v4-task smoke the owner stopped at 16:51, which produced no
  usable quant ranking.
- 2026-09-03 — control session restarted from handoff. State re-verified against it and matching:
  ansible-slb `d9cd381` clean in both clones, GPU idle (1.66 GB, no model loaded), usage 5h 28% /
  weekly-all 84% / Fable-scoped 94%, `D:\avatars` still 3 dirty files under `tools/bench/`.
  Queue unchanged and still not runnable. One new blocker recorded against the authoring work only:
  `findings-2026-09-03-unity-harness.md`, the Unity harness for u01 to u03.
- 2026-09-04 — **cleared to run.** Plan at rev 5.9; the owner gave the authoring go-ahead. The
  worker-runtime precondition is met — acceptance-tested against both live harnesses, four
  defects found and fixed (`ansible-slb/org/worker-runtime-acceptance-2026-09-04.md`). The queue
  below is unchanged and still not runnable: the KV-probe harness faults are the one precondition
  still owed and are the manager's first job, and authoring must land before any GPU cell.
  The manager starts from `handoff-2026-09-04.md` in a fresh session.
- 2026-09-04 — **GPU work stopped before it started; the queue is unchanged and unrunnable.**
  The Opus manager session found FRACTAL serving on CPU only (see above) while proving the
  KV-probe lifecycle fix on real hardware. Three preconditions now stand between this file and
  run 1: Ollama reinstalled and residency verified by a real load; `pibench.py` taught to pad the
  sandbox to the cell's context and to record `VERDICT`; and the suite frozen. The fifteen grid
  model tags were claimed here to exist — **they did not; see the correction below** — and the
  KV-probe lifecycle barrier is fixed and
  proven with a live start/stop/start cycle — but that proof ran CPU-only, so the barrier's
  **VRAM-drain** branch is exercised only against an idle card and is still unproven against a
  real 14 GB allocation. Re-run `kvquality.py --lifecycle-selftest` once the GPU is back; it
  takes about a minute and it is the cheapest confirmation available.
  Authoring and the cloud gates continued and do not touch this queue.
- 2026-09-04 (later) — **GPU repaired and verified; queue still unrunnable, now only on the
  freeze.** The KV-probe lifecycle barrier is fixed and proven on real hardware, the grid
  tags do **not** all exist (corrected below; three of fifteen at the time of writing), and `pibench.py` now pads the sandbox and records `VERDICT` (both verified
  independently). The suite is authored and both cloud gates are part-run: GLM passes 2/3 on all
  eight, Sonnet is at 7/8 on its second trial with a third owed and the whole Haiku row not
  started. No scored row of any kind has been run, and none may be before the freeze.
- 2026-09-04 (end of manager session) — **both primary gates satisfied.** Sonnet 3/3 and GLM
  >=2/3 on all eight tasks, after replacing g03 and g04 with their `cand-1` alternates on gate
  evidence (rule 1's prescribed remedy; no quant evidence existed at any point). The GPU is
  repaired and the KV lifecycle barrier is proven against a real 14,611 MiB allocation. The queue
  is now blocked on exactly two things: the Haiku row, and the freeze. Neither needs the card.
- 2026-09-04 (final) — **the suite is NOT freeze-ready, and that is this session's last finding.**
  Both primary gates pass (Sonnet 3/3, GLM >=2/3, all eight), but section 4's discrimination check
  shows Haiku passing 8/8 with five tasks saturated at 3/3 against a limit of three. Harder
  variants, or an explicit decision to accept and report the saturation, must come before the
  freeze. t01 also needs its prompt tightened. No scored row of any kind has been run.

- 2026-09-04 (correction) — **"fifteen grid model tags | done" was FALSE and is retracted.**
  This file and `findings-2026-09-04-grid-harness-gap.md` both recorded the tags as built. A direct
  `ollama list` on the Windows daemon showed **three** of the fifteen cell tags:
  `q27-Q2_K_L-24k`, `q27-Q3_K_S-64k` and `q27-IQ3_M-64k` — and the last two predate this session,
  so exactly **one** tag was produced by the `make_grid_models.sh` run. The script itself is
  correct and the tag it built is correct (`num_ctx 24576`, `num_gpu 66`); this was an unfinished
  run recorded as a finished one, not a broken script.

  **Why this mattered more than a stale checkbox.** The same `ollama list` also shows five
  suffix-less base tags (`q27-IQ3_M`, `q27-Q2_K_L`, `q27-Q3_K_S`, `q27-Q3_K_L`, `q27-Q3_K_M`).
  A later session starting run 1 on the "done" line would have had twelve of fifteen cells fail
  outright, or — worse — fall back to a base tag that bakes `num_ctx 32768` and no `num_gpu`,
  which is precisely the silent mis-measurement the harness-gap page was written to prevent.
  Verify tags by `ollama list` before run 1; do not trust this table.
