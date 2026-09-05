#!/bin/bash
# Chain phase B behind phase A3. Polls the OUTCOME artifact, never a process name.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
V6=results/v6
until [ -f "$V6/.phaseA3-done" ]; do sleep 30; done
echo "=== $(date +%H:%M:%S) phase A complete, rendering placement" >&2
/mnt/c/Users/slb/scoop/apps/python/current/python.exe "$V6/render_placement.py" > /dev/null 2>&1
echo "=== $(date +%H:%M:%S) starting phase B sentinels" >&2
python3 "$V6/phaseB.py"
echo "=== $(date +%H:%M:%S) PHASE B COMPLETE rc=$?" >&2
