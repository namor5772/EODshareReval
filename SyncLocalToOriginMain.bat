@echo off
setlocal
set "SCRIPT=%~dp0SyncLocalToOriginMain.ps1"
if not exist "%SCRIPT%" (
  echo [Sync] PowerShell script not found: %SCRIPT%
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" %*
endlocal

