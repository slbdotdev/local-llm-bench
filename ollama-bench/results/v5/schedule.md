# GPU schedule

The next GPU runs, each with a one-line reason, rewritten after every result. Rule for choosing
the next run: prefer the run whose result could flip a verdict line.

**The plan of record is `plan-2026-09-05.md`.** It supersedes `plan-rev5-focused.md` (rev 5.9)
wherever the two disagree. Read it, then `handoff-2026-09-05.md`, before touching this queue.

**Status: nothing blocks the manager.** Every precondition that was ever owed has been met or
withdrawn. The suite is not scoreable yet, and making it scoreable is the manager's own work, not
a permission to be asked for.

- **The suite is too easy and that is the whole of the remaining work.** Seven of eight tasks are
  saturated: Haiku passes 3/3, including one-shot with no self-checking. The target is Haiku near
  **80%** — 19 or 20 of 24 trials — with **Sonnet at or above 90%** as the anti-ambiguity guard.
  Method, ladder and loop: plan sections 2.1 to 2.5. `findings-2026-09-04-haiku-saturation.md`.
- **The synthetic fill is withdrawn** (plan section 3). Context now comes from material the task
  genuinely requires. `--fill-tokens` stays in the code for diagnostics and is not used in a
  scored cell. The suite must be **re-banded** — each task's real material size measured and
  recorded — before any GPU cell.
- **Working-margin rule, and it is new:** a cell's `num_ctx` is at least 1.6x the task's material,
  and material never exceeds ~60% of the window. At the 64k acceptance run ~57.9k of 65,536 was
  prompt and the agentic loop **collapsed to a single turn** — that cell measured less room to
  work, not more to read. Flag any trial that comes back single-turn where several were expected.

The GPU is working. The CPU-only fault that dominated 2026-09-04 is **repaired** — `cuda_v13`
reinstalled and verified by a real load (`q27-Q3_K_S`, 100% GPU, 15357 MiB, **52.7 eval tok/s**, on
the gpu-tune curve). Fault: `findings-2026-09-04-gpu-cuda-broken.md`; repair:
`ansible-slb/org/ollama-cuda-repair-2026-09-04.md`.

## Machine and harness state

