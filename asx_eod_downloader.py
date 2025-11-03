#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASX EOD downloader (Yahoo Finance, yfinance)

Version: Loads holdings from asx_eod_output/Tickers_and_Shares.txt,
          3-decimal rounding with zero-padding for prices,
          Value = Shares × Close, rounded to 2 dp and zero-padded.

Features:
1) Consolidated CSV (DailyData.csv) sorted by Date.
2) Columns: Date, Ticker, Shares, Open, High, Low, Close, Volume, Value.
3) Price data rounded to 3 dp (zero-padded).
4) Value rounded to 2 dp (zero-padded, e.g. 5145.60).
5) No command-line arguments; only prompts for date range.
6) Holdings read from asx_eod_output/Tickers_and_Shares.txt.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import re

# ---- Dependencies ----
try:
    import pandas as pd
    import yfinance as yf
except ImportError:
    print("Missing dependencies. Please run:\n  pip install yfinance pandas")
    sys.exit(1)

os.environ["YF_NO_CACHE"] = "1"

# ---- User settings ----
OUTPUT_DIR = "asx_eod_output"
OUTPUT_CSV = "DailyData.csv"
HOLDINGS_FILE = os.path.join(OUTPUT_DIR, "Tickers_and_Shares.txt")

def load_holdings(path: str) -> List[Tuple[str, int]]:
    """Load [Ticker, Shares] pairs from a text file.

    Accepted line formats (one per line):
      - TICKER,SHARES
      - TICKER SHARES
    Lines starting with '#' or '//' are comments.
    """
    holdings: List[Tuple[str, int]] = []
    file_path = os.path.join(os.path.dirname(__file__), path)
    if not os.path.exists(file_path):
        return holdings

    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            if "," in line:
                parts = [p.strip() for p in line.split(",") if p.strip()]
            else:
                parts = re.split(r"\s+", line)
            if len(parts) < 2:
                print(f"Warning: Skipping malformed line {lineno} in {path}: {raw.rstrip()}")
                continue
            ticker = parts[0].strip().strip('"\'')
            shares_s = parts[1].strip()
            try:
                shares = int(float(shares_s))
            except ValueError:
                print(f"Warning: Invalid shares at line {lineno} in {path}: {shares_s}")
                continue
            if not ticker:
                print(f"Warning: Empty ticker at line {lineno} in {path}")
                continue
            holdings.append((ticker, shares))
    return holdings

# 🔧 EDIT YOUR HOLDINGS HERE (2D array: [ [Ticker, Shares], ... ])
TICKERS_AND_SHARES: List[Tuple[str, int]] = [
    ["ALK.AX", 153181],
    ["AMP.AX", 70000], 
    ["ASM.AX", 57458],
    ["BHP.AX", 16327],
    ["CAN.AX", 44090],
    ["CBA.AX", 0],
    ["CNB.AX", 10000],
    ["E25.AX", 20000],
    ["ERA.AX", 700000],
    ["PTR.AX", 9412],  
    ["VML.AX", 6000],
    ["WBC.AX", 0],
    ["WDS.AX", 1288],
] # type: ignore
TICKERS = [sym for sym, _ in TICKERS_AND_SHARES]
SHARES_MAP = {sym: int(sh) for sym, sh in TICKERS_AND_SHARES}

# Optionally override with file-based holdings if present
HOLDINGS_FROM_FILE = False
_loaded_holdings = load_holdings(HOLDINGS_FILE)
if _loaded_holdings:
    TICKERS_AND_SHARES = _loaded_holdings
    TICKERS = [sym for sym, _ in TICKERS_AND_SHARES]
    SHARES_MAP = {sym: int(sh) for sym, sh in TICKERS_AND_SHARES}
    HOLDINGS_FROM_FILE = True

# ---------- Utilities ----------
def parse_date_any(s: str) -> Optional[datetime]:
    s = s.strip()
    if not s:
        return None
    fmts = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%y", "%d-%m-%y"]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            pass
    return None


def prompt_with_default(prompt: str, default: str) -> str:
    s = input(f"{prompt} [{default}]: ").strip()
    return s or default


