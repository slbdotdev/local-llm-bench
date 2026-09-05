#!/bin/bash
# D6-39: re-measure Q2_K_L-64k and Q2_K-64k on t03 BACK TO BACK, under whatever contention
# exists right now, so the 18.8x gap in D6-34/D6-36 is tested under identical conditions.
# The original pair was not identical: Q2_K_L's 31.0 s was taken at 21:54 with the GPU to
# itself, and Q2_K's 584.1 s ran 22:38-22:48, overlapping the prompt campaign's 22:44 start.
# A separate tag, so no campaign artifact is touched.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"
echo "=== $(date +%H:%M:%S) recheck: Q2_K_L-64k then Q2_K-64k, t03, one trial each" >&2
"$PY" pibench.py --models q27-Q2_K_L-64k,q27-Q2_K-64k --tasks t03 \
  --tasks-dir results/v5/authoring/round3/suite \
  --trials 1 --think medium --num-ctx 65536 --no-tps --timeout 900 \
  --tag v6-recheck-64k-t03
echo "=== $(date +%H:%M:%S) RECHECK DONE rc=$?" >&2
touch results/v6/.recheck-done
echo "=== $(date +%H:%M:%S) resuming the campaign chain" >&2
exec bash results/v6/chainAll.sh
