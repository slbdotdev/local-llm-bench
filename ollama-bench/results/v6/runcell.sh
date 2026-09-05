#!/bin/bash
# runcell.sh <quant> <ctxname> <ctx> <band> <tasks> <trials>
# One scored pibench cell under the v6 pi harness. Serial by construction: the caller
# never runs two of these at once (plan section 9). Resumes rather than repeats: the tag's
# JSON is the artifact and pibench skips (task, trial) pairs already in it.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"
quant=$1; ctxname=$2; ctx=$3; band=$4; tasks=$5; trials=$6
case $band in
  tiny)  dir=results/v5/authoring/round2/suite-0; to=300 ;;
  large) dir=results/v5/authoring/round3/suite;   to=600 ;;
  *) echo "unknown band $band" >&2; exit 2 ;;
esac
tag="v6-$quant-$ctxname-$band"
echo "=== $(date +%H:%M:%S) CELL $tag tasks=$tasks trials=$trials timeout=${to}s" >&2
"$PY" pibench.py --models "q27-$quant-$ctxname" --tasks "$tasks" --tasks-dir "$dir" \
  --trials "$trials" --think medium --num-ctx "$ctx" --no-tps --timeout "$to" --tag "$tag"
rc=$?
echo "=== $(date +%H:%M:%S) DONE $tag rc=$rc" >&2
exit $rc
