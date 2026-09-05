#!/bin/bash
# chain_regrade.sh — re-run the three main-band rows invalidated by D7-31's grader defect.
#
# Order matters and each step is a precondition of the next:
#   1. re-assemble suite/ from the repaired cand-*/ candidates (assemble_suite.py rmtree's and
#      re-copies the suite, so it must never run while a cell is reading it);
#   2. quarantine the three invalid rows out of the scored artifact, which is exactly what makes
#      pibench re-run them — it resumes per (task, trial);
#   3. re-run those three tasks into the same tag, so the artifact ends up holding one valid
#      trial per task and the summariser needs no special case.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1

echo "== $(date +%H:%M:%S) re-assembling the suite from the repaired candidates" >&2
PYTHONDONTWRITEBYTECODE=1 python3 results/v7/authoring/assemble_suite.py >&2 || exit 1

echo "== $(date +%H:%M:%S) quarantining the invalidated rows" >&2
python3 results/v7/quarantine_scopegate.py >&2 || exit 1

bash results/v7/runcell.sh IQ2_M 64k 65536 main 1 v7cal-IQ2_M-main \
  m02-main-luna,m05-main-luna,m08-main-luna

echo "== $(date +%H:%M:%S) regrade complete" >&2
touch results/v7/.cal-regrade-done
