#!/bin/bash
# strip.sh -- give each hf.co-derived quant a projector-free build (D6-11).
# Disk and network only: safe to run beside a GPU trial, never beside another import.
# One blob import per quant; every other rung is derived FROM the stripped tag, which is free.
# The hf.co tag is removed straight after, which frees the original blob and its projector.
set -uo pipefail
V6=/mnt/d/local-llm-bench/ollama-bench/results/v6
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
BLOBS='C:\Users\slb\.ollama\models\blobs'

free_gb() { "$PY" -c "import shutil;t,u,f=shutil.disk_usage('C:\\\\');print(int(f/1e9))"; }

strip_one() {  # strip_one <QUANT> <model-digest> <ctx...>
  local q=$1 dig=$2; shift 2
  local f; f=$(free_gb)
  echo "=== $(date +%H:%M:%S) strip $q (C: ${f} GB free)" >&2
  if [ "$f" -lt 15 ]; then echo "=== REFUSING: under the 15 GB floor (D6-10)" >&2; return 1; fi
  local first=1
  for c in "$@"; do
    case $c in 49152) n=48k;; 65536) n=64k;; 98304) n=96k;; 131072) n=128k;; 196608) n=192k;; 262144) n=256k;; esac
    if [ $first -eq 1 ]; then
      bash "$V6/bake.sh" "q27-$q-$n" "$BLOBS\\$dig" "$c" >&2 || return 1
      first=0; base="q27-$q-$n"
    else
      bash "$V6/bake.sh" "q27-$q-$n" "$base" "$c" >&2 || return 1
    fi
  done
  echo "=== $(date +%H:%M:%S) removing hf.co tag for $q" >&2
  "$OLLAMA" rm "hf.co/bartowski/Qwen3.8-27B-GGUF:$q" >/dev/null 2>&1
  echo "=== $(date +%H:%M:%S) $q stripped (C: $(free_gb) GB free)" >&2
}

"$OLLAMA" rm 'hf.co/bartowski/Qwen3.8-27B-GGUF:IQ3_XXS' >/dev/null 2>&1
echo "=== $(date +%H:%M:%S) IQ3_XXS hf.co tag removed (C: $(free_gb) GB free)" >&2
strip_one IQ2_M   sha256-b777952c0a430cd48016dec58a1d84cfd41466eefbc1f59a9f857fe5599fbbc8 49152 65536 98304 131072 196608 262144
strip_one IQ3_XS  sha256-74f04109572b7a931ae559fbaf3e6ba82a4b318f76346e3ca75e13f687512915 49152 65536
strip_one IQ3_M   sha256-dd6cccbaed553b08e958bbd759e5f9d8985d782ea016c5eaf3cd770e64615851 49152
echo "=== $(date +%H:%M:%S) STRIP COMPLETE (C: $(free_gb) GB free)" >&2
touch "$V6/.strip-done"
