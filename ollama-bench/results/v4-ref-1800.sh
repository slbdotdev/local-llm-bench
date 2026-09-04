#!/usr/bin/env bash
# fp8 reference for the v4 keepers at parity with the local ranking (medium, 3 trials, 1800 s), plus
# one 53_gitattr trial. Running USD ledger from the OpenRouter key API; stops at the cap.
cd /c/Users/slb/ollama-bench
LOG=results/v4-ref-medium-1800.log; LED=results/v4-ref-ledger.txt
CAP=9.50
usage() { curl -s https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $OPENROUTER_API_KEY" | python -c "import sys,json; print(json.load(sys.stdin)['data']['usage'])"; }
BASE=$(usage); echo "baseline key usage USD $BASE $(date -Is)" >> "$LED"
run() { # $1 tasks-dir, $2 task, $3 trials
  PYTHONUTF8=1 python pibench.py --provider openrouter --models qwen/qwen3.8-27b --think medium --trials $3 --no-tps --timeout 1800 --tasks-dir $1 --tasks $2 --tag v4-ref-medium-1800 --agent-dir "$PWD/results/pi-agent-v4" >> "$LOG" 2>&1
  NOW=$(usage); SPENT=$(python -c "print(round($NOW-$BASE,4))")
  echo "after $2: key usage USD $NOW, spent this stage USD $SPENT $(date -Is)" >> "$LED"
  echo "=== $2 exit=$? spent=$SPENT" >> "$LOG"
  python -c "import sys; sys.exit(0 if $SPENT < $CAP else 1)" || { echo "CAP REACHED USD $SPENT" | tee -a "$LOG" >> "$LED"; exit 0; }
}
for t in 52_reengine 55_minilang 56_tmpl 57_stateful 59_uri 60_numlit 61_codecs; do run tasks-v4 $t 3; done
run tasks-v4-rejected 53_gitattr 1
echo ALLDONE >> "$LOG"
