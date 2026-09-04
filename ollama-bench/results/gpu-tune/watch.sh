#!/usr/bin/env bash
# overnight watchdog: VRAM, ollama RSS, free host RAM, loaded model count, every 10 s. Alert marker on leak signs.
cd /c/Users/slb/ollama-bench
LOG=results/gpu-watch.log; ALERT=results/gpu-watch.ALERT
echo "# start $(date -Is) pid $$" >> "$LOG"
high_since=""
while true; do
  ts=$(date +%H:%M:%S)
  vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  rss=$(pwsh -NoProfile -Command "[int]((Get-Process ollama* -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum/1MB)" 2>/dev/null)
  free=$(pwsh -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" 2>/dev/null)
  models=$(curl -s -m 5 localhost:11434/api/ps | python -c "import sys,json; print(len(json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo "?")
  echo "$ts vram_mib=$vram ollama_rss_mib=$rss free_ram_mib=$free models=$models" >> "$LOG"
  if [ -n "$free" ] && [ "$free" -lt 8192 ] 2>/dev/null; then echo "$ts free RAM ${free} MiB < 8 GB" >> "$ALERT"; fi
  if [ "$models" = "0" ] && [ -n "$vram" ] && [ "$vram" -gt 6000 ] 2>/dev/null; then
    [ -z "$high_since" ] && high_since=$SECONDS
    if [ $((SECONDS - high_since)) -gt 60 ]; then echo "$ts VRAM ${vram} MiB with 0 models loaded for >60 s" >> "$ALERT"; high_since=$SECONDS; fi
  else high_since=""; fi
  sleep 10
done
