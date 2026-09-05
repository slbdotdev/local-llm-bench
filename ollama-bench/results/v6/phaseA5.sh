#!/bin/bash
# v6 phase A5 -- place reserve rank 2 (mrIQ3M), the swap for rejected Q3_K_S, inside phase A
# so it is ranked against the roster on the same instrument (same reasoning as D6-15).
# Waits on phase A4's flag (GPU free) and on the pull's own outcome (the tag existing).
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
V6=results/v6
NAME=mrIQ3M
SRC='hf.co/mradermacher/Qwen3.8-27B-i1-GGUF:i1-IQ3_M'

have_tag() { "$PY" -c "
import json,urllib.request,sys
d=json.load(urllib.request.urlopen('http://localhost:11434/api/tags',timeout=30))
sys.exit(0 if any(m['name'].split(':')[0]=='q27-$NAME-64k' for m in d['models']) else 1)
" 2>/dev/null; }

until [ -f "$V6/.phaseA4-done" ]; do sleep 30; done
echo "=== $(date +%H:%M:%S) A4 done; waiting on the rank 2 pull" >&2
n=0
until have_tag; do sleep 60; n=$((n+1)); if [ $n -gt 45 ]; then echo "=== rank 2 pull did not land in 45 min; releasing phase B without it" >&2; touch "$V6/.phaseA5-done"; exit 0; fi; done

dig=$("$PY" -c "
import json,os
p=os.path.join(os.path.expanduser('~'),'.ollama','models','manifests','registry.ollama.ai','library','q27-$NAME-64k','latest')
d=json.load(open(p)); mdl=proj=None
for l in d['layers']:
    if l['mediaType'].endswith('.model'): mdl=l['digest'].replace(':','-')
    if l['mediaType'].endswith('.projector'): proj=1
print(mdl if proj else '')
" 2>/dev/null)
if [ -n "$dig" ]; then
  free=$("$PY" -c "import shutil;t,u,f=shutil.disk_usage('C:\\\\');print(int(f/1e9))")
  if [ "$free" -ge 15 ]; then
    echo "=== $(date +%H:%M:%S) stripping $NAME projector (C: ${free} GB free)" >&2
    bash "$V6/bake.sh" "q27-$NAME-48k" "C:\\Users\\slb\\.ollama\\models\\blobs\\$dig" 49152 >&2
    bash "$V6/bake.sh" "q27-$NAME-64k" "q27-$NAME-48k" 65536 >&2
    "$OLLAMA" rm "$SRC" >/dev/null 2>&1
  else
    echo "=== $(date +%H:%M:%S) only ${free} GB free; $NAME keeps its projector and the row says so" >&2
  fi
fi
for spec in "q27-$NAME-64k 65536" "q27-$NAME-48k 49152"; do
  set -- $spec
  echo "=== $(date +%H:%M:%S) placing $1 @ $2" >&2
  "$PY" results/v6/place.py "$1" "$2" 900 >/dev/null 2>&1
done
echo "=== $(date +%H:%M:%S) PHASE A5 COMPLETE" >&2
touch "$V6/.phaseA5-done"
