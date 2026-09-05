#!/bin/bash
# rm_quant.sh <QUANT> [hf-src]
# Remove every tag of a rejected quant, then report disk. Delete-as-you-go is not optional
# (plan section 2): the C: drive cannot hold the roster and the failures at once.
set -uo pipefail
OLLAMA=/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
q=$1
tags=$("$PY" -c "
import json,urllib.request,sys
d=json.load(urllib.request.urlopen('http://localhost:11434/api/tags',timeout=30))
q=sys.argv[1]
for m in d['models']:
    n=m['name']
    if n.startswith('q27-%s-'%q) or n.split(':')[0]=='q27-%s'%q or n.endswith(':%s'%q):
        print(n)
" "$q")
for t in $tags; do echo "  rm $t"; "$OLLAMA" rm "$t" >/dev/null 2>&1 || echo "    (rm failed: $t)"; done
"$PY" -c "import shutil;t,u,f=shutil.disk_usage('C:\\\\');print('C: free %.1f GB'%(f/1e9))"
