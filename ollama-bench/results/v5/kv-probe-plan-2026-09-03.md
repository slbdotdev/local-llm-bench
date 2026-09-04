# Local-GPU KV cache quantisation plan, 2026-09-03

Status: plan only. This document specifies a rerun; it does not start a server, load a
model, or execute a benchmark.

## Question and evidence

The question is whether the desktop's current `OLLAMA_KV_CACHE_TYPE=q8_0` is worth the
capacity it costs, or whether the baked `q4_0` cache assumption in the two 64k models is
the better trade. The test must be at 64k, where the decision matters, not at 8k to 24k
where today's probe could not discriminate.

Today's direct `llama-server` results use the Q3_K_S 27B blob
`sha256-ba0c5dee3026...`. At 16k, symmetric q8_0 and q4_0 both scored 24/24, at 51.9
and 51.4 generation tok/s respectively; at 24k they again both scored 24/24, at 51.0
and 48.6 generation tok/s. The 8k pass produced one successful f16 control and then
three startup failures. The 24k asymmetric q8_0/q4_0 run was never completed. The
per-run records are [8k](kv-probe/kv-8k-Q3_K_S.json),
[16k](kv-probe/kv-16k-Q3_K_S.json), and [24k](kv-probe/kv-24k-Q3_K_S.json).

The 24/24 result is a ceiling, not a quality finding: the exact checksum needle at these
windows cannot fail, so it cannot establish that q4_0 is safe. Asymmetric K/V is removed
from this plan. Ollama cannot express it, and direct llama-server measured 7.1 generation
tok/s and 18.3 prompt tok/s for q8_0/q4_0 against 51.9 and 1443.3 for q8_0/q8_0 at 16k;
the normal 14422 MiB VRAM reading rules out a spill. The likely fused flash-attention
fallback is an inference, not a measured attribution.

The external llama.cpp discussion evidence points in the same direction but is not a
substitute for this run: on Qwen2.5-7B, mean KLD was 5.508897 for q4_0/q4_0, 0.004766
for q8_0/q4_0, and 0.001782 for q8_0/q8_0; same-top-p rates were 11.6%, 96.7%, and
98.0% respectively (f16/q4_0 was 0.004047 and 96.9%). The large change comes from K.
That is a different 7B model, and issue 21591 reports architecture-dependent effects, so
this 27B measurement remains necessary.

## Target and matrix

`ollama list` and `results/gpu-tune/summary.md` identify the exact targets as
`q27-IQ3_M-64k` and `q27-Q3_K_S-64k`. Both bake `num_ctx 65536`, `num_gpu 66`, and the
q4_0-sized 64k configuration. Resolve each model's current GGUF blob path at execution
time; do not guess a blob from a short Ollama ID.

Run one server and one model at a time, directly with the Ollama-vendored
`llama-server.exe`, with `--flash-attn on`, `-np 1`, `-c 65536`, and full layer offload.
The four predeclared cells are:

| model | K / V | purpose |
| --- | --- | --- |
| `q27-IQ3_M-64k` | q8_0 / q8_0 | hardest fit case; first live calibration cell |
| `q27-IQ3_M-64k` | q4_0 / q4_0 | same model, resident quality baseline |
| `q27-Q3_K_S-64k` | q8_0 / q8_0 | current desktop cache on the margin-rich 64k model |
| `q27-Q3_K_S-64k` | q4_0 / q4_0 | baked-cache comparison and likely resident reference |

There are no asymmetric cells. They are settled as both unsupported by Ollama and
catastrophically slow in the direct runner.

## A probe with room to fail

Replace the one-field checksum question in `kvquality.py` with a fixed-seed corpus of
about 1200 look-alike records and 32 needles spread from roughly 1% to 99% depth. Each
needle names two distinct records and asks for four independently scorable fields, for
example the checksum and region from record A and the shard and token budget from record
B. The records should include same-prefix and adjacent-index near-misses, and the
question should explicitly warn that those decoys are not answers. Keep the corpus and
needle seed frozen across all four cells.

Score each of the 128 fields independently, with exact field boundaries and a separate
all-four-fields-per-needle count. Report points, percentage, all-fields success, and
early/middle/late depth buckets. This gives useful partial credit when one retrieved fact
is right and another is wrong, while requiring a two-record join that the current
checksum lookup never required. The grader must reject a value copied from a near-miss
record, not merely search the response for any six-character string.

## Calibration gate

