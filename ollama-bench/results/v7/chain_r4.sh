#!/bin/bash
# chain_r4.sh [tasks-main] [tasks-cheap] — the GPU acceptance sweep for round four.
# One workhorse trial per accepted candidate. Phases, each with a marker
# results/v7/.r4-<phase>-done:
#   probe    the Windows-interpreter scope-gate probe on the round-4 staging (CPU only)
#   r4main   round-4 main-band candidates on q27-IQ2_M-64k
#   r4cheap  round-4 cheap24 candidates on q27-IQ2_M-24k
# Log: results/v7/r4gate.log. A failed probe stops the chain: a reference that cannot score
# `correct` under the grading interpreter makes every row after it meaningless (D7-31,
# calibration section 5).
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
LOG=results/v7/r4gate.log
main_tasks=${1:-}
cheap_tasks=${2:-}
mark() { date +%H:%M:%S > "results/v7/.r4-$1-done"; }
echo "== $(date +%H:%M:%S) chain begins" >> "$LOG"
bash results/v7/probe_scope_gate_r4.sh >> "$LOG" 2>&1; rc=$?
echo "== $(date +%H:%M:%S) probe rc=$rc" >> "$LOG"
if [ $rc -ne 0 ]; then echo "== probe failed; chain stopped" >> "$LOG"; mark probe-failed; exit 1; fi
mark probe
if [ -n "$main_tasks" ] || [ -z "$cheap_tasks" ]; then
  bash results/v7/runcell-r4.sh main v7r4-gate-main "$main_tasks" >> "$LOG" 2>&1
  echo "== $(date +%H:%M:%S) r4main rc=$?" >> "$LOG"; mark r4main
fi
bash results/v7/runcell-r4.sh cheap v7r4-gate-cheap "$cheap_tasks" >> "$LOG" 2>&1
echo "== $(date +%H:%M:%S) r4cheap rc=$?" >> "$LOG"; mark r4cheap
echo "== $(date +%H:%M:%S) chain complete" >> "$LOG"
date +%H:%M:%S > results/v7/.r4-chain-done
