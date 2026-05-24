# Register Echo to run at user logon via Task Scheduler.
# Uses run_echo_logon.vbs (hidden window, venv pythonw, startup log).
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $PSScriptRoot).Path
$Launcher = Join-Path $Root "run_echo_logon.vbs"
if (-not (Test-Path -LiteralPath $Launcher)) {
    throw "Missing launcher: $Launcher"
}

$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "//nologo `"$Launcher`"" -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName "Echo" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force
Write-Host "Scheduled task 'Echo' registered."
Write-Host "  Launcher: $Launcher (hidden, no console)"
Write-Host "  Delay: 20s in launcher (desktop / OneDrive ready)"
Write-Host "  Log: %LOCALAPPDATA%\Echo\logs\startup-last.log"
