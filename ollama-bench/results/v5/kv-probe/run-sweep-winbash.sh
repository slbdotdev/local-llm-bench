#!/usr/bin/env bash
# Launch run-sweep.sh under Git Bash on Windows, which is the only shell that can give
# llama-server.exe and the Windows Python a native cwd and a native HOME. Run this from WSL:
#   setsid -f bash results/v5/kv-probe/run-sweep-winbash.sh > log 2>&1 < /dev/null
set -uo pipefail
GITBASH=/mnt/c/Users/slb/scoop/apps/git/current/bin/bash.exe
exec "$GITBASH" -lc "cd /d/local-llm-bench/ollama-bench/results/v5/kv-probe && PY=/c/Users/slb/scoop/apps/python/current/python.exe OLLAMA=/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe bash ./run-sweep.sh"
