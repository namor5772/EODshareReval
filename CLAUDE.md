# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ASX (Australian Securities Exchange) end-of-day share portfolio tracker. Downloads daily OHLCV price data from Yahoo Finance via `yfinance`, maintains a consolidated CSV, and generates portfolio change reports comparing the last two trading days.

No API keys required. Uses Yahoo Finance public data.

## Running

```bash
# Main workflow: download EOD data and auto-generate reports
python asx_eod_downloader.py

# Generate reports only (no download)
python generate_last_two_report.py

# Windows one-click (finds Python, runs downloader, opens report)
run_eod_downloader_and_report.bat
```

## Dependencies

Python 3.10+. Install with:
```bash
pip install pandas yfinance openpyxl
```

No build system, linter, or test framework is configured.

## Architecture

**Two-script design:**

1. **`asx_eod_downloader.py`** — Main entry point. Loads holdings, downloads multi-ticker data via `yfinance.download()`, normalizes the multi-index DataFrame into long-form rows, computes `Value = Shares * Close`, and applies overwrite-then-append logic on `DailyData.csv`. Automatically calls the report generator when `AUTO_GENERATE_LAST_TWO_REPORT = True`.

2. **`generate_last_two_report.py`** — Reads `DailyData.csv`, finds the last two distinct dates, computes per-ticker changes, and outputs fixed-width TXT, CSV, and XLSX reports. Can run standalone or be imported (called by `asx_eod_downloader.py`).

**Key configuration flags** (top of `asx_eod_downloader.py`):
- `PROMPT: bool = False` — non-interactive mode (uses defaults)
- `AUTO_GENERATE_LAST_TWO_REPORT: bool = True` — auto-generates reports after CSV update

## Data Flow

```
Tickers_and_Shares.txt → asx_eod_downloader.py → yfinance API → DailyData.csv → generate_last_two_report.py → Report_TXT/ + Report_CSV/ + Report_XLSX/
```

## Key Files

- `asx_eod_output/Tickers_and_Shares.txt` — Holdings config (`TICKER.AX,SHARES` per line, `#`/`//` for comments)
- `asx_eod_output/DailyData.csv` — Consolidated data: `Date,Ticker,Shares,Open,High,Low,Close,Volume,Value`
- `asx_eod_output/Report_TXT/Report_YYYYMMDD.txt` — Fixed-width portfolio reports
- `asx_eod_output/Report_CSV/Report_YYYYMMDD.csv` — CSV portfolio reports
- `asx_eod_output/Report_XLSX/Report_YYYYMMDD.xlsx` — Excel portfolio reports

## Formatting Conventions

- Prices: 3 decimal places, zero-padded (e.g., `36.750`)
- Values: 2 decimal places, zero-padded (e.g., `601266.75`)
- ASX tickers always include `.AX` suffix (e.g., `BHP.AX`)
- Report filenames use the latest date: `Report_YYYYMMDD`

## CSV Overwrite-Then-Append Logic

When `DailyData.csv` exists, the script always refreshes the last date present (to handle Yahoo Finance data lag), then appends any newer dates. The default start date is the last date in the CSV; the default end date is today.

## Scheduled Task

A Windows Task Scheduler job named **"ASX EOD Downloader"** runs the downloader automatically:
- **Schedule:** Monday–Friday at 5:00 PM (after ASX market close)
- **Action:** `.venv\Scripts\python.exe asx_eod_downloader.py` (runs silently, no Notepad++)
- **Start if missed:** Yes (catches up if the PC was off/asleep at run time)
- **Manage via:** `taskschd.msc` or `Get-ScheduledTask -TaskName "ASX EOD Downloader"`

## Utility Scripts

- `run_eod_downloader_and_report.bat` — Preferred Windows launcher (auto-finds Python from `.venv` or system, opens report in Notepad++)
- `CreateDesktopShortcut.ps1` — Creates a Windows Desktop shortcut for the batch launcher
- `SyncLocalToOriginMain.ps1` / `SyncLocalToOriginMain.bat` — Force-syncs local `main` to `origin/main`
