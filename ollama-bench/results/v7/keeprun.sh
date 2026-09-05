#!/bin/bash
# keeprun.sh <quant> <ctxname> <ctx> <band> <task> [tag]
#
# One evidence trial: the same cell shape as a scored one, with V7_KEEP=1 so the sandbox
# is preserved under D:\v7keep before pibench deletes it. This is how a fairness re-read
# gets a transcript — pibench keeps only the last 400 characters of the model's final
# message, and the tree it left behind is the rest of the record.
#
# It writes to its OWN tag (default v7keep-<task>) so a scored artifact is never touched
# and no scored (task, trial) pair is ever resumed over.
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
quant=$1; ctxname=$2; ctx=$3; band=$4; task=$5; tag=${6:-v7keep-$band-$task}
mkdir -p /mnt/d/v7keep
V7_KEEP=1 bash results/v7/runcell.sh "$quant" "$ctxname" "$ctx" "$band" 1 "$tag" "$task"
