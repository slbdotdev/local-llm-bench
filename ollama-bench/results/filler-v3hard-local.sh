#!/usr/bin/env bash
# GPU filler while v4 authoring finishes: v3 hard five on the resident quants at the controlled config
# (32k from the Modelfile, q8_0 KV verified in server.log at 02:40). One trial, medium thinking.
cd /c/Users/slb/ollama-bench
for m in q27-IQ3_M q27-Q3_K_M; do
  [ -f results/gpu-watch.ALERT ] && { echo "ALERT present, stopping" ; break; }
  [ -f results/STOP_FILLER ] && { echo "STOP_FILLER present, stopping"; break; }
  PYTHONUTF8=1 python pibench.py --provider ollama --models $m --think medium --trials 1 --no-tps --timeout 1800 --tasks-dir tasks-v3 --tasks 32_wirefmt,33_spanmap,34_tmplfix,35_ledger,36_minilang --tag v3-hard-local-medium >> results/v3-hard-local-medium.log 2>&1
  echo "=== $m exit=$? $(date -Is)" >> results/v3-hard-local-medium.log
done
echo ALLDONE >> results/v3-hard-local-medium.log
