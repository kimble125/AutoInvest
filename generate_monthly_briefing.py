"""Monthly Investment Briefing Generator.

Usage:
    python generate_monthly_briefing.py --month 2026-02 [--dry-run]
"""

import argparse
import calendar
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from chart_generator import generate_bar_chart, generate_line_chart
from data_collector import compute_rsi, fetch_period_data

KST = timezone(timedelta(hours=9))
SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parents[2]


def parse_month_arg(month_str):
    """Parse '2026-02' into month metadata."""
    parts = month_str.split("-")
    year = int(parts[0])
    month = int(parts[1])
    last_day = calendar.monthrange(year, month)[1]

    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)

    # Previous month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    prev_last_day = calendar.monthrange(prev_year, prev_month)[1]
    prev_start = datetime(prev_year, prev_month, 1)

    # Week boundaries for breakdown
    weeks = []
    for w in range(1, 5):
        w_start_day = (w - 1) * 7 + 1
        w_end_day = min(w * 7, last_day) if w < 4 else last_day
        weeks.append({
            "num": w,
            "start": datetime(year, month, w_start_day),
            "end": datetime(year, month, w_end_day),
        })

    return {
        "year": year,
        "month": month,
        "month_str": month_str,
        "start_date": start_date,
        "end_date": end_date,
        "prev_start": prev_start,
        "weeks": weeks,
        "fetch_start": prev_start.strftime("%Y-%m-%d"),
        "fetch_end": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
    }


def aggregate_monthly_data(raw_data, month_info):
    """Aggregate raw daily data into monthly summary with weekly breakdown."""
    start = month_info["start_date"]
    end = month_info["end_date"]
    prev_start = month_info["prev_start"]

    summary = {}
    weekly_breakdown = {w["num"]: {} for w in month_info["weeks"]}
    chart_data = {}

    for category, tickers in raw_data.items():
        summary[category] = {}
        for name, df in tickers.items():
            if df.empty or len(df) < 2:
                summary[category][name] = None
                continue

            # This month
            month_mask = (df.index >= start.strftime("%Y-%m-%d")) & (
                df.index <= end.strftime("%Y-%m-%d")
            )
            month_df = df[month_mask]

            # Previous month
            prev_mask = (df.index >= prev_start.strftime("%Y-%m-%d")) & (
                df.index < start.strftime("%Y-%m-%d")
            )
            prev_df = df[prev_mask]

            if month_df.empty:
                summary[category][name] = None
                continue

            m_open = month_df["Close"].iloc[0]
            m_close = month_df["Close"].iloc[-1]
            m_change = ((m_close - m_open) / m_open) * 100

            result = {
                "month_open": round(m_open, 2),
                "month_close": round(m_close, 2),
                "month_change_pct": round(m_change, 2),
                "month_high": round(month_df["High"].max(), 2),
                "month_low": round(month_df["Low"].min(), 2),
            }

            if not prev_df.empty:
                prev_close = prev_df["Close"].iloc[-1]
                vs_prev = ((m_close - prev_close) / prev_close) * 100
                result["vs_prev_month_pct"] = round(vs_prev, 2)

            if len(df) >= 15:
                rsi = compute_rsi(df["Close"], 14)
                result["rsi"] = rsi

            summary[category][name] = result

            # Weekly breakdown
            for week in month_info["weeks"]:
                w_mask = (month_df.index >= week["start"].strftime("%Y-%m-%d")) & (
                    month_df.index <= week["end"].strftime("%Y-%m-%d")
                )
                w_df = month_df[w_mask]
                if len(w_df) >= 2:
                    w_open = w_df["Close"].iloc[0]
                    w_close = w_df["Close"].iloc[-1]
                    w_change = ((w_close - w_open) / w_open) * 100
                    weekly_breakdown[week["num"]][name] = round(w_change, 2)
                elif len(w_df) == 1:
                    weekly_breakdown[week["num"]][name] = 0.0

            # Chart data (full month daily)
            chart_key = f"{category}/{name}"
            chart_data[chart_key] = {
                "dates": month_df.index.tolist(),
                "values": month_df["Close"].tolist(),
                "name": name,
                "category": category,
            }

    return summary, weekly_breakdown, chart_data


