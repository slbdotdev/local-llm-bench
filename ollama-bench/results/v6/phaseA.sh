#!/bin/bash
# v6 phase A -- placement, all quants, most-informative first (plan section 6A).
# Serial by construction: never two GPU loads at once. Appends to placement.json.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
PLACE=results/v6/place.py
JSON=/mnt/d/local-llm-bench/ollama-bench/results/v6/placement.json

verdict_of() {  # verdict_of <tag> <ctx>
  python3 - "$1" "$2" <<'PY'
import json,sys
try:
    d=json.load(open('/mnt/d/local-llm-bench/ollama-bench/results/v6/placement.json'))
except Exception:
    print('none'); raise SystemExit
for r in reversed(d):
    if r['tag']==sys.argv[1] and r['num_ctx']==int(sys.argv[2]):
        print(r.get('verdict','none')); break
else:
    print('none')
PY
}

cell() {  # cell <tag> <ctx>
  local tag=$1 ctx=$2 to=900
  [ "$ctx" -ge 131072 ] && to=1800
  echo "=== $(date +%H:%M:%S) placing $tag @ $ctx" >&2
  "$PY" "$PLACE" "$tag" "$ctx" "$to" >/dev/null 2>&1
  local v; v=$(verdict_of "$tag" "$ctx")
  echo "=== $(date +%H:%M:%S) $tag @ $ctx -> $v" >&2
  echo "$v"
}

ladder() {  # ladder <quant> <name:ctx> ...  -- stops climbing on spill/load_failed
  local q=$1; shift
  for rung in "$@"; do
    local n=${rung%%:*} c=${rung##*:}
    local v; v=$(cell "q27-$q-$n" "$c")
    if [ "$v" = "spill" ] || [ "$v" = "load_failed" ] || [ "$v" = "none" ]; then
      echo "=== ladder $q stops at $n ($v)" >&2
      return 0
    fi
  done
}

# 0. Calibration cell (D6-5).
cell q27-Q2_K_L-64k 65536 >/dev/null
# 1-2. The campaign's question: does any 3-bit carry 64k?
cell q27-IQ3_XXS-64k 65536 >/dev/null
cell q27-IQ3_XS-64k 65536 >/dev/null
# 3. IQ2_M, the whole ladder -- the one that may reach 128k or more.
ladder IQ2_M 48k:49152 64k:65536 96k:98304 128k:131072 192k:196608 256k:262144
# 4. Q2_K.
ladder Q2_K 48k:49152 64k:65536 96k:98304 128k:131072
# 5. Q2_K_L from 96k up.
ladder Q2_K_L 96k:98304 128k:131072 192k:196608 256k:262144
# 6-7. Expected out, placed last so their failure costs nothing.
cell q27-Q3_K_S-48k 49152 >/dev/null
cell q27-IQ3_M-48k 49152 >/dev/null
echo "=== $(date +%H:%M:%S) PHASE A COMPLETE" >&2
touch /mnt/d/local-llm-bench/ollama-bench/results/v6/.phaseA-done