| item | state |
| --- | --- |
| GPU actually resident | **done**, verified by a real load, not a version string |
| KV-probe lifecycle barrier | **done**, `--lifecycle-selftest` `ok: true` **and `drain_branch_proven: true`**; the artifact records `vram_peak_while_healthy_mib: 14611` per cycle, draining to the 1230 MiB baseline before returning |
| fifteen grid model tags with `num_ctx` + `num_gpu 66` | **done 2026-09-04, verified tag by tag** — all 15 in `ollama list` (Q2_K_L, Q3_K_S, IQ3_M at 24/32/48/64k; Q3_K_M at 24/32/48k), each read back with `ollama show --modelfile`. This row previously read **done** when only three existed. **Confirm with `ollama list` before any run rather than trusting this table.** |
| `pibench.py` records `VERDICT` per trial | **done**, verified (last line wins, absent -> None) |
| `pibench.py` records per-trial residency + gen tok/s | **done**, verified against a live model: all six calibration trials carry `ps_vram_gb`, `ps_pct_gpu`, `nvidia_smi_peak_mib` and measured gen tok/s — 100% GPU throughout, resident 11.83-14.70 GB, peaks 13,061-15,769 MiB, 53.3-59.4 tok/s, no CPU spill |
| `pibench.py --fill-tokens` | **built, accepted, and withdrawn from scored runs** by plan section 3. Kept for diagnostics. Two faults were fixed on the way and both are standing traps: prompts >32,767 chars cannot be an argv on Windows (write to a file, pass with pi's `@file`), and chars/token is **4.664** measured, not 5.95 |
| Sonnet on the current eight | 3/3 on every task — **above the 90% guard, and it must stay there** |
| GLM on the current eight | 3/3 on seven, 2/3 on t02. Second reader only, not a gate |
| Haiku x3 discrimination | **seven of eight saturated at 3/3** (g01, g02, g03, g04, t01, t02, t03; t04 at 2/3). Holds on all four conditions tried, including one-shot and both padded rows. **This is the number the desaturation loop moves.** |
| Haiku x3 prompt-defect read | **done** — t01 flagged by two of three readers, t04 by one. Tighten t01 |
| suite re-banded to real material sizes | **NOT done**, plan section 3.2, and it is a precondition for every GPU cell |
| local calibration | **partial.** g01 and t04 across three cells, one trial each, with achieved fill and full residency. Not measured: the other six tasks, and appetite/wall against a local quant. Nothing from these runs is citable as pass/fail, per rev 5.9 section 4a |

**KV cache: run on `q8_0`, the desktop's live setting, and drop the `q4_0` ritual.** Measured
2026-09-04: both 64k models at full `num_ctx` gave *identical* resident sizes under q8_0 and q4_0
(14.70 and 15.11 GB, both 100% GPU; nvidia-smi differed by 6-42 MiB). Both q8_0 cells **fit**,
falsifying `kv-probe-plan-2026-09-03.md`'s prediction. There is no capacity reason to prefer q4_0
and running on the live setting removes a conditional from the report. It is `q8_0` right now,
verified against the Windows user environment. Detail in
`findings-2026-09-04-grid-harness-gap.md`.

**Unload Ollama before any direct-server (KV probe) run.** Ollama's own model runner is *also*
named `llama-server.exe`, so the KV harness's cleanup barrier cannot tell it from its own child:
with a model resident it burns its full 180 s on a misleading "VRAM did not reach three
consecutive quiescent samples", and in the wrong ordering it would `taskkill /T /F` Ollama's
runner. `keep_alive: 0` returned the card from 15,357 MiB to 1,230 MiB in about two seconds.

## Queue

| # | run | config | why this one |
| --- | --- | --- | --- |
| 0 | **Desaturation rounds** | cloud only, no GPU | Sonnet x3 and Haiku x3 on candidate variants until Haiku is near 80% and Sonnet holds at or above 90%. Plan section 2.5. **This is the phase to protect** — nothing downstream measures anything until it lands, and it needs no card, so it can run while the GPU is busy or absent. |
| 0b | **Re-band the suite** | no GPU | Measure each surviving task's real material size, assign it a band (small ~4-8k, medium ~12-20k, large ~30-45k), record it in the manifest. Cheap, and a precondition for everything below. Plan section 3.2. |
| 0c | **Local calibration on the re-banded suite** | one quant, a few tasks | Does the task fit, does a reference solution land under the appetite ceiling, does a trial finish under 300 s, does the checker fire on a real transcript. **Calibration is not selection** — rev 5.9 section 4a, unchanged and binding. |
| 1 | **Bend-finding pass** | every quant against every band it can hold, `num_gpu 66`, `q8_0` KV, thinking medium, **1 trial** | Finds where quality against context bends before any trial is spent confirming a flat part. The run to protect if the night runs short. Cell count is not knowable until 0b lands, which is why it is not enumerated. |
| 2 | **Three-trial passes at the bend** | the bands where the curve moves, same config, 3 trials | Turns the bend into a verdict input. |
| 3 | **Confirming the winner** | best quant on the evidence, at the band it held, 3 trials on every task with fewer than three | The ranking row. |

Capacity map from `results/gpu-tune/summary.md`: Q2_K_L reaches all four steps comfortably
(13.07 GB at 96k); Q3_K_S reaches 64k at 13.70 GB; IQ3_M reaches 64k at 14.11 GB and is
**fair-weather**, so flag every IQ3_M 64k trial; Q3_K_M stops at 48k (14.16 GB, also fair-weather);
Q3_K_L is excluded by the 32k floor. Each 64k trial costs about **36 s of prefill before any work**.

## Standing run rules

- One model on the GPU at a time.
- Every local trial logs the `ollama ps` processor split, `nvidia-smi` peak memory **and measured
  gen tok/s**. Residency alone is not trusted: on Windows/WDDM an oversized allocation raises no
  OOM — it spills to system RAM while still reporting `100% GPU` and `offloaded 66/66`. A trial
  well below its quant's known resident curve is flagged thrashing.
- Configs above ~14.2 GB are fair-weather and labelled as such if run at all; idle VRAM on this
  desktop drifts 1.0-2.9 GB and reclaims without warning.
- Every pi change stays bench-local through `PI_CODING_AGENT_DIR`; nothing under `~/.pi` or the
  deployed skill roots is touched.
- A timeout is a fail and is recorded as one.
- Trials that collapse to a single turn where several were expected are flagged in the artifact.

## Log

- 2026-09-03 — file created. Queue seeded, nothing run. GPU idle; the last local activity was the
  v4-task smoke the owner stopped at 16:51, which produced no usable quant ranking.
- 2026-09-03 — control session restarted from handoff. State re-verified and matching: ansible-slb
  `d9cd381` clean in both clones, GPU idle (1.66 GB), usage 5h 28% / weekly-all 84% / Fable-scoped
  94%. One new blocker recorded against authoring only:
  `findings-2026-09-03-unity-harness.md`.
- 2026-09-04 — **cleared to run.** The worker-runtime precondition was met, acceptance-tested
  against both live harnesses with four defects found and fixed
  (`ansible-slb/org/worker-runtime-acceptance-2026-09-04.md`). The manager started from
  `handoff-2026-09-04.md` in a fresh session.
- 2026-09-04 — **GPU work stopped before it started.** The manager found FRACTAL serving on CPU
  only while proving the KV-probe lifecycle fix on real hardware. The fifteen grid tags were
  claimed here to exist; they did not — see the correction below. Authoring and the cloud gates
  continued and did not touch this queue.
- 2026-09-04 (later) — **GPU repaired and verified.** The KV-probe lifecycle barrier is fixed and
  proven on real hardware. `pibench.py` records `VERDICT` and per-trial residency, both verified
  independently. The suite is authored and both cloud gates part-run. No scored row of any kind
  has been run.
- 2026-09-04 (end of manager session) — **both cloud gates satisfied.** Sonnet 3/3 and GLM >=2/3 on
  all eight, after replacing g03 and g04 with their `cand-1` alternates on gate evidence (rule 1's
  prescribed remedy; no quant evidence existed at any point).
- 2026-09-04 (final) — **the suite is too easy, and that is the campaign's most consequential
  finding.** Both cloud gates pass, but the discrimination check shows Haiku passing 8/8 with
  **seven** tasks saturated at 3/3 [corrected the same day from an earlier "five"; see
  `findings-2026-09-04-haiku-saturation.md`]. t01 also needs its prompt tightened.
- 2026-09-04 (correction) — **"fifteen grid model tags | done" was FALSE and is retracted.** A
  direct `ollama list` showed **three** of the fifteen, two of which predated the session, so
  exactly one was produced by the `make_grid_models.sh` run. The script was correct; this was an
  unfinished run recorded as a finished one. It mattered more than a stale checkbox: five
  suffix-less base tags sit beside the cell tags and bake `num_ctx 32768` with no `num_gpu`, so a
  later session trusting the row would have had twelve cells fail outright or silently fall back to
  a base tag — precisely the mis-measurement the harness-gap page exists to prevent. **Verify by
  `ollama list`; do not trust the table.** All fifteen were built and verified individually later
  the same day, and `make_grid_models.sh` now ends by counting the tags and failing under fifteen.
- 2026-09-04 (later, superseded by the 2026-09-05 plan) — **disk padding never delivered context.**
  Holding the quant fixed, raising the cell 24k -> 64k *lowered* achieved fill: g01 4,701 -> 3,836
  and t04 10,527 -> 9,382, against 2.67x more padding written. `num_ctx` was demonstrably in effect
  (resident 11.83 -> 13.35 GB) and every trial was fully GPU-resident, so this was neither
  misconfiguration nor thrashing. Padding on disk enters the context only if the model reads it,
  and the local arm reads two or three files. Artifacts `calib-q2kl-24k.json`, `calib-q2kl-64k.json`,
  `calib-q3ks-64k.json`.
- 2026-09-04 (fix, since withdrawn) — prompt-side fill was built and accepted: instruction verbatim
  and first, extra material after, never labelled as filler. Achieved 88-98% of target depending on
  denominator — 24k cell 23,427 / 22,383 and 64k cell 57,871 / 57,857 from the model's own reported
  prompt tokens, which is 97.6/93.3 and 90.4/90.4 against the requested fill and 95.3/91.1 and
  88.3/88.3 against the cell's `num_ctx`. **Both denominators are correct and quoting one as the
  other is not.** Artifacts `accept-24k.json`, `accept-64k.json`. The mechanism works and the owner
  withdrew it on 2026-09-05 anyway: it measures tolerance for padding, which is not the question.
- 2026-09-05 — **plan of record becomes `plan-2026-09-05.md`.** Owner rulings: no freeze, ever;
  desaturate to about 80% on Haiku with Sonnet held at or above 90%, iterating on harder tasks; and
  no synthetic fill — context comes from real material. This file rewritten against it. Queue items
  0, 0b and 0c are new and are all the manager's own; nothing in this file now waits on anyone.
