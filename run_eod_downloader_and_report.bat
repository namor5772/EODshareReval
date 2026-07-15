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
set "LATEST_STAMP="
for /f "delims=" %%F in ('dir /b /a:-d /o:-d "%REPORT_DIR%\Report_*.txt" 2^>nul') do (
    set "LATEST_REPORT=%REPORT_DIR%\%%F"
    set "LATEST_STAMP=%%~nF"
    goto :reports_found
)

:reports_found
if not defined LATEST_REPORT (
    echo No report files found in "%REPORT_DIR%".
    pause
    exit /b 1
)

rem Auto-commit and push the refreshed data + reports so each day lands in git.
rem No pause lines in this block: it also runs hidden via run_eod_hidden.vbs and
rem a pause would leave an invisible cmd.exe waiting forever. Any failure just
rem skips ahead so the report still opens; an unpushed commit rides along with
rem the next successful push.
set "REPORT_DATE=%LATEST_STAMP:Report_=%"
set "REPORT_DATE=%REPORT_DATE:~0,4%-%REPORT_DATE:~4,2%-%REPORT_DATE:~6,2%"

where git >nul 2>&1
if errorlevel 1 (
    echo git not found on PATH; skipping auto-commit.
    goto :open_report
)

pushd "%REPO_DIR%"
set "BRANCH="
for /f "delims=" %%B in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "BRANCH=%%B"
if /i not "%BRANCH%"=="main" (
    echo Not on main branch; skipping auto-commit.
    popd
    goto :open_report
)

git add asx_eod_output/
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Daily EOD data and reports for %REPORT_DATE%"
) else (
    echo No changes in asx_eod_output to commit.
)
git push origin main
popd

:open_report
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
