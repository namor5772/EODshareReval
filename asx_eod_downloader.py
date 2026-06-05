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
from datetime import datetime, timedelta, date
from typing import List, Optional, Tuple
import re

# ---- Dependencies ----
try:
    import pandas as pd
    import yfinance as yf
except ImportError:
    print("Missing dependencies. Please run:\n  pip install yfinance pandas")
    sys.exit(1)

# Local utility to generate the aligned last-two-dates TXT report after CSV updates
try:
    from generate_last_two_report import generate_last_two_report
except Exception:
    generate_last_two_report = None  # type: ignore

os.environ["YF_NO_CACHE"] = "1"

# ---- User settings ----
AUTO_GENERATE_LAST_TWO_REPORT: bool = True # Hardcoded flag: generate last-two-dates TXT/CSV/Excel report after CSV updates
PROMPT: bool = False  # If False, run non-interactively (use defaults as if Enter pressed)

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
    ["BHP.AX", 10000],
    ["CAN.AX", 44090],
    ["CBA.AX", 0],
    ["CNB.AX", 10000],
    ["CSL.AX", 3000],
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
    if not PROMPT:
        # Non-interactive: behave as if user pressed Enter (use default)
        return default
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


def prompt_dates(default_start: Optional[datetime] = None,
                 default_end: Optional[datetime] = None) -> (datetime, datetime): # type: ignore
    print("\n=== ASX EOD Downloader ===")
    print(
        f"Using holdings loaded from {HOLDINGS_FILE}:" if HOLDINGS_FROM_FILE
        else "Using default hard-coded holdings:"
    )
    for sym, sh in TICKERS_AND_SHARES:
        print(f"  - {sym}: {sh} shares")

    if default_start is None:
        default_start_s = (datetime.today() - timedelta(days=60)).strftime("%Y-%m-%d")
    else:
        default_start_s = default_start.strftime("%Y-%m-%d")
    if default_end is None:
        default_end_s   = datetime.today().strftime("%Y-%m-%d")
    else:
        default_end_s   = default_end.strftime("%Y-%m-%d")

    start_s = prompt_with_default("Start date", default_start_s)
    end_s   = prompt_with_default("End date", default_end_s)

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

    # Prepare output path; if it exists, we'll overwrite the last date then append
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, OUTPUT_CSV)

    # Detect last available date in existing CSV (if any)
    existing_max_date: Optional[date] = None
    prev_df: Optional[pd.DataFrame] = None
    if os.path.exists(out_path):
        try:
            prev_df = pd.read_csv(out_path, parse_dates=["Date"], dayfirst=False)
            if not prev_df.empty and "Date" in prev_df.columns:
                max_ts = pd.to_datetime(prev_df["Date"]).max()
                if pd.notna(max_ts):
                    existing_max_date = max_ts.date()
        except Exception as e:
            print(f"Warning: Could not read existing CSV to determine last date: {e}")

    # Default start is the existing max date (so we can overwrite it)
    default_start_dt = None
    if existing_max_date is not None:
        default_start_dt = datetime.combine(existing_max_date, datetime.min.time())

    start_dt, end_dt = prompt_dates(default_start=default_start_dt, default_end=datetime.today())

    # Ensure we always include the last existing date to overwrite it
    if existing_max_date is not None:
        required_start = datetime.combine(existing_max_date, datetime.min.time())
        if start_dt != required_start:
            print(f"\nAdjusting start date to overwrite last day: {start_dt.date()} -> {required_start.date()}")
            start_dt = required_start
        # Ensure end is not before adjusted start
        if end_dt < start_dt:
            print(f"Adjusting end date to not precede start: -> {start_dt.date()}")
            end_dt = start_dt

    end_plus_one = end_dt + timedelta(days=1)

    requested_start = start_dt.date()
    requested_end = end_dt.date()
    print(f"\nRequesting EOD for {', '.join(tickers)} "
          f"from {requested_start} to {requested_end} (inclusive)...")

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
        if 'existing_max_date' in locals() and existing_max_date is not None:
            print("\nNo new trading days to append. Up to date.")
            print("Done.")
            return
        print("No data returned. Check tickers or date range.")
        sys.exit(4)

    df = normalize_yf_panel(raw, tickers)
    if df.empty:
        if 'existing_max_date' in locals() and existing_max_date is not None:
            print("\nNo new trading days to append. Up to date.")
            print("Done.")
            return
        print("No valid data found for selected tickers.")
        sys.exit(5)

    normalized_dates = df["Date"].dt.normalize().dropna()
    if not normalized_dates.empty:
        actual_start = normalized_dates.min().date()
        actual_end = normalized_dates.max().date()
        unique_days = normalized_dates.nunique()
        plural = "" if unique_days == 1 else "s"
        if actual_start == actual_end:
            range_text = f"{actual_start}"
        else:
            range_text = f"{actual_start} -> {actual_end}"
        print(f"\nDownloaded EOD covering {unique_days} trading day{plural} ({range_text}).")

    # ---- Attach Shares ----
    df["Shares"] = df["Ticker"].map(SHARES_MAP).astype("Int64")

    # ---- Compute Value = Shares × Close ----
    close_numeric = pd.to_numeric(df["Close"], errors="coerce")
    df["Value"] = (df["Shares"].astype("float64") * close_numeric).round(2)
    # Convert to string with 2dp and zero padding3/11/235
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

    # ---- Save / Overwrite last date, then Append ----
    if os.path.exists(out_path):
        rows_appended = 0
        did_overwrite_last = False
        append_df = df.copy()

        if existing_max_date is not None:
            # If new data includes the last existing date, drop that date from previous CSV
            df_last = df[df["Date"].dt.date == existing_max_date]
            if not df_last.empty and prev_df is not None and not prev_df.empty:
                keep_prev = prev_df[pd.to_datetime(prev_df["Date"]).dt.date != existing_max_date]
                # Keep column order stable
                base_order = ["Date", "Ticker", "Shares", "Open", "High", "Low", "Close", "Volume", "Value"]
                prev_existing = [c for c in base_order if c in keep_prev.columns]
                prev_extras = [c for c in keep_prev.columns if c not in prev_existing]
                target_cols = prev_existing + prev_extras
                keep_prev = keep_prev[target_cols].sort_values(["Date", "Ticker"]).reset_index(drop=True)
                keep_prev.to_csv(out_path, index=False)
                did_overwrite_last = True
                # For appending, include last date and any newer dates
                append_df = df[df["Date"].dt.date >= existing_max_date]
            else:
                # No replacement possible, only append newer dates
                append_df = df[df["Date"].dt.date > existing_max_date]

        if append_df.empty:
            if did_overwrite_last:
                print("\nReplaced last trading day; no new days to append.")
            else:
                print("\nNo new trading days to overwrite/append. Up to date.")
        else:
            append_df = append_df.sort_values(["Date", "Ticker"]).reset_index(drop=True)
            # Align columns with existing file if present
            if prev_df is not None and not prev_df.empty:
                target_cols = list(prev_df.columns)
                # Only keep/align to target columns for appending
                append_df = append_df.reindex(columns=target_cols)
            # If we didn't overwrite last date above, ensure file exists with header
            if not did_overwrite_last and not os.path.exists(out_path):
                append_df.to_csv(out_path, index=False)
            else:
                append_df.to_csv(out_path, mode="a", header=False, index=False)
            rows_appended = len(append_df)
            action = "Replaced last day and appended" if did_overwrite_last else "Appended"
            print(f"\n{action} {rows_appended} rows to: {out_path}")
    else:
        df.to_csv(out_path, index=False)
        print(f"\nSaved consolidated CSV: {out_path}")

    # Generate the last-two-dates aligned TXT report when CSV has been touched
    if AUTO_GENERATE_LAST_TWO_REPORT and generate_last_two_report is not None and os.path.exists(out_path):
        try:
            d1, d2, rep_path = generate_last_two_report(
                csv_path=out_path,
                holdings_path=HOLDINGS_FILE,
                report_dir=OUTPUT_DIR,
                report_path=None,
                emit_csv=True,
                emit_excel=True,
                quiet=True,
            )
            print(f"\nGenerated last-two-dates reports (TXT/CSV/XLSX). TXT: {rep_path} (dates: {d1}, {d2})")
        except Exception as e:
            print(f"\nWarning: Could not generate last-two-dates report: {e}")

    # ---- Summary ----
    by_ticker = df.groupby("Ticker")["Date"].agg(["min", "max", "count"]).reset_index()
    print("\nSummary:")
    print(by_ticker.to_string(index=False))
    print("\nDone.")


if __name__ == "__main__":
    main()
