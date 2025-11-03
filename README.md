# EOD Share Revaluation / ASX End-of-Day Downloader

This project downloads historical End-of-Day (EOD) price data for selected ASX tickers from Yahoo Finance using `yfinance`, applies rounding and formatting rules, and generates a consolidated CSV (`asx_eod_output/DailyData.csv`) that includes both market data and per-holding value calculations.

The script is designed for personal share portfolio tracking and can be run manually from the terminal. It does not require API keys.

---

## Features

- Downloads daily OHLCV data for multiple ASX tickers.
- Reads holdings from `asx_eod_output/Tickers_and_Shares.txt` (one `TICKER,SHARES` per line).
- Calculates Value = Shares × Close Price for each security, formatted to 2 decimal places.
- Price data rounded and zero‑padded to 3 decimal places.
- Produces a clean, consolidated CSV output with columns:
  - `Date, Ticker, Shares, Open, High, Low, Close, Volume, Value`
- Saves output to: `asx_eod_output/DailyData.csv`
- Prompts for start and end dates, with convenience defaults.

Note: If `Tickers_and_Shares.txt` is missing or empty, the script falls back to its built‑in holdings list and will indicate this when starting.

---

## Requirements

Install Python dependencies:

```bash
pip install pandas yfinance
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
  README.md                    # This file
  asx_eod_output/
    Tickers_and_Shares.txt     # Portfolio holdings (TICKER,SHARES)
    DailyData.csv              # Generated output file
```

---

## License

This project is provided for personal use. You may modify and reuse it freely.

---

## Contributions

Pull requests and improvements are welcome. If you add features, feel free to share suggestions or enhancements!

