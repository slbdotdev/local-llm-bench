#!/bin/bash
# bake.sh <tag-name> <FROM-source> <num_ctx>
# Bakes an Ollama context tag on the WINDOWS daemon from WSL. The Modelfile is written to a
# path the Windows daemon can read and handed over as a Windows path; WSL paths are invisible
# to it.
set -euo pipefail
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
name=$1; src=$2; ctx=$3
mf=/mnt/d/local-llm-bench/ollama-bench/results/v6/_mf
winmf='D:\local-llm-bench\ollama-bench\results\v6\_mf'
printf 'FROM %s\nPARAMETER num_ctx %s\n' "$src" "$ctx" > "$mf"
"$OLLAMA" create "$name" -f "$winmf" >/dev/null
echo "baked $name (FROM $src, num_ctx $ctx)"