Calibration is mandatory before the four-cell sweep. First, add a no-GPU grader fixture
to `kvquality.py`: feed the scorer a known answer set, then a deliberately degraded set
with one wrong field, one near-miss field, and one missing field. The fixture must report
less than 100% (and the expected field and needle counts) before the script is allowed to
continue. This proves that the scoring path can fail; today's all-green checksum probe
proved the opposite only after spending the run budget.

Second, after the offline gate, make the first live cell the expected-hardest
`q27-IQ3_M-64k` q8_0/q8_0 cell, using eight needles distributed across the depth buckets.
It is a short fit-and-sensitivity calibration, not a headline result. If it is clean,
continue that same server/configuration with the remaining needles so the calibration
work becomes the first full q8_0 result rather than a duplicate load. If it spills or
hangs, record the measured prompt/generation collapse and stop that cell safely; do not
silently treat a reported `100% GPU` residency as success. A full cell may proceed only
after the offline degraded control has produced a sub-100% score and the live startup,
cleanup, and watchdog checks are clean.

## Saturation stop rule

The offline fixture above proves the **grader** can fail. It does not prove the **task** can
fail, and those are different things — a grader that correctly rejects a wrong answer, paired
with a question the model never gets wrong, still returns 100% in every cell and discriminates
nothing. That is precisely today's failure, and an offline fixture would not have caught it.

So the rule is declared before the run, not after: **if the first full cell scores at or above
98% of fields with all-four-fields success at or above 90%, the probe is saturated, the sweep
stops there, and the remaining three cells are not run.** A saturated probe cannot separate
q8_0 from q4_0 no matter how many cells it fills, and today's run already bought that lesson
once at the cost of a GPU budget. Stopping is the successful outcome of the rule, not a
failure of the run: it means the next iteration needs a harder task, and it costs one cell to
learn that instead of four.

If the rule fires, record what saturated and at which depths, and do not adjust the threshold
after seeing the score.

## The capacity hypothesis, and why it may decide this

There is a real chance this is settled by what fits rather than by what scores, and the
arithmetic should be on the record before the run so the result can falsify it.

Today's two symmetric pairs give the cost of q8_0 over q4_0 directly: 14621 against 14406 MiB
at 16384, and 15078 against 14766 MiB at 24576 — deltas of 215 and 312 MiB, or 0.0131 and
0.0127 MiB per token of context. Call it 0.0129. At 65536 that is about **845 MiB** of
additional cache.

`results/gpu-tune/summary.md` has the two targets resident at 64k under q4_0 at 14.11 GiB
(IQ3_M) and 13.70 GiB (Q3_K_S) — 14449 and 14029 MiB. Adding 845 gives roughly 15294 and
14874 MiB under q8_0. The card is 16303 MiB total and the desktop was measured holding 1552
MiB at idle on 2026-09-03, drifting 1.0 to 2.9 GB under load per section 5 of the v5 plan.

So both q8_0 cells are predicted **not to fit**, IQ3_M by a wide margin and Q3_K_S narrowly,
and the predicted failure mode is a WDDM spill that still reports `100% GPU` while prompt and
generation rates collapse — exactly the signature the asymmetric cell produced today at 18.3
prompt tok/s. Treat a collapse as the measured answer to the capacity question, not as a
broken run to retry.

If that holds, the decision is made on capacity and the quality comparison never arises at
64k: the 64k variants must run q4_0 because q8_0 does not fit beside them. State it that way
if it happens, rather than reporting a quality verdict the run did not earn.

## What the answer has to serve

`OLLAMA_KV_CACHE_TYPE` is one environment variable on the Ollama server. It is not per-model
and not per-request, so the fleet cannot hold q8_0 for short-context work and q4_0 for the 64k
variants at the same time. The output of this run is therefore not only "which is better" but
which of three shapes the org adopts: a single global setting at one value, a documented switch
of the variable plus an Ollama restart when 64k work starts, or dropping one side of the
requirement. Name the shape in the conclusion.

## Harness changes required

In `kvquality.py` (`results/v5/kv-probe/kvquality.py`), split scoring into a pure function
used by the no-GPU fixture and the live run, add the two-record/four-field corpus and
depth-bucket accounting, and reject `K != V` in argument validation. Preserve raw answers,
per-field scores, timings, peak VRAM, and a reason for every partial or stopped run in the
JSON.

