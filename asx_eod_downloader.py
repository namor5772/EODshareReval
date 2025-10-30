#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASX EOD downloader (Yahoo Finance, yfinance)

Version: Hard-coded tickers, 3-decimal rounding with zero-padding.

Features:
1) Consolidated output CSV (DailyData.csv) sorted by Date.
2) Columns: Date, Ticker, Open, High, Low, Close, Adj Close, Volume.
3) Price data rounded to 3 dp and padded with trailing zeros.
4) No command-line arguments.30/10/2025
5) Hard-coded list of ASX tickers below.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

# ---- Dependencies ----
# pip install yfinance pandas
try:
    import pandas as pd
    import yfinance as yf
except ImportError:
    print("Missing dependencies. Please run:\n  pip install yfinance pandas")
    sys.exit(1)

# Disable caching quirks on OneDrive
os.environ["YF_NO_CACHE"] = "1"

# ---- User settings ----
OUTPUT_DIR = "asx_eod_output"
OUTPUT_CSV = "DailyData.csv"

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 🔧 EDIT YOUR DEFAULT TICKERS HERE:
TICKERS = ["ALK.AX",
           "AMP.AX",
           "ASM.AX",
           "BHP.AX",
           "CAN.AX",
           "CBA.AX",
           "CNB.AX",
           "E25.AX",
           "ERA.AX",
           "PTR.AX",
           "VML.AX",
           "WBC.AX",
           "WDS.AX"]
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# ---------- Utilities ----------

def parse_date_any(s: str) -> Optional[datetime]:
    """Parse AU-friendly and ISO date formats."""
    s = s.strip()
    if not s:
        return None
    fmts = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"]
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
    for t in tickers:
        if t not in df.columns.get_level_values(0):
            continue
        sub = df[t].copy()
        for k in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if k not in sub.columns:
                sub[k] = pd.NA
        sub = sub[["Open", "High", "Low", "Close", "Adj Close", "Volume"]]
        sub = sub.reset_index().rename(columns={"index": "Date"})
        sub.insert(0, "Ticker", t)
        records.append(sub)

    if not records:
        return pd.DataFrame(columns=["Ticker", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"])

    out = pd.concat(records, ignore_index=True)
    out["Date"] = pd.to_datetime(out["Date"]).dt.tz_localize(None)
    return out


def prompt_dates() -> (datetime, datetime):
    """Prompt for start/end dates."""
    print("\n=== ASX EOD Downloader ===")
    print(f"Using hard-coded tickers: {', '.join(TICKERS)}")

    default_start = (datetime.today() - timedelta(days=60)).strftime("%Y-%m-%d")
    default_end   = datetime.today().strftime("%Y-%m-%d")

    start_s = prompt_with_default("Start date", default_start)
    end_s   = prompt_with_default("End date", default_end)

    start_dt = parse_date_any(start_s)
    end_dt   = parse_date_any(end_s)

    if not start_dt or not end_dt:
        print("Invalid date(s). Please use formats like 2025-10-25 or 25/10/2025.")
        sys.exit(2)
    if end_dt < start_dt:
        print("End date cannot precede start date.")
        sys.exit(2)
    return start_dt, end_dt


# ---------- Main ----------

def main():
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

    # ---- Round price data to 3 dp and pad with zeros ----
    price_cols = ["Open", "High", "Low", "Close", "Adj Close"]
    for c in price_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").round(3)
            # Convert to string padded with zeros
            df[c] = df[c].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "")

    # ---- Reorder columns (Date first) and sort ----
    cols = [c for c in df.columns if c not in ("Date", "Ticker")]
    ordered_cols = ["Date", "Ticker"] + cols
    df = df[ordered_cols].sort_values(["Date", "Ticker"]).reset_index(drop=True)

    # ---- Save output ----
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
