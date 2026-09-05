#!/bin/bash
# v6 phase A4 -- place the reserve candidate pulled during phase A (D6-13), so it joins the
# same ordering every roster quant is in rather than being bolted on afterwards.
# Waits on BOTH outcomes: phase A3's flag (the GPU is free) and the pull's own tag existing.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
V6=results/v6
NAME=UDQ3KXL
SRC='hf.co/unsloth/Qwen3.8-27B-GGUF:UD-Q3_K_XL'

have_tag() { "$PY" -c "
import json,urllib.request,sys
d=json.load(urllib.request.urlopen('http://localhost:11434/api/tags',timeout=30))
sys.exit(0 if any(m['name'].split(':')[0]=='q27-$NAME-64k' for m in d['models']) else 1)
" 2>/dev/null; }

until [ -f "$V6/.phaseA3-done" ]; do sleep 30; done
echo "=== $(date +%H:%M:%S) phase A3 done; waiting on the reserve pull" >&2
n=0
until have_tag; do sleep 60; n=$((n+1)); if [ $n -gt 40 ]; then echo "=== pull did not land in 40 min; skipping $NAME" >&2; touch "$V6/.phaseA4-done"; exit 0; fi; done
echo "=== $(date +%H:%M:%S) $NAME tags present" >&2

# Strip the projector if the pull brought one (D6-11). One blob import, then derive.
dig=$("$PY" -c "
import json,os
p=os.path.join(os.path.expanduser('~'),'.ollama','models','manifests','registry.ollama.ai','library','q27-$NAME-64k','latest')
d=json.load(open(p))
mdl=proj=None
for l in d['layers']:
    if l['mediaType'].endswith('.model'): mdl=l['digest'].replace(':','-')
    if l['mediaType'].endswith('.projector'): proj=1
print(mdl if proj else '')
" 2>/dev/null)
if [ -n "$dig" ]; then
  echo "=== $(date +%H:%M:%S) $NAME carries a projector; stripping" >&2
  free=$("$PY" -c "import shutil;t,u,f=shutil.disk_usage('C:\\\\');print(int(f/1e9))")
  if [ "$free" -ge 15 ]; then
    bash "$V6/bake.sh" "q27-$NAME-48k" "C:\\Users\\slb\\.ollama\\models\\blobs\\$dig" 49152 >&2
    bash "$V6/bake.sh" "q27-$NAME-64k" "q27-$NAME-48k" 65536 >&2
    bash "$V6/bake.sh" "q27-$NAME-96k" "q27-$NAME-48k" 98304 >&2
    "$OLLAMA" rm "$SRC" >/dev/null 2>&1
    echo "=== $(date +%H:%M:%S) $NAME stripped" >&2
  else
    echo "=== $(date +%H:%M:%S) only ${free} GB free; leaving $NAME projector in place and saying so" >&2
  fi
else
  bash "$V6/bake.sh" "q27-$NAME-96k" "q27-$NAME-64k" 98304 >&2
fi

for spec in "q27-$NAME-64k 65536" "q27-$NAME-48k 49152"; do
  set -- $spec
  echo "=== $(date +%H:%M:%S) placing $1 @ $2" >&2
  "$PY" results/v6/place.py "$1" "$2" 900 >/dev/null 2>&1
  echo "=== $(date +%H:%M:%S) placed $1" >&2
done
echo "=== $(date +%H:%M:%S) PHASE A4 COMPLETE" >&2
touch "$V6/.phaseA4-done"
