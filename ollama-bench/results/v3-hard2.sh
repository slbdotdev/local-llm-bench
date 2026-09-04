#!/usr/bin/env bash
cd ~/ollama-bench
for t in 34_tmplfix 35_ledger 36_minilang; do
  PYTHONUTF8=1 python pibench.py --provider openrouter --models qwen/qwen3.8-27b --think low --trials 3 --no-tps --tasks-dir tasks-v3 --tasks $t --tag v3-low --agent-dir "$PWD/results/pi-agent-v3" >> results/v3-hard.log 2>&1
  echo "=== $t exit=$?" >> results/v3-hard.log
done
PYTHONUTF8=1 python pibench.py --provider openrouter --models qwen/qwen3.8-27b --think low --trials 6 --no-tps --tasks-dir tasks-v3 --tasks 31_stackvm --tag v3-low --agent-dir "$PWD/results/pi-agent-v3" >> results/v3-hard.log 2>&1
echo ALLDONE >> results/v3-hard.log
