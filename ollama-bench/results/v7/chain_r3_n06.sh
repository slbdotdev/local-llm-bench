#!/bin/bash
# chain_r3_n06.sh — the n06-main-glm workhorse cell, queued behind chain_r3.sh (n06 was in
# revision when the chain started). Marker: results/v7/.r3-n06-done.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
LOG=results/v7/r3gate.log
until [ -f results/v7/.r3-r3cheap-done ]; do sleep 20; done
bash results/v7/runcell-r3.sh main v7r3-gate-n06 n06-main-glm >> "$LOG" 2>&1; echo "== $(date +%H:%M:%S) n06 rc=$?" >> "$LOG"
date +%H:%M:%S > results/v7/.r3-n06-done
