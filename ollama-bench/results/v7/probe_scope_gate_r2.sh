#!/bin/bash
# probe_scope_gate_r2.sh [--breach]
#
# Grade every round-2 candidate's own reference **under the interpreter pibench grades with**,
# which is the check the campaign paid for (D7-31, calibration section 5): the suite was
# validated on one interpreter and scored on another for twenty candidates, five instruments,
# four reference arms and two review rounds, and the defect that fell through was invisible on
# one side of that fork and fired on every sandbox on the other.
#
#   bash results/v7/probe_scope_gate_r2.sh            # every reference must be `correct`
#   bash results/v7/probe_scope_gate_r2.sh --breach   # every scope gate must still fire
#
# CPU only: it copies a seed, overlays a reference and runs a grader. No model, no GPU.
#
# V7_PROBE_BASE has to be a WINDOWS path and has to be named in WSLENV, or it arrives as None
# in the Windows process and the probe silently grades `authoring/suite` instead — which is a
# different set of tasks and a green result that means nothing.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
STAGE=results/v7/authoring/r2/gate-suite
[ -d "$STAGE" ] || { echo "staging directory $STAGE is absent; run stage_gate_suite.py" >&2; exit 2; }

export V7_PROBE_BASE='D:\local-llm-bench\ollama-bench\results\v7\authoring\r2\gate-suite'
export WSLENV="V7_PROBE_BASE${WSLENV:+:$WSLENV}"

slots=$(ls -1 "$STAGE")
# shellcheck disable=SC2086
"$PY" results/v7/probe_scope_gate.py ${1:-} $slots
