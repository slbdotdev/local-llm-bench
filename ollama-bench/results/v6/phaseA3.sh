#!/bin/bash
# v6 phase A3 -- placement for the three quants that needed a projector strip.
# Waits on strip.sh's own artifact (.strip-done), never on a process name (plan section 9).
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
V6=/mnt/d/local-llm-bench/ollama-bench/results/v6
until [ -f "$V6/.strip-done" ] && [ -f "$V6/.phaseA2-done" ]; do sleep 20; done
echo "=== $(date +%H:%M:%S) strip complete, starting A3" >&2

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

# IQ2_M first: 2 GB of headroom, the one that may reach 128k or more (plan section 6A).
ladder IQ2_M 48k:49152 64k:65536 96k:98304 128k:131072 192k:196608 256k:262144
# IQ3_XS: 64k spilled carrying the projector; re-place it stripped, then its real rung.
cell q27-IQ3_XS-64k 65536 >/dev/null
cell q27-IQ3_XS-48k 49152 >/dev/null
# IQ3_M: 48k only, expected out.
cell q27-IQ3_M-48k 49152 >/dev/null
echo "=== $(date +%H:%M:%S) PHASE A3 COMPLETE" >&2
touch "$V6/.phaseA3-done"
