# EOD Share Revaluation / ASX End-of-Day Downloader

This project downloads historical End-of-Day (EOD) price data for selected ASX tickers from Yahoo Finance using `yfinance`, applies rounding/formatting rules, and generates a consolidated CSV (`asx_eod_output/DailyData.csv`) that includes both market data and per-holding value calculations. It can also auto-produce a "last two dates" portfolio report in TXT/CSV/Excel formats.

The script is designed for personal share portfolio tracking and can be run manually from the terminal. It does not require API keys.

Most of this app was designed with help from OpenAI.

---

## Features

- Downloads daily OHLCV data for multiple ASX tickers.
- Reads holdings from `asx_eod_output/Tickers_and_Shares.txt` (one `TICKER,SHARES` per line).
- Calculates Value = Shares * Close Price for each security, formatted to 2 decimal places.
- Price data rounded and zero-padded to 3 decimal places.
- Produces a clean, consolidated CSV output with columns:
  - `Date, Ticker, Shares, Open, High, Low, Close, Volume, Value`
- Saves output to: `asx_eod_output/DailyData.csv`
- Prompts for start and end dates (when interactive mode is enabled), with convenience defaults.
- Console log shows both the requested download window and the actual set of trading days returned (with a count), so you immediately know when Yahoo delivers more than one day or skips holidays.

Note: If `Tickers_and_Shares.txt` is missing or empty, the script falls back to its built-in holdings list and will indicate this when starting.

---

## Requirements

Install Python dependencies:

```bash
pip install pandas yfinance
```

Optional (for Excel report output):

```bash
pip install openpyxl  # or: pip install xlsxwriter
```

Optional tools:

- Notepad++ (optional) to open TXT reports from the batch scripts. `RunEODAndOpenReport.bat` falls back to Windows Notepad if Notepad++ is not found; `run_eod_downloader_and_report.bat` requires Notepad++ and will display the report path if it is not installed.

---

## Usage

By default the script runs **non-interactively** (`PROMPT = False` near the top of `asx_eod_downloader.py`). It uses default dates automatically — refreshing the last day in `DailyData.csv` through today — with no prompts:

```bash
python asx_eod_downloader.py
```

### Non-interactive mode (default)

- Defaults:
  - Start = last date present in `DailyData.csv` (to refresh it) if the file exists, otherwise 60 days ago.
  - End = today.
- To enable interactive date prompts, set `PROMPT = True` near the top of `asx_eod_downloader.py`.

### Interactive mode (PROMPT = True)

When `PROMPT = True`, you will be prompted for:

```
Start date [default]
End date   [default]
```

Accepted date formats:

- `YYYY-MM-DD` (e.g., `2025-01-31`)
- `YYYY/MM/DD` (e.g., `2025/01/31`)
- `DD/MM/YYYY` (e.g., `31/01/2025`)
- `DD-MM-YYYY` (e.g., `31-01-2025`)
- `DD/MM/YY` (e.g., `31/01/25`)
- `DD-MM-YY` (e.g., `31-01-25`)

If no input is given, defaults are applied.

### Console output cues

- `Requesting EOD ... from <start> to <end> (inclusive)` reflects the exact range sent to Yahoo Finance after any automatic adjustments (e.g., forcing inclusion of the last CSV date).
- `Downloaded EOD covering <n> trading day(s)` summarizes what Yahoo actually returned by showing the min/max dates present plus the trading-day count. This makes it obvious when the service provides extra days or skips holidays/weekends.

### Overwrite-Then-Append logic

When `asx_eod_output/DailyData.csv` already exists:

- The default Start date is set to the last date present in the CSV (so it can be refreshed).
- The script downloads data starting from that date up to your End date.
- It removes the existing rows for that last date from the CSV and writes back fresh data for that date, then appends any newer dates.
- If the download does not include that last date (for example, you choose an earlier range), it simply appends rows for dates strictly newer than the last date already in the CSV.
- If your End date is before the adjusted Start date, the script adjusts End = Start to keep the range valid.

