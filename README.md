# EOD Share Revaluation / ASX End-of-Day Downloader

This project downloads historical End-of-Day (EOD) price data for selected ASX tickers from Yahoo Finance using `yfinance`, applies rounding/formatting rules, and generates a consolidated CSV (`asx_eod_output/DailyData.csv`) that includes both market data and per‑holding value calculations. It can also auto‑produce a “last two dates” portfolio report in TXT/CSV/Excel formats.

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
- Prompts for start and end dates, with convenience defaults.

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

---

## Usage

Run the script from the terminal:

```bash
python asx_eod_downloader.py
```

You will be prompted for:

```
Start date [default]
End date   [default]
```

Accepted date formats:

- `YYYY-MM-DD` (e.g., `2025-01-31`)
- `DD/MM/YYYY` (e.g., `31/01/2025`)
- `DD-MM-YYYY` (e.g., `31-01-2025`)

If no input is given, defaults are applied.

### Overwrite-Then-Append logic

When `asx_eod_output/DailyData.csv` already exists:

- The default Start date is set to the last date present in the CSV (so it can be refreshed).
- The script downloads data starting from that date up to your End date.
- It removes the existing rows for that last date from the CSV and writes back fresh data for that date, then appends any newer dates.
- If the download does not include that last date (for example, you choose an earlier range), it simply appends rows for dates strictly newer than the last date already in the CSV.
- If your End date is before the adjusted Start date, the script adjusts End = Start to keep the range valid.

Tip: To refresh the last day and append the current day using defaults, just press Enter twice at the prompts.

### Non-interactive mode (PROMPT flag)

- The script has a boolean flag near the top: `PROMPT: bool = False` by default.
- When `PROMPT = False`, the script skips prompts and uses the default dates automatically (equivalent to pressing Enter for both prompts).
- Defaults:
  - Start = last date present in `DailyData.csv` (to refresh it) if the file exists, otherwise 60 days ago.
  - End = today.

To run interactively, set `PROMPT = True` near the top of `asx_eod_downloader.py`.

---

## Last-Two-Dates Reports

After `DailyData.csv` is updated, a compact portfolio change report can be auto‑generated for the last two distinct dates found in the CSV. This is controlled by a flag near the top of `asx_eod_downloader.py`:

- `AUTO_GENERATE_LAST_TWO_REPORT: bool = True` (default)

Outputs are written to `asx_eod_output/` with names based on the most recent date, for example:

- `asx_eod_output/Report_YYYYMMDD.txt`
- `asx_eod_output/Report_YYYYMMDD.csv`
- `asx_eod_output/Report_YYYYMMDD.xlsx` (requires `openpyxl` or `xlsxwriter`)

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

- [asx_eod_output/Report_20251104.txt](asx_eod_output/Report_20251104.txt)
- [asx_eod_output/Report_20251104.csv](asx_eod_output/Report_20251104.csv)
- [asx_eod_output/Report_20251104.xlsx](asx_eod_output/Report_20251104.xlsx)
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
  asx_eod_downloader.py        # Main script
  generate_last_two_report.py  # Creates last-two-dates TXT/CSV/Excel report
  README.md                    # This file
  asx_eod_output/
    Tickers_and_Shares.txt     # Portfolio holdings (TICKER,SHARES)
    DailyData.csv              # Generated output file
    Report_YYYYMMDD.txt        # Last-two-dates report (latest date)
    Report_YYYYMMDD.csv        # CSV version of the report
    Report_YYYYMMDD.xlsx       # Excel version (optional)
```

---

## Quick Start

- Ensure Python 3.10+ is available.
- (Optional) Create and activate a virtual environment.
- `pip install pandas yfinance` (plus `openpyxl` or `xlsxwriter` for Excel).
- Edit `asx_eod_output/Tickers_and_Shares.txt` with your holdings.
- Run `python asx_eod_downloader.py`.

Notes:
- ASX tickers must include the `.AX` suffix (e.g., `BHP.AX`).
- If the holdings file is absent, a built‑in list is used.

---

## Troubleshooting

- Missing or delayed data: Yahoo Finance can lag or omit some EOD values temporarily. Weekends and ASX public holidays produce no rows by design. If a date looks missing, try again later or widen the date range.
- Ticker format: Ensure tickers include the `.AX` suffix and that each line in `Tickers_and_Shares.txt` is `TICKER,SHARES` or `TICKER SHARES`. Lines starting with `#` or `//` are ignored.
- Dates and defaults: Accepted formats are `YYYY-MM-DD`, `DD/MM/YYYY`, or `DD-MM-YYYY`. End date cannot precede start date. In non‑interactive mode (`PROMPT = False`), defaults are used automatically.
- Refresh logic: When `DailyData.csv` exists, the last date in the file is refreshed (overwritten) and newer dates appended. To force a clean refresh for a wider period, choose an earlier start date.
- Report not created: The last‑two‑dates report requires at least two distinct dates in `DailyData.csv`. Ensure `AUTO_GENERATE_LAST_TWO_REPORT = True` (default). TXT/CSV are always written; Excel output needs `openpyxl` or `xlsxwriter`.
- Network/SSL hiccups: Verify internet connectivity. If you see SSL issues on some systems, updating certificates can help: `pip install --upgrade certifi`. Retry if Yahoo temporarily throttles.
- File in use: If `DailyData.csv` is open in Excel (e.g., via OneDrive), Windows may lock the file. Close it before running the downloader.

## License

This project is provided for personal use. You may modify and reuse it freely.

---

## Contributions

Pull requests and improvements are welcome. If you add features, feel free to share suggestions or enhancements!
