# Register Echo to run at user logon via Task Scheduler
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    $Python = Join-Path $Root ".venv\Scripts\python.exe"
}
$Main = Join-Path $Root "echo\main.py"
$Action = New-ScheduledTaskAction -Execute $Python -Argument "-m echo.main" -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "Echo" -Action $Action -Trigger $Trigger -Settings $Settings -Force
Write-Host "Scheduled task 'Echo' registered."
