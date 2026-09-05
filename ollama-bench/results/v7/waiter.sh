#!/bin/bash
# waiter.sh <phase>
#
# One event per newly-finished trial, one per finished cell, one when the phase's
# marker appears, and a stall alarm when the GPU is idle with no pibench alive and
# no marker — v6's D6-41 cost 26 minutes of idle GPU to exactly that state, which is
# why the alarm prints GPU utilisation beside itself.
#
# Never polls a process name to decide whether work is alive: `pgrep -f` matches the
# waiting shell itself. It polls the log's own trial lines and the marker file, and
# uses a bracket class for the one process check it does make.
#
# Run it under a Monitor; each stdout line becomes one notification, and it emits
# only on change so an hour of quiet work is an hour of quiet.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
phase=${1:?phase}
marker="results/v7/.cal-$phase-done"
log=results/v7/cal.log
seen=0
stalled=0
while true; do
  if [ -f "$log" ]; then
    lines=$(grep -acE '^  m[0-9]|^=== [0-9:]+ (CELL|DONE) ' "$log" 2>/dev/null || echo 0)
    if [ "$lines" -gt "$seen" ]; then
      grep -aE '^  m[0-9]|^=== [0-9:]+ (CELL|DONE) ' "$log" | tail -n $((lines - seen))
      seen=$lines
      stalled=0
    fi
  fi
  if [ -f "$marker" ]; then
    echo "PHASE $phase COMPLETE"
    exit 0
  fi
  g=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1)
  alive=$(ps -eo args | grep -c '[p]ibench\.py')
  if [ "${g:-100}" -lt 5 ] && [ "$alive" -eq 0 ]; then
    stalled=$((stalled + 1))
    if [ "$stalled" -eq 2 ]; then
      echo "STALL ALARM: GPU ${g}% utilisation, no pibench process, no $marker — the chain is dead"
    fi
  else
    stalled=0
  fi
  sleep 45
done
