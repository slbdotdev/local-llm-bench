#!/bin/bash
# The single chain for the rest of the campaign: B (corrected sentinel rule) -> C -> D -> E.
# Every link polls an outcome artifact. Logs are absolute so a cwd surprise cannot kill it.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
V6=results/v6
L=/mnt/d/local-llm-bench/ollama-bench/results/v6
echo "=== $(date +%H:%M:%S) phase B (D6-32 sentinel rule)" >&2
python3 "$V6/phaseB.py"; rc=$?
echo "=== $(date +%H:%M:%S) PHASE B COMPLETE rc=$rc" >&2
[ $rc -ne 0 ] && { echo "=== phase B FAILED; stopping rather than running C on a bad ordering" >&2; exit $rc; }
echo "=== $(date +%H:%M:%S) starting phase C" >&2
python3 "$V6/phaseC.py"
echo "=== $(date +%H:%M:%S) PHASE C COMPLETE rc=$?" >&2
python3 "$V6/summarize.py" > /dev/null 2>&1
echo "=== $(date +%H:%M:%S) starting phases D and E" >&2
python3 "$V6/phaseDE.py"
echo "=== $(date +%H:%M:%S) PHASES D AND E COMPLETE rc=$?" >&2
python3 "$V6/summarize.py" > /dev/null 2>&1
python3 "$V6/render_placement.py" > /dev/null 2>&1
