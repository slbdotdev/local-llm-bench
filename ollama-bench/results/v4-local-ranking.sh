#!/usr/bin/env bash
# v4 local quality ranking: controlled config (32k from Modelfile, q8_0 KV verified), medium, 3 trials, 1800 s.
cd /c/Users/slb/ollama-bench
for m in q27-Q2_K_L q27-Q3_K_S q27-Q3_K_M; do
  [ -f results/gpu-watch.ALERT ] && { echo "ALERT present, stopping $(date -Is)" >> results/v4-local-medium.log; break; }
  [ -f results/STOP_RANKING ] && { echo "STOP_RANKING present $(date -Is)" >> results/v4-local-medium.log; break; }
  PYTHONUTF8=1 python pibench.py --provider ollama --models $m --think medium --trials 3 --no-tps --timeout 1800 --tasks-dir tasks-v4 --tag v4-local-medium >> results/v4-local-medium.log 2>&1
  echo "=== $m exit=$? $(date -Is)" >> results/v4-local-medium.log
done
echo ALLDONE >> results/v4-local-medium.log
