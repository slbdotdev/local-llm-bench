# v5 GPU schedule

The next three GPU runs, each with a one-line reason, rewritten after every result
(plan rev 5.4 section 6). Rule for choosing the next run: prefer the run whose result could flip
a verdict line in section 7; never spend a trial confirming what two trials already showed.

**Status: nothing queued is runnable yet.** Phase A (authoring, selfcheck, the Sonnet 3/3 and
GLM 2/3 gate, then the Haiku and Luna rows) is cloud and subscription only and must land first —
it is what freezes the suite hashes and sizes the local timeouts. The GPU is idle and no model is
loaded.

## Queue

| # | run | config | why this one |
| --- | --- | --- | --- |
| 1 | **B0 critical probe** | `q27-IQ3_M`, `num_ctx 32768`, `num_gpu 66`, thinking medium, q4_0 KV, all 9 tasks, 1 trial | The one run that can end the programme. It says whether the suite is in reach at all and which tasks discriminate; every later phase is shaped by its pass pattern. 32k not 64k: 13.39 GB keeps ~2 GB of VRAM margin where 64k is 14.11 GB and fair-weather. |
| 2 | **B0-control, KV precision** | same quant, same 32k, `OLLAMA_KV_CACHE_TYPE=q8_0`, g05 + the two highest-partial-score headline tasks that failed under q4_0 | Without it a weak B0 cannot separate "this quant is too small" from "this cache is too lossy" — the whole gpu-tune study was measured at q4_0 and no quality was ever measured there. ~15 min. **Revert the env var to q4_0 and restart Ollama afterwards**; the baked `*-64k` models depend on it. |
| 3 | **B1, Q3_K_M full headline set** | `q27-Q3_K_M`, 32k, `num_gpu 66`, q4_0, all 7 headline tasks, 1 trial | The a-priori quality challenger the owner is not ready to discard. Runs the full set, not a sentinel subset, so IQ3_M's B0 pass pattern cannot quietly define what the suite measures. |

Queued behind those, in order, and deliberately not promised a slot yet: **B1 Q2_K_L full
headline set** (the 2-bit verdict line the owner asked for), **B1 Q3_K_S sentinel set**, then
earned re-trials wherever a quant disagreed with IQ3_M.

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
  Queue unchanged and still not runnable. One new blocker recorded against Phase A only:
  `findings-2026-09-03-unity-harness.md`, the Unity harness for u01 to u03.
