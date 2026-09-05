#!/bin/bash
# evidence_p1.sh — targeted keep-runs for the p1 rows that need a transcript read.
#
# Each row here is a trial whose verdict cannot be adjudicated from the artifact alone:
# a whole-tree scope gate that prints `unsafe` with an empty note list says a file it did
# not expect exists, and does not say which. The sandbox is the only evidence, so these
# re-run the same cell shape with V7_KEEP=1 and leave the tree under D:\v7keep.
#
# Serial, and only after the scored phase's marker exists: two cells at once make every
# wall figure a contention figure.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
for task in "$@"; do
  case $task in
    *-main-*)  bash results/v7/keeprun.sh IQ2_M 64k 65536 main  "$task" ;;
    *-cheap-*) bash results/v7/keeprun.sh IQ2_M 24k 24576 cheap "$task" ;;
  esac
done
echo "== $(date +%H:%M:%S) evidence runs complete" >&2
touch results/v7/.evidence-p1-done
