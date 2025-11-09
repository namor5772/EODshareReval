@echo off
setlocal

goto :main_body

:try_python
"%~1" %~2 -c "import sys" >nul 2>&1
if errorlevel 1 (
    goto :eof
)
set "PY_CMD=%~1"
set "PY_ARGS=%~2"
goto :eof

:main_body
for %%I in ("%~dp0.") do set "REPO_DIR=%%~fI"
rem Use the script folder as repo root so the path matches whichever machine runs it.
set "PREFERRED_PY=%REPO_DIR%\.venv\Scripts\python.exe"
set "PY_CMD="
set "PY_ARGS="

if exist "%PREFERRED_PY%" (
    call :try_python "%PREFERRED_PY%" ""
)
if not defined PY_CMD call :try_python python ""
if not defined PY_CMD call :try_python py -3
if not defined PY_CMD call :try_python py ""

if not defined PY_CMD (
    echo Could not locate a working Python interpreter. Install Python or update this script.
    pause
    exit /b 1
)

if defined PY_ARGS (
    echo Running ASX EOD downloader with %PY_CMD% %PY_ARGS%...
) else (
    echo Running ASX EOD downloader with %PY_CMD%...
)

pushd "%REPO_DIR%"
if defined PY_ARGS (
    "%PY_CMD%" %PY_ARGS% "%REPO_DIR%\asx_eod_downloader.py"
) else (
    "%PY_CMD%" "%REPO_DIR%\asx_eod_downloader.py"
)
set "EXITCODE=%ERRORLEVEL%"
popd

if not "%EXITCODE%"=="0" (
    echo Downloader failed with exit code %EXITCODE%.
    pause
    exit /b %EXITCODE%
)

set "REPORT_DIR=%REPO_DIR%\asx_eod_output\Report_TXT"
set "LATEST_REPORT="
for /f "delims=" %%F in ('dir /b /a:-d /o:-d "%REPORT_DIR%\Report_*.txt" 2^>nul') do (
    set "LATEST_REPORT=%REPORT_DIR%\%%F"
    goto :reports_found
)

:reports_found
if not defined LATEST_REPORT (
    echo No report files found in "%REPORT_DIR%".
    pause
    exit /b 1
)

set "NOTEPADPP=C:\Program Files\Notepad++\notepad++.exe"
if not exist "%NOTEPADPP%" (
    set "NOTEPADPP=C:\Program Files (x86)\Notepad++\notepad++.exe"
)

if not exist "%NOTEPADPP%" (
    echo Notepad++ not found. Install it or update the script with the correct path.
    echo Latest report: %LATEST_REPORT%
    pause
    exit /b 1
)

echo Opening latest report: %LATEST_REPORT%
start "" "%NOTEPADPP%" "%LATEST_REPORT%"
exit /b 0
