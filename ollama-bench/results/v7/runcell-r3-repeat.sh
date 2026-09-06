#!/bin/bash
# runcell-r3-repeat.sh <main|cheap> [tag] [tasks] — three trials per round-3 candidate, for step 7:
# does the coverage gate agree with the pass rate? Every round-3 row failed the gate but one,
# and only n06 and the two round-2 misses have more than one trial behind them.
#
# One workhorse trial per candidate against the round-3 staging directory. Round 3 has two
# bands: `main` runs on q27-IQ2_M-64k at 65536 as round 2 did; `cheap24` (12-16k tokens of
# material) runs on q27-IQ2_M-24k at 24576, the cheap-band cell of the calibration. The band
# of each slot is read from its MANIFEST.json, so a band's default task list is measured, not
# typed. Same interpreter, resilience extension, WSLENV, --no-tps and timeouts as runcell.sh;
# a cell without the two exports is not a result (v6 D6-4).
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"

band=${1:?band: main or cheap}
dir=results/v7/authoring/r3/gate-suite
[ -d "$dir" ] || { echo "staging directory $dir is absent; run stage_gate_suite.py" >&2; exit 2; }
case "$band" in
  main)  model=q27-IQ2_M-64k; ctx=65536; timeout=900; want=main ;;
  cheap) model=q27-IQ2_M-24k; ctx=24576; timeout=600; want=cheap24 ;;
  *) echo "band must be main or cheap" >&2; exit 2 ;;
esac
tag=${2:-v7r3-rep-$band}
tasks=${3:-}
if [ -z "$tasks" ]; then
  tasks=$(for s in $(ls -1 "$dir"); do
    b=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('band','main'))" "$dir/$s/MANIFEST.json")
    [ "$b" = "$want" ] && echo "$s"
  done | paste -sd, -)
fi
[ -n "$tasks" ] || { echo "no $want slots staged" >&2; exit 2; }
echo "=== $(date +%H:%M:%S) CELL $tag model=$model ctx=$ctx trials=1 timeout=${timeout}s" >&2
echo "=== tasks: $tasks" >&2
"$PY" pibench.py --models "$model" --tasks "$tasks" --tasks-dir "$dir" \
  --trials 3 --think medium --num-ctx "$ctx" --no-tps --timeout "$timeout" --tag "$tag"
rc=$?
echo "=== $(date +%H:%M:%S) DONE $tag rc=$rc" >&2
exit $rc
