#!/bin/bash
# Wait for the 5-hour window to reset, then restart the guard and launch the endgame:
# the rest of Hlineno-tiny, and the baseline holdout arm, together.
set -u
P=/home/slb/bench-prompt/ollama-bench/results/prompt-v1
HOLDOUT_TASKS="g01,g03,g04,t01,t02,t03,t04"   # g02 excluded: 46% of the band's input tokens
while true; do
  out=$(source ~/.config/devbox/env && python3 "$P/zai-quota.py" waitreset 2>&1)
  pct=$(echo "$out" | sed -n 's/^GATE 5h=\([0-9.]*\)%.*/\1/p')
  echo "$(date -Is) waiting for reset, 5h=${pct:-?}" >> "$P/logs/quota.log"
  if [ -n "${pct:-}" ] && awk "BEGIN{exit !(${pct} < 25)}"; then
    echo "$(date -Is) WINDOW RESET, 5h=${pct}% -- launching endgame" >> "$P/logs/quota.log"
    break
  fi
  sleep 120
done
rm -f "$P/logs/quota.tripped"
setsid --fork bash "$P/quotaguard.sh" < /dev/null > /dev/null 2>&1
sleep 2
bash "$P/launch.sh" Hlineno-tiny Hlineno tiny 3 >> "$P/logs/quota.log" 2>&1
PV1_TASKS="$HOLDOUT_TASKS" bash "$P/launch.sh" base-large baseline large 1 >> "$P/logs/quota.log" 2>&1
echo "$(date -Is) endgame launched" >> "$P/logs/quota.log"
echo launched > "$P/logs/endgame.started"
