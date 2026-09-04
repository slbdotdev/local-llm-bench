# RTX 5080 GPU tuning for Qwen3.8-27B (q27-*) — 2026-09-03

Goal: more tok/s, or reach 64k context, on a 16 GB RTX 5080.
All numbers from `results/gpu-tune/probe.py` (200-token generations, `/api/generate`,
`think:false`), layer residency read from the live server log, VRAM from nvidia-smi.
Raw records: `results/gpu-tune/probe.jsonl`.

## Headline

**Both goals were reached at once, and 64k was not the limit — 96k is.**

Two independent levers, and they must be combined:

1. **`options.num_gpu 66` (force full layer offload).** Ollama's scheduler is markedly
   conservative: it parks 2-7 layers on the CPU while leaving ~600 MiB of VRAM unused.
   Anything short of 66/66 costs 50-75% of generation throughput.
2. **`OLLAMA_KV_CACHE_TYPE=q4_0`.** This model keeps KV for only **16 of its 66 layers**
   (hybrid/sliding attention), so KV is cheap: 1088 MiB at 32k with q8_0, 1152 MiB at
   **64k** with q4_0. q4_0 halves KV and buys exactly the headroom that lets lever 1 fit.

q4_0 alone is not enough (the scheduler still picks 64/66), and forcing alone is not
enough (q8_0 KV overruns VRAM and thrashes). Together they are worth up to **2.3x**.

## Before / after (best fully-resident config per quant)

| quant | before (q8_0, unforced) | after (q4_0 + num_gpu 66) | gain |
|---|---|---|---|
| Q2_K_L | 32k, 100%, 57.2 / 48.6 | **96k**, 100%, 58.2 / 39.3 @94k | 3x ctx, same speed |
| Q3_K_S | 32k, 100%, 51.2 / 46.4 | **64k**, 100%, 53.5 / 41.4 @60k | 2x ctx, +4% speed |
| Q3_K_M | 32k, 90% (62/66), 22.0 / 15.3 | **48k**, 100%, 51.3 / 42.5 @44k | **2.3x tok/s** + 1.5x ctx |
| Q3_K_L | 32k, 87% (59/66), 14.6 / 12.2 | **24k**, 100%, 47.1 / 45.0 @20k | **3.2x tok/s** (ctx 32k->24k) |

`gen tok/s empty / near-full`. Every "after" row is 66/66 layers, `graph splits = 2`.

## Is 64k reachable?

Yes — on **Q2_K_L (up to 96k)** and **Q3_K_S (64k)**, both at 100% residency and full speed.
Q3_K_S @64k, q4_0, forced is the recommended quality/context pick: **53.5 tok/s empty,
41.4 tok/s at 60k fill, 1495 tok/s prompt**, 13.70 GB.
Q3_K_M reaches 48k and Q3_K_L only 24k; neither reaches 64k.

## Full measurements

### q8_0 KV (original env)
| quant | ctx | forced | layers | ps GB | gen empty | gen near-full | prompt tok/s |
|---|---|---|---|---|---|---|---|
| Q2_K_L | 32k | no | 66/66 | 12.14 | 58.8 | 49.2 @28.6k | 1553 |
| Q2_K_L | 48k | no | 66/66 | 12.74 | 59.4 | 48.0 @45k | 1462 |
| Q2_K_L | 64k | no | 66/66 | 13.35 | 58.4 | 44.5 @61k | 727 |
| Q3_K_S | 48k | no | 62/66 | 14.82 | 24.8 | 13.6 @45k | 1201 |
| Q3_K_S | 64k | no | 59/66 | 15.48 | 17.0 | 9.6 @61k | 1011 |
| Q3_K_S | 48k | **66** | 66/66 | 14.09 | **52.3** | **43.0** @45k | 1317 |
| Q3_K_S | 64k | 66 | — | — | FAIL (thrash) | — | — |
| Q3_K_M | 32k | 66 | — | — | FAIL (thrash) | — | — |

