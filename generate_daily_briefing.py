"""Morning Investment Briefing Generator.

Usage:
    python generate_daily_briefing.py [--date YYYY-MM-DD] [--dry-run]
"""
import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from data_collector import fetch_all_data
from formatter import render_briefing, write_briefing
from ai_analyst import generate_ai_commentary

KST = timezone(timedelta(hours=9))
SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parents[2]  # kimble/ vault root


def inject_ai_commentary(content: str, commentary: str) -> str:
    """브리핑 마크다운의 ## 메모 섹션에 AI 코멘트를 삽입합니다."""
    memo_marker = "## 메모"
    if memo_marker in content:
        # 메모 섹션 바로 아래에 AI 코멘트 블록 삽입
        insert_block = (
            f"\n### AI 시황 분석\n"
            f"> {commentary}\n"
        )
        return content.replace(
            memo_marker,
            memo_marker + insert_block,
            1,
        )
    else:
        # 메모 섹션이 없으면 파일 끝에 추가
        return content + f"\n\n## AI 시황 분석\n> {commentary}\n"


def main():
    parser = argparse.ArgumentParser(description="Generate morning investment briefing")
    parser.add_argument("--date", default=None, help="Override date (YYYY-MM-DD)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print to stdout instead of writing file"
    )
    parser.add_argument("--output-dir", default=None, help="Override output base directory")
    parser.add_argument(
        "--no-ai", action="store_true", help="Skip AI commentary generation"
    )
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

    # AI 시황 분석 코멘트 생성 및 삽입
    if not args.no_ai:
        print("AI 시황 분석 생성 중...", file=sys.stderr)
        try:
            commentary = generate_ai_commentary(data, date)
            content = inject_ai_commentary(content, commentary)
            print("AI 코멘트 삽입 완료.", file=sys.stderr)
        except Exception as e:
            print(f"AI 코멘트 생성 실패 (건너뜀): {e}", file=sys.stderr)

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
