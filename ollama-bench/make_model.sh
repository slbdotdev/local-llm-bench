#!/usr/bin/env bash
# make_model.sh <QUANT> [num_ctx]  -> creates ollama model q27-<QUANT> from bartowski/Qwen3.8-27B-GGUF:<QUANT>
# with a fixed context length so pi's OpenAI-compatible requests get it.
set -euo pipefail
q=$1; ctx=${2:-32768}
src="hf.co/bartowski/Qwen3.8-27B-GGUF:$q"
ollama list | grep -q "Qwen3.8-27B-GGUF:$q" || ollama pull "$src"
tmp=$(mktemp)
printf 'FROM %s\nPARAMETER num_ctx %s\n' "$src" "$ctx" > "$tmp"
ollama create "q27-$q" -f "$tmp"
rm -f "$tmp"
ollama list | grep "q27-$q"