Tip: In interactive mode, to refresh the last day and append the current day using defaults, just press Enter twice at the prompts.

---

## Last-Two-Dates Reports

After `DailyData.csv` is updated, a compact portfolio change report can be auto-generated for the last two distinct dates found in the CSV. This is controlled by a flag near the top of `asx_eod_downloader.py`:

- `AUTO_GENERATE_LAST_TWO_REPORT: bool = True` (default)

Outputs are written into dedicated subfolders under `asx_eod_output/`, with names based on the most recent date, for example:

- `asx_eod_output/Report_TXT/Report_YYYYMMDD.txt`
- `asx_eod_output/Report_CSV/Report_YYYYMMDD.csv`
- `asx_eod_output/Report_XLSX/Report_YYYYMMDD.xlsx` (requires `openpyxl` or `xlsxwriter`)

Note: The `YYYYMMDD` part in the filename equals the latest date present in `DailyData.csv` used for the report (i.e., the second of the last two distinct dates).

Report columns:

- `Ticker` (base code without `.AX`)
- `Close` (latest, 3 dp)
- `+/-` (change vs prior close, 3 dp)
- `%` (percentage change vs prior close, 2 dp)
- `Units` (shares, with thousands separator)
- `Value` (`Units * Close`, 2 dp)
- `Day Gain` (`Units * (Close change)`, 2 dp)

To regenerate the report manually (without running a download):

```bash
python generate_last_two_report.py
```

If Excel dependencies are missing, the TXT and CSV files are still produced.

---

### Example Files (from this repo)

- [asx_eod_output/Report_TXT/Report_20251104.txt](asx_eod_output/Report_TXT/Report_20251104.txt)
- [asx_eod_output/Report_CSV/Report_20251104.csv](asx_eod_output/Report_CSV/Report_20251104.csv)
- [asx_eod_output/Report_XLSX/Report_20251104.xlsx](asx_eod_output/Report_XLSX/Report_20251104.xlsx)
- [asx_eod_output/DailyData.csv](asx_eod_output/DailyData.csv)

---

## Holdings File

- Location: `asx_eod_output/Tickers_and_Shares.txt`
- Format per line: `TICKER,SHARES` or `TICKER SHARES`
- Examples:
  - `BHP.AX,120`
  - `CBA.AX 50`
- Blank lines and lines starting with `#` or `//` are ignored.

Changes to this file take effect the next time you run the script.

---

## Output Example

```
Date,Ticker,Shares,Open,High,Low,Close,Volume,Value
2025-01-15,BHP.AX,16327,45.210,45.800,45.000,45.600,12345678,744511.20
```

---

## Project Structure

```
EODshareReval/
  asx_eod_downloader.py              # Main script
  generate_last_two_report.py        # Creates last-two-dates TXT/CSV/Excel report
  run_eod_downloader_and_report.bat  # Windows: preferred launcher (auto-finds Python)
  RunEODAndOpenReport.bat            # Windows: older launcher (Notepad fallback)
  CreateDesktopShortcut.ps1          # Windows: create Desktop shortcut for RunEODAndOpenReport.bat
  SyncLocalToOriginMain.ps1          # Windows: force local main to origin/main (with options)
  SyncLocalToOriginMain.bat          # Windows: one-click wrapper for the sync script
  CLAUDE.md                          # Guidance for Claude Code AI assistant
  README.md                          # This file
  asx_eod_output/
    Tickers_and_Shares.txt           # Portfolio holdings (TICKER,SHARES)
    DailyData.csv                    # Generated output file
    Report_TXT/                      # TXT reports
      Report_YYYYMMDD.txt
    Report_CSV/                      # CSV reports
      Report_YYYYMMDD.csv
    Report_XLSX/                     # Excel reports
      Report_YYYYMMDD.xlsx
```

---

## Quick Start

