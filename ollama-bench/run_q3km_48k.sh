#!/bin/bash
# Queue item 3: Q3_K_M at 48k on the three large-band tasks whose 1.6x working margin fits.
#
# Q3_K_M stops at 48k (plan section 4), so it cannot hold the large band as a whole -- but
# g03 (30,018 tok), t02 (31,102) and t03 (30,604) all clear 1.6x inside a 48k window, and
# running them turns a blank cell in the grid into a stated capacity result.
#
# Chained behind the 64k pass by polling that pass's OWN ARTIFACT, never `pgrep -f`, whose
# pattern would match this waiter's own command line.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
until "$PY" -c "
import json,sys
d=json.load(open('results/bend-large-64k.json'))
sys.exit(0 if len([t for t,v in d.items() if len(v.get('runs',[]))>=8])>=3 else 1)
" 2>/dev/null; do sleep 60; done
echo "64k large band complete; starting Q3_K_M 48k partial row" >&2
"$PY" pibench.py \
  --models q27-Q3_K_M-48k \
  --tasks g03,t02,t03 \
  --tasks-dir results/v5/authoring/round3/suite \
  --trials 1 --think medium --num-ctx 49152 --tag bend-large-48k-q3km
echo "exit=$?"
