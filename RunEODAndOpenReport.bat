@echo off
setlocal enabledelayedexpansion

rem Resolve repo directory to where this script resides
set "REPO_DIR=%~dp0"
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"

echo [EOD] Working directory: "%REPO_DIR%"
pushd "%REPO_DIR%" >nul 2>&1

rem Prefer py launcher, fall back to python
set "PY=py"
where py >nul 2>&1
if errorlevel 1 (
  set "PY=python"
)

echo [EOD] Running downloader...
"%PY%" "asx_eod_downloader.py"
set "PY_EXITCODE=%ERRORLEVEL%"
if not "%PY_EXITCODE%"=="0" (
  echo [EOD] Downloader exited with code %PY_EXITCODE%.
  echo [EOD] Aborting opening report.
  popd >nul 2>&1
  exit /b %PY_EXITCODE%
)

rem Find latest report file
set "REPORT_DIR=%REPO_DIR%\asx_eod_output\Report_TXT"
if not exist "%REPORT_DIR" (
  echo [EOD] Report folder not found: "%REPORT_DIR%"
  popd >nul 2>&1
  exit /b 1
)

set "REPORT_FILE="
for /f "delims=" %%F in ('dir /b /a:-d /o:-d "%REPORT_DIR%\Report_*.txt" 2^>nul') do (
  set "REPORT_FILE=%%F"
  goto :found
)

:found
if not defined REPORT_FILE (
  echo [EOD] No report file found in "%REPORT_DIR%".
  popd >nul 2>&1
  exit /b 1
)

set "REPORT_PATH=%REPORT_DIR%\%REPORT_FILE%"
echo [EOD] Opening report: "%REPORT_PATH%"

rem Locate Notepad++
set "NPP_EXE=notepad++"
where notepad++ >nul 2>&1
if errorlevel 1 (
  if exist "C:\Program Files\Notepad++\notepad++.exe" (
    set "NPP_EXE=C:\Program Files\Notepad++\notepad++.exe"
  ) else if exist "C:\Program Files (x86)\Notepad++\notepad++.exe" (
    set "NPP_EXE=C:\Program Files (x86)\Notepad++\notepad++.exe"
  ) else (
    echo [EOD] Notepad++ not found. Falling back to Notepad.
    set "NPP_EXE=notepad.exe"
  )
)

start "" "%NPP_EXE%" "%REPORT_PATH%"

popd >nul 2>&1
endlocal

