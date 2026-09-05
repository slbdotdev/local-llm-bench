#!/bin/bash
# runcell.sh <quant> <ctxname> <ctx> <band> <trials> <tag> [tasks]
#
# One scored pibench cell of the v7 calibration. Modelled on results/v6/runcell.sh.
# Serial by construction: the caller never runs two of these at once.
# Resumes rather than repeats: the tag's JSON is the artifact and pibench skips
# (task, trial) pairs already in it, so a killed cell costs one trial.
#
#   quant    IQ2_M | UDQ3KXL | Q2_K ...
#   ctxname  the tag suffix, which is where the context window actually lives
#            (it is baked into the tag; --num-ctx only feeds the tps probe, which
#            --no-tps disables)
#   ctx      the same number, passed for the record
#   band     main | cheap  -> timeout 900 / 300, task set by name
#   trials   trials per task
#   tag      the results tag, e.g. v7cal-IQ2_M-main
#   tasks    optional explicit comma list; default is every task of that band
#
# The two exports are mandatory: PIBENCH_PI_ARGS carries the pi resilience
# extension, and WSLENV is what makes it cross the WSL/Windows boundary at all.
# A cell without them is not a result (v6 D6-4).
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"
# Opt-in only, and unset for the scored passes so they are unchanged: V7_KEEP=1 makes
# pibench preserve each sandbox under D:\v7keep before deleting it, which is the evidence
# a fairness re-read needs — pibench keeps only the last 400 characters of the model's
# final message, so the tree it left behind is the transcript. The path is a Windows path
# because pibench runs under the Windows interpreter, and it is outside every git checkout
# (D7-18: a sandbox inside the bench's own repository is one `git show HEAD:` from the
# hidden grader). WSLENV is what carries the variable across the interop boundary at all.
if [ "${V7_KEEP:-}" = "1" ]; then
  export PIBENCH_KEEP='D:\v7keep'
  export WSLENV="PIBENCH_KEEP${WSLENV:+:$WSLENV}"
fi

quant=$1; ctxname=$2; ctx=$3; band=$4; trials=$5; tag=$6; tasks=${7:-}
dir=results/v7/authoring/suite
case $band in
  main)  to=900 ;;
  cheap) to=300 ;;
  *) echo "unknown band $band" >&2; exit 2 ;;
esac
if [ -z "$tasks" ]; then
  tasks=$(ls -1 "$dir" | grep -- "-$band-" | paste -sd, -)
fi
echo "=== $(date +%H:%M:%S) CELL $tag model=q27-$quant-$ctxname band=$band trials=$trials timeout=${to}s" >&2
echo "=== tasks: $tasks" >&2
"$PY" pibench.py --models "q27-$quant-$ctxname" --tasks "$tasks" --tasks-dir "$dir" \
  --trials "$trials" --think medium --num-ctx "$ctx" --no-tps --timeout "$to" --tag "$tag"
rc=$?
echo "=== $(date +%H:%M:%S) DONE $tag rc=$rc" >&2
exit $rc
