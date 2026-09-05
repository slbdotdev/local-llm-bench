#!/bin/bash
# reserve_pull.sh <NAME> <src> [ctx ...]
# Pull a reserve candidate and bake its context tags. Network and disk only -- safe to run
# while the GPU is busy with a trial (plan section 9: a pull and a trial may overlap).
# Brief: some hf.co pulls fail at the digest or manifest step with `context deadline exceeded`
# while the blob is already complete on disk. Retry once; if it fails again, register the blob
# by Modelfile against its path, which is what worked for Q2_K.
set -uo pipefail
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
V6=/mnt/d/local-llm-bench/ollama-bench/results/v6
name=$1; src=$2; shift 2
ctxs=("$@"); [ ${#ctxs[@]} -eq 0 ] && ctxs=(49152 65536)
echo "=== $(date +%H:%M:%S) pulling $src" >&2
if ! "$OLLAMA" pull "$src"; then
  echo "=== $(date +%H:%M:%S) pull failed once, retrying $src" >&2
  if ! "$OLLAMA" pull "$src"; then
    echo "=== $(date +%H:%M:%S) PULL FAILED TWICE for $src -- register the blob by Modelfile" >&2
    exit 3
  fi
fi
for c in "${ctxs[@]}"; do
  case $c in 49152) n=48k;; 65536) n=64k;; 98304) n=96k;; 131072) n=128k;; *) n="${c}";; esac
  bash "$V6/bake.sh" "q27-$name-$n" "$src" "$c" >&2
done
echo "=== $(date +%H:%M:%S) PULLED $name" >&2
