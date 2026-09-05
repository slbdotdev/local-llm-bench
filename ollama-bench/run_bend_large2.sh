#!/bin/bash
# Resume the 64k large-band pass after the Q3_K_S throughput-curve probe hit the 900 s HTTP
# timeout in pibench.post() and killed the whole run.
#
# --no-tps is deliberate. The curve probe pushes a 27,000-token prefill through a model that is
# already resident at 15.78 GB on a 16.3 GB card, and that is what timed out -- not a task. Plan
# step 4 says the bend-finding pass is the run to protect, so the diagnostic that killed it is
# dropped and throughput is taken separately per quant.
#
# Q2_K_L's eight rows are already in the artifact and pibench resumes rather than repeating them.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
"$PY" pibench.py \
  --models q27-Q3_K_S-64k,q27-IQ3_M-64k \
  --tasks-dir results/v5/authoring/round3/suite \
  --trials 1 --think medium --num-ctx 65536 --no-tps --tag bend-large-64k
echo "exit=$?"
