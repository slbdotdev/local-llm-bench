#!/bin/bash
# chain_cal_r4.sh — round-four calibration, one GPU cell at a time.
#   s   survivors pass: the suite tasks round four cannot replace, three trials each,
#       written under the round's final tags so the post-admission cells resume the same
#       artifact instead of repeating it (pibench skips (task, trial) pairs already there).
#   f   full pass: every suite task, three trials, same tags — only the missing rows run.
#   n   neighbours: one trial per task, both bands, UDQ3KXL-48k and Q2_K-64k.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
phase=${1:?phase}
R=results/v7/runcell.sh
D=/home/slb/v7r4
echo "== $(date +%H:%M:%S) cal phase $phase begins" >&2
case $phase in
  s)
    bash "$R" IQ2_M 64k 65536 main  3 v7r4cal-IQ2_M-main \
      m03-main-glm,m06-main-glm,m07-main-claude,m08-main-luna,m10-main-claude
    bash "$R" IQ2_M 24k 24576 cheap 3 v7r4cal-IQ2_M-cheap \
      m01-cheap-luna,m02-cheap-glm,m03-cheap-claude,m04-cheap-luna,m05-cheap-glm,m06-cheap-claude,m07-cheap-luna,m09-cheap-claude,m10-cheap-luna
    ;;
  f)
    bash "$R" IQ2_M 64k 65536 main  3 v7r4cal-IQ2_M-main
    bash "$R" IQ2_M 24k 24576 cheap 3 v7r4cal-IQ2_M-cheap
    ;;
  n)
    bash "$R" UDQ3KXL 48k 49152 main  1 v7r4cal-UDQ3KXL-main
    bash "$R" UDQ3KXL 24k 24576 cheap 1 v7r4cal-UDQ3KXL-cheap
    bash "$R" Q2_K    64k 65536 main  1 v7r4cal-Q2_K-main
    bash "$R" Q2_K    24k 24576 cheap 1 v7r4cal-Q2_K-cheap
    ;;
  *) echo "unknown phase $phase" >&2; exit 2 ;;
esac
echo "== $(date +%H:%M:%S) cal phase $phase complete" >&2
date +%H:%M:%S > "$D/.cal-r4-$phase-done"
