#!/usr/bin/env bash
# low-thinking leg of the rapid quant smoke: same 4 tasks x 1 trial, --think low, fixed harness (pi-agent-v5), 32k.
# Runs after results/v5-smoke.sh has written "SMOKE ALLDONE" (or is started by hand at a quant boundary).
cd /c/Users/slb/ollama-bench
LOG=results/v5-smoke-low.log
QUANTS="${QUANTS:-q27-Q3_K_S q27-Q2_K_L q27-Q3_K_M}"
for q in $QUANTS; do
  echo "=== start $q low $(date -Is)" >> "$LOG"
  PYTHONUTF8=1 python pibench.py --provider ollama --models "$q" --think low --trials 1 --no-tps \
    --tasks-dir tasks-v4 --tasks 52_reengine,55_minilang,57_stateful,60_numlit \
    --tag "v5-smoke-low-$q" --timeout 1200 --agent-dir "$PWD/results/pi-agent-v5" >> "$LOG" 2>&1
  echo "=== $q low exit=$? $(date -Is)" >> "$LOG"
  [ -f results/gpu-watch.ALERT ] && { echo "ALERT present, stopping" >> "$LOG"; break; }
done
echo "=== SMOKE-LOW ALLDONE $(date -Is)" >> "$LOG"
