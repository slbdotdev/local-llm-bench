# Local LLM Benchmarks

**How good can a 27B open-weight model be on a single consumer GPU, and what
actually moves the result: the quant, the hardware, the harness, or the
prompt?**

I ran a three-week evaluation program to answer that for **Qwen3.8-27B** on an
**RTX 5080 (16 GB)** desktop and a rented **RTX 5090 (32 GB)**. I built the
harnesses, wrote the task suites and graders, pre-registered the comparisons,
and had the grades audited independently before reporting anything. Frontier
hosted models (Claude, GPT, GLM, DeepSeek) served as reference arms.

---

## At a glance

| | |
| --- | --- |
| **Scope** | 15+ campaigns, 2026-09-03 → 09-22 |
| **Model** | Qwen3.8-27B in 20+ GGUF quants, from 1.8 to 8.5 bits per weight |
| **Hardware** | RTX 5080 16 GB (Windows, Ollama); RTX 5090 32 GB (Runpod) |
| **Reference arms** | Claude Opus / Sonnet / Haiku, GPT-5.6 family, GLM 5.3 Flash, DeepSeek V4.1 Flash, MiMo, Qwen3.8 Flash |
| **Harnesses** | pi, slbh (my own Go agent harness), Claude Code, Codex CLI |
| **Stack** | Python, Go, Bash, llama.cpp (CUDA 13.3, `sm_120`), Ollama, vLLM, Runpod, Tailscale, Ansible |
| **Stats** | Fisher exact tests, Newcombe and Wilson intervals, paired t-tests on per-chunk NLL |

---

## Key results

- **Found the best quant for a 16 GB card, with statistical backing.**
  - `UD-IQ3_S` has **54% lower KL divergence** than the next-best candidate and
    beats it on both prose and code (t = −4.1 and −9.0 over 40 chunks).
  - `UD-Q2_K_XL` beat the incumbent quant by 5.7% perplexity while being
    **693 MB smaller**.
- **Unlocked a free 1.25x–2.05x decode speed-up.** The model file already
  contained a trained draft head for speculative decoding (MTP), and the
  engine already supported it; the flag had never been passed. Turning it on
  needed no rebuild and no download.
- **Measured the 5090's advantage directly: 1.56x–1.95x faster decode** on
  identical prompts, seeds and caps, up to **220 tok/s** single-stream. The
  5090 is also the only way to serve the 4-bit and 8-bit quants, which do not
  fit in 16 GB at any context length.
- **Showed the harness matters more than the model on a question that needs a
  live lookup.** Asked *"How fast is Pluto right now?"*:
  - The same 27B scored **13/15** in a harness that tells it to verify with
    tools, and **6/15** in Claude Code's default prompt.
  - **Claude Opus 4.6 scored 0/15** in Claude Code (p = 0.017, pre-registered).
    It answered from memory every time.
- **Kept a promising result from shipping.** A prompt change scored 9/10
  against a 6/10 baseline on the 5090. I replicated it at n=15 on the 5080,
  where it went 7/15 against 7/15; pooled, the difference was p = 0.57. It was
  not shipped.
- **Caught a VRAM measurement that was wrong.** Ollama's own VRAM report said
  13 of 13 configurations fit, including one that was spilling into system
  memory and decoding at 9 tok/s. A second instrument, device-level
  `nvidia-smi` deltas, caught it and became the standard.

---

## What I built

- **`pibench.py`, an agentic coding benchmark.** It runs each task in a seeded
  sandbox, grades it with a hidden test, and gives one of five verdicts:
  correct, *confidently wrong*, visibly failed, unsafe, or timeout. When
  ranking arms, confidently-wrong answers count for more than pass rate.
- **Five generations of task suites (v1–v5, then the 20-slot v7 suite).**
  v5 was written after v4 stopped separating frontier models. Every model
  failed on the same kind of check: requirements stated only in prose, such
  as exact error kinds, offsets and phase precedence. v5 targets that.
- **An acceptance instrument (v8)** that asks go/no-go questions for specific
  uses instead of ranking quants. Each grader was proved in both directions:
  a perfect answer scores 1.0 and an all-wrong answer scores 0.0.
- **Quality, context and throughput matrices.** Perplexity and KLD against a
  `Q8_0` reference, a context-length ladder measured two ways (the engine's
  report and the device), and served decode speed with speculative-decoding
  acceptance rates, across 60+ cells.
- **Pod automation for Runpod.** Checks placement bandwidth against both
  download origins, times the cold start, enforces a hard-stop teardown, and
  verifies the account is empty afterwards. Every rented-GPU run stayed under
  its approved budget: $1.53–$2.23 per campaign.
- **Pre-registered trial rigs** with frozen input hashes, interleaved
  conditions, a retry contract and a classifier pinned by regression tests.
  Every grade was independently audited against the raw answers.

---

## Selected results

### Quant quality on the 5080 (Qwen3.8-27B vs a `Q8_0` reference)