### q4_0 KV
| quant | ctx | forced | layers | ps GB | gen empty | gen near-full | prompt tok/s |
|---|---|---|---|---|---|---|---|
| Q2_K_L | 64k | no | 66/66 | 12.35 | 59.0 | 44.4 @61k | 1375 |
| Q2_K_L | 64k | 66 | 66/66 | 12.35 | 59.4 | 44.8 @60k | 1382 |
| Q2_K_L | 96k | 66 | 66/66 | 13.07 | 58.2 | 39.3 @94k | 1231 |
| Q3_K_S | 64k | no | 64/66 | 14.33 | 33.7 | 28.8 @61k | 1342 |
| Q3_K_S | 64k | **66** | 66/66 | 13.70 | **53.5** | **41.4** @60k | 1495 |
| Q3_K_M | 32k | no | 64/66 | 14.42 | 31.8 | 26.1 @28.6k | 1541 |
| Q3_K_M | 12k | 66 | 66/66 | 13.36 | 51.2 | 49.2 @8.2k | 1876 |
| Q3_K_M | 16k | 66 | 66/66 | 13.44 | 51.0 | 48.3 @12.3k | 1857 |
| Q3_K_M | 20k | 66 | 66/66 | 13.53 | 51.2 | 47.5 @16.4k | 1840 |
| Q3_K_M | 24k | 66 | 66/66 | 13.62 | 50.9 | 46.3 @20.5k | 1819 |
| Q3_K_M | 32k | 66 | 66/66 | 13.80 | 50.9 | 44.7 @28.6k | 1758 |
| Q3_K_M | 40k | 66 | 66/66 | 13.98 | 48.7 | 41.6 @36.8k | 1618 |
| Q3_K_M | **48k** | 66 | 66/66 | 14.16 | **51.3** | **42.5** @44k | 1648 |
| Q3_K_M | 64k | 66 | — | — | FAIL (thrash) | — | — |
| Q3_K_L | 8k | 66 | 66/66 | 13.90 | 49.5 | 48.7 @4.1k | 1856 |
| Q3_K_L | 12k | 66 | 66/66 | 13.98 | 49.4 | 47.8 @8.2k | 1881 |
| Q3_K_L | 16k | 66 | 66/66 | 14.07 | 49.6 | 47.0 @12.3k | 1865 |
| Q3_K_L | **24k** | 66 | 66/66 | 14.25 | **47.1** | **45.0** @20k | 1747 |
| Q3_K_L | 28k | 66 | 66/66 | 14.34 | 49.0 | 43.9 @24.6k | 1520 (unreliable, see below) |
| Q3_K_L | 32k | 66 | — | — | FAIL (thrash) | — | — |

### Prompt-fill curves (q4_0 + forced 66), gen tok/s
| fill | Q2_K_L 64k | Q3_K_S 64k | Q3_K_M 48k | Q3_K_L 24k |
|---|---|---|---|---|
| 0 | 59.4 | 53.5 | 51.3 | 47.1 |
| 8k | 57.0 | 51.4 | 49.4 | 46.2 |
| 16k | 54.5 | 49.5 | 47.8 | 45.8 |
| 20k | — | — | — | 45.0 |
| 32k | 50.4 | 45.8 | 44.4 | — |
| 44-48k | 46.9 | 43.1 | 42.5 | — |
| 60k | 44.8 | 41.4 | — | — |

Decay is gentle and roughly linear: ~25% from empty to 60k. Prompt throughput stays
1200-1900 tok/s as long as the model is fully resident.

## The fit ceiling, and why "100% GPU" can still be a lie

Fully-resident configs succeed up to about **14.4 GB of Ollama-side allocation**
(`model buffer + KV + compute buffer`) and fail from ~14.6 GB up, with the desktop
holding ~1.0-1.4 GB:

- works: Q3_K_M @48k = 13169 + 864 + 320 = 14353 MiB; Q3_K_L @24k = 14444 MiB
- fails: Q3_K_L @32k = 14628 MiB; Q3_K_M @64k = 14721 MiB; Q3_K_S @64k q8_0 = 14901 MiB

**Failure mode is not an OOM error.** On Windows/WDDM an oversized CUDA allocation
silently spills to system RAM: `/api/ps` still reports `100% GPU` and the log still says
`offloaded 66/66`, but generation collapses to unusable speeds (a 200-token request did
not finish in 800s) and host RAM drops by ~11 GB. Judge configs by measured tok/s, never
by the reported residency.

**Caveat — desktop VRAM is the confound.** Idle desktop usage drifted from 2.9 GB at the
start of the session to ~1.0 GB later; every "after" number above was taken in the
1.0-1.5 GB regime. Configs above ~14.2 GB (Q3_K_M @40k+, Q3_K_L @24k+) will thrash if the
desktop reclaims its 2.9 GB. Q3_K_L @28k proved this directly: it passed once at 49.0/43.9
and thrashed on a later identical rerun. Treat >14.2 GB configs as fair-weather only;
**Q3_K_S @64k (13.70 GB) and Q2_K_L @64k (12.35 GB) keep ~1.5-2.5 GB of margin and are the
robust picks.**

## Quality caveat

q4_0 KV is a lossier cache than q8_0; this was a speed/fit study and no quality
measurement was made at q4_0. Long-context recall is the usual casualty. Q2_K_L's 96k is
also nominal capacity, not verified comprehension.

## Alternative GGUF: IQ3_M (pulled 2026-09-03)

**Why this one.** The study showed the binding constraint is *model bytes*, so the useful
axis is quality-per-byte, not a different fine-tune. From the same bartowski repo,
**IQ3_M (12.95 GB) is smaller than Q3_K_M (13.60 GB)** — which could only reach 48k — while
imatrix quantization normally puts IQ3_M at or above Q3_K_M in quality. If the IQ dequant
penalty were small it would dominate the whole set: Q3_K_M-class quality at Q3_K_S-class
context and speed. It does.

