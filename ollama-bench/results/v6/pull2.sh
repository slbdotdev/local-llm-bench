#!/bin/bash
# Chain the reserve rank 2 pull behind rank 1, so two downloads never share the link.
# Waits on the OUTCOME: rank 1's tag existing on the Windows daemon.
cd /mnt/d/local-llm-bench/ollama-bench || exit 1
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
have() { "$PY" -c "
import json,urllib.request,sys
d=json.load(urllib.request.urlopen('http://localhost:11434/api/tags',timeout=30))
sys.exit(0 if any(m['name'].split(':')[0]=='q27-UDQ3KXL-64k' for m in d['models']) else 1)
" 2>/dev/null; }
n=0
until have; do sleep 30; n=$((n+1)); [ $n -gt 60 ] && { echo "=== rank 1 never landed; pulling rank 2 anyway" >&2; break; }; done
echo "=== $(date +%H:%M:%S) rank 1 present; pulling reserve rank 2" >&2
bash results/v6/reserve_pull.sh mrIQ3M 'hf.co/mradermacher/Qwen3.8-27B-i1-GGUF:i1-IQ3_M' 49152 65536
