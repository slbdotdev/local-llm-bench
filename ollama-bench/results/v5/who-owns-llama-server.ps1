Get-CimInstance Win32_Process -Filter "Name='llama-server.exe'" |
  Select-Object ProcessId, ParentProcessId, ExecutablePath |
  Format-List
Get-CimInstance Win32_Process -Filter "Name='ollama.exe'" |
  Select-Object ProcessId, ExecutablePath |
  Format-List
