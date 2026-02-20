<#
.SYNOPSIS
    Creates (or replaces) the "ASX EOD Downloader" Windows scheduled task.

.DESCRIPTION
    Registers a Task Scheduler job that silently runs the EOD downloader
    every weekday at 5:00 PM using the project's .venv Python.

    Settings:
      - Monday-Friday at 5:00 PM
      - Runs on battery
      - Wakes the PC from sleep
      - Catches up if the run was missed

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File CreateScheduledTask.ps1
#>

$ErrorActionPreference = 'Stop'

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = Join-Path $repoDir '.venv\Scripts\python.exe'
$script = Join-Path $repoDir 'asx_eod_downloader.py'
$taskName = 'ASX EOD Downloader'

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: .venv not found at $pythonExe" -ForegroundColor Red
    Write-Host "Create it first:  py -m venv .venv && .venv\Scripts\pip install pandas yfinance openpyxl"
    exit 1
}

$action   = New-ScheduledTaskAction -Execute $pythonExe -Argument $script -WorkingDirectory $repoDir
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 5:00PM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings `
    -Description 'Downloads ASX EOD data and generates portfolio reports after market close' -Force

Write-Host ""
Write-Host "Scheduled task '$taskName' created successfully." -ForegroundColor Green
Write-Host "  Schedule:       Mon-Fri at 5:00 PM"
Write-Host "  Python:         $pythonExe"
Write-Host "  Script:         $script"
Write-Host "  Wake to run:    Yes"
Write-Host "  Start if missed: Yes"
Write-Host ""
Write-Host "Manage via: taskschd.msc or Get-ScheduledTask -TaskName '$taskName'"
