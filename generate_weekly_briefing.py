"""Weekly Investment Briefing Generator.

Usage:
    python generate_weekly_briefing.py --week 2026-02-4w [--dry-run]
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from chart_generator import generate_bar_chart, generate_line_chart
from data_collector import compute_rsi, fetch_period_data

KST = timezone(timedelta(hours=9))
SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parents[2]


def parse_week_arg(week_str):
    """Parse '2026-02-4w' into (year, month, week_num, start_date, end_date)."""
    parts = week_str.split("-")
    year = int(parts[0])
    month = int(parts[1])
    week_num = int(parts[2].replace("w", ""))

    # Calculate week boundaries
    # 1w = 1st~7th, 2w = 8th~14th, 3w = 15th~21st, 4w = 22nd~end
    start_day = (week_num - 1) * 7 + 1
    if week_num == 4:
        # 4th week goes to end of month
        import calendar
        end_day = calendar.monthrange(year, month)[1]
    else:
        end_day = week_num * 7

    start_date = datetime(year, month, start_day)
    end_date = datetime(year, month, end_day)
    # Previous week for comparison
    prev_start = start_date - timedelta(days=7)

    return {
        "year": year,
        "month": month,
        "week_num": week_num,
        "week_str": week_str,
        "start_date": start_date,
        "end_date": end_date,
        "prev_start": prev_start,
        "fetch_start": (prev_start - timedelta(days=14)).strftime("%Y-%m-%d"),
        "fetch_end": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
    }


def aggregate_weekly_data(raw_data, week_info):
    """Aggregate raw daily data into weekly summary."""
    start = week_info["start_date"]
    end = week_info["end_date"]
    prev_end = start - timedelta(days=1)
    prev_start = week_info["prev_start"]

    summary = {}
    chart_data = {}

    for category, tickers in raw_data.items():
        summary[category] = {}
        for name, df in tickers.items():
            if df.empty or len(df) < 2:
                summary[category][name] = None
                continue

            # Filter to this week
            week_mask = (df.index >= start.strftime("%Y-%m-%d")) & (
                df.index <= end.strftime("%Y-%m-%d")
            )
            week_df = df[week_mask]

            # Filter to previous week
            prev_mask = (df.index >= prev_start.strftime("%Y-%m-%d")) & (
                df.index < start.strftime("%Y-%m-%d")
            )
            prev_df = df[prev_mask]

            if week_df.empty:
                summary[category][name] = None
                continue

            week_open = week_df["Close"].iloc[0]
            week_close = week_df["Close"].iloc[-1]
            week_change = ((week_close - week_open) / week_open) * 100

            result = {
                "week_open": round(week_open, 2),
                "week_close": round(week_close, 2),
                "week_change_pct": round(week_change, 2),
                "week_high": round(week_df["High"].max(), 2),
                "week_low": round(week_df["Low"].min(), 2),
            }

            # Volume average
            if "Volume" in week_df.columns and not week_df["Volume"].isna().all():
                result["avg_volume"] = int(week_df["Volume"].mean())

            # Previous week comparison
            if not prev_df.empty:
                prev_close = prev_df["Close"].iloc[-1]
                vs_prev = ((week_close - prev_close) / prev_close) * 100
                result["vs_prev_week_pct"] = round(vs_prev, 2)

            # RSI at end of week (use all available data)
            if len(df) >= 15:
                rsi = compute_rsi(df["Close"], 14)
                result["rsi"] = rsi

            summary[category][name] = result

            # Store chart data
            chart_key = f"{category}/{name}"
            chart_data[chart_key] = {
                "dates": week_df.index.tolist(),
                "values": week_df["Close"].tolist(),
                "name": name,
                "category": category,
            }

    return summary, chart_data


def generate_charts(chart_data, week_info, charts_dir):
    """Generate chart PNGs for the weekly briefing."""
    prefix = week_info["week_str"]

    # 1. Index trend chart (normalized to 100)
    index_series = {}
    for key, data in chart_data.items():
        cat = data["category"]
        if cat in ("korean_indices", "us_indices") and data["dates"]:
            index_series[data["name"]] = {
                "dates": data["dates"],
                "values": data["values"],
            }
    if index_series:
        generate_line_chart(
            index_series,
            f"{prefix} 주요 지수 추이",
            charts_dir / f"{prefix}_indices_trend.png",
            normalize=True,
        )

    # 2. Stock comparison bar chart
    stock_names = []
    stock_changes = []
    for key, data in chart_data.items():
        cat = data["category"]
        if cat in ("korean_stocks", "us_stocks") and len(data["values"]) >= 2:
            name = data["name"]
            vals = data["values"]
            change = ((vals[-1] - vals[0]) / vals[0]) * 100
            stock_names.append(name)
            stock_changes.append(round(change, 1))
    if stock_names:
        generate_bar_chart(
            stock_names,
            stock_changes,
            f"{prefix} 종목별 주간 등락률",
            charts_dir / f"{prefix}_stocks_comparison.png",
        )

    return [
        f"{prefix}_indices_trend.png",
        f"{prefix}_stocks_comparison.png",
    ]


def render_weekly(summary, chart_paths, week_info, template_dir):
    """Render weekly briefing using Jinja2 template."""
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

    template = env.get_template("weekly_template.md")
    return template.render(
        data=summary,
        week=week_info,
        charts=chart_paths,
    )


def main():
    parser = argparse.ArgumentParser(description="Generate weekly investment briefing")
    parser.add_argument("--week", required=True, help="Week identifier (e.g., 2026-02-4w)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout")
    parser.add_argument("--output-dir", default=None, help="Override output base directory")
    args = parser.parse_args()

    week_info = parse_week_arg(args.week)
    year = str(week_info["year"])

    config_path = SCRIPT_DIR / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"[{args.week}] 주간 데이터 수집 중...", file=sys.stderr)
    raw_data = fetch_period_data(config, week_info["fetch_start"], week_info["fetch_end"])

    print("주간 데이터 집계 중...", file=sys.stderr)
    summary, chart_data = aggregate_weekly_data(raw_data, week_info)

    # Generate charts
    month = f"{week_info['month']:02d}"
    if args.output_dir:
        base = Path(args.output_dir)
    else:
        output_base = config.get("output", {}).get("base_path", "50_Archive/Daily/Economy")
        base = VAULT_ROOT / output_base
    month_dir = base / year / month
    week_dir = month_dir / f"{week_info['week_num']}w"
    charts_dir = month_dir / "charts"

    print("차트 생성 중...", file=sys.stderr)
    chart_paths = generate_charts(chart_data, week_info, charts_dir)

    print("주간 브리핑 렌더링 중...", file=sys.stderr)
    template_dir = SCRIPT_DIR / "templates"
    content = render_weekly(summary, chart_paths, week_info, template_dir)

    if args.dry_run:
        print(content)
    else:
        week_dir.mkdir(parents=True, exist_ok=True)
        filepath = week_dir / f"{args.week}_weekly-briefing.md"
        filepath.write_text(content, encoding="utf-8")
        print(f"저장 완료: {filepath}", file=sys.stderr)


if __name__ == "__main__":
    main()