def normalize_yf_panel(df: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    """Flatten yfinance’s multi-index into long-form table."""
    if not isinstance(df.columns, pd.MultiIndex):
        df = pd.concat({tickers[0]: df}, axis=1)

    records = []
    available_lvl0 = set(df.columns.get_level_values(0))
    for t in tickers:
        if t not in available_lvl0:
            continue
        sub = df[t].copy()
        for k in ["Open", "High", "Low", "Close", "Volume"]:
            if k not in sub.columns:
                sub[k] = pd.NA
        sub = sub[["Open", "High", "Low", "Close", "Volume"]]
        sub = sub.reset_index().rename(columns={"index": "Date"})
        sub.insert(0, "Ticker", t)
        records.append(sub)

    if not records:
        return pd.DataFrame(columns=["Ticker", "Date", "Open", "High", "Low", "Close", "Volume"])

    out = pd.concat(records, ignore_index=True)
    out["Date"] = pd.to_datetime(out["Date"]).dt.tz_localize(None)
    return out


def prompt_dates() -> (datetime, datetime): # type: ignore
    print("\n=== ASX EOD Downloader ===")
    print(
        f"Using holdings loaded from {HOLDINGS_FILE}:" if HOLDINGS_FROM_FILE
        else "Using default hard-coded holdings:"
    )
    for sym, sh in TICKERS_AND_SHARES:
        print(f"  - {sym}: {sh} shares")

    default_start = (datetime.today() - timedelta(days=60)).strftime("%Y-%m-%d")
    default_end   = datetime.today().strftime("%Y-%m-%d")

    start_s = prompt_with_default("Start date", default_start)
    end_s   = prompt_with_default("End date", default_end)

    start_dt = parse_date_any(start_s)
    end_dt   = parse_date_any(end_s)

    if not start_dt or not end_dt:
        print("Invalid date(s). Use formats like 2025-10-25 or 25/10/2025.")
        sys.exit(2)
    if end_dt < start_dt:
        print("End date cannot precede start date.")
        sys.exit(2)
    return start_dt, end_dt


# ---------- Main ----------

def main():
    if not TICKERS_AND_SHARES:
        print(f"No holdings defined. Create {HOLDINGS_FILE} with lines like 'BHP.AX,120'.")
        sys.exit(2)

    tickers = TICKERS
    start_dt, end_dt = prompt_dates()
    end_plus_one = end_dt + timedelta(days=1)

    print(f"\nDownloading EOD for {', '.join(tickers)} "
          f"from {start_dt.date()} to {end_dt.date()} ...")

    try:
        raw = yf.download(
            tickers,
            start=start_dt.strftime("%Y-%m-%d"),
            end=end_plus_one.strftime("%Y-%m-%d"),
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            threads=False,
            progress=False
        )
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(3)

    if raw is None or (isinstance(raw, pd.DataFrame) and raw.empty):
        print("No data returned. Check tickers or date range.")
        sys.exit(4)

    df = normalize_yf_panel(raw, tickers)
    if df.empty:
        print("No valid data found for selected tickers.")
        sys.exit(5)

    # ---- Attach Shares ----
    df["Shares"] = df["Ticker"].map(SHARES_MAP).astype("Int64")

    # ---- Compute Value = Shares × Close ----
    close_numeric = pd.to_numeric(df["Close"], errors="coerce")
    df["Value"] = (df["Shares"].astype("float64") * close_numeric).round(2)
    # Convert to string with 2dp and zero padding
    df["Value"] = df["Value"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

    # ---- Round and format price data (3 dp padded) ----
    price_cols = ["Open", "High", "Low", "Close"]
    for c in price_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").round(3)
        df[c] = df[c].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "")

    # ---- Ensure Volume is numeric ----
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").astype("Int64")

    # ---- Reorder columns ----
    base_order = ["Date", "Ticker", "Shares", "Open", "High", "Low", "Close", "Volume", "Value"]
    existing = [c for c in base_order if c in df.columns]
    extras = [c for c in df.columns if c not in existing]
    df = df[existing + extras].sort_values(["Date", "Ticker"]).reset_index(drop=True)

    # ---- Save ----
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, OUTPUT_CSV)
    df.to_csv(out_path, index=False)
    print(f"\nSaved consolidated CSV: {out_path}")

    # ---- Summary ----
    by_ticker = df.groupby("Ticker")["Date"].agg(["min", "max", "count"]).reset_index()
    print("\nSummary:")
    print(by_ticker.to_string(index=False))
    print("\nDone.")


if __name__ == "__main__":
    main()
