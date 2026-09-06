#!/bin/bash
# chain_r3.sh — the GPU acceptance sweep for rounds 2 and 3, one workhorse trial per candidate.
# Phases, each with a marker results/v7/.r3-<phase>-done:
#   probe   the Windows-interpreter scope-gate probe on the round-3 staging (CPU only)
#   r2      nine round-2 main-band candidates on q27-IQ2_M-64k
#   r3main  round-3 main-band candidates on q27-IQ2_M-64k
#   r3cheap round-3 cheap24 candidates on q27-IQ2_M-24k
# Log: results/v7/r3gate.log. A failed probe stops the chain: a reference that cannot score
# `correct` under the grading interpreter makes every row after it meaningless (D7-31).
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
LOG=results/v7/r3gate.log
mark() { date +%H:%M:%S > "results/v7/.r3-$1-done"; }
echo "== $(date +%H:%M:%S) chain begins" >> "$LOG"
bash results/v7/probe_scope_gate_r3.sh >> "$LOG" 2>&1; rc=$?
echo "== $(date +%H:%M:%S) probe rc=$rc" >> "$LOG"
if [ $rc -ne 0 ]; then echo "== probe failed; chain stopped" >> "$LOG"; mark probe-failed; exit 1; fi
mark probe
bash results/v7/runcell-r2.sh v7r2-gate >> "$LOG" 2>&1; echo "== $(date +%H:%M:%S) r2 rc=$?" >> "$LOG"; mark r2
bash results/v7/runcell-r3.sh main v7r3-gate-main n01-main-claude,n02-main-glm,n03-main-luna,n04-main-claude,n05-main-luna,n07-main-claude >> "$LOG" 2>&1; echo "== $(date +%H:%M:%S) r3main rc=$?" >> "$LOG"; mark r3main
bash results/v7/runcell-r3.sh cheap >> "$LOG" 2>&1; echo "== $(date +%H:%M:%S) r3cheap rc=$?" >> "$LOG"; mark r3cheap
echo "== $(date +%H:%M:%S) chain complete" >> "$LOG"
