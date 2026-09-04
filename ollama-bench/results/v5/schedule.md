# v5 GPU schedule

The next GPU runs, each with a one-line reason, rewritten after every result (plan rev 5.8
section 6). Rule for choosing the next run: prefer the run whose result could flip a verdict line
in section 7.

**Status: the fill blocker is FIXED and measured; the freeze is now the sole remaining blocker.**
The context axis used to be delivered by padding the sandbox, which did not work — filler on disk
enters the context only if the model reads it, and raising the cell 24k -> 64k *lowered* achieved
fill. The owner decided the fix and it is built: **fill is delivered in the prompt**
(`pibench.py --fill-tokens N`), with sandbox padding demoted to realism. Acceptance on
`q27-Q3_K_S`, quant held constant, achieved fill from the model's own reported prompt tokens:
**24k cell 23,427 / 22,383 (97.6% / 93.3%), 64k cell 57,871 / 57,857 (both 90.4%)** — every trial
past 90% of its cell target and the 64k figure far above the 24k figure for the same task, where it
previously went down. Artifacts `results/accept-24k.json`, `results/accept-64k.json`; detail in
`findings-2026-09-04-grid-harness-gap.md`. **The remaining blocker is the freeze, which is the
owner's**, and the seven-of-eight saturation count still argues against taking it.

The GPU itself is working. The CPU-only
fault that dominated 2026-09-04 is **repaired** — `cuda_v13` was reinstalled and verified by a
real load (`q27-Q3_K_S`, 100% GPU, 15357 MiB, **52.7 eval tok/s**, on the gpu-tune curve). Fault:
`findings-2026-09-04-gpu-cuda-broken.md`; repair: `ansible-slb/org/ollama-cuda-repair-2026-09-04.md`.

Preconditions for run 1, current state:

