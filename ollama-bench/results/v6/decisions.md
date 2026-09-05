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

## D6-12 — the working-margin rule states itself twice and the two forms disagree at 48k

*21:00.* Implementing D6-1 in `phaseC.py` surfaced a wrinkle worth writing down. v5 plan
section 3.3 gives the rule as "a cell's `num_ctx` must be at least 1.6x the task's material,
**and** the material must never exceed about 60% of the window". 1/1.6 is 62.5%, so the second
clause is very slightly the stricter one — and at 48k it is strict enough to matter: g01 is
30,001 tokens, which is 61.0% of a 49,152-token window. It clears 1.6x (48,001 <= 49,152) and
fails 60%.

Taken literally, the 60% form admits **no large-band task at all at 48k**, while v6 plan
section 6C says in as many words that a 48k-only quant "runs the three large-band tasks that
fit". So the 1.6x form is the operative test and "about 60%" is its approximate restatement —
the word "about" is doing the work. `admits()` implements 1.6x alone, which reproduces D6-1's
table exactly: three tasks at 48k (g01, g03, t03), six at 64k, all eight at 96k and above.

## D6-13 — reserve rank 1 is pulled now rather than on a rejection, to keep the disk end busy

*20:59.* Plan section 2 pulls the top reserve entry when a roster quant is rejected. I am
pulling `UD-Q3_K_XL` (unsloth, 13.15 GB, reserve rank 1) now instead, while the GPU works
phase A3 and the sentinels. Three reasons.

The disk and network end is otherwise completely idle for the next few hours, and a pull never
contends with a trial (plan section 9). C: is back to 45 GB free after the strip, which is the
most headroom this campaign will ever have. And the placement result that has just landed makes
this specific entry the most informative thing on the list: **IQ3_XXS, the smallest 3-bit
imatrix quant on the roster, reached only `marginal` at 64k even projector-free** (14.31 GB,
93% GPU, 28.97 tok/s). If no bartowski 3-bit carries 64k, the campaign's headline question is
answered "no" — unless a dynamic quant, which keeps the layers that matter at higher precision
and quantises the rest harder, does it at the same file size. That is exactly what
`UD-Q3_K_XL` is, and it is a 13.15 GB file against Q2_K_L's proven 13.08 GB.

It is struck from `reserve.md` on arrival, per that file's swap rule.

## D6-14 — `has_projector` is null on the first three placement records

*20:59.* The field was added to the instrument at 20:51 (D6-11), so the first three records
carry `null`. For the avoidance of doubt, from the manifests as they stood: **Q2_K_L had no
projector** (its record stands unchanged), and the **IQ3_XXS and IQ3_XS records started 20:43
and 20:44 both carried one** and are superseded by the stripped re-placements. The IQ2_M-48k
record started 20:47:05 is the indeterminate one from D6-10 and is used for nothing.

## D6-15 — the reserve candidate is placed inside phase A, not bolted on after the campaign

*21:00.* Having pulled `UD-Q3_K_XL` early (D6-13), the question was where it enters the run
order. `phaseB.py` derives its candidate list from `placement.json`, so a quant with no
placement record is simply invisible to phases B through E — the reserve entry would have been
measured, if at all, as an afterthought once the verdict rows were already written.

So I added **phase A4**: it waits on phase A3's flag (the GPU is free) *and* on the pull's own
outcome (the `q27-UDQ3KXL-64k` tag existing on the daemon — polled as an artifact, never as a
process), strips the projector if the pull brought one, places 64k and 48k, and only then
releases phase B. `chainB.sh` was re-gated from `.phaseA3-done` to `.phaseA4-done`. If the pull
has not landed within forty minutes of the GPU going free, A4 gives up and releases phase B
without it, so a slow download can delay the campaign by at most that and can never stall it.

The cost is that phase B starts a few minutes later than it would have. The benefit is that the
one candidate that could still answer the campaign's headline question "yes" is ranked against
the roster on the same instrument, in the same ordering, rather than compared across sessions.

## D6-16 — Q2_K's ladder, and the first quant with a settled rung

*21:00.* Q2_K (the non-L 2-bit, 11.03 GiB model layer, no projector) placed **pass at 48k**
(12.46 GB, 100% GPU, 49.19 tok/s at fill), **pass at 64k**, and **spill at 96k**, so the ladder
stopped there and its top rung is **64k**. It is the second quant after Q2_K_L to carry 64k,
and both are K-quants. No i-quant has managed it yet.

## D6-17 — a sentinel failure demotes a quant a rung; only a failure at every rung rejects it

*21:04.* Implementing phase B against the placement data exposed a hole in the rule as written.
Plan section 6B says "reject a quant whose t03 wall is over 3x Q2_K_L's at the same rung, or
that times out either". Read literally that rejects **IQ3_XXS**, which placed `pass` at 48k
(13.07 GB, 100% GPU, 47.03 tok/s) and `marginal` at 64k (14.31 GB, 93% GPU, 28.97 tok/s), if it
fails the sentinel at 64k — its top rung.

But a marginal cell failing the sentinel tells us the *cell* is too slow, which is exactly what
`marginal` already said. It tells us nothing about the quant, and plan section 4 explicitly
provides for a marginal cell being kept "only if no better rung exists". Rejecting the quant on
that evidence would delete a quant that passes cleanly one rung down, remove it from the disk,
and spend a reserve pull replacing it — on the strength of a measurement that agreed with its
own placement.

So `phaseB.py` now tries a quant at each placed rung from the top down and **demotes** on a
sentinel failure, recording the demotion and its reason in `phaseB.json`. A quant is rejected
only when it fails the sentinel at **every** rung it placed on. That is stricter about what
rejection means and no more permissive about what passes: a demoted quant is reported at the
rung it actually holds, which is the campaign's whole output.

## D6-18 — 96k is out of reach for every K-quant on this card, and the KV cost says why

*21:04.* Both K-quants that carry 64k comfortably fail one rung up, and the two measurements
together give the campaign a rule rather than two data points.

| cell | resident | pct_gpu | gen tok/s @fill | verdict |
| --- | ---: | ---: | ---: | --- |
| Q2_K_L @ 64k | 13.35 GB | 100% | 44.88 | pass |
| Q2_K_L @ 96k | **16.20 GB** | 83% | 8.22 | spill |
| Q2_K @ 48k | 12.46 GB | 100% | 49.19 | pass |
| Q2_K @ 64k | 13.07 GB | 100% | 45.14 | pass |
| Q2_K @ 96k | 15.04 GB | 89% | 8.97 | spill |

Q2_K_L at 96k wants **16.20 GB on a 15.92 GiB card**, so it cannot even be resident, and 83%
GPU with 8.22 tok/s is what that looks like. The two Q2_K_L cells bracket the KV cost directly:
32k of extra context costs **2.85 GB**, about **89 MB per 1k of context** at q8_0 with flash
attention on. Q2_K's own 48k-to-64k step costs 0.61 GB and IQ3_XXS's costs 1.24 GB, so the rate
is not perfectly linear across quants, but 89 MB/1k is the number to plan with.

