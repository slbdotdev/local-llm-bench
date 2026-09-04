#!/usr/bin/env bash
# fp8 reference (OR qwen3.8-27b, medium) on the v3 hard subset, for quant-loss comparison
cd ~/ollama-bench
PYTHONUTF8=1 python pibench.py --provider openrouter --models qwen/qwen3.8-27b --think medium --trials 2 --no-tps --tasks-dir tasks-v3 --tasks 32_wirefmt,33_spanmap,34_tmplfix,35_ledger,36_minilang --tag v3-hard-ref-medium --agent-dir "$PWD/results/pi-agent-v3" >> results/v3-hard-ref-medium.log 2>&1
echo "ALLDONE exit=$?" >> results/v3-hard-ref-medium.log
