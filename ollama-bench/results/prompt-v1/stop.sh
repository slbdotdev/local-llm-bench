#!/bin/bash
# Stop only THIS campaign's supervisors and pibench processes. Ownership is proved by the
# command line carrying 'prompt-v1' -- never by image name, which cannot tell two campaigns
# apart (the lesson the v6 campaign's kill_pi.ps1 learned the hard way tonight).
for pid in $(ps -eo pid,cmd | grep 'supervise\.sh' | grep -v grep | awk '{print $1}'); do
  kill "$pid" 2>/dev/null && echo "stopped supervisor $pid"
done
cat > /mnt/c/Users/slb/bench-prompt-variants/stop_mine.ps1 <<'PS'
$mine = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -match 'pibench\.py' -and $_.CommandLine -match 'prompt-v1' }
$ids = @($mine | ForEach-Object { $_.ProcessId })
foreach ($p in $mine) { Write-Output ("stopping pibench {0}" -f $p.ProcessId) }
# Kill only node children whose ancestry reaches one of those pibench pids.
$all = Get-CimInstance Win32_Process
foreach ($n in ($all | Where-Object { $_.Name -eq 'node.exe' })) {
  $cur = $n; $hops = 0
  while ($cur -and $hops -lt 6) {
    if ($ids -contains $cur.ParentProcessId) {
      Write-Output ("stopping pi child {0}" -f $n.ProcessId)
      Stop-Process -Id $n.ProcessId -Force -ErrorAction SilentlyContinue; break
    }
    $cur = $all | Where-Object { $_.ProcessId -eq $cur.ParentProcessId } | Select-Object -First 1
    $hops++
  }
}
foreach ($id in $ids) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
PS
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -File 'C:\Users\slb\bench-prompt-variants\stop_mine.ps1' < /dev/null 2>&1 | tr -d '\r'