Fix the lifecycle sequencing before another sweep. `run_config` currently terminates a
server, waits at most 30 seconds, sleeps only three seconds, and then allows the next
launch; it does not prove that the process tree has exited, port 18080 is free, or the
VRAM allocation has drained. `kill_stray_servers` only kills processes named
`llama-server` and accepts one low VRAM sample as sufficient. On the failed 8k pass that
allowed a startup/VRAM-release race to become three indistinguishable health failures.

Replace that with one cleanup routine that terminates the whole server tree, waits for
the parent and children, waits for the port to be free, and requires three consecutive
quiescent VRAM samples (also requiring no unexpected `llama-server` process) before
launch. After a health failure, kill and drain before recording the error; do not start
the next cell while cleanup is incomplete. Give each launch a unique port or explicitly
verify 18080 is unbound, and include the server-log tail in a startup error. Keep the
health poll process-aware, but do not use health success as a substitute for the
post-termination drain.

In `run-sweep.sh` (`results/v5/kv-probe/run-sweep.sh`), use `set -euo pipefail`, run the
offline calibration first, resolve the two named 64k model blobs, run only the four
symmetric cells at `--ctx 65536`, and stop on a nonzero harness result. Keep each output
in a separate file so a startup failure cannot be mistaken for a model result. The script
must leave the desktop's user setting unchanged; direct cache flags are per server, and
any environment change made for setup must be restored and logged before exit.

## Safety and acceptance

Start the RAM watchdog from `results/gpu-tune/watch.sh` and verify it is live before the
first live calibration cell. Stop if free RAM approaches the watchdog's 8 GiB alert or
if a prior server has not released. Never run Ollama's model service concurrently with
the direct server, and never place two models on the GPU.

The watchdog's `/api/ps` model count and `ollama*` RSS do not see a directly launched
`llama-server`, so `models=0` is not proof that the GPU is idle during this harness. Add
the direct-server process and port to the run log, and use free RAM, `nvidia-smi`, and the
explicit cleanup barrier as the safety signals.

For every cell record load time, prompt tok/s, generation tok/s, cold and warm prompt
timings, peak VRAM, free RAM, and the complete graded score. Judge usability by measured
tok/s and completion behavior. On Windows/WDDM an oversized allocation can report 100%
GPU while spilling into system RAM; residency is evidence to record, never the verdict.

## Wall-clock budget

The 24k JSONs provide 22,897 prompt tokens per query and measured symmetric prompt rates
of 1432.4 tok/s (q8_0) and 1417.7 tok/s (q4_0), with 51.0 and 48.6 generation tok/s.
Scaling the corpus to about 60,000 prompt tokens gives a cold prompt pass of
`60,000 / 1,417.7 = 42.3 s`. With prompt caching only the question suffix is reprocessed;
at roughly 512 tokens per suffix and taking 1,100 tok/s as a deliberately pessimistic warm
rate — today's measured rates are 1417 to 1443, so this is a margin rather than an
observation, and it is the one number here that is assumed rather than measured — the other
31 questions add about `31 * 512 / 1,100 = 14.4 s`. Allow 32 answers averaging ten generated
tokens: `32 * 10 / 48.6 = 6.6 s`, plus 15 s for load, health, teardown, and the verified
drain. The resident nominal is therefore about `42.3 + 14.4 + 6.6 + 15 = 78 s`, or 1.3
minutes per full cell.

That nominal describes a **resident** cell only, and per the capacity hypothesis above the
two q8_0 cells are predicted not to be resident. A spilled cell runs at the asymmetric run's
order of magnitude — 18.3 prompt tok/s would turn the cold pass alone into roughly 55 minutes
— so the 10-minute per-cell safety cap is what actually bounds those two, and hitting it is a
result to record rather than an overrun to absorb.

Budget 4 minutes per cell to cover 64k allocation and cleanup variance: 16 minutes for
the four cells, plus 4 minutes for the offline/live calibration gate and 10 minutes of
recovery allowance, for a 30-minute wall-clock envelope. A q8_0 cell that falls below
usable prompt/generation speed or reaches the 10-minute safety cap is a measured
thrashing outcome with its partial score, not a residency success. If the envelope is
overrun, cut any repeat or extra needles first; retain the four first-pass symmetric
cells, and only then cut the second q8_0 model cell if the first q8_0 64k result already
establishes the same spill mode.

The decision is made from paired q4_0/q8_0 scores and measured throughput on each named
64k model. A q4_0 result that is slightly lower on this harder probe is not automatically
unsafe, and a perfect result on the old checksum probe is not evidence of safety.
