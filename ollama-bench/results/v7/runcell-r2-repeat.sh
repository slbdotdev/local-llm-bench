#!/bin/bash
# runcell-r2-repeat.sh — three workhorse trials each on the round-two candidates the first sweep
# missed (m01-main-glm, m10-main-glm), as the calibration did for its changed tasks. Same cell
# as runcell-r2.sh in every other respect. Marker: results/v7/.r2-repeat-done.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"
dir=results/v7/authoring/r2/gate-suite
tag=v7r2-gate-repeat
tasks=${1:-m01-main-glm,m10-main-glm}
LOG=results/v7/r2repeat.log
echo "=== $(date +%H:%M:%S) CELL $tag model=q27-IQ2_M-64k trials=3 timeout=900s tasks=$tasks" >> "$LOG"
"$PY" pibench.py --models q27-IQ2_M-64k --tasks "$tasks" --tasks-dir "$dir" \
  --trials 3 --think medium --num-ctx 65536 --no-tps --timeout 900 --tag "$tag" >> "$LOG" 2>&1
echo "=== $(date +%H:%M:%S) DONE $tag rc=$?" >> "$LOG"
date +%H:%M:%S > results/v7/.r2-repeat-done
