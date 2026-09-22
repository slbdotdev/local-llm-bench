# Local LLM Benchmarks

Benchmarks, harnesses and results for running **Qwen3.8-27B** on consumer
NVIDIA cards. The main card is a desktop **RTX 5080 (16 GB)** running Ollama on
Windows. The comparison card is a rented **RTX 5090 (32 GB)** on Runpod. Hosted
frontier models serve as reference arms.

The work ran from 2026-09-03 to 2026-09-22 as a series of campaigns. Each
campaign had a frozen plan, pre-registered hypotheses where it compared
conditions, and grades that were audited after the run. The results below
include the qualifications recorded when each result was taken.

- [Headline findings](#headline-findings)
- [Hardware and software](#hardware-and-software)
- [Results by campaign](#results-by-campaign)
- [RTX 5080 vs RTX 5090](#rtx-5080-vs-rtx-5090)
- [Repository layout](#repository-layout)
- [Grading](#grading)
- [Methodology notes and lessons](#methodology-notes-and-lessons)
- [Provenance](#provenance)

---

## Headline findings

1. **The best quant for a 16 GB card is `UD-Q2_K_XL` or `UD-IQ3_S`.** Both are
   Unsloth Dynamic quants. `UD-IQ3_S` wins on every quality measure. With the
   MTP head resident, `UD-Q2_K_XL` still holds 192k context; `UD-IQ3_S` drops
   to 128k.
2. **The MTP head embedded in the GGUF gives a free 1.25x–2.05x decode
   speed-up** on llama.cpp. It needs no extra download and no rebuild; the flag
   had simply never been passed.
3. **The 5090 decodes 1.56x–1.95x faster than the 5080** on identical prompts,
   seeds and caps. It is also the only way to serve `UD-Q4_K_XL` or `Q8_0`,
   because neither fits in 16 GB at any context length.
4. **On coding tasks the 2-bit 27B saturates the v7 suite.** It scored 19–20/20
   across three quants, and harness choice (pi or slbh) changed cost, not
   correctness.
5. **On a live-lookup question the harness matters more than the model or the
   prompt.** Asked for Pluto's current speed:
   - The same 27B `Q8_0` scored 13/15 in a harness that tells it to verify with
     tools, and 6/15 in Claude Code's default prompt.
   - Opus 4.6 in Claude Code at medium effort scored 0/15.
   - Hosted flash models (GLM 5.3 Flash, DeepSeek V4.1 Flash) scored 15/15 at
     about 1/20th of the local model's work per correct answer.
6. **No seat-prompt tweak has a demonstrated effect.** The best candidate
   scored 9/10 against a 6/10 baseline on the 5090. On the 5080 it went 7/15
   against 7/15, and pooled across both cards the difference was p=0.57.

---

## Hardware and software

| | Desktop | Rented pod |
| --- | --- | --- |
| GPU | RTX 5080, 16 GB (~15.8 GB usable before paging) | RTX 5090, 32 GB |
| Host | Windows, shared with a working desktop | Runpod community / secure cloud, ~$0.69–0.99/hr |
| Serving | Ollama 0.34.x, llama.cpp (CUDA 13.3, `sm_120`) | Ollama 0.34.2, llama.cpp, vLLM (round one) |
| Harnesses | pi, slbh, Claude Code, Codex CLI | same, reached over Tailscale |

Model under test: **Qwen3.8-27B** (27.32e9 parameters), in GGUF quants from
Unsloth, bartowski, ByteShape, PrismML (Bonsai) and GSQ-RCO.

---

## Results by campaign

In chronological order. Directory references are relative to this repo.

### v4 → v5: task calibration (2026-09-03 → 09-05)

`ollama-bench/tasks-v4/`, `tasks-v5/`, `results/*-v4/`, `results/v5/`

The v4 coding suite had stopped discriminating at the top of the range:

| taker | pass | mean SCORE |
| --- | ---: | ---: |
| Claude Sonnet | 13/21 (62%) | 0.968 |
| gpt-5.6-luna (medium, 4-task subset) | 4/12 (33%) | 0.805 |
| Claude Haiku | 1/21 (5%) | 0.658 |
| Qwen3.8-27B fp8, local | partial | ~0.71–0.99 |

Every model failed in the same place: parts of a spec that are stated only in
prose and never shown in an example, such as exact error kinds and offsets,
precedence between phases, and canonical text forms. v5 was written to target
that on purpose.

### v6: quant placement and scoring on the 5080 (2026-09-05)

`ollama-bench/results/v6/` (see `summary.md`)

Nine quants were run on the frozen v5 suite with the pi harness:

| quant | max viable ctx | resident | gen tok/s |
| --- | ---: | ---: | ---: |
| IQ2_M | 96k | 13.27 GB | 41.9 |
| Q2_K | 64k | 13.07 GB | 45.1 |
| Q2_K_L | 64k | 13.35 GB | 44.9 |
| UD-IQ3_S | 64k | 13.03 GB | 46.5 |
| IQ3_XXS | 48k | 13.07 GB | 47.0 |
| UD-Q3_K_XL | 48k | 13.45 GB | 44.8 |
| mradermacher IQ3_M | 48k | 13.25 GB | 42.7 |
| IQ3_XS | 48k (marginal) | 14.34 GB | 26.7 |
| Q3_K_S, IQ3_M | none | — | — |

- Across all scored rows: **111/148 passed (75%)**, 16% were confidently wrong,
  9% failed visibly and 5% timed out.
- **IQ2_M at 64k became the workhorse.** It was chosen on pass rate first, then
  confidently-wrong rate (4%, against 25% for UD-Q3_K_XL), then wall time. It
  also held 96k context at 6/8 on the large band with no confidently-wrong
  answers.

### v7: the 20-task agentic suite (2026-09-06 → 09-08)

`ollama-bench/results/v7/`

- **Calibration:** IQ2_M 19/20, UD-Q3_K_XL 20/20, Q2_K 19/20, and 10/10 for all
  three on the main band. The suite was the ceiling, not the quant: trials read
  about 4 of 91 files and used 4–27% of the window.
- **Acceptance (r6), IQ2_M at 64k:** results ranged by slot, from 10/10
  (`m09`, Wilson 95% interval 0.72–1.00) to 7/10 (`m03`, with 2 confidently
  wrong).
- The only task shape that has separated this model from frontier models is
  long serial state (`q09`): the 27B scored 1/3 against 12/12 for the frontier
  arms.

### v7.5: the harness as the only variable (2026-09-12)

`ollama-bench/results/v75/`

The 20 v7 slots were re-run with only the harness changed:

| harness | score | relative cost |
| --- | ---: | --- |
| pi | 20/20 | 1x |
| slbh (with tool-output fix) | 20/20 | about 2x wall time, tool calls and API rounds |
| slbh (without the fix) | 18/20 | about 1.2x the cost of the fixed build |

Much of slbh's extra cost came from the Windows build: its `quick_bash` ran
`cmd.exe`, and 54% of its shell calls failed until the model adapted.

### v7.6: tool-layer candidates (2026-09-13)

`ollama-bench/results/v76/` (see `v76-candidates.md`)

The rule was one change per sweep, kept only if the score stayed at 20/20 and
cost dropped on wall time, tool calls, API rounds and output tokens.

| candidate | change | result |
| --- | --- | --- |
| c1 | recursive `**` in `glob`, and an explicit "no matches" message | **kept**, with a stated caveat: judged on the median slot, 19/20 |
| c2 | report empty-but-successful tool results | reverted: it worked as designed, but all four cost measures rose |
| c3 | batch file reads | reverted: 16/20, +27 tool calls, +10 rounds, +21k output tokens |
| c4 | shell environment documentation | reverted: 19/20 at higher cost (+50 tool calls) |

9.7 GPU-hours across 178 rows. Wall-time figures before the fsync fix are
historical only. Calls, rounds and token counts are unaffected.

### Runpod RTX 5090 throughput rounds (2026-09-08)

`runpod-qwen38-5090/`

The goal was 300 tok/s single-stream decode with vLLM and MTP.

- **Round one baseline: 184.32 tok/s median. That fails the 300 target.**
- Round two produced no valid verdict. Nine of twelve rows were the model
  echoing its own padding, because the filler sat between the instruction and
  the generation point. That turned MTP into a copy task and inflated
  acceptance.
  - The only clean rows measured 157–159 tok/s, from one pod with n=2.
  - The round-one baseline shows the same degenerate signature, so it is in
    doubt as well.
- The harness fixes (salt first, usage-only token counts, a shared-prefix
  assertion) stand. The lesson is to put the instruction last.

### Quant matrix: quality, context and throughput on the 5080 (2026-09-14 → 09-16)

Perplexity and KL divergence against a `Q8_0` reference, 40 chunks, paired
t-tests:

| arm | bpw | wikitext-2 PPL | KLD | top-1 % | code PPL |
| --- | ---: | ---: | ---: | ---: | ---: |
| UD-IQ1_S | 1.81 | 8.146 | 0.407 | 74.6 | 2.680 |
| UD-IQ1_M | 1.97 | 7.223 | 0.293 | 78.2 | 2.426 |
| UD-IQ2_XXS | 2.13 | 6.874 | 0.221 | 80.5 | 2.277 |
| UD-IQ2_S | 2.45 | 6.461 | 0.140 | 85.4 | 2.147 |
| **UD-Q2_K_XL** | 2.88 | 6.126 | 0.093 | 87.9 | 2.088 |
| **UD-IQ3_S** | 3.53 | **5.940** | **0.043** | **92.1** | **2.046** |
| IQ2_M (bartowski, old baseline) | 3.08 | 6.499 | — | — | — |
| UD-Q4_K_XL (does not fit) | 5.14 | 5.823 | — | — | — |

- `UD-Q2_K_XL` beats the old IQ2_M baseline by 5.7% on PPL (t = −5.6) and is
  693 MB smaller.
- `UD-IQ2_S` ties IQ2_M (t = −0.9) while being 2.1 GB smaller.
- `UD-IQ3_S` beats `UD-Q2_K_XL` on both corpora (t = −4.1 on wikitext-2,
  −9.0 on code).
- `UD-Q4_K_XL` has a fixed floor of about 17.7 GB before any context, so it
  pages even at `-c 2048` on a 16 GB card.
- A second measurement method mattered: Ollama's own `size_vram` passed 13 of
  13 configurations, including some that were paging to system memory. One of
  them decoded at 8.96 tok/s. Only device-level `nvidia-smi` deltas caught this.

### Speculative decoding on the 5080 (2026-09-16 → 09-17)

- The **embedded MTP head** gave **1.25x–2.05x**, depending on workload and
  depth, at about half the resident cost of a separate 1.37 GB draft model.
- With the head resident, `UD-IQ3_S` drops from 192k to **128k** max context
  (46.4 tok/s there). `UD-Q2_K_XL` keeps **192k** (37.1 tok/s).
- On Ollama the head costs 920 MiB fixed plus 3.0 MiB per 1k tokens of
  context.

Deployed local routes after this campaign:

| tag | use |
| --- | --- |
| `q27-UD-Q2_K_XL-96k` | the default. It runs next to a working desktop: 37.2 tok/s decode, 1,355 tok/s prefill |
| `q27-UD-IQ3_S-128k` | the quality pick |
| `q27-UD-IQ2_XXS-192k` | maximum context |

### v8: acceptance instrument (2026-09-11 → 09-17)

`ollama-bench/results/v8/`

v7 hit its ceiling, so v8 asks go/no-go questions for specific uses instead of
ranking quants. It has three items: agentic tool use, long-context summary
occupancy, and abstention. Each instrument was checked in both directions: a
perfect answer scores 1.0 and an all-wrong answer scores 0.0.

Phase 0 findings:
- On Ollama, `/v1` forces `top_p = 1.0` and ignores `num_ctx`, so the native
  API is the path of record.
- Served decode was **64.5 tok/s** (`UD-Q2_K_XL`) and **56.6 tok/s**
  (`UD-IQ3_S`).

### v8.1: quant speed matrix on both cards (2026-09-19)

*Raw data not yet in this repo.* Each result is a p50 over 3 runs for each
arm and prompt kind. Prompt kinds are K, L (long input), M, P and S. MTP is on
where the draft acceptance column is filled in.

`llama-bench` on the **5090**:

| arm | pp512 tok/s | tg128 tok/s (d0) | tg128 tok/s (d16k) |
| --- | ---: | ---: | ---: |
| PrismML `PQ2_0` | 4,084 | 126.9 | 91.0 |
| PrismML `PTQ1_0` | 1,907 | 120.7 | 87.6 |
| ByteShape-GPU-1 | 3,972 | 113.3 | 81.6 |
| GSQ-RCO-IQ2_S | 3,435 | 104.5 | 77.3 |
| UD-Q2_K_XL | 3,643 | 103.3 | 76.8 |
| UD-IQ3_XXS | 3,745 | 97.4 | 73.2 |
| UD-IQ3_S | 3,687 | 92.0 | 70.1 |
| UD-Q3_K_XL | 3,860 | 88.3 | 68.1 |
| UD-Q4_K_XL | 3,741 | 73.9 | 59.0 |

Served decode with MTP on the 5090 (p50 tok/s; M and S are short-output kinds,
P is the shared cross-card prompt):

| arm | M | S | P | draft acceptance (M) |
| --- | ---: | ---: | ---: | ---: |
| ByteShape-GPU-1 | 220.7 | 219.8 | 138.6 | 0.82 |
| UD-Q2_K_XL | 211.4 | 203.2 | 134.9 | 0.81 |
| UD-IQ3_XXS | 205.7 | 198.9 | 127.0 | 0.80 |
| UD-IQ3_S | 196.4 | 190.4 | 123.3 | 0.82 |
| UD-Q4_K_XL | 140.6 | 137.9 | 90.4 | 0.82 |

The community MTP and DFlash2 add-ons for Bonsai `PQ2_0` give 1.33x–1.55x on
most prompt kinds but **slow down the P kind (0.85x)**, where draft acceptance
falls to about 0.30. Neither add-on is published by PrismML. No generation was
flagged for looping.

### Seat-prompt trials (2026-09-20 → 09-21)

*Raw data not yet in this repo.* The prompt was *"How fast is pluto right
now"*. Ground truth from `de440s`: **5.22 km/s**, 35.60 AU, receding. Answering
it correctly requires computing an ephemeris, not recalling a figure.

| setup | card | n | correct |
| --- | --- | ---: | ---: |
| 27B `UD-Q4_K_XL`, baseline prompt | 5090 | 10 | 6/10 |
| 27B `UD-Q4_K_XL`, "change 2" | 5090 | 10 | **9/10** |
| 27B `UD-Q2_K_XL`, baseline prompt | 5080 | 15 | 7/15 |
| 27B `UD-Q2_K_XL`, "change 2" | 5080 | 15 | 7/15 |
| 27B `UD-Q2_K_XL`, each sentence of change 2 alone | 5080 | 15 + 15 | 9/15, 9/15 |

- **Nothing is significant.** Pooled, the difference is +12 percentage points,
  with a 95% interval of −15 to +39 and p=0.57.
- "Change 2" reads: *"Read a failed call's error before the next attempt and
  fix what it names… If two attempts at the same approach both fail, change
  approach."*
- The recommendation was not to ship it.
- Lowering the sampler's presence penalty from 1.5 to 0 changed nothing (6/10
  either way).
- On the 5080, prefill measured 321 tok/s against 1,545 in the earlier load
  test. The cause has not been isolated.
- Ollama ignores `OLLAMA_NUM_PARALLEL` for this architecture, so the card
  serves one stream at a time.

### Model and harness comparison on the Pluto question (2026-09-21 → 09-22)

| model | setup | n | correct |
| --- | --- | ---: | ---: |
| GLM 5.3 Flash | slbh, hosted | 15 | 15/15 |
| DeepSeek V4.1 Flash | slbh, OpenRouter | 15 | 15/15 |
| Claude Sonnet | Claude Code subagent | 15 | 15/15 |
| gpt-5.6-luna | Codex CLI | 15 | 15/15 |
| MiMo V2.6 Flash | slbh, OpenRouter | 15 | 14/15 |
| Qwen3.8 Flash | slbh, OpenRouter | 15 | 14/15 |
| **Qwen3.8-27B `Q8_0`** | **slbh, 5090** | 15 | **13/15** |
| Claude Haiku | Claude Code subagent | 15 | 10/15 |
| Qwen3.8-27B `UD-Q2_K_XL` | slbh, 5080 | 15 | 7/15 |
| **Qwen3.8-27B `Q8_0`** | **Claude Code, 5090** | 15 | **6/15** |
| Qwen3.8-27B `UD-Q4_K_XL` | slbh, 5090 | 10 | 6/10 |
| **Claude Opus 4.6** | **Claude Code, medium effort** | 15 | **0/15** |

- The comparison of Opus 4.6 and the 27B, both in Claude Code, was
  pre-registered. Opus scored −40 points, with a Newcombe 95% interval of −64
  to −11 and Fisher p=0.017. The verdict holds under every re-reading of the
  audited grades.
- **Neither model called a tool in Claude Code**, so that comparison measures
  what each one recalls, not what it can compute. Opus answered from memory in
  about 6 seconds with Pluto's *mean* orbital speed. In slbh, whose prompt says
  to check with a tool, the same 27B computed the answer in 13 of 15 runs.
- The 5090 served 638 requests on `Q8_0` at 96k context with no truncation,
  using 30.5 of 32.6 GB of VRAM.

---

## RTX 5080 vs RTX 5090

Same arms, prompts, seeds and caps (v8.1, P kind, MTP n-max 3):

| arm | 5080 tok/s | 5090 tok/s | ratio |
| --- | ---: | ---: | ---: |
| PQ2_0 | 79.5 | 124.3 | 1.56x |
| UD-Q2_K_XL | 67.9–73.8 | 126.1–144.2 | 1.86–1.95x |
| UD-IQ3_XXS | 68.4–74.3 | 118.7–130.3 | 1.71–1.77x |
| UD-IQ3_S | 66.0–70.7 | 116.0–129.7 | 1.76–1.83x |
| UD-Q3_K_XL | 64.1–66.6 | 109.3–122.0 | 1.71–1.83x |
| GSQ-RCO-IQ2_S | 67.1–72.2 | 108.8–115.5 | 1.59–1.62x |
| GSQ-RCO-IQ3_S | 61.0–67.2 | 99.5–108.4 | 1.61–1.66x |

Other differences between the cards:

- **Capacity.** On the 5080, `UD-Q3_K_XL` is the largest quant tested that
  fits, at 14.6 GB peak. The 5090 runs `UD-Q4_K_XL` at 256k context
  (28.5 GB resident) or `Q8_0` at 96k (30.5 GB).
- **Cost.** A full v8.1 matrix took 135 GPU-minutes (about $2.23). A 45-trial
  `Q8_0` experiment took 2 h 08 min (about $1.53).
- **Cold start.** The first pod took about 12 minutes from creation to a loaded
  model. Weight download speed depends on the host: Hugging Face ranged from
  11 to 126 MB/s, and a CDN mirror held steady at 17–30 MB/s.

---

## Repository layout

```
ollama-bench/            task-based coding benchmark (local Ollama + hosted refs)
  pibench.py             the harness
  tasks/ … tasks-v5/     versioned task suites (prompt + hidden test.py per task)
  tasks-v4-rejected/     authoring evidence
  results/               per-campaign output: v5, v6, v7, v75, v76, v8, …
runpod-qwen38-5090/      2026-09-08 Runpod RTX 5090 throughput campaign
  build/, manifests/     pinned build
  scripts/, artifacts/   measurement scripts
  prompts/, briefs/      fixed prompt set and worker briefs
  results/               per-round results (incl. round two row-* streams)
  STATUS.md              run log
```

## Grading

The hidden `test.py` is copied into the sandbox as `_hidden_test.py` and run
with `cwd=sandbox` and `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`, under a 60 s
timeout with a process-tree kill.

- A run **passes** if and only if `rc==0` and `'PASS'` appears in stdout.
- The **score** is the last `SCORE n/m` line, as a fraction.
- A grader **timeout** is a fail with score 0.
- Each verdict is one of five: correct, confidently wrong, visibly failed,
  unsafe, or timeout. **Confidently wrong outranks pass rate** when ranking
  arms.

---

## Methodology notes and lessons

These lessons came from mistakes made during the runs, not from planning.

- **Read the answers against the grades.** Re-grading and reading every flipped
  grade catches regressions. It cannot catch a rule that was wrong from the
  start, because that rule never flips anything. Six grader defects were found
  only by an independent audit that read the answers.
- **The engine's own VRAM report is not evidence of fit.** Measure device
  memory, and treat slow decode as a sign of paging.
- **Instruction last.** Filler between the instruction and the generation point
  turns speculative decoding into a copy task and inflates acceptance.
- **Wait on a result count, never on a process name.** A `pgrep -f` waiter that
  matches its own command line never exits, and it idled paid pod time twice.
- **Check more than one download origin.** A pod that is fast to one origin can
  be 0.19 MB/s to another.
- **Keep trials inside their sandbox.** Agents will fetch a 3 GB ephemeris when
  a 33 MB one covers the epoch. Run trials in their own process group, and
  watch disk space on a timer rather than inside the output-reading loop.
- **Retries must append, not overwrite.** Otherwise the hardest runs disappear
  from the record.
- **Pin model aliases.** A silent model-name normalisation served an older
  model while reporting success.

## Provenance

This tree was pruned from 29 MB to 7.3 MB before its first commit. Full taker
transcripts, pi overseer transcripts, llama-server logs and Ollama pull logs
were dropped; the findings extracted from them are kept in the project's
private notes. The analysis write-ups for every campaign above are also kept
there. The v8.1, seat-prompt and model-comparison raw data have not been
imported into this repo yet.

`runpod-qwen38-5090/` moved here on 2026-09-09 from an untracked directory,
so older write-ups cite it by an absolute path.
