"""Plot closing prices for all tickers in DailyData.csv."""

import pandas as pd
import matplotlib.pyplot as plt
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asx_eod_output")
CHART_DIR = os.path.join(DATA_DIR, "Charts")
CSV_PATH = os.path.join(DATA_DIR, "DailyData.csv")

os.makedirs(CHART_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH, parse_dates=["Date"])
tickers = sorted(df["Ticker"].unique())

print(f"Generating charts for {len(tickers)} tickers...\n")

for ticker in tickers:
    data = df[df["Ticker"] == ticker].sort_values("Date")
    label = ticker.replace(".AX", "")

    plt.figure(figsize=(12, 5))
    plt.plot(data["Date"], data["Close"], linewidth=1.2, color="#1f77b4")
    plt.title(f"{ticker} \u2014 Daily Closing Price")
    plt.xlabel("Date")
    plt.ylabel("Close (AUD)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    out_path = os.path.join(CHART_DIR, f"{label}_close.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  {ticker:10s} -> {out_path}")

print(f"\nDone. {len(tickers)} charts saved to {CHART_DIR}")