def generate_charts(chart_data, month_info, charts_dir):
    """Generate chart PNGs for the monthly briefing."""
    prefix = month_info["month_str"]
    chart_paths = []

    # 1. Index trend (full month, normalized)
    index_series = {}
    for key, data in chart_data.items():
        cat = data["category"]
        if cat in ("korean_indices", "us_indices") and data["dates"]:
            index_series[data["name"]] = {
                "dates": data["dates"],
                "values": data["values"],
            }
    if index_series:
        path = f"{prefix}_indices_trend.png"
        generate_line_chart(
            index_series,
            f"{prefix} 주요 지수 월간 추이",
            charts_dir / f"{prefix}_indices_trend.png",
            normalize=True,
        )
        chart_paths.append(path)

    # 2. Stock comparison bar
    stock_names = []
    stock_changes = []
    for key, data in chart_data.items():
        cat = data["category"]
        if cat in ("korean_stocks", "us_stocks") and len(data["values"]) >= 2:
            vals = data["values"]
            change = ((vals[-1] - vals[0]) / vals[0]) * 100
            stock_names.append(data["name"])
            stock_changes.append(round(change, 1))
    if stock_names:
        path = f"{prefix}_stocks_comparison.png"
        generate_bar_chart(
            stock_names,
            stock_changes,
            f"{prefix} 종목별 월간 등락률",
            charts_dir / f"{prefix}_stocks_comparison.png",
        )
        chart_paths.append(path)

    # 3. FX + Commodities trend
    fx_comm_series = {}
    for key, data in chart_data.items():
        cat = data["category"]
        if cat in ("fx", "commodities", "crypto") and data["dates"]:
            fx_comm_series[data["name"]] = {
                "dates": data["dates"],
                "values": data["values"],
            }
    if fx_comm_series:
        path = f"{prefix}_fx_commodities.png"
        generate_line_chart(
            fx_comm_series,
            f"{prefix} 환율·원자재·크립토 월간 추이",
            charts_dir / f"{prefix}_fx_commodities.png",
            normalize=True,
        )
        chart_paths.append(path)

    return chart_paths


def render_monthly(summary, weekly_breakdown, chart_paths, month_info, template_dir):
    """Render monthly briefing using Jinja2 template."""
    import jinja2
    from formatter import _emoji, _format_net_flow, _format_number, _format_pct, _format_volume

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        undefined=jinja2.Undefined,
        keep_trailing_newline=True,
    )
    env.filters["emoji"] = _emoji
    env.filters["num"] = _format_number
    env.filters["pct"] = _format_pct
    env.filters["vol"] = _format_volume
    env.filters["flow"] = _format_net_flow

    template = env.get_template("monthly_template.md")
    return template.render(
        data=summary,
        weekly=weekly_breakdown,
        month=month_info,
        charts=chart_paths,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate monthly investment briefing")
    parser.add_argument("--month", required=True, help="Month identifier (e.g., 2026-02)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout")
    args = parser.parse_args()

    month_info = parse_month_arg(args.month)
    year = str(month_info["year"])

    config_path = SCRIPT_DIR / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"[{args.month}] 월간 데이터 수집 중...", file=sys.stderr)
    raw_data = fetch_period_data(config, month_info["fetch_start"], month_info["fetch_end"])

    print("월간 데이터 집계 중...", file=sys.stderr)
    summary, weekly_breakdown, chart_data = aggregate_monthly_data(raw_data, month_info)

    output_base = config.get("output", {}).get("base_path", "50_Archive/Daily/Economy")
    month = f"{month_info['month']:02d}"
    output_dir = VAULT_ROOT / output_base / year / month
    charts_dir = output_dir / "charts"

    print("차트 생성 중...", file=sys.stderr)
    chart_paths = generate_charts(chart_data, month_info, charts_dir)

    print("월간 브리핑 렌더링 중...", file=sys.stderr)
    template_dir = SCRIPT_DIR / "templates"
    content = render_monthly(summary, weekly_breakdown, chart_paths, month_info, template_dir)

    if args.dry_run:
        print(content)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"{args.month}_monthly-briefing.md"
        filepath.write_text(content, encoding="utf-8")
        print(f"저장 완료: {filepath}", file=sys.stderr)


if __name__ == "__main__":
    main()
