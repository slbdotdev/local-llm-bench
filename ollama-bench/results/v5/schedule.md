# GPU schedule

The next GPU runs, each with a one-line reason, rewritten after every result. Rule for choosing
the next run: prefer the run whose result could flip a verdict line.

**The plan of record is `plan-2026-09-05.md`.** Read it, then **`handoff-2026-09-05-round3.md`**
— the newest handoff and the one to start from — then this file. `handoff-2026-09-05-manager.md`,
`handoff-2026-09-05.md` and `handoff-2026-09-04.md` are older and are kept for their evidence.

**Status: nothing blocks the manager.** Every precondition ever owed has been met or withdrawn.

## Where the campaign stands

- **The suite is re-banded and both bands are real.** Tiny (`round2/suite-0`, 174-770 tokens of
  material, t03 alone 6,235) at 24k, and large (`round3/suite`, eight `cand-5` tasks,
  30,018-42,570 tokens) at 64k. Same eight families in both, which is what makes the comparison
  mean anything. `authoring/bands-2026-09-05.json`.
- **Synthetic fill is withdrawn from every scored row.** No `--fill-tokens`, no `--pad-tokens`.
- **The desaturation target is met.** Haiku **38/48 = 79.2%** across both bands against a target of
  "near 80%"; Sonnet **40/40 = 100%** against a floor of 90%. Per band: tiny 87.5% / 100%, large
  70.8% / 100%. `findings-2026-09-05-large-band.md`.
- **Five task or checker defects found and fixed**, four of them by reading a tool's report of what
  it could not do rather than by looking at a rate. `findings-2026-09-05-checker-format-bias.md`,
  `findings-2026-09-05-unanswerable-tasks.md`, `decisions.md` D-R3-3 and D-R3-5.
- **`verify_candidates.py`: REF 39/39, EMPTY 39/39**, re-run after the last propagation.

## Machine and harness state

| item | state |
| --- | --- |
| GPU actually resident | **done 2026-09-05**, verified by real load on every quant in the 24k pass: `pct_gpu` 100, resident 11.83-14.00 GB, gen 50.7-58.5 tok/s, all on the known curve. Never verify by a version string. Script: `gpu_verify.py` |
| fifteen grid model tags | **done**, confirmed from the **Windows** daemon on 2026-09-05: `/api/tags` returns 21 — the 15 cell tags, 5 suffix-less base tags, the upstream repo tag. `ollama list` run from WSL returns none of them: a WSL-side `ollama serve` with zero models holds 127.0.0.1:11434 inside WSL |
| `pibench.py` per-trial residency + gen tok/s | **done**, exercised across 32 no-fill 24k trials and the 64k pass |
| `pibench.py --fill-tokens` | **withdrawn from scored runs**. Diagnostics only |
| suite re-banded | **done**; it emptied two of three bands and moved authoring onto the critical path |
| local calibration, tiny band | **done, no fill**: 8/8 tasks, wall 8.9-185.1 s against 300 s, turns 4-10, 100% GPU throughout |
| local calibration, large band | **done**: the 64k cells load at full `num_ctx`, stay 100% GPU, and the first trials come back multi-turn — not single-turn, so they are quality results and not capacity results |
| desaturation, Haiku | **three trials on each band.** 87.5% tiny, 70.8% large |
| desaturation, Sonnet guard | **three trials tiny, two large.** 100% on both |
| `cand-5` large band gated | **done.** All eight carry a Sonnet guard row and three Haiku rows |
| KV cache | `q8_0`, the machine's own setting. The `q4_0` ritual is withdrawn: identical resident sizes measured under both |
| fair-weather threshold | per **resident** size from `/api/ps`, not `nvidia-smi` whole-device. `Q2_K_L-64k` 13.35 GB (**not** fair-weather); `Q3_K_S-64k` 14.70, `Q3_K_M-48k` 14.91, `IQ3_M-64k` 15.11 (all fair-weather). `decisions.md` D-R3-9, D-R3-10 |
| GPU at end of session | **idle**, `nvidia-smi` 604 MiB / 0%. No run of this session's is live or queued |
| the bend | **found, and it is a headroom bend.** Same task t03: 35.4 s at 13.35 GB, 216.3 s at 15.11, 498.4 s at 14.70, 880.6 s at 14.91 — all 100% GPU, all 66 layers offloaded. `Q2_K_L` wins the large band outright and the ranking is the reverse of the bit ordering |

