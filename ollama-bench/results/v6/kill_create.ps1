# Kill only `ollama.exe create` processes, never the daemon or a model runner.
# The daemon and its runner share the image name, so match on the command line (org README).
$procs = Get-CimInstance Win32_Process -Filter "Name='ollama.exe'"
foreach ($p in $procs) {
  if ($p.CommandLine -match '\screate\s') {
    Write-Output ("killing {0}: {1}" -f $p.ProcessId, $p.CommandLine)
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  } else {
    Write-Output ("keeping {0}: {1}" -f $p.ProcessId, $p.CommandLine)
  }
}
