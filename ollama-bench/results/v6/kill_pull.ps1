# Kill only `ollama.exe pull` clients, never the daemon or a model runner.
# The daemon and its runner share the image name, so match on the command line (org README).
$procs = Get-CimInstance Win32_Process -Filter "Name='ollama.exe'"
foreach ($p in $procs) {
  if ($p.CommandLine -match '\spull\s') {
    Write-Output ("killing pull client {0}: {1}" -f $p.ProcessId, $p.CommandLine)
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  } else {
    Write-Output ("keeping {0}" -f $p.ProcessId)
  }
}
