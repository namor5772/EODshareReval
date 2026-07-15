<#
.SYNOPSIS
    Creates (or replaces) the "ASX EOD Downloader" Windows scheduled task.

.DESCRIPTION
    Registers a Task Scheduler job that does EXACTLY what the
    "Run EOD + Open Report" desktop shortcut does: it launches
    run_eod_hidden.vbs via wscript.exe, which silently runs
    run_eod_downloader_and_report.bat (download EOD data + generate
    reports) and then opens the latest TXT report in Notepad++.

    Because the job opens a GUI window (Notepad++), it runs under an
    INTERACTIVE principal and ONLY when the user is logged on -- a task
    set to "run whether logged on or not" would launch Notepad++ in the
    invisible Session 0 instead of on your desktop.

    Settings:
      - Monday-Friday at 5:00 PM
      - Runs on battery
      - Wakes the PC from sleep
      - Catches up if the run was missed

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File CreateScheduledTask.ps1
#>

$ErrorActionPreference = 'Stop'

$repoDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$vbs       = Join-Path $repoDir 'run_eod_hidden.vbs'
$bat       = Join-Path $repoDir 'run_eod_downloader_and_report.bat'
$wscript   = Join-Path $env:SystemRoot 'System32\wscript.exe'
$taskName  = 'ASX EOD Downloader'

if (-not (Test-Path $vbs)) {
    Write-Host "ERROR: VBS launcher not found at $vbs" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $bat)) {
    Write-Host "ERROR: Batch launcher not found at $bat" -ForegroundColor Red
    exit 1
}

# Action mirrors the desktop shortcut exactly: wscript.exe "<repo>\run_eod_hidden.vbs"
$action    = New-ScheduledTaskAction -Execute $wscript -Argument ('"' + $vbs + '"') -WorkingDirectory $repoDir
$trigger   = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 5:00PM
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun
# Interactive principal so Notepad++ opens on the user's desktop (runs only when logged on).
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
    -Description 'Runs the EOD downloader + report and auto-commits the results to GitHub (same as the "Run EOD + Open Report" shortcut) after market close' -Force

Write-Host ""
Write-Host "Scheduled task '$taskName' created successfully." -ForegroundColor Green
Write-Host "  Schedule:        Mon-Fri at 5:00 PM"
Write-Host "  Action:          $wscript ""$vbs"""
Write-Host "  Behaviour:       Same as the 'Run EOD + Open Report' shortcut (downloads, reports, opens Notepad++)"
Write-Host "  Runs:            Only when you are logged on (interactive, so Notepad++ is visible)"
Write-Host "  Wake to run:     Yes"
Write-Host "  Start if missed: Yes"
Write-Host ""
Write-Host "Manage via: taskschd.msc or Get-ScheduledTask -TaskName '$taskName'"
