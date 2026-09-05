#!/bin/bash
# chain_after.sh — everything that follows the tuning, in one detached run.
#
#   1. re-assemble suite/ from the repaired and hardened candidates. This must happen before
#      any cell reads the suite, and must never happen while one is reading it: assemble_suite
#      rmtree's the directory and re-copies it.
#   2. phase p2 — three trials per task on every task that changed, on the workhorse.
#   3. phase p3 — one trial per task on the two neighbours, both bands.
#
# Launched detached, watched by polling the markers:
#   setsid -f bash results/v7/chain_after.sh < /dev/null >> results/v7/cal.log 2>&1
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1

echo "== $(date +%H:%M:%S) re-assembling the suite with the hardened tasks" >&2
PYTHONDONTWRITEBYTECODE=1 python3 results/v7/authoring/assemble_suite.py >&2 || exit 1

bash results/v7/chain_cal.sh p2
bash results/v7/chain_cal.sh p3

echo "== $(date +%H:%M:%S) p2 and p3 complete" >&2
touch results/v7/.cal-after-done
