#!/bin/bash
# runcell-r2.sh — the acceptance sweep cell for the nine re-authored main-band candidates.
#
# One workhorse trial per candidate, on q27-IQ2_M-64k, against the staging directory rather
# than the suite: a round-2 candidate is not in the suite and does not enter it until it
# clears the gate of plan section 2.2 and its row is written into the roundtable register.
#
# Identical in every other respect to results/v7/runcell.sh, which it is modelled on, and
# which the calibration ran: same interpreter, same resilience extension, same WSLENV, same
# baked tag, same --no-tps, same 900 s main-band timeout. A cell without the two exports is
# not a result (v6 D6-4).
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"

dir=results/v7/authoring/r2/gate-suite
tag=${1:-v7r2-gate}
tasks=${2:-}
[ -d "$dir" ] || { echo "staging directory $dir is absent; run stage_gate_suite.py" >&2; exit 2; }
if [ -z "$tasks" ]; then
  tasks=$(ls -1 "$dir" | paste -sd, -)
fi
echo "=== $(date +%H:%M:%S) CELL $tag model=q27-IQ2_M-64k trials=1 timeout=900s" >&2
echo "=== tasks: $tasks" >&2
"$PY" pibench.py --models q27-IQ2_M-64k --tasks "$tasks" --tasks-dir "$dir" \
  --trials 1 --think medium --num-ctx 65536 --no-tps --timeout 900 --tag "$tag"
rc=$?
echo "=== $(date +%H:%M:%S) DONE $tag rc=$rc" >&2
exit $rc