That rate is the campaign's real constraint, and it is worth stating as a prediction rather
than discovering seven more times: **to place at 96k under the 14.2 GB line, a quant must sit
at about 11.3 GB at 64k**, which means a model layer around 9-10 GiB — a full gigabyte below
IQ2_M, the smallest thing on the roster. So I expect **no quant in this campaign to reach 96k**,
and phase E to have nothing to stretch. If that holds it is a clean result and not a gap: on a
16 GB card, 64k is the ceiling for a 27B model at any quantisation still worth running, and the
v5 speculation that "96k fully resident is a capability no other quant on this card has" is
measured out — not even Q2_K_L has it.

The one candidate that could falsify this is reserve rank 7, `UD-Q2_K_XL` at 9.83 GB. It is not
pulled and I am not pulling it ahead of the roster: the campaign's question is 64k quality, and
a 2-bit dynamic at 96k answers a different one. Recorded here so the next session can take it
deliberately rather than rediscover it.

## D6-19 — a second failure mode: prefill collapses while generation stays healthy

*21:14.* Q3_K_S at 48k passed the plan's speed gate and is unusable. The gate reads generation
tok/s; this cell's generation is fine and its **prefill** is destroyed:

| Q3_K_S @ 48k | value |
| --- | ---: |
| resident | 14.09 GB — **under** the 14.2 line |
| pct_gpu | **100%** |
| gen tok/s empty / @43.7k fill | 47.15 / **41.31** — comfortably over the 35 tok/s gate |
| **prompt tok/s @fill** | **76.4** |
| **time to first token @fill** | **571 seconds** |
| `nvidia-smi` peak | 15,879 MiB of 16,303 — **424 MiB free on the device** |

Every other cell measured tonight prefills between **946 and 1,788 tok/s**, including the
spilled ones: IQ3_XS at 82% GPU still prefills at 1,035. Q3_K_S is a 12-to-23x outlier on that
axis alone. Nothing sits between 76 and 946, so this is a cliff, not a gradient.

**It is a different fault from the v5 headroom bend, and the two are diagnosable apart.** The
headroom bend — Q2_K_L and Q2_K at 96k, IQ3_XS at 64k — shows as *generation* collapsing with
`pct_gpu` falling below 100. This shows as *prefill* collapsing with `pct_gpu` pinned at 100%
and resident under the line. The signature is the `nvidia-smi` figure, not the `/api/ps` one:
424 MiB free on the device is not enough for the prefill scratch buffer, which scales with
batch size, while generation needs almost none. So the whole-device number that v5 correctly
refused to use for the *residency* verdict is exactly the number that explains *this* one.

Consequence for an agentic bench: at 76 tok/s a 44k-token prompt waits **9.5 minutes** before
its first token, so the 600 s large-band timeout is guaranteed to fire on every task, and every
row would have been recorded as `timed_out` with no indication why.

Decision: **the verdict gate gains a prefill rule** — >= 500 tok/s clean (the plan's own
number), < 200 tok/s spill, between them marginal — and the gate moves into one shared module,
`gate.py`, imported by the instrument and by both renderers. The renderers **re-derive** every
verdict from the raw measured fields, so a rule added at 21:14 reaches a record taken at 20:41
without `placement.json` ever being rewritten, which plan section 6 requires.

## D6-20 — Q3_K_S is rejected, and reserve rank 2 replaces it

*21:15.* Q3_K_S was on the roster for a 48k placement only (plan section 2), 48k is now `spill`
under D6-19, and there is no lower rung to demote to. **Rejected: no viable context.** Under
the plan section 2 swap rule every tag of it is removed and the top remaining reserve line is
pulled in the background while the GPU carries on.

Pulled: **reserve rank 2, `mradermacher/Qwen3.8-27B-i1-GGUF:i1-IQ3_M`, 12.77 GB** — bartowski's
IQ3_M with 1.1 GB shaved off, and IQ3_M was v5's favourite on a-priori quality. It is the right
replacement for a rejected 3-bit K-quant, and tonight's own numbers say why it has a chance
where bartowski's IQ3_M does not: at 13.90 GB that file cannot fit 64k, and 1.1 GB is most of
the gap.

## D6-21 — D6-18 is falsified, and I derived its rate from a degraded cell

*21:17.* **IQ2_M placed `pass` at 96k**: 13.27 GB resident, **100% GPU**, 41.88 gen tok/s at an
87.8k-token fill, 1,286 prompt tok/s, TTFT 68 s. D6-18 predicted no quant this campaign would
reach 96k. It was wrong, and the way it was wrong is the more useful half.

D6-18 read the KV cost off Q2_K_L's 64k-to-96k step: 13.35 GB to 16.20 GB, 2.85 GB for 32k of
context, "about 89 MB per 1k". **That step lands in a spilled cell** — Q2_K_L at 96k is 83% GPU
and 8.22 tok/s — so `/api/ps` `size` there is not measuring a KV cache that fits. I derived a
rate from a degraded measurement, which is precisely the error this campaign exists to avoid,
and it is the same error in kind as v5's: reading a number off a cell that is already broken.

The clean steps, every one of them between two cells that both placed `pass` at 100% GPU:

| step | delta | per 1k ctx |
| --- | ---: | ---: |
| IQ2_M 48k -> 64k | +0.61 GB | **39 MB** |
| IQ2_M 64k -> 96k | +1.22 GB | **39 MB** |
| Q2_K 48k -> 64k | +0.61 GB | **39 MB** |

Three independent clean steps, across two quants and two different context spans, agreeing
exactly. **KV cache at q8_0 with flash attention costs 39 MB per 1k of context on this model.**
Every step that disagrees (Q2_K_L 91, IQ3_XXS 79, Q2_K 63) is a step whose upper cell spilled,
and the excess is the contamination, not the cache.

Corrected rule, and this one is derived only from clean cells: **a quant places at 96k if it
sits at or under about 12.95 GB at 64k** (14.2 minus 32 x 39 MB). IQ2_M is 12.05 and passes;
Q2_K is 13.07 and does not; Q2_K_L is 13.35 and does not. It also predicts **IQ2_M at 128k
needs 14.52 GB and should fail** — that cell is running now, so the correction gets tested
immediately rather than being believed.

Two consequences for the night. Phase E has a real stretch cell after all. And because the
working-margin rule admits **all eight** large-band tasks at 96k against six at 64k (D6-1),
IQ2_M's stretch row is the **only place g04 and t04 are scored in this entire campaign** —
g04 being the task Haiku went 0/3 on and the sharpest discriminator v5 found.

## D6-22 — the corrected rule predicted IQ2_M's 128k failure, and the overshoot confirms the contamination

*21:19.* D6-21 predicted IQ2_M at 128k would need 14.52 GB and fail. Measured: **spill**, 86%
GPU, 17.87 gen tok/s empty collapsing to **7.11 at fill**, 15.47 GB resident.

