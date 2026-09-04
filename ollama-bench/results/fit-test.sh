#!/usr/bin/env bash
# Hypothesis test: are Q3_K_M / Q3_K_L slower because they partially offload at 32k ctx?
# Re-measure them at 8k ctx (fits fully in VRAM) and compare gen tok/s against the 32k figures.
cd ~/ollama-bench
while [ "$(pwsh -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'pibench.py --provider ollama' -and \$_.Name -eq 'python.exe' }).Count")" != "0" ]; do sleep 60; done
echo "retps finished $(date -Is), running 8k-context fit test"
python pibench.py --provider ollama --models q27-Q3_K_M,q27-Q3_K_L,q27-Q3_K_S --trials 0 --retps --num-ctx 8192 --tag local-ctx8k
echo "# fit test done"
