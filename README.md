# Local LLM Benchmarks

**How good can a 27B open-weight model be on a single consumer GPU, and what
actually moves the result: the quant, the engine, the hardware, the harness,
or the prompt?**

A three-week evaluation program on **Qwen3.8-27B**, run on an **RTX 5080
(16 GB)** desktop and rented **RTX 5090 (32 GB)** cloud GPUs. I built the
harnesses, wrote the task suites and graders, registered each comparison
before running it, and had the grades audited independently. Hosted frontier
models (Claude, GPT, GLM, DeepSeek) served as reference arms.

---

## At a glance

| | |
| --- | --- |
| **Scope** | 15+ campaigns, 2026-09-03 → 09-23 |
| **Model** | Qwen3.8-27B in 20+ GGUF quants (1.8–8.5 bits per weight) and two NVFP4 checkpoints |
| **Hardware** | RTX 5080 16 GB (Windows, Ollama); RTX 5090 32 GB (Runpod community and secure cloud) |
| **Engines** | llama.cpp, Ollama, NInfer and its Cinference fork, vLLM |
| **Reference arms** | Claude Opus, Sonnet and Haiku; GPT-5.6; GLM 5.3 Flash; DeepSeek V4.1 Flash; MiMo V2.6 Flash; Qwen3.8 Flash |
| **Harnesses** | pi, slbh (my own Go agent harness), Claude Code, Codex CLI |
| **Stack** | Python, Go, Bash, CUDA 13 (`sm_120`), Runpod, Tailscale, Ansible, Open WebUI, Caddy |
| **Statistics** | Fisher exact tests, Newcombe and Wilson intervals, paired t-tests on per-chunk NLL |

---

## Key results

- **The best quant for a 16 GB card, with statistical backing.**
  - `UD-IQ3_S` has **54% lower KL divergence** than the next-best candidate
    and beats it on prose and on code (t = −4.1 and −9.0 over 40 chunks).
  - `UD-Q2_K_XL` beat the incumbent quant by 5.7% perplexity while being
    693 MB smaller.
- **A 1.25–2.05x speed-up that needed no new software.** The GGUF files
  already contained a trained multi-token-prediction (MTP) draft head, and the
  engine already supported it; enabling it took one flag.
- **450 tok/s reproduced, and put in context.** A published NVFP4 recipe
  reports 450 tok/s on a 5090. On stock weights it measured 426–457 tok/s,
  on the same recall workload. That workload copies text from the prompt, so
  nearly every draft is accepted. On ordinary prose the same configuration
  decodes at 113–141 tok/s.
- **A better general-purpose configuration than the recipe's.** The DFlash2
  block drafter decoded 267–282 tok/s on a mixed short-prompt set, against 192
  for the recipe's MTP-10, and 254–275 against about 180 on long sampled
  reasoning.
- **Engine choice matters as much as the GPU.** With speculation off on both
  sides, NInfer decoded 34–38% faster than vLLM on the same model. With each
  engine at its best, NInfer was 2.3–2.4x faster.
- **A public chat demo on a rented 5090.** The winning configuration serves an
  Open WebUI front end over Tailscale:
  - a median of about 240 tok/s on real conversations, against about 105 on
    the 5080;
  - two concurrent chats, at about 125–130 tok/s each when both are
    generating.
- **The harness mattered more than the model on a question that needs a live
  lookup.** Asked *"How fast is Pluto right now?"*:
  - The same 27B scored **13/15** in a harness that tells it to verify with
    tools, and **6/15** in Claude Code's default prompt.
  - Claude Opus 4.6 scored 0/15 in Claude Code (p = 0.017, registered in
    advance), answering from memory every time.
- **A promising prompt change was not shipped.** It scored 9/10 against 6/10
  on the 5090, but went 7/15 against 7/15 when replicated at n = 15 on the
  5080 (pooled p = 0.57).
- **A wrong VRAM reading was caught.** Ollama reported that 13 of 13
  configurations fit, including one that was spilling into system memory and
  decoding at 9 tok/s. Device-level `nvidia-smi` readings caught it and became
  the standard.
