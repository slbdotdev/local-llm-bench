#!/usr/bin/env bash
# rapid quant smoke: 4 tasks x 1 trial per quant on the v5-fixed harness (results/pi-agent-v5), 32k ctx, medium.
cd /c/Users/slb/ollama-bench
LOG=results/v5-smoke.log
for q in q27-Q3_K_S q27-Q2_K_L q27-Q3_K_M; do
  echo "=== start $q $(date -Is)" >> "$LOG"
  PYTHONUTF8=1 python pibench.py --provider ollama --models "$q" --think medium --trials 1 --no-tps \
    --tasks-dir tasks-v4 --tasks 52_reengine,55_minilang,57_stateful,60_numlit \
    --tag "v5-smoke-$q" --timeout 1200 --agent-dir "$PWD/results/pi-agent-v5" >> "$LOG" 2>&1
  echo "=== $q exit=$? $(date -Is)" >> "$LOG"
  [ -f results/gpu-watch.ALERT ] && { echo "ALERT present, stopping" >> "$LOG"; break; }
done
echo "=== SMOKE ALLDONE $(date -Is)" >> "$LOG"
