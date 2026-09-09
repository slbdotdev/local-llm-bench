# Window three, arm B — measured single-stream result (corrected)

Target `sakamakismile/Qwen3.8-27B-MTP-NVFP4`, revision
`a0b936f0bbcb362c38d39840602c8d7b2476a9fc`, native `qwen3_5_mtp` only, no
DFlash2 anywhere. Official image pinned by digest
`vllm/vllm-openai:v0.28.0-cu129@sha256:50509e700235cea487715cedeb501d20a1cd15fa6a54ce93688284bd0d96995d`.
Secure RTX 5090, host CUDA 13.0, pod-local disk, MCP tooling only.
Datacenter EU-RO-1 (EU-CZ-1 reported zero RTX 5090 stock for the whole window).

**Read the corrections section before quoting any earlier arm-B number.**

## Verdict

**FAIL against 300 output tokens/s single stream — at 184 t/s median decode,
194 t/s best, with MTP n=3.** That is 61–65% of target, not a hopeless gap.

## Boot gate — PASS

Quantized weights did **not** fall back to `torch.bfloat16`.

- `WARNING [compressed_tensors_w4a4_nvfp4.py:102] In NVFP4 linear, the weight
  global scale is different for parallel layers (e.g. q_proj, k_proj, v_proj).`
- `INFO [__init__.py:1100] Using FlashInferCutlassNvFp4LinearKernel for NVFP4 GEMM`
- `INFO [gpu_model_runner.py:5515] Model loading took 18.48 GiB memory`
- The only `torch.bfloat16` is the activation/query dtype: `FlashInfer resolved
  query dtypes: prefill=torch.bfloat16, decode=torch.bfloat16,
  decode_backend=xqa, kv_cache_dtype=torch.float8_e4m3fn, arch=sm120`

## Measurements — streaming, TTFT excluded

Decode rate is `(completion_tokens - 1) / (total - TTFT)`. Every prompt carries
a unique salt so prefix caching never answers the prefill. Rows with an early
EOS (<16 tokens) are excluded from the decode statistic and reported separately.

| arm | prompt tokens | median decode t/s | max | TTFT s | prefill t/s | tau |
|---|---:|---:|---:|---:|---:|---:|
| AR | 8201–8234 | 77.25 | 77.42 | 1.346 | 6111 | — |
| AR | 65512/65544 | 71.36 | 71.41 | 10.262 | 6392 | — |
| AR | 130935 | 66.19 | 66.19 | 29.303 | 4468 | — |
| AR, encoder dropped | 8198–8234 | 77.71 | 77.74 | 1.340 | 6138 | — |
| MTP n=3 | 8206/8232 | 184.32 | 194.47 | 1.600 | 5170 | 3.818 |
| MTP n=3 | 65511/65548 | 184.60 | 184.78 | 11.512 | 5701 | 4.000 |

`tau` is `1 + accepted/drafts` over that window from
`vllm:spec_decode_num_accepted_tokens_total` / `..._drafts_total`. At 8K:
148 drafts, 444 draft tokens, 417 accepted — per-position acceptance **0.939**.
The 64K value is saturated at the n=3 ceiling because the synthetic context
padding is trivially predictable; it is a padding artifact, not a workload
result.

**MTP n=3 is a 2.4x decode speedup over AR and it holds from 8K to 64K.**

## Peak VRAM

28.96 GiB with MTP n=3 at 131072, under the 30 GB gate:
`Actual usage is 19.76 GiB for consumed memory (weights + non-torch), 1.06 GiB
for peak activation, and 0.11 GiB for CUDAGraph memory. ... Current kv cache
memory in use is 8.03 GiB.` No `nvidia-smi` reading — MCP exposes no on-pod
exec tool.

## Vision encoder (owner ruling)

`--limit-mm-per-prompt '{"image":0,"video":0}'` **does drop the encoder
weights**, not merely the profiling. With it, `gpu_worker.py:804` reports
**17.98 GiB** for weights *plus* non-torch overhead, strictly below the
**18.48 GiB** that weights alone took without it; the tower is ~0.41B bf16
params (depth 27, hidden 1152, intermediate 4304) ≈ 0.8 GiB, the right size for
the gap. Corroborating: `qwen_triton_warmup.py:270 Warming up Qwen Triton
kernels for model_type=qwen3_5_text`, and the `Encoder cache will be
initialized ... profiled with 1 image items` line is gone.

It is **throughput-neutral**: 77.71 t/s decode with the encoder dropped vs
77.25 t/s with it, at the same context.

It was **not** the cause of the 131072 OOMs. It recovers ~0.8 GiB against an
~11.7 GiB shortfall — about 7%. The fit lever is `--max-num-seqs 4
--max-num-batched-tokens 4096`: at vLLM's default `max_num_seqs=1024` this
hybrid GDN model holds ~11.7 GiB of per-request state, and the engine OOMs at
`_init_minimal_kv_cache_for_profiling` (`Tried to allocate 784.00 MiB … 30.22
GiB is allocated by PyTorch` against 18.48 GiB of weights). Keep the flag — it
is free memory and free of cost — but it is not the fix.

## What actually costs time at long context

Prefill, not decode. TTFT is 1.35 s at 8K, 10.26 s at 64K, 29.30 s at 128K,
while decode falls only 77.25 → 71.36 → 66.19 t/s. Any 128K interactive use is
TTFT-bound.

## Correctness

Each server is self-deterministic. Greedy MTP output diverged from greedy AR on
all four fixed prompts (common prefixes 62/25/19/27 chars) — a spec correctness
fail under plan §12, so `n=7` was not attempted. Caveat: separate processes with
separate FlashInfer NVFP4 autotune caches, and the checkpoint warns its
per-layer NVFP4 global scales differ. Not attributable to the MTP module alone.

Separately, the model emits an early EOS on some padded prompts (completions of
1, 3, 7, 19, 35 tokens were seen on both configs). This is a property of the
synthetic padding, not of a config.

## Corrections to earlier arm-B reporting

1. **Withdrawn: "decode collapses 57 → 10.4 → 2.0 t/s with context."** The
   first driver divided completion tokens by *total* wall time, folding prefill
   into the rate. `ar-64k` was 12.31 s total with a 9.95 s prefill for 128
   tokens. Corrected decode is 77 → 71 → 66 t/s.
2. **Withdrawn: the GDN Triton-fallback line explains the collapse.** The boot
   line `Falling back to the Triton GDN decode path:
   torch.ops._C.fused_gdn_decode_post_conv_mtp is not built` is real, but there
   is no collapse for it to explain.
3. **Withdrawn: "MTP gives 1.22x / 1.02x / 0.90x."** Same contaminated metric.
   Corrected: 2.4x at 8K and 64K.
4. **Withdrawn: "the encoder-dropped config is a 12x regression."** Those rows
   returned 1–7 completion tokens (early EOS), so the ratio measured a ~1 s
   prefill against a handful of tokens. It is throughput-neutral.
5. Best single-stream figure rises from a claimed 81.0 t/s to **194.47 t/s**.

Superseded files kept for audit: `ar-*.jsonl`, `mtp3-*.jsonl`,
`control-8k-*.jsonl`. Authoritative files: `stream-*.jsonl`.
