#!/bin/bash
# v6 phase A2 -- the placement cells that need no projector strip, run while strip.sh works
# the disk. Q2_K, Q2_K_L, Q3_K_S were never projector-carrying; IQ3_XXS is already stripped.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
V6=/mnt/d/local-llm-bench/ollama-bench/results/v6

verdict_of() {
  python3 - "$1" "$2" <<'PY'
import json,sys
try: d=json.load(open('/mnt/d/local-llm-bench/ollama-bench/results/v6/placement.json'))
except Exception: print('none'); raise SystemExit
for r in reversed(d):
    if r['tag']==sys.argv[1] and r['num_ctx']==int(sys.argv[2]): print(r.get('verdict','none')); break
else: print('none')
PY
}
cell() {
  local tag=$1 ctx=$2 to=900
  [ "$ctx" -ge 131072 ] && to=1800
  echo "=== $(date +%H:%M:%S) placing $tag @ $ctx" >&2
  "$PY" results/v6/place.py "$tag" "$ctx" "$to" >/dev/null 2>&1
  local v; v=$(verdict_of "$tag" "$ctx"); echo "=== $(date +%H:%M:%S) $tag @ $ctx -> $v" >&2; echo "$v"
}
ladder() {
  local q=$1; shift
  for rung in "$@"; do
    local n=${rung%%:*} c=${rung##*:}
    local v; v=$(cell "q27-$q-$n" "$c")
    case "$v" in spill|load_failed|none) echo "=== ladder $q stops at $n ($v)" >&2; return 0;; esac
  done
}

# IQ3_XXS is stripped: find its real rung, and check 96k only if 48k is clean.
cell q27-IQ3_XXS-48k 49152 >/dev/null
# Q2_K -- never carried a projector.
ladder Q2_K 48k:49152 64k:65536 96k:98304 128k:131072
# Q2_K_L from 96k up (its 64k is the calibration cell, already placed).
ladder Q2_K_L 96k:98304 128k:131072 192k:196608 256k:262144
# Expected out, placed last so their failure costs nothing.
cell q27-Q3_K_S-48k 49152 >/dev/null
echo "=== $(date +%H:%M:%S) PHASE A2 COMPLETE" >&2
touch "$V6/.phaseA2-done"
