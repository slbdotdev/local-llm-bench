#!/usr/bin/env bash
cd ~/ollama-bench
while [ "$(pwsh -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'pibench.py --provider ollama --models' -and \$_.Name -eq 'python.exe' }).Count")" != "0" ]; do sleep 60; done
echo "ladder finished $(date -Is), re-measuring TPS with extended curve"
python pibench.py --provider ollama --models q27-Q3_K_M,q27-Q3_K_L,q27-Q3_K_S,q27-Q2_K_L --trials 0 --retps --tag local-medium
