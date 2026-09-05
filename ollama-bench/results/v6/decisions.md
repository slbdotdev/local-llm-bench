# v6 decisions log

*Every decision the v6 manager session takes, recorded as it is taken (plan section 10).
Nothing in this campaign is gated on the owner. Times are the host's local clock, which
reports `2026-09-04` while every campaign document is dated 2026-09-05; the campaign date
is used in filenames and the wall-clock time in these entries.*

## D6-1 — the working-margin rule is applied strictly, so the 64k large band is six tasks

*20:33.* Plan section 6C says the v5 working-margin rule stands: a cell's `num_ctx` must be
at least 1.6x the task's material **and** the material must never exceed about 60% of the
window (v5 `plan-2026-09-05.md` section 3.3). Applied to the round3 large-band material:

| task | large material (tok) | 1.6x | fits 48k (49152) | fits 64k (65536) |
| --- | ---: | ---: | :---: | :---: |
| g01 | 30,001 | 48,001 | yes | yes |
| g03 | 30,018 | 48,028 | yes | yes |
| t03 | 30,604 | 48,966 | yes | yes |
| t02 | 31,102 | 49,763 | no | yes |
| g02 | 32,476 | 51,961 | no | yes |
| t01 | 36,643 | 58,628 | no | yes |
| t04 | 41,138 | 65,820 | no | **no** |
| g04 | 42,570 | 68,112 | no | **no** |

So a 48k cell runs **g01, g03, t03** (the three the plan names) and a 64k cell runs **six**,
not eight. v5 ran all eight at 64k, which was v5 not applying its own rule: g04 is 65% of a
64k window and t04 is 63%, both over the 60% ceiling that exists because the agentic loop
collapsed to a single turn at 57.9k of 65,536.

Decision: apply the rule strictly. It costs nothing in comparability, because plan section
0.4 already supersedes every v5 local row (different pi harness), and it buys two tasks per
quant per band of overnight budget. **g04 and t04 re-enter at 96k and above** (1.6x42,570 =
68,112), which makes phase E's stretch cells the only place the two hardest tasks are scored
— worth saying in the report rather than hiding.

## D6-2 — resident GB is `/api/ps` `size` divided by 2^30

*20:34.* The 14.2 GB fair-weather line and the v5 measured table (Q2_K_L-64k 13.35,
Q3_K_S-64k 14.70, IQ3_M-64k 15.11, Q3_K_M-48k 14.91) are `pibench.py`'s `ps_size_gb`, which
is `size / 2**30` — GiB. `reserve.md`'s "file-to-resident offset" column mixes units (HF file
sizes are decimal GB), so that offset is not usable arithmetic; the placement measurement is.
Every v6 resident figure is `size / 2**30`, the same field v5 measured, against the same
14.2 line. The card is 16,303 MiB = 15.92 GiB.

## D6-3 — GPU verified by real load before the first scored trial

*20:33.* `results/v5/gpu_verify.py q27-Q2_K_L-24k` through the Windows interpreter:
**58.35 gen tok/s**, 12.70 GB resident, **pct_gpu 100%**, `nvidia-smi` 13,393 MiB. Q2_K_L's
known curve is 58 tok/s empty, so the card is on its curve and CUDA is not in the state
`ansible-slb:org/ollama-cuda-repair-2026-09-04.md` describes. Verified by load, never by a
version string. Daemon is Ollama 0.33.3 on Windows with `OLLAMA_FLASH_ATTENTION=1` and
`OLLAMA_KV_CACHE_TYPE=q8_0`, read from the Windows environment, which is the machine's own
setting and not a lever in this campaign.

## D6-4 — the pi-harness hook is proven in both directions before any scored row

*20:38.* Plan section 0.4 requires the proof, because a row that ran without the extension
looks normal.

- **Negative control**, `PIBENCH_PI_ARGS='-e .../NO-SUCH-EXTENSION.ts'`, artifact
  `results/v6-hookproof-bad.json`: the trial died in **0.4 s**, rc 1, stderr
  `Error: Failed to load extension "C:\Users\slb\.claude\skills\pi-run\scripts\NO-SUCH-EXTENSION.ts"`.
  So `PIBENCH_PI_ARGS` crosses `WSLENV` into the Windows process and reaches pi's argv.