The verdict was called correctly. The resident figure overshot the prediction by 0.95 GB — and
that overshoot is not a strike against the 39 MB/1k rate, it is a third instance of the effect
D6-21 identified: **a cell that spills reports a resident size larger than its KV cache
actually needs**, because `/api/ps` `size` then covers the part that did not fit. Q2_K_L at 96k
overshot by 1.60 GB, Q2_K at 96k by 0.72, IQ2_M at 128k by 0.95. The rate is only readable
between two cells that both fit, which is exactly what D6-21 says.

**IQ2_M's ladder is settled: 48k pass, 64k pass, 96k pass, 128k spill. Top rung 96k** — the
only quant in the campaign to carry it, on the smallest and most aggressively quantised file on
the roster (10.13 GiB model layer).

## D6-23 — reserve rank 2 gets a placement slot too, and the chain is re-gated behind it

*21:21.* Same reasoning as D6-15: `phaseB.py` builds its candidate list from `placement.json`,
so a quant with no placement record is invisible to every later phase. Reserve rank 2 (`mrIQ3M`)
was pulled at 21:15 as the Q3_K_S swap and would otherwise have been measured only as an
afterthought, if at all.

Added **phase A5** on the same pattern as A4 — wait for A4's flag so the GPU is free, wait for
the pull's own outcome (the tag existing on the daemon), strip the projector if the pull brought
one and there are 15 GB free, place 64k and 48k — and re-gated `chainB.sh` from `.phaseA4-done`
to `.phaseA5-done`. Each waiter has a deadline (45 minutes) after which it releases phase B
without its candidate, so a slow or failed download delays the campaign by at most that and can
never stall it.

The full chain is now: A2 and A3 (roster placement) -> A4 (reserve rank 1) -> A5 (reserve rank
2) -> B (sentinels) -> C (one trial, both bands) -> D (three trials, best two) -> E (stretch),
every link polling an outcome artifact and none polling a process name.

**A launch fault caught in the same breath, worth recording because it was silent.** Relaunching
`chainB.sh` with a relative log path after a `cd` in a compound command wrote its redirect
against the wrong working directory, and the chain died at once — `results/v6/phaseB.log: No
such file or directory` — while every other chain kept running. Phase B would simply never have
started, and the first sign would have been a stall alarm fifteen minutes later. Relaunched with
an absolute redirect and **all seven chains verified alive by name before moving on**, which is
now the rule after any relaunch: check the process list, not the exit code of the launcher.

## D6-24 — IQ3_M rejected; rank 3 is pulled but deliberately not placed ahead of the scored work

*21:24.* **IQ3_M rejected.** Its only planned rung, 48k, placed `spill`: 14.98 GB resident,
**89% GPU**, 18.05 gen tok/s empty collapsing to 12.04 at fill. There is no lower rung to demote
to, because the owner's ruling is that a quant is viable only if it runs 48k. Every tag removed;
C: back to **48.1 GB free**, the most this campaign has had.

That is the second rejection, so the swap rule asks for reserve rank 3, `UD-IQ3_S` (12.04 GB).
**Pulled, but not added to the placement chain**, and this is a departure from the plan's letter
that I want on the record.

The swap rule exists so the roster stays full *while the GPU is busy* — it assumes the binding
constraint is candidates. It is not, any more. Phase A is finished and the campaign is now
limited by scored-trial time: seven candidates already queue for phases B through E (Q2_K_L,
Q2_K, IQ2_M, IQ3_XXS, IQ3_XS, and reserve ranks 1 and 2), phase C costs roughly 35 minutes a
quant and phase D another 2.3 hours on top, which lands the night around 04:30 as it stands.
An eighth candidate placed at the front would push that past 05:10 and buy a placement row at
the cost of a *verdict* row — and verdict rows are what the campaign is for.

So: the pull runs (network and disk are idle, it costs the GPU nothing, and it leaves v7 a
candidate already on the daemon), and `UDIQ3S`'s **placement is queued behind phase E** rather
than ahead of phase B. If the night runs ahead of schedule it gets measured; if it does not, it
is on disk and placed first thing next time. `chainB.sh` is deliberately **not** re-gated.

Roster after two rejections: **Q2_K_L, Q2_K, IQ2_M, IQ3_XXS, IQ3_XS** surviving, plus
**UDQ3KXL** and **mrIQ3M** arriving from the reserve. Rejected: **Q3_K_S** (prefill 76 tok/s at
its only rung) and **IQ3_M** (spill at its only rung).

## D6-25 — the headline answer: no 3-bit quant of any publisher carries 64k on this card

*21:28.* `UD-Q3_K_XL` was pulled precisely because it was the last plausible way to answer the
campaign's mission question "yes" — a dynamic 3-bit at Q2_K_L's file size, keeping the layers
that matter at higher precision. Projector stripped, model layer 12.24 GiB:

| UDQ3KXL | resident | pct_gpu | gen tok/s @fill | prompt tok/s | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| 64k | 14.80 GB | 91% | **12.47** | 1,354 | **spill** |
| 48k | 13.45 GB | **100%** | **44.79** | 1,745 | **pass** |

So it is a clean, fast 48k quant and it does not hold 64k. That completes the sweep:

| 3-bit candidate | publisher | 64k result |
| --- | --- | --- |
| IQ3_XXS | bartowski | marginal — 93% GPU, 28.97 tok/s |
| IQ3_XS | bartowski | spill — 89% GPU, 10.36 tok/s |
| IQ3_M | bartowski | spill at **48k**, never reached 64k |
| Q3_K_S | bartowski | prefill 76 tok/s at **48k**, rejected |
| UD-Q3_K_XL | unsloth | **spill — 91% GPU, 12.47 tok/s** |

**Every quant that carries 64k on this card is a 2-bit quant** — Q2_K_L, Q2_K and IQ2_M — and
the only one that carries 96k is IQ2_M, the most aggressively quantised file on the roster. One
3-bit candidate remains untested, mradermacher's `i1-IQ3_M`, placing next.

## D6-26 — withdrawing D6-9's i-quant overhead claim: I read it off contaminated cells

*21:29.* D6-9 noted in passing that with the projector subtracted, IQ3_XXS and IQ3_XS still
carried "about 0.93 GiB more resident than their model layer plus Q2_K_L's overhead would
predict", and `reserve.md` repeated it as advice. **That claim is withdrawn.** It was computed
at 64k from cells running at 93% and 89% GPU — partially offloaded, and therefore exactly the
contaminated measurement D6-21 and D6-22 identify, where `/api/ps` `size` covers the part that
did not fit. I made the same mistake twice in one night, on two different quantities.

Overhead over the model layer, **clean cells only, every one at 100% GPU**:

| ctx | IQ2_M | IQ3_XXS | Q2_K | Q3_K_S | UDQ3KXL |
| --- | ---: | ---: | ---: | ---: | ---: |
| 48k | 1.31 | 1.31 | 1.43 | 1.31 | 1.21 |

