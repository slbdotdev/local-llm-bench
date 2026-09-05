#!/bin/bash
# jit_pull.sh <NAME> <src> -- the owner's just-in-time pull rule (D6-29).
#
# Launched by phaseDE.py at the START of the campaign's final scored cell, so the download
# overlaps exactly one trial and nothing else. The PLACEMENT then waits for the campaign's own
# completion flag before touching the GPU, so a pull and a trial overlap (which the plan allows)
# but two GPU loads never do (which it forbids).
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
V6=results/v6
NAME=$1; SRC=$2

echo "=== $(date +%H:%M:%S) JIT resume of $SRC (blob is already on disk as a -partial)" >&2
if ! "$OLLAMA" pull "$SRC"; then
  echo "=== $(date +%H:%M:%S) pull failed; retrying once" >&2
  "$OLLAMA" pull "$SRC" || { echo "=== $(date +%H:%M:%S) PULL FAILED TWICE; giving up, no placement" >&2; exit 3; }
fi
echo "=== $(date +%H:%M:%S) pulled; waiting for the GPU to go idle before placing" >&2
until [ -f "$V6/.phaseE-done" ]; do sleep 20; done

bash "$V6/bake.sh" "q27-$NAME-64k" "$SRC" 65536 >&2 || exit 4
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
    echo "=== $(date +%H:%M:%S) stripping $NAME projector (D6-11)" >&2
    bash "$V6/bake.sh" "q27-$NAME-48k" "C:\\Users\\slb\\.ollama\\models\\blobs\\$dig" 49152 >&2
    bash "$V6/bake.sh" "q27-$NAME-64k" "q27-$NAME-48k" 65536 >&2
    "$OLLAMA" rm "$SRC" >/dev/null 2>&1
  else
    echo "=== $(date +%H:%M:%S) only ${free} GB free; $NAME keeps its projector and the row says so" >&2
    bash "$V6/bake.sh" "q27-$NAME-48k" "$SRC" 49152 >&2
  fi
else
  bash "$V6/bake.sh" "q27-$NAME-48k" "q27-$NAME-64k" 49152 >&2
fi
for spec in "q27-$NAME-64k 65536" "q27-$NAME-48k 49152"; do
  set -- $spec
  echo "=== $(date +%H:%M:%S) placing $1 @ $2" >&2
  "$PY" results/v6/place.py "$1" "$2" 900 >/dev/null 2>&1
done
echo "=== $(date +%H:%M:%S) JIT PLACEMENT COMPLETE for $NAME" >&2
touch "$V6/.jitpull-done"