- **Healthy-looking cloud GPUs were not always usable.** On one day, 7 of 8
  community 5090s passed `nvidia-smi` but could not start CUDA. Another host
  was already running someone else's workload. A third data center could only
  download at 1–2 MB/s per connection. The placement probe now tests each of
  these before setup starts.

---

## What I built

- **`pibench.py`, an agentic coding benchmark.** It runs each task in a seeded
  sandbox, grades it with a hidden test, and gives one of five verdicts:
  correct, *confidently wrong*, visibly failed, unsafe, or timeout. When
  ranking arms, confidently-wrong answers weigh more than pass rate.
- **Task suites v1–v5 and the 20-task v7 suite.** v5 was written when v4
  stopped separating frontier models. It targets the kind of check every
  model had failed: requirements stated only in prose, such as exact error
  kinds, offsets and phase precedence.
- **An acceptance instrument (v8)** that answers go/no-go questions for
  specific uses instead of ranking quants. Every grader was checked in both
  directions: a perfect answer scores 1.0 and an all-wrong answer scores 0.0.
- **Quality, context and throughput matrices** across 60+ cells:
  - perplexity and KLD against a `Q8_0` reference;
  - a context-length ladder measured by the engine and by the device;
  - served decode speed with speculative-decoding acceptance.
- **A throughput harness for three engines** (llama.cpp, NInfer, vLLM). It
  times every request by the server's own counters and by the client's clock,
  which agreed to within 1% on every row. It flags prefix-cache hits as
  invalid and drives a whole campaign against a deadline.
- **Automation for rented GPUs.** Before setup starts, each host
  must show:
  - a working CUDA driver, checked with `cuInit`;
  - an idle GPU;
  - enough parallel download bandwidth from every origin the setup uses.

  Pods tear down on a hard timer and leave the account verified empty.
  Measurement campaigns cost $1.53–$2.23 each.
- **Registered trial rigs** with frozen input hashes, interleaved conditions,
  a retry contract and a classifier pinned by regression tests. Every grade
  was independently audited against the raw answers.

---

## Selected results

### Quant quality on the 5080 (Qwen3.8-27B against a `Q8_0` reference)

| quant | bits/weight | wikitext-2 PPL | KLD | top-1 agreement | code PPL |
| --- | ---: | ---: | ---: | ---: | ---: |
| UD-IQ1_S | 1.81 | 8.146 | 0.407 | 74.6% | 2.680 |
| UD-IQ2_XXS | 2.13 | 6.874 | 0.221 | 80.5% | 2.277 |
| UD-IQ2_S | 2.45 | 6.461 | 0.140 | 85.4% | 2.147 |
| **UD-Q2_K_XL** | 2.88 | 6.126 | 0.093 | 87.9% | 2.088 |
| **UD-IQ3_S** | 3.53 | **5.940** | **0.043** | **92.1%** | **2.046** |

The 5080 serves `UD-Q2_K_XL` at 64k context with the MTP head on: it keeps
the head, terminates reliably with reasoning on, and fits 64k beside a working
desktop, where `UD-IQ3_S` with the head fits only an idle one.

### RTX 5080 against RTX 5090, GGUF decode (same prompts, seeds and caps)

| quant | 5080 tok/s | 5090 tok/s | speed-up |
| --- | ---: | ---: | ---: |
| UD-Q2_K_XL | 67.9–73.8 | 126.1–144.2 | 1.86–1.95x |
| UD-IQ3_S | 66.0–70.7 | 116.0–129.7 | 1.76–1.83x |
| UD-Q3_K_XL | 64.1–66.6 | 109.3–122.0 | 1.71–1.83x |
| PrismML PQ2_0 | 79.5 | 124.3 | 1.56x |

### NVFP4 on the 5090 (single stream, tok/s)

| workload | no speculation | recipe (MTP-10) | best | best configuration |
| --- | ---: | ---: | ---: | --- |
| Recall, 8K / 131K / 260K | 76 / 66 / 59 | **442 / 319 / 264** | same | the recipe |
| Code, 1,024 tokens | 77 | 281 | **396–402** | DFlash2, K = 10–15 |
| Six short prompts, median | 77 | 192 | **267–282** | DFlash2, K = 7–10 |
| Reasoning, sampled, 4K tokens | 77 | 180–183 | **254–275** | DFlash2, K = 7 |
| Prose summary, 8K / 131K | 76 / 67 | 117 / 89 | **142 / 122** | MTP-4 |
| 8 concurrent requests, total | 423 | — | **673** | MTP-3 |
| vLLM, same workloads | 56 | — | 122 short / 187 recall | MTP-5 |

