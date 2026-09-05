#!/bin/bash
# Chain the large-band bend-finding pass behind the small-band one.
# Poll the OUTCOME (the small pass's own artifact reaching four completed tags),
# never `pgrep -f`, whose pattern matches this waiter's own command line.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
until "$PY" -c "
import json,sys
d=json.load(open('results/bend-small-24k.json'))
sys.exit(0 if len([t for t,v in d.items() if len(v.get('runs',[]))>=8])>=4 else 1)
" 2>/dev/null; do sleep 30; done
echo "small band complete; starting large band" >&2
# Q3_K_M is excluded: it stops at 48k and the large band needs 64k.
"$PY" pibench.py \
  --models q27-Q2_K_L-64k,q27-Q3_K_S-64k,q27-IQ3_M-64k \
  --tasks-dir results/v5/authoring/round3/suite \
  --trials 1 --think medium --num-ctx 65536 --tag bend-large-64k
echo "exit=$?"
