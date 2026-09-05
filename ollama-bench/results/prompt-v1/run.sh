#!/bin/bash
# usage: run.sh <tag> <tiny|large> <trials> [extra pi args...]
# Optional: PIBENCH_TASKS=t03  restrict to one task.
set -u
source ~/.config/devbox/env
export WSLENV="ZAI_API_KEY:PIBENCH_PI_ARGS:PIBENCH_KEEP:PV1_TRACE_DIR${WSLENV:+:$WSLENV}"
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
HERE=/home/slb/bench-prompt/ollama-bench
TAG=$1; BAND=$2; TRIALS=$3; shift 3
if [ "$BAND" = tiny ]; then
  D=results/v5/authoring/round2/suite-0; CTX=24576; TO=300
else
  D=results/v5/authoring/round3/suite; CTX=65536; TO=600
fi
export PIBENCH_PI_ARGS="$*"
TASKARG=()
if [ -n "${PIBENCH_TASKS:-}" ]; then TASKARG=(--tasks "$PIBENCH_TASKS"); fi
LOG="$HERE/results/prompt-v1/logs/$TAG.log"
OUT="$HERE/results/prompt-v1/logs/$TAG.outcome"
rm -f "$OUT"
cd "$HERE" || exit 9
{ echo "=== $TAG band=$BAND trials=$TRIALS start=$(date -Is)"
  echo "=== PIBENCH_PI_ARGS=[$PIBENCH_PI_ARGS]"; } > "$LOG"
PYTHONUTF8=1 "$PY" pibench.py --provider zai --models glm-5.3-flash \
  --think medium --trials "$TRIALS" --no-tps --timeout "$TO" \
  --tasks-dir "$D" --num-ctx "$CTX" --tag "prompt-v1/$TAG" \
  "${TASKARG[@]}" >> "$LOG" 2>&1 < /dev/null
RC=$?
{ echo "tag=$TAG"; echo "rc=$RC"; echo "finished=$(date -Is)"; } > "$OUT"
exit $RC