- **Positive control**, the real path, artifact `results/v6-hookproof-good.json`: g01 tiny
  band PASS, score 1.0, `correct`, 183.9 s, 12 turns, 11 tool calls, 9,890 out tokens,
  11.83 GB resident, 100% GPU. 11.83 GB is v5's measured Q2_K_L-24k resident to the
  hundredth, so the placement instrument agrees with v5's.

Both exports go into every pibench launch of this session:
`PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'` and
`WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"`.

## D6-5 — Q2_K_L at 64k is placed first, as the calibration cell

*20:41.* Plan section 6A orders phase 0 most-informative-first and puts Q2_K_L last, from 96k
up. Taking one extra cell out of order: **Q2_K_L at 64k, measured first.** It is the proven
cell, v5 measured it at 13.35 GB resident, and plan section 5 asks every quant's summary row
for "gen tok/s at 64k for comparability" — which is meaningless without the reference quant's
own 64k figure taken on the same instrument on the same night. Five minutes, and it makes
every later placement number readable.

## D6-6 — context tags baked for the whole phase A ladder up front

*20:40.* A tag is a manifest over an existing blob, so baking costs no disk and no GPU.
Baked before phase A: `q27-IQ3_XXS-64k`, `q27-IQ3_XS-64k`, `q27-IQ2_M-{48k,64k,96k,128k,192k,256k}`,
`q27-Q2_K-{48k,64k}`, `q27-Q2_K_L-{96k,128k}`, `q27-IQ3_M-48k`. `q27-Q3_K_S-48k` and
`q27-Q2_K_L-64k` already existed. IQ2_M/IQ3_XS/IQ3_XXS bake from the `hf.co` tags,
Q2_K from the blob-registered `q27-Q2_K` base, IQ3_M's 48k from `q27-IQ3_M` — the three
`FROM` sources the plan and the brief name, because `make_model.sh` hard-codes bartowski and
the removed IQ3_M sub-tags pointed at a stale upload. `results/v6/bake.sh` is the worked form:
the Modelfile is written where the Windows daemon can read it and handed over as a Windows
path, since a WSL path is invisible to that daemon.

## D6-7 — both task bands run in the quant's own cell, not the tiny band at a fixed 24k

*20:52.* Plan section 1 asks for each quant's "quality on both v5 bands **there**", where
*there* is the largest context it carries; sections 6C and 6D say "both bands at its top rung
up to 64k"; and the brief's tag scheme `v6-<quant>-<ctx>-<band>` carries context and band as
separate axes. So the tiny-band tasks run in the same cell as the large-band ones — the
quant's top rung capped at 64k — rather than in a separate 24k cell.

Two reasons beyond the wording. It isolates the variable: a tiny row taken at 24k and a large
row at 64k differ in both material and window, and the campaign is about the window. And it
halves the model loads, because one cell serves both bands. The tiny material (174-770 tokens,
t03 6,235) clears the working-margin rule at every rung, so nothing is excluded by moving it up.

The cost, stated rather than hidden: v6 tiny rows are **not** comparable to v5's 24k tiny rows,
which ran in a 24k window. Plan section 0.4 already supersedes every v5 local row for a
different reason (the pi harness), so this adds no new incomparability.

## D6-8 — phases B, C and D share one artifact per cell and resume into it

*20:53.* `pibench.py` keys completed work by (task, trial) inside `results/<tag>.json`, so the
sentinel pass (phase B: `--tasks g03,t03 --trials 1`), the one-trial row (phase C: the full
band, `--trials 1`) and the verdict row (phase D: `--trials 3`) all write the same tag and each
does only the work the previous one did not. No trial is ever run twice and no phase discards
the one before it. `runcell.sh` is the single entry point for every scored cell and carries
both harness exports, so no row can be launched without the extension.
