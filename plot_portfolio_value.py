"""Plot total daily portfolio value across all tickers."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asx_eod_output")
CHART_DIR = os.path.join(DATA_DIR, "Charts")
CSV_PATH = os.path.join(DATA_DIR, "DailyData.csv")

os.makedirs(CHART_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH, parse_dates=["Date"])

# Sum Value across all tickers for each date
daily_total = df.groupby("Date")["Value"].sum().sort_index()

plt.figure(figsize=(14, 6))
plt.plot(daily_total.index, daily_total.values, linewidth=1.4, color="#2ca02c")
plt.fill_between(daily_total.index, daily_total.values, alpha=0.15, color="#2ca02c")

plt.title("Total Daily Portfolio Value", fontsize=14, fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (AUD)")
plt.grid(True, alpha=0.3)

# Format y-axis with dollar signs and commas
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

# Auto-format date axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=45)

plt.tight_layout()

out_path = os.path.join(CHART_DIR, "Portfolio_Total_Value.png")
plt.savefig(out_path, dpi=150)
plt.close()

print(f"Portfolio value chart saved to {out_path}")
print(f"  Date range: {daily_total.index.min().date()} to {daily_total.index.max().date()}")
print(f"  Trading days: {len(daily_total)}")
print(f"  Latest value: ${daily_total.iloc[-1]:,.2f}")
