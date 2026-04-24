#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a narrative commentary for the latest last-two-dates portfolio report
using the Claude API (Anthropic).

Reads the most recent Report_CSV/Report_YYYYMMDD.csv plus a trailing window of
DailyData.csv for trend context, and writes a Markdown commentary to
asx_eod_output/Report_Narrative/Report_YYYYMMDD_narrative.md.

Requires:
  - pip install anthropic
  - ANTHROPIC_API_KEY environment variable
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

OUTPUT_DIR = "asx_eod_output"
DAILY_CSV = os.path.join(OUTPUT_DIR, "DailyData.csv")
REPORT_CSV_DIR = os.path.join(OUTPUT_DIR, "Report_CSV")
NARRATIVE_DIR = os.path.join(OUTPUT_DIR, "Report_Narrative")

MODEL = "claude-opus-4-7"
# Opus 4.7 pricing, USD per 1M tokens. Update if MODEL changes.
INPUT_PRICE_PER_MTOK = 5.00
OUTPUT_PRICE_PER_MTOK = 25.00
TREND_WINDOW_DAYS = 10  # Trailing distinct trading days included as trend context
MAX_TOKENS = 4000

SYSTEM_PROMPT = """You are a concise Australian equities portfolio commentator.

You will be given:
1. A daily change report for an ASX share portfolio (latest two trading days).
2. A short trailing window of closing prices and holdings values for trend context.

Write a Markdown commentary with these sections, in this order:

## Headline
One sentence: the total portfolio value, the day's dollar gain/loss, and direction.

## Top Movers
Bullet list of the 3-5 most notable ticker moves by dollar impact on the portfolio
(i.e. Day Gain magnitude, not raw percent). For each: ticker, close, % move, dollar
impact. Briefly note whether the move is consistent with the trailing trend or a
reversal.

## Trend Notes
2-4 short bullets on tickers whose trailing window shows a meaningful pattern
(sustained drift, break from range, zero-volume stall). Only call out patterns
visible in the provided data - do not speculate on causes.

## Risks / Watch
1-3 bullets on exposures worth flagging: concentration, tickers with zero units
held (watchlist), or names dragging the portfolio repeatedly.

Rules:
- Be factual. No advice, no predictions, no emoji.
- Round dollars to whole numbers in prose; keep percentages to one decimal.
- Tickers with 0 units are watchlist-only - mention only if their move is large.
- Keep the whole commentary under ~350 words.
"""


def _latest_report_csv() -> Optional[str]:
    if not os.path.isdir(REPORT_CSV_DIR):
        return None
    files = [f for f in os.listdir(REPORT_CSV_DIR)
             if f.startswith("Report_") and f.endswith(".csv")]
    if not files:
        return None
    files.sort()
    return os.path.join(REPORT_CSV_DIR, files[-1])


def _date_from_report_name(path: str) -> str:
    base = os.path.basename(path)
    stem = os.path.splitext(base)[0]
    return stem.replace("Report_", "")


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build_trend_context(daily_csv: str, window: int = TREND_WINDOW_DAYS) -> str:
    if not os.path.exists(daily_csv):
        return "(DailyData.csv not found; trend context omitted.)"

    with open(daily_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return "(DailyData.csv empty; trend context omitted.)"

    distinct_dates = sorted({r["Date"] for r in rows})
    window_dates = set(distinct_dates[-window:])

    # Per-ticker close series over the window
    series: Dict[str, List[Tuple[str, float, int]]] = {}
    for r in rows:
        if r["Date"] not in window_dates:
            continue
        t = r["Ticker"].split(".")[0]
        try:
            close = float(r.get("Close", "0") or 0)
            shares = int(float(r.get("Shares", "0") or 0))
        except ValueError:
            continue
        series.setdefault(t, []).append((r["Date"], close, shares))

    for t in series:
        series[t].sort(key=lambda x: x[0])

    lines: List[str] = []
    lines.append(f"Trailing window: {sorted(window_dates)[0]} to {sorted(window_dates)[-1]} "
                 f"({len(window_dates)} trading days).")
    lines.append("")
    lines.append("Ticker,Date,Close,Shares,Value")
    for ticker in sorted(series.keys()):
        for d, close, shares in series[ticker]:
            value = shares * close
            lines.append(f"{ticker},{d},{close:.3f},{shares},{value:.2f}")
    return "\n".join(lines)


def _call_claude(report_csv_text: str, trend_text: str, report_date: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise SystemExit(
            "anthropic package not installed. Run:\n"
            "  .venv\\Scripts\\python.exe -m pip install anthropic"
        )

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Set it in your shell, e.g. PowerShell:\n"
            "  $env:ANTHROPIC_API_KEY = \"sk-ant-...\""
        )

    client = anthropic.Anthropic()

    user_content = (
        f"Report date (latest): {report_date}\n\n"
        f"=== Latest daily report CSV ===\n"
        f"{report_csv_text}\n\n"
        f"=== Trailing window (from DailyData.csv) ===\n"
        f"{trend_text}\n"
    )

    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        final = stream.get_final_message()

    print()  # newline after streamed output

    usage = final.usage
    input_cost = usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
    output_cost = usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK
    total_cost = input_cost + output_cost
    print(f"[usage] input={usage.input_tokens} output={usage.output_tokens}")
    print(f"[cost]  input=${input_cost:.4f}  output=${output_cost:.4f}  "
          f"total=${total_cost:.4f} USD")

    return "".join(block.text for block in final.content if block.type == "text")


def generate_narrative_report(report_csv_path: Optional[str] = None,
                              daily_csv_path: str = DAILY_CSV,
                              output_dir: str = NARRATIVE_DIR) -> str:
    if report_csv_path is None:
        report_csv_path = _latest_report_csv()
    if not report_csv_path or not os.path.exists(report_csv_path):
        raise SystemExit(
            f"No Report_CSV found under {REPORT_CSV_DIR}. "
            f"Run asx_eod_downloader.py or generate_last_two_report.py first."
        )

    report_date = _date_from_report_name(report_csv_path)
    report_text = _read_text(report_csv_path)
    trend_text = _build_trend_context(daily_csv_path)

    narrative = _call_claude(report_text, trend_text, report_date)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"Report_{report_date}_narrative.md")

    header = (
        f"# Portfolio Commentary - {report_date}\n\n"
        f"_Source: `{os.path.relpath(report_csv_path)}`_  \n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {MODEL}_\n\n"
        f"---\n\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + narrative.strip() + "\n")

    print(f"\nNarrative written: {out_path}")
    return out_path


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else None
    generate_narrative_report(report_csv_path=path)


if __name__ == "__main__":
    main()
