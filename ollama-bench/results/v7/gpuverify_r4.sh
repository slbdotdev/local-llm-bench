#!/bin/bash
# gpuverify.sh — verify the GPU by a real load on every tag this calibration will run.
# Never a version string (org/ollama-cuda-repair-2026-09-04.md). One tag at a time,
# unloaded in between, so each row is that tag's own placement and not a leftover.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
OUT=results/v7/gpuverify-r4.log
: > "$OUT"
for tag in q27-IQ2_M-64k q27-IQ2_M-24k q27-UDQ3KXL-48k q27-Q2_K-64k; do
  echo "=== $(date +%H:%M:%S) $tag" >> "$OUT"
  "$PY" results/v5/gpu_verify.py "$tag" >> "$OUT" 2>&1
  "$PY" -c "import json,urllib.request;urllib.request.urlopen(urllib.request.Request('http://localhost:11434/api/generate',data=json.dumps({'model':'$tag','keep_alive':0}).encode(),headers={'Content-Type':'application/json'}),timeout=60).read()" >> "$OUT" 2>&1
  sleep 3
done
echo "=== $(date +%H:%M:%S) DONE" >> "$OUT"
touch results/v7/.r4-gpuverify-done
