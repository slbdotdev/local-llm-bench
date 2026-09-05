#!/bin/bash
# usage: launch.sh <tag> <variant-name> <tiny|large> <trials>
# Every arm loads the fleet's production pi-resilience.ts FIRST, then the variant, then the
# tracer, exactly as the brief's PIBENCH_PI_ARGS line specifies.
set -u
H=/home/slb/bench-prompt/ollama-bench
V=C:/Users/slb/bench-prompt-variants
RES=C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts
TAG=$1; NAME=$2; BAND=$3; TRIALS=$4
cd "$H" || exit 9
PV1_TASKS="${PV1_TASKS:-}" \
  PIBENCH_KEEP="C:/Users/slb/bench-prompt-variants/keep/$TAG" \
PV1_TRACE_DIR="C:/Users/slb/bench-prompt-variants/traces/$TAG" \
setsid --fork bash results/prompt-v1/supervise.sh "$TAG" "$BAND" "$TRIALS" \
  -e "$RES" -e "$V/$NAME.ts" -e "$V/trace.ts" \
  < /dev/null >> "results/prompt-v1/logs/$TAG.sup" 2>&1
echo "launched $TAG ($NAME, $BAND, $TRIALS trials)"