1. Ensure Python 3.10+ is available.
2. (Optional) Create and activate a virtual environment.
3. `pip install pandas yfinance` (plus `openpyxl` or `xlsxwriter` for Excel).
4. Edit `asx_eod_output/Tickers_and_Shares.txt` with your holdings.
5. Run `python asx_eod_downloader.py`.

Notes:
- ASX tickers must include the `.AX` suffix (e.g., `BHP.AX`).
- If the holdings file is absent, a built-in list is used.

### Windows batch helpers

There are two batch files for one-click operation on Windows:

| Batch file | Python detection | Notepad++ fallback |
|---|---|---|
| `run_eod_downloader_and_report.bat` (preferred) | Tries `.venv\Scripts\python.exe`, then `python`, `py -3`, `py` | Requires Notepad++ (shows report path if missing) |
| `RunEODAndOpenReport.bat` (older) | Tries `py`, then `python` | Falls back to Windows Notepad |

Both run the downloader and then open the latest TXT report. Double-click either from Explorer or run from PowerShell/CMD.

**Desktop shortcut:** Run `CreateDesktopShortcut.ps1` to create a Desktop shortcut for `RunEODAndOpenReport.bat`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File CreateDesktopShortcut.ps1
```

---

## Troubleshooting

- **Missing or delayed data:** Yahoo Finance can lag or omit some EOD values temporarily. Weekends and ASX public holidays produce no rows by design. If a date looks missing, try again later or widen the date range.
- **Ticker format:** Ensure tickers include the `.AX` suffix and that each line in `Tickers_and_Shares.txt` is `TICKER,SHARES` or `TICKER SHARES`. Lines starting with `#` or `//` are ignored.
- **Dates and defaults:** Accepted formats are `YYYY-MM-DD`, `YYYY/MM/DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, `DD/MM/YY`, or `DD-MM-YY`. End date cannot precede start date. In non-interactive mode (`PROMPT = False`), defaults are used automatically.
- **Refresh logic:** When `DailyData.csv` exists, the last date in the file is refreshed (overwritten) and newer dates appended. To force a clean refresh for a wider period, choose an earlier start date.
- **Report not created:** The last-two-dates report requires at least two distinct dates in `DailyData.csv`. Ensure `AUTO_GENERATE_LAST_TWO_REPORT = True` (default). TXT/CSV are always written; Excel output needs `openpyxl` or `xlsxwriter`.
- **Network/SSL hiccups:** Verify internet connectivity. If you see SSL issues on some systems, updating certificates can help: `pip install --upgrade certifi`. Retry if Yahoo temporarily throttles.
- **File in use:** If `DailyData.csv` is open in Excel (e.g., via OneDrive), Windows may lock the file. Close it before running the downloader.

---

## Git: Force Local to Remote (Windows)

Use the included script to make local `main` exactly match `origin/main` in one click. It safely stashes any uncommitted work first.

- Double-click: `SyncLocalToOriginMain.bat`
- Or run in terminal:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File SyncLocalToOriginMain.ps1
```

Behavior:
- Fetches `origin` and prunes stale refs.
- If there are uncommitted changes, stashes them as `pre-reset-YYYYMMDDHHmmss`.
- Forces local `main` to `origin/main` via `git checkout -B main origin/main` and sets upstream tracking.

Options:
- `-Remote <name>` and `-Branch <name>` to target other remotes/branches.
- `-NoStash` to skip stashing uncommitted changes.
- `-Clean` to remove untracked files (`git clean -fd`). Add `-CleanIgnored` to also remove ignored files (`-x`).

Examples:

```powershell
# Default: sync local main to origin/main, stash if needed
powershell -File SyncLocalToOriginMain.ps1

# Also remove untracked files after syncing
powershell -File SyncLocalToOriginMain.ps1 -Clean

# Target a different branch
powershell -File SyncLocalToOriginMain.ps1 -Branch develop
```

## License

This project is provided for personal use. You may modify and reuse it freely.

---

## Contributions

Pull requests and improvements are welcome. If you add features, feel free to share suggestions or enhancements!