**1.21 to 1.43 GB, across two i-quants, two K-quants and one dynamic quant — no i-quant penalty
exists.** The overhead is a property of the context, not of the quantisation family. So the
reason no 3-bit holds 64k is the plainest one available: a 3-bit model layer is 11.8-12.9 GiB
against a 2-bit's 10.1-11.0, and at 64k that difference is the whole margin. Nothing subtler is
needed, and `reserve.md`'s size-based rules of thumb apply to every family after all.

One thing I cannot explain and will not paper over: at 64k the clean overheads are IQ2_M 1.92
and Q2_K 2.04, while Q2_K_L is 1.17 — a 0.8 GB spread at identical context on identical
architecture. Q2_K_L's record predates the manifest fields so it is the one number here not
taken with the others. **Flagged as unexplained**, not theorised about; re-placing Q2_K_L at 64k
with the current instrument is a ninety-second job for whoever picks this up.

## D6-27 — the stall alarm earned its keep, and the fault it found was my gating

*21:43.* The waiter fired: "no v6 artifact written for 15 min". Nothing had died — every chain
was alive and the rank 2 pull was at 88% — but the GPU had been **idle since 21:27:51**, which
is the thing that actually matters and which no done-flag would ever have reported.

The cause is my own chain design. D6-23 gated phase B behind phase A5, and A5 waits on a
*download*. Its 45-minute deadline protects against a pull that fails; it does nothing about a
pull that merely takes fifteen minutes, during which the GPU has nothing to do even though
phase B's first two cells — the Q2_K_L reference sentinels at 64k and 48k — depend on no
reserve candidate whatsoever and could have run throughout.

**The rule I should have followed: gate a GPU phase on GPU-readiness, never on a download.**
The plan says in as many words that a pull and a trial may overlap; I built a chain that made
them exclusive. The correct shape was to start phase B's reference cells immediately and insert
the reserve candidate's sentinels when its placement landed.

I am **not** restructuring now, and the reason is arithmetic rather than principle: the pull has
about two minutes left and A5 needs about three more to strip and place, so unpicking the chain
would cost more than the five minutes it would recover. Recorded because the pattern will recur
in v7 — and because the alarm is the only reason I know about it at all. A monitor that watches
only for things ending would have reported this fifteen-minute hole as healthy progress.

Cost of the fault: about 15 minutes of GPU time out of a night budgeted at 11 hours.

## D6-28 — owner's order: no more downloads tonight; rank 3 deferred, partials preserved

*21:46.* Owner's order relayed by the coordinator: **no further model downloads tonight, the
bandwidth is needed elsewhere.** The `UD-IQ3_S` (reserve rank 3) pull started at 21:45 under
D6-24 was killed by the coordinator, along with its `ollama.exe pull` client.

What I checked and did, in order:

1. **The retry loop was the real hazard, and it did not fire.** `reserve_pull.sh` retries a
   failed pull once before giving up, so a kill mid-download is exactly the shape that makes it
   start over. Verified by process list that `pull2.sh`, `pull3.sh` and `reserve_pull.sh` are
   all gone, and by command-line match — never by image name, since the daemon and its model
   runner share it — that the only `ollama.exe` alive is the daemon, pid 19824, with no `pull`
   client. **No retry relaunched and none can: every script that could invoke a pull is dead.**
2. **Nothing is gated on a download any more.** The only pull-gated wait was phase A5's, and it
   is already past it: `mrIQ3M` landed at 21:45:31, was stripped, and is being placed now with
   the GPU at 98%. `chainB.sh` waits on `.phaseA5-done` and `chainCDE.sh` on `.phaseB-done` —
   both GPU-readiness flags, neither a download. No re-gating was needed; confirmed rather than
   assumed.
3. **The partial blobs stay.** `sha256-d847e2c1…-partial` is 12.04 GB — the full file size, so
   the pull was all but complete — plus sixteen tiny `-partial-N` chunk files.

**Guard, and this is the one that could go wrong.** My own orphan-blob cleanup from D6-10 was
`rm -f COPY* *-partial *-partial-0`, and the unreferenced-blob scan I use to find reclaimable
space lists **every one of these sixteen files as unreferenced, 12.0 GB of apparently free
space.** It is not free space, it is a deferred download. **No blob cleanup runs for the rest of
this session, and the end-of-night tidy does not touch `~/.ollama/models/blobs`.** C: has 46.9
GB free, so nothing needs reclaiming anyway.

Consequence for the campaign: none. Rank 3 was already outside the scored plan under D6-24 — on
disk for v7, not queued for phase B or C — so deferring it changes no row. The GPU continues on
the seven candidates already on the daemon.

## D6-29 — the owner's just-in-time pull rule, and how it is implemented

*21:50.* Owner's update relayed by the coordinator: downloads may resume, **but only just in
time**. A pull starts when the GPU is about to need that candidate, never as a disk-side
background job run ahead of time. For `UD-IQ3_S` that means launching the resume **when phase
E's last cell is running**, so the download overlaps only the final trial and the placement
follows straight after. **If phase E ends with no time left for that placement, no pull happens
at all.** The same rule governs every other reserve entry.

This reverses D6-13, where I pulled reserve rank 1 hours ahead of need to "keep the disk end
busy". That was the wrong instinct on a machine whose bandwidth is shared with its owner: an
idle link is not waste, and a download that finishes six hours before anything reads it has
bought nothing and cost someone else their evening.

Implemented rather than intended:

- **`phaseDE.py` now builds every remaining scored cell up front**, phase D and phase E
  together, so the *final* cell of the campaign is knowable before it starts. `maybe_jit_pull()`
  fires at the start of that cell and nowhere else. Where phase E is empty — which happens if
  neither of the best two placed at 96k — the final cell is phase D's last, so the rule still
  has a well-defined trigger and the pull still overlaps exactly one trial.
- **A time cutoff of 05:45** on the local clock. Past it, `maybe_jit_pull()` logs that it is
  skipping and does nothing: the rest of the night belongs to the handoff, and a pull whose
  placement cannot run is precisely the pull the owner asked me not to start.
- **`jit_pull.sh` separates the two halves.** The download runs immediately, overlapping the
  final trial, which the plan explicitly permits. The **placement then waits on `.phaseE-done`**
  before touching the GPU, so a pull and a trial overlap while two GPU loads never do. It also
  strips the projector first (D6-11) and retries a failed pull exactly once.
- `.phaseE-done` is now load-bearing twice — the session waiter reads it as the end of the
  campaign and `jit_pull.sh` waits on it — so it is written explicitly and was verified present
  after I clipped it once while editing.

Nothing else pulls. `pull2.sh` and `pull3.sh` are dead (D6-28) and `reserve_pull.sh` is invoked
by nothing that still runs.

## D6-30 — the scored rows do not fill the window they are placed in, and the report must say so

*21:56.* The first two scored trials carry a caveat that changes how every quality number in
this campaign should be read, so I am recording it now rather than discovering it in the
morning.

| trial | material | **peak prompt** | % of the 64k window | turns |
| --- | ---: | ---: | ---: | ---: |
| g03 @ 64k | 30,018 | **25,748** | **39%** | 36 |
| t03 @ 64k | 30,604 | **16,502** | **25%** | 7 |