## Queue

| # | run | config | why this one |
| --- | --- | --- | --- |
| 1 | **Finish bend-finding, large band** | Q3_K_S at 64k (5 tasks left), IQ3_M at 64k (7 left) | **Partial.** `results/bend-large-64k.json` holds Q2_K_L 8/8, Q3_K_S 3/8, IQ3_M 1/8. Stopped deliberately: Q3_K_S answered g01 and g02 correctly at 1,456.9 s and 1,779.7 s, both past the 900 s verdict wall, and finishing was ~6 h with the converge held. **Re-run resumes rather than repeats.** Use `--no-tps` (the curve probe is what killed the first attempt) and `--timeout 900` |
| 2 | **Three-trial passes** | wherever the 24k-to-64k curve moves | Turns the bend into a verdict input. Choose the tasks from the 1-trial result, not from a guess |
| ~~3~~ | ~~Q3_K_M at 48k~~ | g03, t02, t03 | **Done.** `results/bend-large-48k-q3km.json`: 1/3, one confidently-wrong at the 900 s timeout and the campaign's only `visibly_failed` verdict. 880.6 s on t03 against Q2_K_L-64k's 35.4 s |
| 4 | **Confirming the winner** | best quant on the evidence, 3 trials on every task with fewer | The ranking row |
| 5 | **The 64k KV quality probe** | direct `llama-server`, q8_0 against q4_0 | `kv-probe-plan-2026-09-03.md`. Its capacity half is answered and the prediction was wrong; the quality half is still open and nothing else answers it. **Unload Ollama (`keep_alive: 0`) and confirm nvidia-smi near idle first** — Ollama's own runner is also named `llama-server.exe` |

## Standing run rules

- One model on the GPU at a time.
- Every local trial logs the `ollama ps` processor split, the `nvidia-smi` peak **and** measured
  gen tok/s. Residency alone is not trusted: on Windows/WDDM an oversized allocation spills to
  system RAM while still reporting `100% GPU` and `offloaded 66/66`.
- Configs above ~14.2 GB **resident** are fair-weather and labelled; idle VRAM drifts 1.0-2.9 GB.
  `nvidia-smi` whole-device usage is 1.8 GB higher than resident and is the wrong number for this.
- Every pi change stays bench-local through `PI_CODING_AGENT_DIR`.
- A timeout is a fail and is recorded as one.
- Trials that collapse to a single turn where several were expected are flagged in the artifact
  and reported as a **capacity** result, not a quality one.
- **Unload Ollama (`keep_alive: 0`) and confirm nvidia-smi near idle before any direct
  `llama-server` probe.** Ollama's own runner shares the image name.
- **`round.py prep` is destructive.** Pass a **comma-separated** task list when fixing one task;
  re-prepping a whole arm to fix one of its tasks destroyed about twenty finished runs on
  2026-09-05. A scoped `grade` merges; an unscoped one replaces.
- **Never poll with `pgrep -f`** — the pattern matches the waiter's own command line. Poll the
  outcome; `run_bend_large.sh` is the worked example.

## Log

- 2026-09-03 — file created. Queue seeded, nothing run.
- 2026-09-04 — GPU found serving on CPU only; repaired the same day and verified by a real load.
  Suite authored, both cloud gates satisfied, `VERDICT` and per-trial residency added to
  `pibench.py`. Prompt-side fill built and accepted, then withdrawn by the owner on 2026-09-05.
- 2026-09-04 (final) — discrimination check: Haiku 8/8 with **seven of eight tasks saturated**.
- 2026-09-05 — plan of record becomes `plan-2026-09-05.md` on three owner rulings.
- 2026-09-05 (manager session) — **the re-banding measurement emptied two of three bands**, which
  moved authoring onto the critical path. Eight large-band `cand-5` tasks authored and gated.
  Three desaturation rounds run. **Five task and checker defects found by probing and by reading
  rather than by report**, all fixed or withdrawn. Both bands calibrated with no fill. 24k
  bend-finding complete across all four quants; 64k bend-finding complete for `Q2_K_L` and partial
  for the other two, stopped deliberately at the 900 s verdict wall. The `Q3_K_M` 48k partial row
  was run. **The desaturation target was met at 79.2% Haiku / 100% Sonnet, and the bend was found:
  it is headroom, not bits.** Session ended with the card idle at 604 MiB / 0%.
