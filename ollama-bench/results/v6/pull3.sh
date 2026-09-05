#!/bin/bash
# Chain reserve rank 3 behind rank 2 so two downloads never share the link.
# Waits on rank 2's own outcome (its tag existing on the Windows daemon).
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
have() { "$PY" -c "
import json,urllib.request,sys
d=json.load(urllib.request.urlopen('http://localhost:11434/api/tags',timeout=30))
sys.exit(0 if any(m['name'].split(':')[0]=='q27-mrIQ3M-64k' for m in d['models']) else 1)
" 2>/dev/null; }
n=0
until have; do sleep 30; n=$((n+1)); [ $n -gt 60 ] && break; done
echo "=== $(date +%H:%M:%S) pulling reserve rank 3 (for v7 unless the night runs ahead)" >&2
bash results/v6/reserve_pull.sh UDIQ3S 'hf.co/unsloth/Qwen3.8-27B-GGUF:UD-IQ3_S' 49152 65536