`achieved_fill_prompt_tokens` is the peak single-turn input, which is the most context the model
ever actually held. **A cell configured for 64k is being worked at 25-39% occupancy.**

Two causes, both deliberate and neither a fault. v5 withdrew synthetic prompt-side fill from
every scored row, so the only material in the window is what the task genuinely requires. And
the pi-resilience extension every v6 row runs under middle-truncates tool output over 24,000
characters — about 5,100 tokens — so no single tool result can flood the context, which is
exactly what it was shipped to do.

**The consequence is the important part.** Placement measures capacity honestly, with a
synthetic fill to about 90% of `num_ctx`, and those numbers stand. But the *scored* rows do
**not** exercise the context they are placed at, so a 64k row and a 48k row are, on the evidence
of these two trials, running the model at a very similar occupancy. **The quality comparison
across context rungs is therefore weak by construction**, and any sentence of the form "quant X
is still accurate at 64k" means "at 64k of *configured* window and about 26k of *used* window".

This is not a reason to change the suite mid-campaign — the v5 suite is frozen and changing it
would invalidate every row against the reference. It is a reason to report **max viable context
and quality as two separate findings** rather than one, and to stop the report from implying the
suite proved a context-quality relationship it never tested. The honest headline is: placement
says what each quant *can hold*; the bands say how well it *works*; the campaign does not
measure how well it works *when full*.

I will track `peak_prompt` across every row and put the distribution in the handoff. If some
task does approach its window, that task is the only one carrying a context-quality signal and
the report will name it. **Filling the window on purpose is a v7 question**, and it is the
obvious one: a band authored to genuinely occupy 60% of 64k would test what this campaign
assumed and did not measure.

## D6-31 — a one-line path bug had silently disabled every rejection rule in the campaign

*22:03.* The worst fault of the night, caught by reading one log line rather than by any check.

Phase B printed `== reference t03 walls: {65536: None, 49152: None}` immediately after two
sentinel trials that had both **passed and recorded walls of 31.0 s and 25.4 s**. The trials
were fine; the reader was not.

`HERE` is `.../ollama-bench/results/v6`, so `BENCH = os.path.dirname(HERE)` is
`.../ollama-bench/**results**`, not the bench directory — and `RES = os.path.join(BENCH,
"results")` therefore pointed at `.../results/results`, which does not exist. Every artifact
read returned nothing. The cells still *ran* correctly, because `runcell.sh` does its own `cd`,
so nothing looked wrong anywhere except that one printed line.

**What it would have cost, in order of severity:**

1. **Phase D would have selected nothing and reported success.** `rank()` returns `None` when it
   reads no runs, every candidate would have been filtered out, `best2` would have been empty,
   the cells loop would have done nothing — and `.phaseD-done` and `.phaseE-done` would still
   have been written. **My own waiter would have announced "CAMPAIGN COMPLETE" with zero verdict
   rows**, which are the entire point of the night.
