#!/bin/bash
# usage: supervise.sh <tag> <tiny|large> <trials> [extra pi args...]
# Runs pibench.py repeatedly until every (task, trial) cell for the tag is filled with a
# trial that completed on its own (rc == 0) or genuinely timed out. Cells whose pi child was
# killed from outside (rc != 0, not timed_out) are deleted and re-run: the other campaign on
# this box runs results/v6/kill_pi.ps1, which Stop-Processes EVERY node.exe whose command line
# matches 'pi-coding-agent', machine-wide, and cannot tell its pi from ours.
set -u
source ~/.config/devbox/env
export WSLENV="ZAI_API_KEY:PIBENCH_PI_ARGS:PIBENCH_KEEP:PV1_TRACE_DIR:PV1_THINK${WSLENV:+:$WSLENV}"
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
HERE=/home/slb/bench-prompt/ollama-bench
TAG=$1; BAND=$2; TRIALS=$3; shift 3
if [ "$BAND" = tiny ]; then
  D=results/v5/authoring/round2/suite-0; CTX=24576; TO=300
else
  D=results/v5/authoring/round3/suite; CTX=65536; TO=600
fi
export PIBENCH_PI_ARGS="$*"
NTASK=8
TASKARG=()
if [ -n "${PV1_TASKS:-}" ]; then
  TASKARG=(--tasks "$PV1_TASKS")
  NTASK=$(echo "$PV1_TASKS" | tr ',' '\n' | grep -c .)
fi
WANT=$((NTASK * TRIALS))
JSON="$HERE/results/prompt-v1/$TAG.json"
LOG="$HERE/results/prompt-v1/logs/$TAG.log"
OUT="$HERE/results/prompt-v1/logs/$TAG.outcome"
rm -f "$OUT"
cd "$HERE" || exit 9
{ echo "=== $TAG band=$BAND trials=$TRIALS want=$WANT start=$(date -Is)"
  echo "=== PIBENCH_PI_ARGS=[$PIBENCH_PI_ARGS]"; } >> "$LOG"

# Drop cells whose pi child was killed from outside, so pibench refills them.
scrub() {
  [ -f "$JSON" ] || return 0
  python3 - "$JSON" >> "$LOG" 2>&1 <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
for model, r in d.items():
    keep, drop = [], []
    for x in r["runs"]:
        if x.get("rc", 0) != 0 and not x.get("timed_out"):
            drop.append("%s#%s rc=%s" % (x["task"], x["trial"], x.get("rc")))
        else:
            keep.append(x)
    if drop:
        print("[supervise] dropping externally-killed cells: " + ", ".join(drop))
    r["runs"] = keep
json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
PY
}

count() {
  [ -f "$JSON" ] || { echo 0; return; }
  python3 -c "
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
print(sum(len(r['runs']) for r in d.values()))" "$JSON" 2>/dev/null || echo 0
}

RC=1
for attempt in 1 2 3 4 5 6 7 8; do
  scrub
  HAVE=$(count)
  if [ "$HAVE" -ge "$WANT" ]; then RC=0; break; fi
  echo "=== attempt $attempt: $HAVE/$WANT cells filled, $(date -Is)" >> "$LOG"
  PYTHONUTF8=1 "$PY" pibench.py --provider zai --models glm-5.3-flash \
    --think "${PV1_THINK:-medium}" --trials "$TRIALS" --no-tps --timeout "$TO" \
    --tasks-dir "$D" --num-ctx "$CTX" --tag "prompt-v1/$TAG" "${TASKARG[@]}" \
    >> "$LOG" 2>&1 < /dev/null
  echo "=== attempt $attempt exited rc=$? at $(date -Is)" >> "$LOG"
done
scrub
HAVE=$(count)
[ "$HAVE" -ge "$WANT" ] && RC=0 || RC=1
{ echo "tag=$TAG"; echo "rc=$RC"; echo "cells=$HAVE/$WANT"; echo "finished=$(date -Is)"; } > "$OUT"
exit $RC
