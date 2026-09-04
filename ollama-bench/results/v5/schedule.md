# v5 GPU schedule

The next GPU runs, each with a one-line reason, rewritten after every result (plan rev 5.8
section 6). Rule for choosing the next run: prefer the run whose result could flip a verdict line
in section 7.

**Status: nothing queued is runnable yet.** The authoring work (authoring, selfcheck, the Sonnet
3/3 and GLM 2/3 gate, then the Haiku row) is cloud and subscription only and must land first — it
is what freezes the suite hashes and sizes the local timeouts. The GPU is idle and no model is
loaded.

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