| quant | bits/weight | wikitext-2 PPL | KLD | top-1 agreement | code PPL |
| --- | ---: | ---: | ---: | ---: | ---: |
| UD-IQ1_S | 1.81 | 8.146 | 0.407 | 74.6% | 2.680 |
| UD-IQ2_XXS | 2.13 | 6.874 | 0.221 | 80.5% | 2.277 |
| UD-IQ2_S | 2.45 | 6.461 | 0.140 | 85.4% | 2.147 |
| **UD-Q2_K_XL** | 2.88 | 6.126 | 0.093 | 87.9% | 2.088 |
| **UD-IQ3_S** | 3.53 | **5.940** | **0.043** | **92.1%** | **2.046** |

Deployed as three local routes: a daily default (`UD-Q2_K_XL`, 96k context),
a quality pick (`UD-IQ3_S`, 128k) and a long-context pick (`UD-IQ2_XXS`, 192k).

### RTX 5080 vs RTX 5090 decode (same prompts, seeds and caps)

| quant | 5080 tok/s | 5090 tok/s | speed-up |
| --- | ---: | ---: | ---: |
| UD-Q2_K_XL | 67.9–73.8 | 126.1–144.2 | 1.86–1.95x |
| UD-IQ3_S | 66.0–70.7 | 116.0–129.7 | 1.76–1.83x |
| UD-Q3_K_XL | 64.1–66.6 | 109.3–122.0 | 1.71–1.83x |
| PrismML PQ2_0 | 79.5 | 124.3 | 1.56x |

With MTP on, the 5090 served `UD-Q2_K_XL` at up to 211 tok/s and
ByteShape-GPU-1 at up to 221 tok/s, with 81–82% draft acceptance on those
prompts.

### Coding benchmark on the 5080 (2-bit quant)

| suite | result |
| --- | --- |
| v6 on the v5 suite, 9 quants | 111/148 passed (75%); IQ2_M chosen for its 4% confidently-wrong rate |
| v7, 20 agentic tasks | 19–20/20 across three quants: the suite, not the quant, was the ceiling |
| v7.5, harness swap | pi 20/20, slbh 20/20: the harness changed cost (about 2x), not correctness |
| v7.6, tool-layer changes | 4 pre-registered candidates: 1 kept, 3 reverted on cost |

### Same question, 12 models and harnesses

| model | setup | correct |
| --- | --- | ---: |
| GLM 5.3 Flash · DeepSeek V4.1 Flash · Sonnet · gpt-5.6-luna | various | 15/15 |
| MiMo V2.6 Flash · Qwen3.8 Flash | slbh, OpenRouter | 14/15 |
| **Qwen3.8-27B `Q8_0`** | **slbh, 5090** | **13/15** |
| Claude Haiku | Claude Code subagent | 10/15 |
| Qwen3.8-27B `UD-Q2_K_XL` | slbh, 5080 | 7/15 |
| Qwen3.8-27B `Q8_0` | Claude Code, 5090 | 6/15 |
| **Claude Opus 4.6** | **Claude Code, medium effort** | **0/15** |

The hosted flash models reached a correct answer with about **1/20th** of the
local model's work tokens.

---

## How I worked

- **Pre-register, then measure.** Hypotheses, stopping rules and keep/revert
  criteria were written before the data came in, so a result could not be read
  backwards into the reason it was tried.
- **Report what the data supports.** Null results, withdrawn results and
  non-replications are reported as prominently as wins. One throughput round
  was withdrawn when I found its prompt design caused the model to echo
  padding, which inflated the numbers.
- **Audit the grader, not just the model.** Twelve grader defects were found
  and fixed. The six that never changed a grade were found only by
  independently reading every answer against its grade.
- **Use two instruments when one might be wrong.** VRAM was measured by the
  engine and by the device, and served decode speed by `llama-bench` and by
  the live server.
- **Control confounds explicitly.** Conditions were interleaved on a shared
  desktop GPU, input hashes were frozen, and a trial that ran on the wrong
  backend was rejected rather than aggregated.
- **Keep cost in check.** Every rented-GPU run was budgeted and torn down
  automatically, with the teardown verified.

---

## Repository layout

```
ollama-bench/            agentic coding benchmark
  pibench.py             harness: sandbox, hidden-test grading, five-way verdicts
  tasks/ … tasks-v5/     versioned task suites (prompt + hidden test.py per task)
  results/               per-campaign data and write-ups: v5, v6, v7, v75, v76, v8
runpod-qwen38-5090/      RTX 5090 single-stream throughput campaign
  build/, manifests/     pinned engine build
  scripts/, prompts/     measurement harness and fixed prompt set
  results/, STATUS.md    per-round results and run log
```

The v8.1 speed matrix, the seat-prompt trials and the model comparison live in
separate rigs and are summarized above. Their raw data has not been imported
here yet.

---

*Built by [slb](https://slb.dev).*
