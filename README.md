# EOD Share Revaluation / ASX End‑of‑Day Downloader

This project downloads historical End‑of‑Day (EOD) price data for selected ASX tickers from Yahoo Finance using `yfinance`, applies rounding and formatting rules, and generates a consolidated CSV (`DailyData.csv`) that includes both market data and per‑holding value calculations.

The script is designed for personal share portfolio tracking and can be run manually from the terminal. It does **not** require API keys. It was however crafted by using ChatGPT-5 as was this Readme file.

---

## ✨ Features

- Downloads daily OHLCV data for multiple ASX tickers.
- Uses a hard‑coded list of `[Ticker, Shares]` pairs to represent your portfolio.
- Calculates **Value = Shares × Close Price** for each security, formatted to **2 decimal places**.
- Price data rounded and zero‑padded to **3 decimal places**.
- Produces a clean, consolidated CSV output:
  - `Date, Ticker, Shares, Open, High, Low, Close, Volume, Value`
- Saves output to: `asx_eod_output/DailyData.csv`
- Prompts for start and end dates, with convenience defaults.

---

## 📦 Requirements

Install Python dependencies:

```bash
pip install pandas yfinance
```

---

## ▶️ Usage

Run the script from the terminal:

```bash
python asx_eod_downloader.py
```

You will be prompted for:

```
Start date [default]
End date   [default]
```

Dates may be entered in formats such as:

- `2025-01-31`
- `31/01/2025`
- `31-01-2025`

If no input is given, defaults are applied.

---

## 🧾 Output Example

```
Date,Ticker,Shares,Open,High,Low,Close,Volume,Value
2025-01-15,BHP.AX,16327,45.210,45.800,45.000,45.600,12345678,744511.20
```

---

## 🛠 Customising Your Portfolio

Edit the array inside the script:

```python
TICKERS_AND_SHARES = [
    ["BHP.AX", 120],
    ["CBA.AX", 50],
    ["WES.AX", 80],
]
```

Changing values here automatically changes downstream calculations.

---

## 📁 Project Structure

```
EODshareReval/
│
├── asx_eod_downloader.py   # Main script
├── README.md               # This file
└── asx_eod_output/
    └── DailyData.csv       # Generated output file
```

---

## 📜 License

This project is provided under a permissive personal‑use basis.
You may modify and reuse it freely.

---

## 🤝 Contributions

Pull requests and improvements are welcome.
If you add features, feel free to share suggestions or enhancements!

---