| config | layers | ps GB | gen empty | gen @60k | prompt tok/s |
|---|---|---|---|---|---|
| IQ3_M 32k, q4_0, forced | 66/66 | 13.39 | 52.6 | 46.3 @28.6k | 1716 |
| IQ3_M **64k**, q4_0, forced | 66/66 | 14.11 | **52.8** | **41.0** | **2039 @8k** |

Curve (gen tok/s): 52.7 / 50.4 @8k / 48.7 @16k / 45.4 @32k / 42.8 @48k / 41.0 @60k.
There is **no IQ dequant penalty** — it matches Q3_K_S (53.5 / 41.4) within noise and has
the best prompt throughput of any quant tested (2039 tok/s vs 1810 for Q3_K_S).
It keeps its place; nothing was removed.

## Task-level sanity (pibench)

`--models q27-IQ3_M-64k --tasks 01_rle,05_bugfix,07_dijkstra,10_intervals --trials 1
--think medium --num-ctx 65536` -> **4/4 pass, 32 s wall/run**, 1473 out tok/run.
For reference the 32k baseline was 47 s/run (Q3_K_S), 80 s (Q3_K_M), 107 s (Q3_K_L).
Full output: `results/gpu-tune/sanity.log`, `results/gpu-tune-sanity.md`.

## Recommended configurations

| use | model | why |
|---|---|---|
| **default** | `q27-IQ3_M-64k` | best quality at 64k; 53.7 / 41.2 tok/s; 4/4 sanity |
| most VRAM margin at 64k | `q27-Q3_K_S-64k` | 13.70 GB, ~2 GB margin, 53.5 / 41.4 |
| very long context | `q27-Q2_K_L` + `num_ctx 98304`, `num_gpu 66` | 96k resident, 58.2 / 39.3 |

Two new models bake the winning settings in (`PARAMETER num_ctx 65536`,
`PARAMETER num_gpu 66`), so they need no per-request options:
`q27-IQ3_M-64k`, `q27-Q3_K_S-64k`. Verified end-to-end against the restored desktop
service: 66/66 layers, 53.7 tok/s empty, 41.2 tok/s at 61k, with no options passed.

## Ending state

- **Env changed (this one wins):** user env var `OLLAMA_KV_CACHE_TYPE` **q8_0 -> q4_0**.
  `OLLAMA_FLASH_ATTENTION=1` unchanged. Ollama desktop app stopped and restarted so it
  took effect; server.log confirms `OLLAMA_FLASH_ATTENTION:true OLLAMA_KV_CACHE_TYPE:q4_0`.
  **Revert:** set `OLLAMA_KV_CACHE_TYPE` back to `q8_0` (user env) and restart the Ollama
  app. Note the two `*-64k` models depend on q4_0; under q8_0 they would exceed VRAM and
  must be dropped to 32k.
- **Models:** the four original `q27-*` are untouched. Added `q27-IQ3_M`,
  `q27-IQ3_M-64k`, `q27-Q3_K_S-64k`, and the `hf.co/...:IQ3_M` source. Nothing removed.
- **Disk:** 83 GB -> 68 GB free (~15 GB for IQ3_M + its 0.9 GB mmproj). A 13.7 GB orphaned
  `-partial` blob from an aborted re-download was deleted, reclaiming 7 GB.
- **Leaks:** none attributable to this work. VRAM returned to 0.3-1.5 GB after every
  unload; Ollama private bytes stayed <100 MB.
- Files: `probe.py`, `probe.jsonl`, `summary.md`, `env-changes.log`, `sanity.log`,
  `serve-q4.log` / `serve-q4b.log` / `serve-q8.log`, `pull-IQ3_M.log` in `results/gpu-tune/`.

## Incidents

1. **Orphaned probe (mine, contained).** A shell timeout killed the wrapper but left
   `probe.py` (PID 34864) running against a thrashing Q3_K_L; tree-killed, VRAM recovered.
   `timeout ... | tee` masks the exit code — use `set -o pipefail` or the fail-fast branch
   never fires.
2. **Runaway `python.exe -` (NOT mine).** PID 2524, parented
   `bash -> node(pi) -> bash -> python -`, i.e. a model-authored script under another
   session's pibench run. It grew ~1 GB/min to 19 GB, driving host commit to 60.7/75.7 GB
   — roughly 15 minutes from the failure mode that took WSL down earlier. It exited on its
   own (that harness's timeout) just as it was being killed; free RAM recovered to 48.8 GB
   and commit to 38.6 GB. **Worth confirming the other session's run_tree timeout is doing
   its job**, since this is the second occurrence of the same pattern.