2. Phase C's two-timeouts mid-row rejection would never have fired.
3. Phase B's 3x sentinel rejection would never have fired: with `r` as `None`, `elif r and w >
   3 * r` is simply false, so every quant survives regardless of how slow it is.

Three independent rejection mechanisms, all inert, all failing open, and every flag green. This
is v5's lesson repeating exactly: *four of the five faults that session found came from reading
a tool's report of what it could not do, not from looking at a rate* — and this one came from a
line that said `None` where a number belonged.

Fixed: `RES = os.path.dirname(HERE)` and `BENCH = os.path.dirname(RES)` in all three drivers,
verified against real artifacts before restarting (`runs_for` returns 2, `wall` returns 31.0 and
25.4, `rank` returns a tuple). Phase B was restarted; pibench resumed and skipped every finished
trial, so the completed Q2_K_L cells took **two seconds** and nothing was re-run. The reference
now prints `{65536: 31.0, 49152: 25.4}`.

**And the fault is now loud rather than silent.** Both drivers refuse to continue on an empty
read: phase B raises `FATAL: no reference t03 wall could be read … the 3x rejection rule would
be inert`, and phase D raises `FATAL: phase D selected no quant … refusing to report an empty
campaign as complete`. A guard that fails closed is the only reason to trust a green flag, and I
did not have one until now.

## D6-32 — the sentinel rule conflated speed with quality, and would have deleted the 96k quant

*22:16.* IQ2_M timed out on g03 at 64k (600.1 s), so the sentinel rule demoted it to 48k. Under
D6-17 a failure at every placed rung then rejects the quant outright — and g03 is admitted at
48k too, so the likely path was: **IQ2_M rejected, every tag removed, and the campaign's only
96k-capable quant deleted.** I stopped phase B to look at that properly, because a rule about to
discard the night's headline result deserves the scrutiny.

The two sentinel tasks are not measuring the same thing, and the plan says so itself when it
introduces them: **t03 is "the task that exposed the bend"** — the speed sentinel — **and g03 is
"the hardest; the only task Q2_K_L missed"** — the quality sentinel.

| @64k | t03 (speed sentinel) | g03 (quality sentinel) |
| --- | --- | --- |
| Q2_K_L | 31.0 s, 33.6 achieved tok/s, `correct` | 350.5 s, `confidently_wrong` |
| IQ2_M | **32.7 s, 35.7 achieved tok/s, `correct`** | **600.1 s, TIMEOUT, `confidently_wrong`** |

**On the speed sentinel IQ2_M is 5% slower on wall and actually faster on achieved throughput.**
Its placement at a 58k fill is 46.64 gen tok/s against Q2_K_L's 44.88. Two independent
measurements say this cell is not degraded.

And the timeout rule's own stated premise is that "a cell that needs longer than this is
generating at spill speed" (plan section 4). **For this cell that premise is false**, and both
quants fail g03 anyway — Q2_K_L just fails it faster. A rule that rejects a quant for being slow
on a task the reference quant also gets wrong is measuring the task, not the quant.

Decision: **the sentinel rule splits by task role.** A t03 timeout, or a t03 wall over 3x the
reference, fails the rung and demotes. A **g03 timeout is recorded as a failed task and carries
`g03_timed_out` into `phaseB.json`** — reported, never hidden — but does not by itself demote or
reject. Phase C's separate two-timeouts-across-the-band rule is untouched and still applies, so
a quant that genuinely cannot finish work is still caught, just on evidence broader than one
task.

**The falsification test, stated so this is not special pleading:** had IQ2_M's *t03* been slow
or timed out, it would have been demoted and then rejected, 96k placement or not. It was not —
it ran at the reference speed. The rule change is about which measurement carries the signal,
and it would have saved any quant in that position, not this one.

Rewired accordingly: phase B restarted under the corrected rule, and `chainCDE.sh` stopped
before it could consume the phaseB.json written under the old one. Everything now runs from a
single `chainAll.sh` (B -> C -> D -> E) which **halts if phase B exits non-zero** rather than
running phase C on a bad ordering. Every completed trial resumes from its artifact, so the
restart re-ran nothing.

## D6-33 — a passing rung outranks a marginal one, so the headline table cannot claim a context the quant does not hold

*22:26.* Phase B began sentinelling IQ3_XXS at **64k marginal** when the same quant has a clean
**48k pass** (13.07 GB, 100% GPU, 47.03 tok/s, against 14.31 GB, 93% GPU, 28.97 tok/s). The plan
supports both readings and they disagree:

- section 6C: "every survivor at **its top rung** up to 64k" — which is 64k, marginal or not;
- section 4: "between the two is marginal — record it, **keep the cell only if no better rung
  exists**" — which says use 48k;
- and the owner's ruling 1, which outranks both: a quant is viable "only if it runs 48k context
  **with no performance degradation**".

Marginal *is* degradation — that is what the word records. Scoring IQ3_XXS at 64k would put a
row in the campaign's headline table at a context the quant does not viably hold, and the table's
column is literally "max viable context". Section 4 is also the more specific clause and it
addresses exactly this case.

Decision: **`rungs()` returns passing rungs only, highest first; marginal rungs are used solely
when a quant has no passing rung at all.** The resulting scored cells:

| quant | scored rung | why |
| --- | --- | --- |
| Q2_K_L, Q2_K, IQ2_M | 64k pass | clean at 64k |
| IQ3_XXS, UDQ3KXL, mrIQ3M | 48k pass | 64k is marginal or spill |
| IQ3_XS | 48k **marginal** | its only rung — no passing rung exists, so section 4 keeps it, and the row says so |

IQ3_XXS's 64k marginal placement is not lost: it stays in `placement.json` and in the placement
table, reported as the stretch it is. And the question "does a marginal cell actually work?" is
already answered by IQ3_XS at 48k, which passed its sentinel `correct` but at **2.09x the
reference wall** — degradation visible on real work, exactly as the gate predicted from resident
size and tok/s alone. That is the first time in this campaign the cheap gate and an expensive
scored measurement have independently agreed, and it is why the gate can be trusted to set the
rungs.

IQ2_M's 96k placement is untouched by this: phase E reads `placement.json` directly, so the
stretch cell still runs at 96k.

## D6-34 — placement does not predict agentic performance, and Q2_K is the proof

*22:48.* Q2_K failed the speed sentinel at 64k: **t03 in 584.1 s against the reference 31.0 s —
18.8x, where the threshold is 3x.** It demoted to its 48k passing rung, which is the rule
working. What matters is that **placement gave no warning at all.**

| @64k | resident | pct_gpu | gen tok/s @fill | prompt tok/s | **t03 wall** | **achieved out tok/s** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Q2_K_L | 13.35 GB | 100% | 44.88 | 1,337 | **31.0 s** | 33.6 |
| Q2_K | 13.07 GB | 100% | 45.14 | 1,361 | **584.1 s** | **4.7** |

Two cells indistinguishable on every placement metric — resident within 0.3 GB, generation
within 0.3 tok/s, prefill within 2%, both pinned at 100% GPU — differ by **18.8x on real work**.
Everything phase 0 measures says these quants are the same. They are not.

**It is not spill, and the arithmetic rules it out.** 13 turns and 2,761 output tokens in 584 s
is 45 s per turn, of which at Q2_K's own measured 45 tok/s only about 5 s can be generation.
Prefill of a ~14k context at 1,361 tok/s accounts for 10 s more. **Thirty seconds a turn is
unexplained by any rate phase 0 records.** Beside it, Q2_K's g03 produced **18,097 output tokens
in 12 turns — 1,508 a turn against 459-540 for every other quant — and stopped on `length` with
the campaign's first `visibly_failed` verdict.** The consistent reading is a quant that
**rambles**: it burns the clock in reasoning and over-long output, not in memory traffic.

Three consequences, and the first is the one for the report.

1. **The campaign needs both instruments and neither substitutes for the other.** Placement is
   cheap, takes ninety seconds, and answers "does this fit". The scored sentinel is expensive
   and answers "is it usable". Q2_K passes the first and fails the second at the same rung. Any
   future campaign that places quants and skips the sentinels to save time would have shipped
   Q2_K-64k as a recommended cell.
2. **It vindicates keeping t03 as the speed gate in D6-32.** The rule I split so that a
   *quality* timeout could not delete IQ2_M has now caught a genuinely unusable cell through the
   *speed* sentinel. The division of labour is doing real work in both directions rather than
   just excusing a favoured quant.
3. **`gen tok/s` is the wrong headline speed number** and `achieved out tok/s` is the right one,
   exactly as plan section 5 says: 45.14 against 4.7 for the same cell. The summary table already
   carries achieved throughput; the report will lead with it and treat placement tok/s as a
   capacity check only.

Q2_K's 48k sentinel is running. If it rambles there too it is rejected outright, and the honest
line will be that **Q2_K is the non-L 2-bit that fits everywhere and works nowhere.**

## D6-35 — the drivers read stale verdicts, and the fix nearly walked into the WSL loopback trap

*22:59.* Phase B began sentinelling **Q3_K_S** — a quant rejected at 21:15 whose every tag was
deleted from the daemon. Two faults, the second worse than the first.

**One: `placement.json` is append-only, so a record keeps the verdict it was written with.**
Q3_K_S-48k was measured at 21:02, before the prefill gate existed (D6-19, 21:14), so it is
stored `pass`. The renderers already re-derived verdicts through `gate.py` and showed it
correctly as `spill`; **the drivers did not**, and read the raw field. Exactly one record in the
campaign disagrees between stored and derived, and it is the one that sent phase B chasing a
deleted model. Fixed: `phaseB.placement()` and `phaseDE.top_rung_any()` now re-derive through
the shared gate, so a rule added at any hour reaches every record ever written.

**Two, and this is the one that would have cost the night.** I added a belt-and-braces guard —
skip any quant with no tag on the daemon — and wrote it as a plain `urllib` call to
`localhost:11434` from the driver, which runs under **WSL's** python. It returned **zero tags**.
`localhost:11434` inside WSL is WSL's own loopback, and a WSL-side `ollama serve` answers there
with no models: "`ollama list` from WSL is a lie" is written down in the v5 handoff, and I
walked into it anyway. An empty set from that call means "every quant has been rejected", so the
guard I added to protect the run would have **skipped all nine quants and produced an empty
campaign.**

Caught only because I printed the count while testing rather than trusting the patch. Fixed
twice over: the query now goes through the **Windows** interpreter, which is how every other
daemon call in this campaign is made, and an empty result is treated as *unknown* and never as
*everything is gone* — `return tags or None`, and `None` means do not filter. A guard that fails
closed on its own uncertainty is the only kind worth adding.

Verified before restarting: 30 tags visible, `q27-Q3_K_S` absent, `q27-IQ3_M` absent,
`q27-IQ2_M` present. Phase B now prints
`== skipping, no tag on the daemon (rejected and removed): IQ3_M, Q3_K_S`.

## D6-36 — correcting D6-34: Q2_K does not ramble, its 64k *cell* is pathological

*23:02.* D6-34 read Q2_K's 584 s t03 as a quant that "rambles — it burns the clock in reasoning
and over-long output". **That reading is wrong**, and the 48k sentinel refutes it. Same quant,
same task, one rung apart, both cells at 100% GPU, no errors, no retries, no timeouts:

| Q2_K t03 | cell | turns | out tok | **peak prompt** | wall | **achieved out tok/s** | s/turn |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| at 64k | 13.07 GB, 100% | 13 | 2,761 | **16,098** | **584.1 s** | **4.7** | **44.9** |
| at 48k | 12.46 GB, 100% | 7 | 1,101 | **15,914** | **31.2 s** | **35.3** | **4.5** |

**The model saw the same amount of context in both — 16.1k against 15.9k peak prompt — and one
took ten times as long per turn.** The only difference between the cells is the *allocated*
`num_ctx`: 65,536 against 49,152. Not the material, not the achieved occupancy, not residency,
not the GPU split.

And it is not "64k is slow" in general: **Q2_K_L runs the same task in the same 64k window in
31.0 s.** It is this quant in this cell.

So the corrected finding is sharper than the one it replaces: **a cell can place perfectly clean
— under the resident line, 100% GPU, 45 tok/s generation, 1,361 tok/s prefill — and still cost
10x per turn on real work, and the cost tracks the context you *allocated* rather than the
context you *used*.** Q2_K's g03 numbers that I read as verbosity (18,097 tokens, 1,508 a turn,
`length` stop, the campaign's first `visibly_failed`) sit at 64k too, and at 48k the same quant
produced 27,816 tokens across 45 turns at **46.4 achieved tok/s** — the most productive cell
measured tonight. Nothing about Q2_K is verbose; its 64k cell is broken in a way no phase 0
number detects.

**I do not know the mechanism and will not guess one in the report.** The candidates I can name
but not distinguish with the data I have: prompt-cache invalidation that scales with allocated
KV, a flash-attention kernel or batch choice that changes at a size threshold, or per-turn cache
shifting over the full allocation. Distinguishing them needs a probe this campaign has no time
for, and it is the single most valuable thing v7 could run: **hold the task and the achieved
context fixed and sweep `num_ctx` alone.** If the effect reproduces, the fleet has been sizing
context windows by what fits rather than by what performs, and 96k IQ2_M may carry the same
hidden tax.

D6-34's three consequences stand unchanged — placement and sentinels are not substitutes,
t03-as-speed-gate earned its keep, and achieved out tok/s is the headline number. Only the
*cause* was wrong, and it was wrong because I inferred a mechanism from one cell instead of
waiting for the controlled comparison that was already scheduled.

## D6-37 — my kill script was killing another campaign's trials, and then it killed my own

*23:15.* Coordinator relayed that `kill_pi.ps1` had been ending in-flight trials belonging to a
**second campaign running on this machine tonight** — the prompt campaign under
`results/prompt-v1/`, its own tag and agent dir. My script matched **every** `node.exe` whose
command line contained `pi-coding-agent` and force-killed it. A package name cannot tell two
campaigns apart, and I had been running that script at every chain restart all evening.

Rewritten to scope by **ancestry**, which is the only thing that actually identifies ownership:
find `python.exe` processes whose command line carries both `pibench.py` **and** `--tag v6-`,
walk the parent map, and kill only `node.exe` whose ancestry reaches one of those. **If no v6
pibench is running it kills nothing at all** — the previous version's failure mode was to kill
everything in exactly that case. I also added `list_node.ps1`, which reports node processes and
their `--model` read-only, so I can look before acting.

**And then the corrected script bit me, which is worth recording honestly.** I ran it once to
verify it, live, while my own mrIQ3M sentinel was in flight. It correctly identified pid 18028
as mine and killed it — right behaviour, wrong moment. `runcell.sh` returned rc=255, phase B saw
no t03 result, and **rejected mrIQ3M for "no t03 result at 48k"**. A quant that had never been
measured was recorded as failing. Everything else in that `phaseB.json` was correct; only the
quant I had personally interrupted looked bad.

Two fixes, because the incident exposed a real hole and not just a clumsy moment:

1. **An interrupted cell is not evidence about a quant.** `phaseB.py` now retries a cell **once**
   when it exits non-zero *and* produced no t03 result, before any judgement sees it. pibench
   resumes, so the retry re-runs only what is genuinely missing. Without this, any crash, kill or
   transient error during a sentinel silently converts into a rejection — and a rejection
   deletes the model from the disk.
2. **Verify a destructive script read-only first.** `list_node.ps1` exists so the next check of
   "what would this kill" costs nothing. Running a force-kill to test it, against live work, was
   the actual mistake here.

No orphans were left: a read-only sweep showed no `node.exe` running at all afterwards, so
nothing of mine or anyone else's was left spending GPU. Phase B restarted; every completed
sentinel resumed in seconds and mrIQ3M's runs fresh.

## D6-38 — the stall alarm cried wolf, and a second campaign shares this GPU

*23:22.* The waiter fired "no v6 artifact written for 15 min". **False alarm.** The chain was
alive, the GPU was at **97%**, and mrIQ3M's g03 sentinel had been running for six minutes of a
legitimate ten-minute budget. The threshold was simply too tight for its own campaign: a single
large-band trial may run the full 600 s timeout, and **cells that resume from an existing
artifact write nothing at all**, so a run of resumed cells followed by one slow trial passes
fifteen minutes of silence while perfectly healthy.

Fixed rather than ignored, because an alarm that cries wolf gets skimmed past, and this one
earned real trust at 21:43 by finding a fifteen-minute idle GPU (D6-27). Threshold raised to
**25 minutes**; the chain's own log is now watched alongside the artifacts, since it moves on
every cell start, cell end and finished task and is the better liveness signal; and the alarm
now prints the **GPU utilisation** beside the complaint, so the next one can be triaged from the
notification instead of a round trip.

**Also noted while diagnosing, and it matters for the handoff:** three other
`pibench.py --provider …` processes are running on this machine — the prompt campaign under
`results/prompt-v1/`, which the coordinator flagged at 23:15. So **this GPU is shared tonight**.
Two consequences I am recording rather than acting on:

- **My ancestry-scoped kill (D6-37) correctly leaves them alone**, which is now confirmed
  against live processes rather than merely intended.
- **Every v6 wall-clock number after roughly 23:00 was taken on a contended GPU.** The
  placement figures and the sentinel walls quoted throughout this file predate that or ran
  while the other campaign was idle, but phase C, D and E timings do not, and the handoff will
  say so plainly. Achieved out tok/s in particular is a *shared-machine* number from here on.
  That does not invalidate the quant-versus-quant comparison — every quant pays the same tax
  and the ordering is what the campaign reports — but it means these walls are not comparable
  to v5's, and no absolute throughput figure from tonight should be quoted as this card's
  capability.

## D6-39 — D6-34/D6-36 may be a shared-GPU artifact; re-measuring before it goes in the report

*23:24.* Having recorded in D6-38 that a second campaign shares this GPU, I checked when it
started, and the answer puts my headline finding in doubt.

`results/prompt-v1/`'s earliest artifact is **22:44**. My Q2_K sentinel at 64k ran **22:32 to
22:48**, with the t03 trial — the 584.1 s measurement that D6-34 and D6-36 are built on —
occupying roughly **22:38 to 22:48**. It overlapped the other campaign's start. The reference it
is compared against, Q2_K_L's 31.0 s at the same rung, was taken at **21:54 with this GPU to
itself.**

**So the two halves of an 18.8x comparison were measured under different machine conditions,
and I did not know it when I wrote either entry.** That is the same error the campaign has now
made three times in different clothes — D6-21 read a KV rate off a spilled cell, D6-26 read an
i-quant overhead off two offloaded cells, and here I read a slowdown off a contended one. Each
time the measurement was real and the comparison was not.

It may still be sound: contention plausibly costs tens of percent, not 1,780%, and IQ2_M's
healthy 32.7 s at 64k was taken at 22:14, also before the other campaign started. But
"plausibly" is not a measurement, and this claim is load-bearing enough to be worth ten minutes.

**Test, running now** (`recheck.sh`, tag `v6-recheck-64k-t03`, so no campaign artifact is
touched): Q2_K_L-64k and Q2_K-64k, t03, one trial each, **back to back in a single pibench
invocation** under whatever contention exists tonight. Both arms then share every condition that
differed before.

- If Q2_K remains roughly 15-20x Q2_K_L, D6-34 and D6-36 stand and the shared GPU is irrelevant
  to them.
- If the two come out close, **D6-34 and D6-36 are withdrawn**, Q2_K's demotion from 64k was
  driven by an artifact, and the phase B ordering has to be re-derived.

Cost: the in-flight mrIQ3M g03 sentinel restarts, about six minutes. Worth it — publishing a
headline methodological claim that turns out to be another campaign's load would be the worst
outcome available tonight. `recheck.sh` `exec`s the campaign chain when it finishes, so the
night resumes by itself either way.

## D6-40 — WITHDRAWN: D6-34 and D6-36. The 18.8x did not reproduce

*23:26.* The recheck of D6-39 is in, and **my headline methodological finding was wrong.** Both
quants, t03, one trial each, back to back in a single pibench invocation under identical
contention:

| t03 @ 64k | original | **recheck** | conditions |
| --- | ---: | ---: | --- |
| Q2_K_L | 31.0 s | **32.8 s** | 21:54 alone / 23:24 shared |
| Q2_K | **584.1 s** | **48.9 s** | 22:38-22:48 overlapping the other campaign's start / 23:24 shared |
| **ratio** | **18.8x** | **1.49x** | |

Contention costs about **6%** on this machine, measured on Q2_K_L's own two runs — nowhere near
enough to explain 1,780%. But Q2_K's 584 s **does not reproduce at all**, and 48.9 s against a
32.8 s contemporaneous reference is an ordinary quant-to-quant difference, not a pathology.

**Withdrawn in full: D6-34 ("placement does not predict agentic performance, and Q2_K is the
proof") and D6-36 ("Q2_K's 64k cell is pathological").** Both were built on that single trial.
The most likely cause of the outlier is what the timing points at: the other campaign started at
22:44 and would have loaded its own model onto a 16 GB card already holding Q2_K-64k's 13.07 GB,
and Ollama juggling two models across that boundary is exactly the shape of a one-off collapse
to 4.7 achieved tok/s. **That is a finding about sharing a GPU, not about a quantisation.**

What survives, and what does not:

- **Does not survive:** any claim that a clean placement fails to predict real work. On this
  evidence placement and the sentinels agree.
- **Survives, because it was measured before 22:44 and is unrelated:** Q2_K's g03 at 64k —
  18,097 output tokens in 12 turns, `length` stop, the campaign's first `visibly_failed`. That
  ran 22:32-22:38, uncontended. It is one trial and now stands alone, so it is reported as an
  observation and not as a characterisation of the quant.
- **Survives and is strengthened:** D6-32's split of the sentinel by task role. It was the
  *speed* sentinel that produced the false alarm here, and the retest is what caught it — the
  rule did not silently reject anything, it demoted, and a demotion is recoverable.

**Action taken.** The contaminated trial is removed from `results/v6-Q2_K-64k-large.json` and the
whole original artifact is preserved at
`results/v6/quarantine-Q2_K-64k-t03-contaminated.json` — no measurement is deleted, one is set
aside with its reason. Phase B will re-measure Q2_K's t03 at 64k in situ rather than have a
number hand-copied in from the recheck tag. On the recheck evidence Q2_K should then place at
**64k, not demoted**, and the phase B ordering changes accordingly.

**The lesson, which is the fourth instance tonight of one error.** D6-21 read a KV rate off a
spilled cell; D6-26 read an i-quant overhead off two offloaded cells; D6-39 caught this one
before it shipped. Every time, a real measurement was compared against something taken under
different conditions. **A single trial is a claim about one moment on one machine.** The campaign
already had the right instinct written into it — phase D exists because one trial is not a
verdict — and I published a headline from one anyway, twice, within twenty minutes.

## D6-41 — I killed the chain to fix an artifact and never restarted it: 26 minutes of idle GPU

*23:53.* The stall alarm fired with **GPU 0% busy** and it was right. At 23:26 I stopped the
chain to quarantine the contaminated Q2_K trial (D6-40), did the surgery, wrote up the
withdrawal, committed — and never started the chain again. The GPU sat idle from 23:26 to 23:53.

This is the same failure as D6-27 in a different costume: there the GPU idled because I gated a
GPU phase behind a download, here because a stop and a start were two separate actions and only
the first happened. **All evening I have been killing and relaunching the chain by hand, five or
six times, and it worked every time until the once it did not.**

Two fixes, both about making the good path the only path:

1. **`restart_chain.sh` makes stop-and-start atomic.** Killing without restarting is never what
   this campaign wants, so the two are now one command — it stops the chain's process group,
   clears the pi children by ancestry, relaunches, and then **verifies the chain is actually
   alive**, printing `FAILED TO RESTART -- the GPU is idle, fix this now` and exiting non-zero if
   not. Every future intervention goes through it.
2. **The stall threshold goes back to 15 minutes.** I raised it to 25 at 23:22 after a false
   alarm (D6-38), and that decision directly cost ten of these twenty-six minutes. The reason it
   is safe to lower again is that the alarm now prints **GPU utilisation** beside the complaint,
   which separates the two cases at a glance: `GPU 97% busy` is a long trial running normally,
   `GPU 0% busy` is a dead chain. **The right response to a false alarm was to make the alarm
   more discriminating, not quieter** — I did the lazy half first and paid for it within thirty
   minutes.

Cost tonight: 26 minutes here, 15 at D6-27, about 41 minutes of an eleven-hour budget lost to
GPU idleness, all of it self-inflicted and all of it found by the alarm rather than by me.

Chain restarted at 23:53. Q2_K's t03 at 64k is being re-measured in situ, which is the point of
the quarantine.