- **Long drafts pay only on predictable text.** MTP gains up to 10 draft
  tokens on recall and JSON, but peaks at 3–4 on prose.
- **KV cache and prefill settings:** 8- and 4-bit KV formats sit within 10%
  of each other, while bf16 costs about a fifth of decode at 131K. A 4096
  prefill chunk gives 6–12% more prefill throughput than the recipe's 1024.
- **Carried back to the 5080:**
  - KV format and prefill batch size made no measurable difference at up to
    60K context.
  - Three draft tokens beat two by 4–7% with reasoning on, and cost about
    4% on free prose.

### Coding benchmark on the 5080 (2-bit quant)

| suite | result |
| --- | --- |
| v6 (v5 tasks, 9 quants) | 111/148 passed (75%); IQ2_M chosen for its 4% confidently-wrong rate |
| v7, 20 agentic tasks | 19–20/20 across three quants: the suite, not the quant, was the ceiling |
| v7.5, harness swap | pi and slbh both 20/20; the harness changed cost (about 2x), not correctness |
| v7.6, tool-layer changes | 4 registered candidates: 1 kept, 3 reverted on cost |

### Same question, 12 models and harnesses

| model | setup | correct |
| --- | --- | ---: |
| GLM 5.3 Flash, DeepSeek V4.1 Flash, Claude Sonnet, GPT-5.6 Luna | various | 15/15 |
| MiMo V2.6 Flash, Qwen3.8 Flash | slbh, OpenRouter | 14/15 |
| **Qwen3.8-27B `Q8_0`** | **slbh, 5090** | **13/15** |
| Claude Haiku | Claude Code subagent | 10/15 |
| Qwen3.8-27B `UD-Q2_K_XL` | slbh, 5080 | 7/15 |
| Qwen3.8-27B `Q8_0` | Claude Code, 5090 | 6/15 |
| Claude Opus 4.6 | Claude Code, medium effort | 0/15 |

The hosted flash models reached a correct answer with about 1/20th of the
local model's work tokens.

---

## Method

- **Register first, then measure.** Hypotheses, stopping rules and keep or
  revert criteria were written before the data came in.
- **Report what the data supports.** Null results, withdrawals and
  non-replications are reported alongside the wins. One throughput round was
  withdrawn because its prompts made the model echo padding, which inflated
  the numbers.
- **Audit the grader as well as the model.** Twelve grader defects were found
  and fixed. Six of them never changed a grade and were found only by reading
  every answer against its grade.
- **Use two instruments where one might be wrong.** VRAM was read from the
  engine and from the device. Decode speed was read from the server's
  counters and from the client's clock.
- **Control confounds.** Conditions were interleaved, repeats were run to
  measure drift, and input hashes were frozen. A trial that ran on the wrong
  backend was rejected rather than aggregated.
- **Budget every rented GPU.** Each campaign was costed in advance, torn down
  on a timer, and checked for an empty account afterwards.

---

## Repository layout

```
ollama-bench/            agentic coding benchmark
  pibench.py             harness: sandbox, hidden-test grading, five-way verdicts
  tasks/ … tasks-v5/     versioned task suites (prompt + hidden test.py per task)
  results/               per-campaign data and write-ups: v5, v6, v7, v75, v76, v8
runpod-qwen38-5090/      RTX 5090 single-stream GGUF throughput campaign
  build/, manifests/     pinned engine build
  scripts/, prompts/     measurement harness and fixed prompt set
  results/, STATUS.md    per-round results and run log
```

The v8.1 speed matrix, the seat-prompt trials, the model comparison, the NVFP4
campaign and the chat-serving lane live in separate rigs and are summarized
above. Their raw data has not been imported here.

---

*Built by [slb](https://slb.dev).*
