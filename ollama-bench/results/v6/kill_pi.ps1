# Stop any orphaned pi/node bench child left by a killed pibench, never the Ollama daemon.
$procs = Get-CimInstance Win32_Process -Filter "Name='node.exe'"
foreach ($p in $procs) {
  if ($p.CommandLine -match 'pi-coding-agent') {
    Write-Output ("killing orphaned pi {0}" -f $p.ProcessId)
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  }
}
