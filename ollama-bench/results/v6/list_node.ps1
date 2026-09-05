# Report node.exe processes and enough of their command line to tell campaigns apart.
# Read-only: this script never kills anything.
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | ForEach-Object {
  $cl = $_.CommandLine
  $model = if ($cl -match '--model\s+(\S+)') { $Matches[1] } else { '?' }
  Write-Output ("pid {0} ppid {1} model {2}" -f $_.ProcessId, $_.ParentProcessId, $model)
}
