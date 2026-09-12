# Cachy GTX 1080 Ti options — 2026-09-08

## Outcome

The best all-round choice is `qwen3:8b` (`Q4_K_M`) in the scratch Vulkan
Ollama build, with `think: false` for interactive work and `num_ctx: 32768`.
It gives the strongest combination tested: an acceptable summary, the best
next-turn suggestion, exact needle retrieval at 23,857 prompt tokens, and a
full-GPU 32k run. `qwen2.5:7b` Q4 is the better low-latency choice: it decodes
faster and uses less VRAM. Q5 did not earn its extra size. Qwen3 14B is a
short-context quality option, not a practical general-purpose model on this
card. The 27B IQ2_M model technically runs, but CPU offload makes it a
slow specialist rather than a useful default.

| Model / quant | Practical context ceiling | VRAM at test | Prompt processing at ceiling | Decode | Summary | Next turn | NIAH |
|---|---:|---:|---:|---:|---|---|---|
| `qwen3:8b` Q4_K_M, q8 KV | 32k tested (package metadata: 40,960) | 7.562 GB API-reported at 32k | 30,417 tok / 150.889 s = 201.6 tok/s | 34.2 tok/s at 32k; 53.8 short | Good, preserves caveats | Best of tested | Exact `cobalt-7319` at 23,857 tok |
| `qwen2.5:7b` Q4_K_M, q8 KV | 32k native/tested | 5.698 GB at 32k | 30,430 / 111.344 s = 273.3 tok/s | 51.4 at 32k; 63–66 short | Good | Best low-latency option | Exact at 23,870 tok |
| `qwen2.5:7b` Q5_K_M, q8 KV | 32k native/tested | 6.392 GB at 32k | 30,430 / 125.169 s = 243.1 tok/s | 41.5 at 32k; 47.6 short | Good | Usable but less time-aware than Q4 | Exact at 23,870 tok |
| `qwen3:14b` Q4_K_M, q8 KV | 4k clean; 8k verified with CPU spill | 9.321 GB at 4k; 9.494 GB at 8k | 129 / 1.154 s = 111.8 tok/s warm at 4k; 7,707 / 40.455 s = 190.5 tok/s at 8k NIAH | 29.8 at 4k; 22.4 at 8k | Good | Mixed/noisy | Exact at 7,707 tok, but spilled |
| Local qwen3.8 27B IQ2_M, q8 KV | 4k tested; 16k configured but not recommended | 8.669 GiB on GPU; 1.9 GiB weights CPU-mapped | 9,404 / 186.558 s = 50.4 tok/s at 16k | 7.38 at 9.4k input | Good | Coherent, but slow | Exact at 9,404 tok; very slow |

For short prompts, the practical decode ordering is Qwen2.5 Q4 (about
63–66 tok/s), Qwen3 8B (about 54 tok/s), Qwen2.5 Q5 (about 48 tok/s), Qwen3
14B (about 30 tok/s), then 27B IQ2_M (about 9 tok/s). Long-context decode
slows as the KV cache grows.

## Recommendations by task

- **Summarization:** choose Qwen3 8B Q4 for quality and caveat retention. Use
  Qwen2.5 7B Q4 when response latency matters more than instruction quality.
  The 14B answer was also good at 4k, but its cold load was about 205 seconds.
- **Next-turn suggestion:** choose Qwen2.5 7B Q4 for a small, fast local
  assistant. Its answer was a concrete microwave spinach-and-egg omelette
  with a 1.523-second total warm request. Qwen3 8B was slightly more useful
  in wording (1.171 seconds); use it when quality outweighs a little VRAM.
- **Needle-in-a-haystack:** choose Qwen3 8B Q4 at 24k–32k. It returned the
  exact needle at 23,857 prompt tokens and still fits the GPU at 32k. Qwen2.5
  7B Q4 is the faster alternative and also retrieved exactly at 23,870.
- **Short-context larger model:** Qwen3 14B Q4 is viable for quality-sensitive
  work at 4k. Its 8k NIAH result is real but involves CPU weight spill and
  should not be treated as a clean 8k serving target.

## What was measured

The host was `cachyos-x8664`: NVIDIA GeForce GTX 1080 Ti, 11,264 MiB,
driver 580.178.04, Ryzen 5 5600X (12 logical CPUs), and 15 GiB RAM. At the
final idle check the card had 1,099 MiB used by the desktop. Vulkan identified
the same NVIDIA device and driver.

The managed `/usr/bin/ollama` service was left untouched. It is package
version 0.33.3-1.1 and remained CPU-only despite its existing
`OLLAMA_VULKAN=true` environment. I unpacked the matching `ollama-vulkan`
package into the scratch directory and ran a second Ollama server only on
`127.0.0.1:11435`, with the scratch model directory and Vulkan backend. Its
logs show Vulkan layer placement on the GTX 1080 Ti. The scratch server and
all of its runners were stopped after testing.

