#!/usr/bin/env bash
# GLM 5.3 Flash on the 7 v4 keepers at fp8-reference parity (medium, 3 trials, 1800 s, pi-agent-v4),
# one pibench process per task in parallel (OpenRouter, no GPU). Results results/glm-v4-<task>.json.
cd /c/Users/slb/ollama-bench
LOG=results/glm-v4.log; LED=results/glm-v4-ledger.txt
usage() { curl -s https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $OPENROUTER_API_KEY" | python -c "import sys,json; print(json.load(sys.stdin)['data']['usage'])"; }
BASE=$(usage); echo "baseline key usage USD $BASE $(date -Is)" >> "$LED"
echo "=== start glm-v4 parallel $(date -Is)" >> "$LOG"
for t in 52_reengine 55_minilang 56_tmpl 57_stateful 59_uri 60_numlit 61_codecs; do
  ( PYTHONUTF8=1 python pibench.py --provider openrouter --models z-ai/glm-5.3-flash --think medium --trials 3 --no-tps \
      --timeout 1800 --tasks-dir tasks-v4 --tasks $t --tag "glm-v4-$t" --agent-dir "$PWD/results/pi-agent-v4" \
      > "results/glm-v4-$t.log" 2>&1; echo "=== $t exit=$? $(date -Is)" >> "$LOG" ) &
done
wait
NOW=$(usage); echo "after all: key usage USD $NOW, spent USD $(python -c "print(round($NOW-$BASE,4))") $(date -Is)" >> "$LED"
echo "=== GLM-V4 ALLDONE $(date -Is)" >> "$LOG"
