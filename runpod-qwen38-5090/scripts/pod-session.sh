#!/usr/bin/env bash
set -euo pipefail
ROOT="${ROOT:-/runpod-volume}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="$ROOT/results/$RUN_ID"
mkdir -p "$ROOT/huggingface/hub" "$ROOT/manifests" "$OUT"
case "${1:-help}" in
  verify)
    nvidia-smi
    test -w "$ROOT"
    python3 --version
    sha256sum -c "$ROOT/manifests/harness.sha256"
    curl --fail --silent http://127.0.0.1:8000/health || true
    ;;
  download)
    command -v hf >/dev/null || python3 -m pip install --no-cache-dir -q huggingface_hub
    HF_HOME="$ROOT/huggingface" hf download doth4580/Qwen3.8-27B-NVFP4-FULL --local-dir "$ROOT/huggingface/target"
    HF_HOME="$ROOT/huggingface" hf download lued/Qwen3.8-27B-DFlash2-W8 --local-dir "$ROOT/huggingface/drafter"
    ;;
  start)
    exec vllm serve "$ROOT/huggingface/target" --served-model-name qwen38 --kv-cache-dtype fp8 --enable-prefix-caching --max-model-len 131072
    ;;
  start-spec)
    exec vllm serve "$ROOT/huggingface/target" --served-model-name qwen38 --kv-cache-dtype fp8 --enable-prefix-caching --max-model-len 131072 --speculative-config '{"model":"'"$ROOT"'/huggingface/drafter","num_speculative_tokens":7,"method":"draft_model"}'
    ;;
  measure)
    python3 /opt/harness/measure.py --base-url http://127.0.0.1:8000 --model qwen38 --prompts /opt/harness/prompts/fixed.jsonl --context "$2" --output "$OUT/measure-$2.jsonl"
    ;;
  metrics)
    /opt/harness/collect_metrics.sh "$OUT"
    ;;
  *)
    echo "usage: pod-session.sh {verify|download|start|start-spec|measure CONTEXT|metrics}" >&2
    exit 2
    ;;
esac
