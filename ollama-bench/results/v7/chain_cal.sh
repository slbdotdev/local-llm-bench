#!/bin/bash
# chain_cal.sh <phase>
#
# The v7 calibration chain. One phase per invocation, one cell at a time, always
# serial: two cells at once would make every wall figure a contention figure.
# Launched detached, never as a harness background task — this harness kills
# long-lived background tasks that use memory (org/pending.md, 2026-09-05):
#
#   setsid -f bash results/v7/chain_cal.sh p1 < /dev/null > results/v7/cal.log 2>&1
#
# and watched by polling the marker file, never a process name (pgrep -f matches
# the waiting shell itself).
#
#   p1  first pass: one trial per task, both bands, on the workhorse IQ2_M at 64k
#   p2  second pass: three trials per task on whatever calibration changed,
#       task list read from results/v7/tuned-tasks.txt (one slot per line)
#   p3  neighbours: one trial per task, both bands, UDQ3KXL at 48k and Q2_K at 64k
#
# Markers: results/v7/.cal-<phase>-done
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
phase=${1:?phase}
R=results/v7/runcell.sh

echo "== $(date +%H:%M:%S) phase $phase begins" >&2

case $phase in
  p1)
    bash "$R" IQ2_M 64k 65536 main  1 v7cal-IQ2_M-main
    bash "$R" IQ2_M 24k 24576 cheap 1 v7cal-IQ2_M-cheap
    ;;
  p2)
    list=$(paste -sd, - < results/v7/tuned-tasks.txt)
    main=$(printf '%s\n' "${list//,/$'\n'}" | grep -- '-main-' | paste -sd, -)
    cheap=$(printf '%s\n' "${list//,/$'\n'}" | grep -- '-cheap-' | paste -sd, -)
    [ -n "$main" ]  && bash "$R" IQ2_M 64k 65536 main  3 v7cal2-IQ2_M-main  "$main"
    [ -n "$cheap" ] && bash "$R" IQ2_M 24k 24576 cheap 3 v7cal2-IQ2_M-cheap "$cheap"
    ;;
  p3)
    bash "$R" UDQ3KXL 48k 49152 main  1 v7cal-UDQ3KXL-main
    bash "$R" UDQ3KXL 24k 24576 cheap 1 v7cal-UDQ3KXL-cheap
    bash "$R" Q2_K    64k 65536 main  1 v7cal-Q2_K-main
    bash "$R" Q2_K    24k 24576 cheap 1 v7cal-Q2_K-cheap
    ;;
  *) echo "unknown phase $phase" >&2; exit 2 ;;
esac

echo "== $(date +%H:%M:%S) phase $phase complete" >&2
touch "results/v7/.cal-$phase-done"
