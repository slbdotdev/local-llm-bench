#!/bin/bash
# OpenRouter smoke: four models, v5 tiny band, one trial each, all four in parallel.
# Windows-only bench driven from WSL through the Windows interpreter over interop; no ssh.
cd /mnt/c/Users/slb/bench-orsmoke/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
AGENT='C:\Users\slb\bench-orsmoke\ollama-bench\results\pi-agent-smoke'
LOG=results/or-smoke.log
LED=results/or-smoke-ledger.txt
usage() { curl -s https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['usage'])"; }
BASE=$(usage); echo "baseline key usage USD $BASE $(date -Is)" >> "$LED"
echo "=== start or-smoke parallel $(date -Is)" >> "$LOG"
run() { # $1 = tag short, $2 = model id
  PYTHONUTF8=1 "$PY" pibench.py --provider openrouter --models "$2" --think medium --trials 1 \
    --no-tps --timeout 300 --tasks-dir results/v5/authoring/round2/suite-0 --num-ctx 24576 \
    --tag "smoke-$1" --agent-dir "$AGENT" > "results/smoke-$1.log" 2>&1
  echo "=== smoke-$1 exit=$? $(date -Is)" >> "$LOG"
}
run solar    upstage/solar-pro4 &
run ling     inclusionai/ling-3.0-flash &
run nemotron nvidia/nemotron-3-nano-30b-a3b &
run mercury  inception/mercury-2.5-preview &
wait
NOW=$(usage)
echo "after all: key usage USD $NOW, spent USD $(python3 -c "print(round($NOW-$BASE,6))") $(date -Is)" >> "$LED"
echo "=== OR-SMOKE ALLDONE $(date -Is)" >> "$LOG"
