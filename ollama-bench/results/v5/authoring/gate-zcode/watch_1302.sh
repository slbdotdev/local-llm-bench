#!/bin/bash
# Sample the 1302 retry counts of the currently-running tiny-band z-runs twice,
# WAIT seconds apart, so the arm can tell whether throttling is still climbing at
# the current pool size. Prints counts only.
G="$(cd "$(dirname "$0")" && pwd)"
BAND="${1:-tiny}"
WAIT="${2:-180}"
R="$HOME/.agent-runs"

sample() {
  for t in g01 g02 g03 g04 t01 t02 t03 t04; do
    f="$G/$BAND/trial-0/$t.zrun.log"
    [ -f "$f" ] || continue
    id=$(grep -o 'z-run: run [^ ]*' "$f" 2>/dev/null | head -1 | awk '{print $3}')
    [ -n "$id" ] || continue
    [ -f "$R/$id/harness.log" ] || continue
    n=$(grep -c 'Rate limit reached for requests' "$R/$id/harness.log" 2>/dev/null)
    st=$(python3 -c "import json;print(json.load(open('$R/$id/state.json')).get('state','?'))" 2>/dev/null)
    echo "$t $id $st $n"
  done
}

echo "=== sample A $(date -u +%H:%M:%SZ) pool=$(cat "$G/conc.txt" 2>/dev/null)"
sample
sleep "$WAIT"
echo "=== sample B $(date -u +%H:%M:%SZ) (+${WAIT}s)"
sample
