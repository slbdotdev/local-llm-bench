# v6 reserve — ranked candidates not yet on disk

*Written 2026-09-05 from a Luna web sweep of every GGUF repo for Qwen3.8-27B on Hugging Face
(878 GGUF-tagged repos searched, file sizes from the HF tree API), verified by the control
session against the bartowski tree directly. The plan is `plan-2026-09-05.md`, section 2.*

## How to read the sizes

The proven cell is bartowski `Q2_K_L`: **13.08 GB on disk, 13.35 GB resident at 64k**. The
file-to-resident offset measured on 2026-09-05 was **not constant**: 0.27 GB for Q2_K_L, 0.98
for Q3_K_S, 1.21 for IQ3_M, 0.30 for Q3_K_M at 48k. So a file at or under 13.1 GB is a strong
bet for 64k, 13.1-13.5 is a coin flip, and anything larger is a 48k-only candidate at best.
Placement (phase 0) is the measurement; nothing here is a verdict.

Two things the sweep found that the roster did not know:

- **mradermacher's files are markedly smaller than bartowski's for the same quant name** —
  `i1-Q3_K_M` is 13.50 GB against bartowski's 14.61, `i1-IQ3_M` 12.77 against 13.90. Bartowski
  keeps the embedding and output tensors at higher precision (the `_L` suffix is that choice
  made explicit); mradermacher does not. Smaller is exactly what this card wants, and whether
  the quality cost shows on the suite is a measurement worth one row.
- **unsloth's UD dynamic quants** keep the layers that matter at higher precision and quantise
  the rest harder; `UD-Q3_K_XL` at 13.15 GB is a 3-bit file the size of Q2_K_L.

## The ranked reserve

Pull with `ollama pull <src>`, then bake a tag the way `make_model.sh` does but with this
`FROM` line, since that script hard-codes the bartowski repo:

```
printf 'FROM %s\nPARAMETER num_ctx %s\n' "<src>" 65536 > /tmp/mf && ollama create q27-<NAME>-64k -f /tmp/mf
```

| rank | name for tags | src (`ollama pull`) | file GB | imatrix | why |
| ---: | --- | --- | ---: | :---: | --- |
| ~~1~~ | ~~`UDQ3KXL`~~ | ~~`hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q3_K_XL`~~ | 13.15 | yes | **pulled 2026-09-05 20:59 (D6-13)**, ahead of a rejection, because IQ3_XXS reached only `marginal` at 64k and a dynamic 3-bit at Q2_K_L's file size is the only remaining way the campaign's headline question is answered yes |
| ~~2~~ | ~~`mrIQ3M`~~ | ~~`hf.co/mradermacher/Qwen3.8-27B-i1-GGUF:i1-IQ3_M`~~ | 12.77 | yes | **pulled 2026-09-05 21:15 (D6-20)** as the swap for rejected Q3_K_S |
| ~~3~~ | ~~`UDIQ3S`~~ | ~~`hf.co/unsloth/Qwen3.8-27B-GGUF:UD-IQ3_S`~~ | 12.04 | yes | **pulled 2026-09-05 21:24 (D6-24)** as the swap for rejected IQ3_M; on disk but **not yet placed** — queued behind phase E |
| 4 | `GSQIQ3S` | `hf.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S` | 11.77 | yes | a research-lab quantisation method (GSQ-RCO), not a llama.cpp default; the one genuinely different algorithm in the sweep |
| 5 | `mrQ3KM` | `hf.co/mradermacher/Qwen3.8-27B-i1-GGUF:i1-Q3_K_M` | 13.50 | yes | Q3_K_M at 48k was degraded from bartowski's 14.61 GB file; this one is 1.1 GB smaller and may pass 48k, possibly 64k |
| 6 | `UDIQ3XXS` | `hf.co/unsloth/Qwen3.8-27B-GGUF:UD-IQ3_XXS` | 10.93 | yes | dynamic IQ3_XXS, 1.7 GB under bartowski's; a 128k candidate at 3 bits |
| 7 | `UDQ2KXL` | `hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q2_K_XL` | 9.83 | yes | the 2-bit dynamic; the 128k-256k candidate if IQ2_M disappoints |

Skipped on purpose: every uncensored, heretic, abliterated or distilled fine-tune (this campaign
compares quantisations of one model, and a fine-tune changes the model); the `orcarouter`
mirror, which is bartowski's files re-uploaded without the imatrix flag; `ubergarm` and
`ggml-org`, which ship no 2-3 bit file; and any file over 13.6 GB.

The sweep found **no newer Qwen model in the 25-30B class** as of 2026-09-04.

## Swap rule (plan section 6)

When a roster quant is rejected: `ollama rm` every tag of it, pull the top remaining line here
in the background while the GPU runs the next quant, bake its 48k and 64k tags, and move the
line to `decisions.md` with the reason. Keep this file current: strike a line when it is pulled,
add a line if a later sweep finds a better one.

## Struck lines and what replaced them

- **rank 1 `UDQ3KXL`, pulled 2026-09-05 20:59** (`decisions.md` D6-13). Pulled ahead of a
  rejection to keep the disk end busy while the GPU ran phase A.
- **rank 2 `mrIQ3M`, pulled 2026-09-05 21:15** (`decisions.md` D6-20), as the swap for
  **Q3_K_S**, rejected because its only rung (48k) prefills at 76 tok/s — a 571-second wait
  before the first token — while generating at a healthy 41 tok/s and reporting 100% GPU.
- **rank 3 `UDIQ3S`, pulled 2026-09-05 21:24** (`decisions.md` D6-24), as the swap for
  **IQ3_M**, rejected at 14.98 GB and 89% GPU on its only rung. **On disk, not yet placed**:
  the campaign is limited by scored-trial time rather than by candidates, so its placement is
  queued behind phase E. First thing for the next session if this one does not reach it.

## What the v6 placement pass adds to this file

**Check every reserve candidate for a vision projector before comparing it to anything.** Four
of the seven roster quants turned out to carry the 927 MB `mmproj` layer in their Ollama
manifest and three did not, which on a 16 GB card is the difference between a `pass` and a
`spill` verdict at 64k (`decisions.md` D6-9, D6-11). Every publisher in this list ships the
projector alongside the model, so every one of these entries needs the same strip. The worked
procedure is `strip.sh`: `ollama create` from the model blob's own path imports one
projector-free copy, every other context rung is derived `FROM` that tag for free, and the
`hf.co` tag is removed straight after to give the disk back.

**~~And budget for the i-quant overhead.~~ WITHDRAWN 2026-09-05 21:29** (`decisions.md` D6-26).
The earlier claim here — that an IQ file needs about 1 GB more headroom than a K-quant of the
same size — was read off cells running at 89-93% GPU, i.e. already partially offloaded, where
`/api/ps` overstates resident size. On clean 100%-GPU cells the overhead over the model layer is
**1.21-1.43 GB at 48k across two i-quants, two K-quants and one dynamic quant alike**. There is
no i-quant penalty, and the size-based rules of thumb above apply to every family.

**What the size rule should say instead.** Overhead at 48k is about 1.3 GB and the KV cache
costs about **39 MB per 1k of context** (D6-21, measured between clean cells only). So a file
holds 64k if its model layer is under about **11.1 GiB**, and 96k if it is under about
**10.2 GiB**. Measured against that: IQ2_M (10.13) holds 96k, Q2_K (11.03) and Q2_K_L (12.18)
hold 64k, and every 3-bit file on the roster (11.76-12.95) holds 48k at best. **No 3-bit quant
of any publisher tested carries 64k on this card** (D6-25).
