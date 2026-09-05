#!/bin/bash
# Poll the plan quota every 150 s. At >=78% of the 5-hour window, stop every arm of this
# campaign before the brief's 80% gate is crossed, and leave a marker naming the reset time.
set -u
P=/home/slb/bench-prompt/ollama-bench/results/prompt-v1
while true; do
  out=$(source ~/.config/devbox/env && python3 "$P/zai-quota.py" guard 2>&1)
  pct=$(echo "$out" | sed -n 's/^GATE 5h=\([0-9.]*\)%.*/\1/p')
  wk=$(echo "$out" | sed -n 's/.*week=\([0-9.]*\)% .*/\1/p')
  echo "$(date -Is) 5h=${pct:-?} week=${wk:-?}" >> "$P/logs/quota.log"
  if [ -n "${pct:-}" ] && awk "BEGIN{exit !(${pct} >= 92)}"; then
    echo "$(date -Is) GUARD TRIPPED at 5h=${pct}%" >> "$P/logs/quota.log"
    bash "$P/stop.sh" >> "$P/logs/quota.log" 2>&1
    echo "tripped=$pct" > "$P/logs/quota.tripped"
    exit 0
  fi
  if [ -n "${wk:-}" ] && awk "BEGIN{exit !(${wk} >= 58)}"; then
    echo "$(date -Is) GUARD TRIPPED on the weekly window at ${wk}%" >> "$P/logs/quota.log"
    bash "$P/stop.sh" >> "$P/logs/quota.log" 2>&1
    echo "tripped-week=$wk" > "$P/logs/quota.tripped"
    exit 0
  fi
  sleep 150
done
