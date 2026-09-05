#!/bin/bash
# restart_chain.sh -- stop the campaign chain and start it again, atomically.
#
# D6-41: stopping the chain and restarting it were two separate actions all evening, and the
# one time the second was forgotten the GPU sat idle for 26 minutes. Killing without restarting
# is never what this campaign wants, so the two are now one command.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
V6=/mnt/d/local-llm-bench/ollama-bench/results/v6
for g in $(ps -eo pgid,args | grep -v grep | awk '$0 ~ /chainAll\.sh|recheck\.sh|phaseB\.py|phaseC\.py|phaseDE\.py/ {print $1}' | sort -u); do
  kill -TERM -"$g" 2>/dev/null && echo "stopped pgid $g"
done
sleep 3
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass \
  -File 'D:\local-llm-bench\ollama-bench\results\v6\kill_pi.ps1' 2>&1 | tr -d '\r'
rm -f "$V6/.phaseB-done" "$V6/.phaseC-done"
setsid nohup bash results/v6/chainAll.sh > "$V6/phaseAll.log" 2>&1 < /dev/null &
sleep 5
if ps -eo args | grep -v grep | grep -q 'chainAll\.sh'; then
  echo "chain restarted at $(date +%H:%M:%S)"
else
  echo "FAILED TO RESTART -- the GPU is idle, fix this now"; exit 1
fi
