#!/bin/bash
# Bounded closing GPU burst, so the campaign ends with the card idle rather than with a
# six-hour pass holding the Windows converge.
#
# Why this shape. q27-Q3_K_S-64k took 1456.9 s on g01 where q27-Q2_K_L-64k took 58.6 s -- 25x --
# because it sits at 15.78 GB resident on a 16.3 GB card. Plan section 6's verdict wall is 900 s,
# so every remaining Q3_K_S-64k and IQ3_M-64k trial is already a fail on wall time whatever its
# checker says. Confirming that on seven more tasks costs three hours to re-establish a
# disqualification that one row and two resident sizes already establish.
#
# So: one cheap task (t03, 35.4 s on Q2_K_L) on each of the two remaining 64k quants to show the
# slowdown is the configuration and not the task, then the Q3_K_M 48k partial row. --timeout 900
# aligns the harness with the verdict wall, so a trial that would breach it is recorded as the
# timeout it is instead of running to 1800 s.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
"$PY" pibench.py --models q27-Q3_K_S-64k,q27-IQ3_M-64k --tasks t03 \
  --tasks-dir results/v5/authoring/round3/suite \
  --trials 1 --think medium --num-ctx 65536 --no-tps --timeout 900 --tag bend-large-64k
echo "64k-confirm exit=$?"
"$PY" pibench.py --models q27-Q3_K_M-48k --tasks g03,t02,t03 \
  --tasks-dir results/v5/authoring/round3/suite \
  --trials 1 --think medium --num-ctx 49152 --no-tps --timeout 900 --tag bend-large-48k-q3km
echo "48k exit=$?"