| precondition | state |
| --- | --- |
| GPU actually resident | **done**, verified by a real load, not a version string |
| KV-probe lifecycle barrier fixed and proven | **done**, `--lifecycle-selftest` `ok: true` **and `drain_branch_proven: true`** — the artifact records `vram_peak_while_healthy_mib: 14611` per cycle, draining to the 1230 MiB baseline before returning |
| fifteen grid model tags with `num_ctx` + `num_gpu 66` | **done 2026-09-04, and verified tag by tag** — all 15 present in `ollama list` (Q2_K_L and Q3_K_S and IQ3_M at 24/32/48/64k, Q3_K_M at 24/32/48k), each read back with `ollama show --modelfile` confirming its own `num_ctx` and `num_gpu 66`. This row previously read **done** when only three existed; see the correction below. `make_grid_models.sh` also had a second defect fixed the same day — it built only the first quant family and exited 0 — and now ends by counting the tags and failing if fewer than fifteen. **Confirm the count before run 1 rather than trusting this row.** |
| `pibench.py` fills the context to the cell target | **done and accepted.** Fill is prompt-side (`--fill-tokens N`), instruction verbatim and first, extra material after, never labelled as filler. Achieved 90.4-97.6% of target across both cells (`accept-24k.json`, `accept-64k.json`). Two faults fixed on the way: prompts >32,767 chars cannot be passed as an argv on Windows (now written to a file and passed with pi's `@file`), and the chars/token constant was 28% wrong (measured 4.664, not 5.95). Sandbox padding is now realism only and is NOT sized to the cell. |
| ~~`pibench.py` pads the sandbox to the cell context~~ (superseded) | **The old disk mechanism did not deliver fill.** It writes what it is asked to write (seed untouched, filler named and placed like real material since the excludability fix). What *reaches the context*, measured from the model's reported prompt tokens rather than character counts: **3,836-12,640 achieved against 24,000-64,000 requested, and it does not track the cell.** The earlier "~24,173 est. tokens" figure was a `chars/5.95` estimate and has been removed here for the same reason it was removed from the artifacts — it reads like a measurement. |
| `pibench.py` records `VERDICT` per trial | **done**, verified (last line wins, absent -> None) |
| `pibench.py` records per-trial residency + gen tok/s | **done**, now verified against a live model. All six calibration trials carry `ps_vram_gb`, `ps_pct_gpu`, `nvidia_smi_peak_mib` and a measured gen tok/s: 100% GPU throughout, resident 11.83-14.70 GB, peaks 13,061-15,769 MiB, 53.3-59.4 tok/s, no CPU spill. `results/calib-q2kl-24k.json`, `calib-q2kl-64k.json`, `calib-q3ks-64k.json` |
| suite frozen | **NOT done**, and not the manager session's to take |
| Sonnet 3/3 on all eight | **done** — 3/3 on every task, after replacing g03 and g04 on gate evidence |
| GLM >=2/3 on all eight | **done** — 3/3 on seven, 2/3 on t02 |
| Haiku x3 discrimination check | **done** — and it says **do not freeze**: **seven** tasks saturated at 3/3 against a section 4 limit of three (g01, g02, g03, g04, t01, t02, t03; only t04 is not, at 2/3). Corrected from an earlier "five"; holds on all four conditions tried, including one-shot Haiku and both padded rows. `findings-2026-09-04-haiku-saturation.md` |
| Haiku x3 prompt-defect read | **done** — t01 flagged by two of three readers, t04 by one; tighten t01 before freezing |
| suite freeze-ready | **NO** — the saturation count must be resolved first, and that decision is structural and was banked, not taken |
| local calibration (section 6 step 3) | **PARTIALLY done.** Measured: g01 and t04 across three cells (Q2_K_L 24k/64k, Q3_K_S 64k), one trial each, giving achieved fill per trial and full residency. Not measured: the other **six of eight tasks**, and the appetite/wall questions — no reference-solution output-token ceiling or 300 s wall target has been checked against a local quant. Pass/fail from these runs is not recorded and is not citable, per 4a. |

**This q4_0 ritual may be a no-op — measured 2026-09-04.** Loading both 64k models at full
`num_ctx` under q8_0 and again under q4_0 gave *identical* resident sizes (14.70 and 15.11 GB, both
100% GPU); nvidia-smi differed by 6-42 MiB. Both q8_0 cells **fit**, falsifying
`kv-probe-plan-2026-09-03.md`'s prediction that neither would. So there is no capacity reason to
prefer q4_0 at 64k. Keep the ritual if you want insurance, but do not cite it as a controlled
variable. Detail in `findings-2026-09-04-grid-harness-gap.md`.

**Before any cell: set `OLLAMA_KV_CACHE_TYPE=q4_0` and revert it to `q8_0` with an Ollama restart
afterwards.** It is `q8_0` right now, verified against the Windows user environment on 2026-09-04 after the calibration runs, which did set it to `q4_0` and revert it. No scored cell has ever run.

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
| — | **RUNS 1-3: fill blocker CLEARED, freeze blocker remains** | — | The fill mechanism is fixed, accepted and measured (see the status header), so the context axis now varies with the cell and run 1 can find a bend. **What still holds runs 1-3 is the freeze alone**, which is the owner's. Two things to carry into run 1: each 64k trial costs ~36 s of prefill before any work, and at 64k the agentic loop collapsed to a single turn because ~57.9k of a 65,536 window is prompt — the 64k end measures less room to work, not only more to read. |
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
  shows Haiku passing 8/8 with five tasks saturated at 3/3 against a limit of three [**corrected
  later the same day: the count is seven, not five** — see the entry below and
  `findings-2026-09-04-haiku-saturation.md`]. Harder
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

- 2026-09-04 (final, superseding) — **the queue is held on the fill mechanism, not only on the
  freeze.** Local calibration on the pi/Ollama arm (section 6 step 3) measured achieved fill from
  the model's own reported prompt tokens across three cells. Holding the quant fixed, raising the
  cell 24k -> 64k **lowered** achieved fill: g01 4,701 -> 3,836 and t04 10,527 -> 9,382, against
  2.67x more padding written. `num_ctx` was demonstrably in effect (resident 11.83 -> 13.35 GB) and
  every trial was fully GPU-resident (100% GPU, 53-59 tok/s), so this is neither a configuration
  error nor a thrashing artefact. **Cell label and achieved fill are uncorrelated, so runs 1-3
  cannot produce section 7's curve** — run 1 has no bend to find. Padding on disk enters the
  context only if the model reads it, and the local arm reads two or three files. The fix is to put
  the fill in the prompt; that is a plan change and was banked, not taken. Calibration only — no
  pass/fail from these runs is recorded or citable, per 4a. Artifacts: `results/calib-q2kl-24k.json`,
  `calib-q2kl-64k.json`, `calib-q3ks-64k.json`.

  Two blockers now stand between this file and run 1, and **both are the owner's**: redesign the
  fill mechanism, and take the freeze (which the seven-of-eight saturation count still argues
  against). Nothing further in the plan can proceed without one of those decisions.
