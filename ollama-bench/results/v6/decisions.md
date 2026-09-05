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

## D6-9 — the roster is not comparing like with like: four quants carry a vision projector

*20:46.* IQ3_XXS placed **spill** at 64k — 14.72 GB resident, **pct_gpu 87%**, 15.1 gen tok/s
empty and 10.3 at fill — even though its file (12.63 GB) is *smaller* than Q2_K_L's (13.08 GB),
which placed **pass** at 13.35 GB and 100% GPU. That is not a quantisation effect, so I read the
manifests. Model layer vs vision projector, `~/.ollama/models/manifests`:

| tag | model layer | projector |
| --- | ---: | ---: |
| q27-Q2_K_L-64k | 12.18 GiB | none |
| q27-Q3_K_S-64k | 12.78 GiB | none |
| q27-Q2_K-64k | 11.03 GiB | none |
| q27-IQ3_XXS-64k | 11.76 GiB | **0.86 GiB** |
| q27-IQ3_XS-64k | 12.41 GiB | **0.86 GiB** |
| q27-IQ2_M-64k | 10.13 GiB | **0.86 GiB** |
| q27-IQ3_M-64k | 12.95 GiB | **0.86 GiB** |

The four quants pulled tonight from `hf.co` carry the 927 MB vision projector the brief warned
every pull also fetches; the three older tags, baked before the projector was in the upload or
registered from a bare blob, do not. **The suite is text-only and never uses the vision tower.**
So the roster as it stands charges four quants ~0.86 GiB of VRAM the other three do not pay, on
a card whose whole margin is about 1 GiB. Comparing them is comparing manifests, not quants.

Note the projector does not explain the whole gap: at 64k, Q2_K_L's model-to-resident overhead
is 1.17 GiB while IQ3_XXS's is 2.96 and IQ3_XS's 2.97. Subtract the projector and about 0.93 GiB
of extra overhead remains on both i-quants, consistent across two different file sizes — an
i-quant compute-buffer cost, which is itself a finding worth the report.

## D6-10 — stripping the projector by blob re-bake is abandoned: `ollama create` copies the blob

*20:52.* The fix for D6-9 is to bake the context tags `FROM <blob path>` so the manifest carries
the model layer alone — the technique the brief names for Q2_K. It works, and it is unaffordable:
**`ollama create` from a file path imports a fresh copy of the blob rather than referencing it.**
One IQ3_XXS re-bake wrote a second 12.63 GB blob, and the loop I started for all four quants took
C: from **45.8 GB free to 11.3 GB** before I stopped it. Four quants would have needed ~48 GB the
disk does not have.

What I did about it, in order: stopped the driver by process group (the first `kill` had targeted
the exited `nohup` pid, so two placement cells ran on tags I was re-baking underneath — **the
IQ2_M-48k record started 20:47:05 is of an indeterminate build and is not used**); stopped the
bake loop; deleted the orphaned `COPY*` and `*-partial` blobs; and found that the *daemon*, not
the killed client, owns the import, so a client kill does not stop a copy in flight. Freed back
to 24.3 GB, then watched it fall again as the daemon finished the copy it had already started.
`ollama.exe create` is matched by **command line, never by image name** (`kill_create.ps1`),
because the daemon and its model runner share that name.

Standing rule for the rest of the night: **no `FROM <blob path>` bake unless C: has 15 GB free
and the quant it replaces is removed immediately afterwards.** Deriving a tag `FROM <another
tag>` is free — it reuses the manifest's layers — so one blob import per quant can serve every
context rung.

## D6-11 — the projector is stripped from every roster quant, and D6-10's cost estimate was wrong

*20:53.* Two corrections to D6-10, both measured.

**One: the blob import happens once per quant, not once per tag.** Ollama content-hashes the
imported file, so `q27-IQ3_XXS-48k` and `q27-IQ3_XXS-64k`, baked from the same blob path in
succession, ended up sharing the single imported blob `sha256-b6e8a5c9…`. The economics are
therefore: one transient copy per quant, and after `ollama rm` of the `hf.co` tag the original
blob **and** its projector are freed, so the steady-state disk cost is about zero. Deriving the
remaining rungs `FROM` the projector-free tag is free. The rule stands as written in D6-10 —
15 GB of headroom before an import, removal straight after — but the campaign can afford it.

**Two: the projector was worth measuring, and the A/B is the sharpest number of the night.**
Same quant, same rung, same instrument, 90 seconds apart:

| IQ3_XXS @ 64k | resident | pct_gpu | gen tok/s empty | gen tok/s @58.4k fill | smi peak | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| with 0.86 GiB projector | 14.72 GB | 87% | 15.05 | **10.28** | 15,332 MiB | spill |
| projector stripped | 14.31 GB | 93% | 33.67 | **28.97** | 14,968 MiB | marginal |

**0.41 GB of resident bought a 2.8x generation speedup**, because the cell sits exactly on the
cliff the v5 large-band finding describes: below the line the work runs at conversational speed,
above it the same work takes six to twenty-five times longer while still reporting 100% GPU and
every layer offloaded. Note the resident saving (0.41 GB) is half the projector's file size
(0.86 GiB), so Ollama is not simply loading the whole tower into VRAM — but on a card with about
1 GB of margin, 0.41 GB is the difference between two verdicts.

Decision: **every roster quant runs projector-free**, one import at a time, so the campaign
compares quantisations rather than manifests. The projector-carrying records already in
`placement.json` are kept — they are the A/B — and every record from 20:51 onward carries
`has_projector` and `manifest_model_gib` fields, so no record's build is ever in doubt again.

Decision: **IQ3_XXS does not carry 64k even projector-free.** 14.31 GB is over the 14.2 line,
93% GPU means about 0.95 GB is still on the CPU, and 28.97 tok/s is under the 35 tok/s gate.
It is placed 64k **marginal**, and its real rung is 48k, to be measured.
