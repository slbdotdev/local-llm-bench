#!/bin/bash
# probe_scope_gate_suite.sh [--breach]
# Grade every ACCEPTED suite task's own reference under the Windows interpreter pibench grades
# with (D7-31, calibration section 5). CPU only: no model, no GPU.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
STAGE=results/v7/authoring/suite
export V7_PROBE_BASE='D:\local-llm-bench\ollama-bench\results\v7\authoring\suite'
export WSLENV="V7_PROBE_BASE${WSLENV:+:$WSLENV}"
slots=$(ls -1 "$STAGE")
# shellcheck disable=SC2086
"$PY" results/v7/probe_scope_gate.py ${1:-} $slots
