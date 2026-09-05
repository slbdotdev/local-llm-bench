#!/bin/bash
# Chain phase C behind phase B, then D and E behind C. Polls the OUTCOME artifacts.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
V6=results/v6
until [ -f "$V6/.phaseB-done" ]; do sleep 30; done
echo "=== $(date +%H:%M:%S) starting phase C" >&2
python3 "$V6/phaseC.py"
echo "=== $(date +%H:%M:%S) PHASE C COMPLETE rc=$?" >&2
python3 "$V6/summarize.py" > /dev/null 2>&1
echo "=== $(date +%H:%M:%S) starting phases D and E" >&2
python3 "$V6/phaseDE.py"
echo "=== $(date +%H:%M:%S) PHASES D AND E COMPLETE rc=$?" >&2
python3 "$V6/summarize.py" > /dev/null 2>&1
