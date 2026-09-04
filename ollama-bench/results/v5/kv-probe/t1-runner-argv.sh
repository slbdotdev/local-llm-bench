#!/usr/bin/env bash
# T1: what does Ollama actually pass to llama-server for --cache-type-k / --cache-type-v?
# Loads one model, reads the runner command line from server.log and from the live process,
# then unloads. Costs one model load, no generation.
set -u
LOG="$HOME/AppData/Local/Ollama/server.log"
OUT="$HOME/ollama-bench/results/v5/kv-probe"
mkdir -p "$OUT"

echo "=== server startup env (current) ==="
grep -aoE "OLLAMA_(FLASH_ATTENTION|KV_CACHE_TYPE):[^ ]*" "$LOG" | tail -4

MARK=$(wc -c < "$LOG")
echo "=== loading q27-IQ3_M (32k) ==="
curl -s http://127.0.0.1:11434/api/generate \
  -d '{"model":"q27-IQ3_M","prompt":"hi","stream":false,"options":{"num_predict":1}}' \
  -o /dev/null -w 'http=%{http_code} t=%{time_total}s\n'

echo "=== live runner command line ==="
powershell.exe -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"Name='ollama.exe'\" | Select-Object -ExpandProperty CommandLine" \
  2>/dev/null | tr ' ' '\n' | grep -nE "cache-type|flash|ctx-size|n-gpu-layers|--model" -A1 | head -30

echo "=== server.log runner argv since load ==="
tail -c +"$MARK" "$LOG" | grep -aoE "cmd[^\r\n]{0,600}" | head -3
tail -c +"$MARK" "$LOG" | grep -aiE "cache.type|flash_attn|kv cache|type_k|type_v" | head -20

echo "=== ollama ps ==="
curl -s http://127.0.0.1:11434/api/ps

echo
echo "=== unload ==="
curl -s http://127.0.0.1:11434/api/generate \
  -d '{"model":"q27-IQ3_M","keep_alive":0}' -o /dev/null -w 'unload http=%{http_code}\n'
