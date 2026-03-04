"""Morning Investment Briefing Generator.

Usage:
    python generate_Invest_briefing.py [--date YYYY-MM-DD] [--dry-run]
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from data_collector import fetch_all_data
from formatter import render_briefing, write_briefing

KST = timezone(timedelta(hours=9))
SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parents[2]  # kimble/ vault root


def main():
    parser = argparse.ArgumentParser(description="Generate morning investment briefing")
    parser.add_argument("--date", default=None, help="Override date (YYYY-MM-DD)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print to stdout instead of writing file"
    )
    parser.add_argument("--output-dir", default=None, help="Override output base directory")
    args = parser.parse_args()

    date = args.date or datetime.now(KST).strftime("%Y-%m-%d")
    year = date[:4]

    # Load config
    config_path = SCRIPT_DIR / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"[{date}] 데이터 수집 시작...", file=sys.stderr)
    data = fetch_all_data(config, date)

    print("브리핑 마크다운 생성 중...", file=sys.stderr)
    template_dir = SCRIPT_DIR / "templates"
    content = render_briefing(data, template_dir, date)

    if args.dry_run:
        print(content)
    else:
        dt = datetime.strptime(date, "%Y-%m-%d")
        month = f"{dt.month:02d}"
        week_num = min((dt.day - 1) // 7 + 1, 4)
        if args.output_dir:
            base = Path(args.output_dir)
        else:
            output_base = config.get("output", {}).get("base_path", "50_Archive/Daily/Economy")
            base = VAULT_ROOT / output_base
        output_dir = base / year / month / f"{week_num}w"
        path = write_briefing(content, output_dir, date)
        print(f"저장 완료: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
