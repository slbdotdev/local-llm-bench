Role: worker. Model family is pinned to Luna (`gpt-5.6-luna`) through the
native `pi-slb-launch` harness. Do not launch a nested worker.

Re-derive the round-two gate baseline on exactly one fresh cold secure RTX
5090 pod using MCP tools only for Runpod infrastructure. Read back
`cudaVersion` before spending; reject/delete the pod if it is not 13.0. Never
touch `practical_beige_snipe` or `skilled_yellow_pig`. Use the official pinned
image `vllm/vllm-openai:v0.28.0-cu129@sha256:50509e700235cea487715cedeb501d20a1cd15fa6a54ce93688284bd0d96995d` and the
round-one target/model command with native MTP n=3, FP8 KV, prefix caching,
131072 max context, `--max-num-seqs 4`, `--max-num-batched-tokens 4096`,
`--limit-mm-per-prompt '{"image":0,"video":0}'`, and
`--skip-mm-profiling`. Read pod logs for boot and kernel evidence before
measurement.

Use the corrected producer at
`/home/slb/runpod-qwen38-5090/artifacts/harness/stream-measure.py` against
the public pod proxy, with `prompts/fixed.jsonl`, context 8192, repeats 3,
max tokens 256, model `qwen38`, and a new output path
`results/round2/baseline-corrected.jsonl`. The producer must submit exactly
salt + padding + instruction, and its saved rows must include salt and
submitted_prompt; completion_tokens must come only from streaming usage and
chunks must remain a separate field. If the proxy returns 403, record the
fact and use the plan-approved controller workaround or stop; do not claim a
number from a different prompt/order. Compute the median of the 12
`decode_tps` rows using `(completion_tokens - 1)/(elapsed - TTFT)` and flag
any early-EOS rows rather than silently treating them as a valid baseline.

Write a concise summary JSON to `results/round2/baseline-summary.json` with
pod/template IDs, CUDA version, row count, per-row validity, median, and any
blocking issue. Before reporting, delete the pod and its template with MCP,
then verify `list-pods`, `list-templates`, and `list-network-volumes`; do not
delete the two protected pre-existing resources. Append timestamped actions
and cumulative pod-minute accounting to `STATUS.md`. Do not edit ansible-slb,
do not commit, and do not put credentials in prompts, logs, or files. Report
the exact measured result or plainly state that the baseline is void.
