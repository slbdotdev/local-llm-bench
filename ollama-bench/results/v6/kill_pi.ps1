# Stop ONLY this campaign's own pi/node children.
#
# The earlier version of this script matched every node.exe whose command line contained
# "pi-coding-agent" and force-killed it. That is wrong on a machine running more than one
# bench: it ended in-flight trials belonging to the prompt campaign (results/prompt-v1/),
# which runs pi through pibench under its own tag and agent dir. Matching a package name
# cannot tell two campaigns apart.
#
# Scope instead by ANCESTRY. A v6 pibench is a python.exe whose command line carries both
# "pibench.py" and "--tag v6-"; its node children are the only ones this campaign owns.
# If no v6 pibench is running, this script kills nothing at all.

$mine = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -match 'pibench\.py' -and $_.CommandLine -match '--tag\s+v6-' }
$mineIds = @($mine | ForEach-Object { [int]$_.ProcessId })

if ($mineIds.Count -eq 0) {
  Write-Output "no v6 pibench running -- nothing owned by this campaign, killing nothing"
  exit 0
}
Write-Output ("v6 pibench pids: " + ($mineIds -join ', '))

# Parent map, built once.
$all = Get-CimInstance Win32_Process
$parentOf = @{}
foreach ($p in $all) { $parentOf[[int]$p.ProcessId] = [int]$p.ParentProcessId }

function Owned-ByMine([int]$startPid, $roots, $parentOf) {
  $cur = $startPid
  for ($i = 0; $i -lt 12; $i++) {
    if ($roots -contains $cur) { return $true }
    if (-not $parentOf.ContainsKey($cur)) { return $false }
    $next = $parentOf[$cur]
    if ($next -eq 0 -or $next -eq $cur) { return $false }
    $cur = $next
  }
  return $false
}

foreach ($p in ($all | Where-Object { $_.Name -eq 'node.exe' })) {
  if (Owned-ByMine ([int]$p.ProcessId) $mineIds $parentOf) {
    Write-Output ("killing v6-owned node {0}" -f $p.ProcessId)
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  }
}
foreach ($id in $mineIds) {
  Write-Output ("killing v6 pibench {0}" -f $id)
  Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
}