Models came from the Ollama library pages [qwen2.5](https://ollama.com/library/qwen2.5)
and [qwen3](https://ollama.com/library/qwen3):

- `qwen2.5:7b-instruct-q4_K_M`, 4.7 GB GGUF, digest prefix `845dbda0ea48`.
- `qwen2.5:7b-instruct-q5_K_M`, 5.4 GB GGUF, digest prefix `a1040ddd2b49`.
- `qwen3:8b`, 5.2 GB GGUF, digest prefix `500a1f067a9f`.
- `qwen3:14b`, 9.3 GB GGUF, digest prefix `bdbd181c33f`.

The 27B test used the existing local FRACTAL blob
`q27-IQ2_M-24k:latest`, Qwen3.8 27.3B IQ2_M, copied to cachy; it has no
public pull URL in this experiment. The model blob is 10,873,357,920 bytes.
At 4k the runner offloaded 59/66 layers: 8,226.45 MiB Vulkan model buffer,
1,904.79 MiB CPU-mapped model buffer, 136 MiB KV, and 157.73 MiB Vulkan
compute. At 16k it reported an 8.4 GiB GPU runner and took 177.21 seconds
to prefill 9,400 tokens before returning the NIAH result.

### Pascal and KV-cache findings

- Q8 KV with flash attention disabled fails immediately with
  `quantized V cache requires flash_attn to be enabled`. All q8 measurements
  therefore used `OLLAMA_KV_CACHE_TYPE=q8_0` and flash attention enabled.
- On Qwen2.5 7B, the stable 8k–32k q8 KV slope was about 32.5 KiB/token for
  both Q4 and Q5. Q4 rose from 4.899 GB at 8k to 5.698 GB at 32k; Q5 rose
  from 5.859 GB at 16k to 6.392 GB at 32k.
- Qwen3 8B rose from 5.287 GB at 4k to 7.562 GB at 32k. It still had useful
  headroom on the 11 GB card, but its long-context decode fell to 34.2 tok/s.
- Qwen3 14B used 9.321 GB at 4k. At 8k only 40/41 layers remained on GPU;
  at 16k only 37/41 did, and decode fell to 12.2 tok/s with visibly degraded
  output. This is the practical ceiling despite the nominal model context.
- A Qwen2.5 Q4 f16-KV comparison at about 4k used 4.741 GB and decoded at
  66.9 tok/s, versus 4.631 GB and 65.7 tok/s for q8 KV. f16 avoided the q8
  flash-attention requirement but did not provide a meaningful Pascal speed
  win; q8 is the more memory-efficient default.
- Ollama's runner context reservation matters. A 4k `num_ctx` allowed only
  about 2,050 input tokens; an attempted 16k NIAH was truncated to 8,194.
  The corrected NIAH runs used a runner context at least twice the document
  size. A 64k request against the Qwen2.5 32,768-token runner was truncated
  to an effective 16,386-token input and was not counted as a 64k result.

### Quality checks and raw numbers

The summary prompt described a battery-bus switch with 42% lifecycle-emission
reduction, mineral-extraction and coal-electricity caveats, an 18% winter
range loss, and council conditions. Qwen3 8B returned all four facts in
three bullets. Qwen2.5 Q4/Q5 retained the main 42% and caveat facts. Qwen3
14B and 27B also produced acceptable three-bullet summaries.

The next-turn prompt supplied eggs, spinach, a microwave, and one bowl.
Qwen3 8B suggested beating eggs with spinach and microwaving for 45–60
seconds. Qwen2.5 Q4 suggested a 1–1.5 minute microwave omelette. Qwen2.5
Q5 suggested a baked muffin-tin omelette (usable but less context-aware),
and Qwen3 14B suggested a no-cook “scramble” (mixed quality). Q27 gave a
coherent two-minute microwave scramble.

NIAH used repetitive synthetic archive lines with the midpoint needle
`emergency contact code cobalt-7319`; the required answer was only
`cobalt-7319`. Successful runs were:

- Qwen3 8B Q4: 23,857 prompt tokens, 105.917 s prefill, 0.217 s / 8 output
  tokens, 106.231 s total.
- Qwen2.5 7B Q4: 23,870 prompt tokens, 78.842 s prefill, 0.148 s / 8 output
  tokens, 302.7 tok/s prefill and 54.0 tok/s decode.
- Qwen2.5 7B Q5: 23,870 prompt tokens, 89.502 s prefill, 0.184 s / 8
  output tokens, 266.7 tok/s prefill and 43.4 tok/s decode.
- Qwen3 14B Q4: 7,707 prompt tokens, 40.455 s prefill, 0.358 s / 8 output
  tokens, 190.5 tok/s prefill and 22.4 tok/s decode.
- Qwen3.8 27B IQ2_M: 9,404 prompt tokens, 186.558 s prefill, 0.948 s / 8
  output tokens, 50.4 tok/s prefill and 7.38 tok/s decode.

Representative long-context Qwen2.5/Qwen3 request metrics above are Ollama
API durations in nanoseconds converted to seconds; short-task metrics use
the same API fields. Cold model-load time is reported separately where it
changes the recommendation: Qwen3 14B's first 4k load was 204.793 s, while
the tested 7B/8B runners were generally warm or incurred 44–85 s context
reloads. The full JSON responses and server logs stayed on cachy, the machine
that produced them, in temporary state that is not version controlled and is
not part of this record. The figures quoted here are the record.

Limitations: this is a hands-on options map, not a blind benchmark; quality
judgments use one controlled prompt per task class. I did not claim native
64k behavior where the runner truncated input, and I did not modify the
managed service or ansible configuration.

`org/cachy-1080ti-options-2026-09-08.md` — single best all-round pick: `qwen3:8b` Q4_K_M.
