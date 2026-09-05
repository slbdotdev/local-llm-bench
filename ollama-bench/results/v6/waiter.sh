#!/bin/bash
# v6 waiter -- one event per phase boundary, plus a stall alarm, then exits at the end of
# phase E. Polls OUTCOMES only: the done-flags the phase drivers touch, and the mtime of the
# newest artifact under results/. Never `pgrep -f`.
#
# Coverage note: a chain that dies produces no new flag, which is indistinguishable from
# "still working" -- so silence is not success here. The stall alarm is what covers that: if
# no artifact anywhere has been written for STALL_MIN minutes, something is wrong and it says
# so rather than staying quiet.
V6=/mnt/d/local-llm-bench/ollama-bench/results/v6
RES=/mnt/d/local-llm-bench/ollama-bench/results
STALL_MIN=15
seen=""
last_change=$(date +%s)
last_stamp=""
while true; do
  for f in "$V6"/.*-done; do
    [ -e "$f" ] || continue
    b=$(basename "$f")
    case " $seen " in *" $b "*) ;; *)
      seen="$seen $b"
      echo "PHASE BOUNDARY: $b at $(date +%H:%M:%S)"
      ;;
    esac
  done
  # newest artifact mtime across the campaign's outputs
  stamp=$(find "$RES" -maxdepth 1 -name 'v6-*.json' -newermt '-1 day' -printf '%T@\n' 2>/dev/null | sort -n | tail -1)
  pstamp=$(stat -c %Y "$V6/placement.json" 2>/dev/null)
  cur="${stamp}-${pstamp}"
  if [ "$cur" != "$last_stamp" ]; then last_stamp="$cur"; last_change=$(date +%s); fi
  now=$(date +%s)
  if [ $(( (now - last_change) / 60 )) -ge $STALL_MIN ]; then
    echo "STALL: no v6 artifact written for $STALL_MIN min as of $(date +%H:%M:%S) -- a chain may have died"
    last_change=$now
  fi
  if [ -e "$V6/.phaseE-done" ]; then
    echo "CAMPAIGN COMPLETE: phase E done at $(date +%H:%M:%S)"
    exit 0
  fi
  sleep 45
done
