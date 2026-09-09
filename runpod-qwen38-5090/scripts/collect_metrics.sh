#!/usr/bin/env bash
set -euo pipefail
out="$1"; base="${2:-http://127.0.0.1:8000}"
mkdir -p "$out"
curl --fail --silent --show-error "$base/metrics" > "$out/vllm.metrics"
nvidia-smi --query-gpu=name,compute_cap,power.draw,clocks.sm,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits > "$out/nvidia-smi.csv"
nvidia-smi -q > "$out/nvidia-smi.txt"
