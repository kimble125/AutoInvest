"""AI 시황 분석 모듈 - Gemini API를 사용해 메모 섹션에 AI 코멘트를 자동 생성합니다.

Usage:
    from ai_analyst import generate_ai_commentary
    comment = generate_ai_commentary(data, date)

API 키 설정 방법 (우선순위 순):
    1. 프로젝트 루트의 .env 파일에 GEMINI_API_KEY=your_key_here 작성 (권장)
    2. 시스템 환경변수로 GEMINI_API_KEY 설정
    3. generate_ai_commentary(data, date, api_key="your_key") 로 직접 전달

    .env 파일은 .gitignore에 등록되어 있어 GitHub에 올라가지 않습니다.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# .env 파일 로드 (python-dotenv가 설치된 경우 자동으로 .env를 읽음)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    # 스크립트 위치 기준으로 .env 탐색 (없어도 에러 없이 패스)
    _env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=_env_path, override=False)
except ImportError:
    pass  # python-dotenv 미설치 시 환경변수만 사용

GEMINI_MODEL = "gemini-1.5-flash"  # 무료 플랜 기준 가장 빠름


def _build_market_summary(data: dict) -> str:
    """시장 데이터를 Gemini에 넣을 텍스트 요약으로 변환합니다."""
    lines = []

    # 미국 시장
    us = data.get("us_indices", {})
    for name, d in us.items():
        if d:
            sign = "+" if d["change_pct"] >= 0 else ""
            lines.append(f"미국 {name}: {d['price']:,.2f} ({sign}{d['change_pct']:.2f}%)")

    # 한국 시장
    kr = data.get("korean_indices", {})
    for name, d in kr.items():
        if d:
            sign = "+" if d["change_pct"] >= 0 else ""
            lines.append(f"한국 {name}: {d['price']:,.2f} ({sign}{d['change_pct']:.2f}%)")

    # 환율
    fx = data.get("fx", {})
    for name, d in fx.items():
        if d:
            sign = "+" if d["change_pct"] >= 0 else ""
            lines.append(f"{name}: {d['price']:,.2f} ({sign}{d['change_pct']:.2f}%)")

    # 원자재
    comm = data.get("commodities", {})
    for name, d in comm.items():
        if d:
            sign = "+" if d["change_pct"] >= 0 else ""
            lines.append(f"{name}: ${d['price']:,.2f} ({sign}{d['change_pct']:.2f}%)")

    # 비트코인
    crypto = data.get("crypto", {})
    for name, d in crypto.items():
        if d:
            sign = "+" if d["change_pct"] >= 0 else ""
            lines.append(f"{name}: ${d['price']:,.2f} ({sign}{d['change_pct']:.2f}%)")

    # VIX
    vix = data.get("volatility", {})
    for name, d in vix.items():
        if d:
            lines.append(f"VIX(변동성): {d['price']:,.2f}")

    # 투자자 수급 (있는 경우)
    flows = data.get("investor_flows")
    if flows:
        for investor, flow in flows.items():
            net_100m = flow["net"] / 100_000_000
            sign = "+" if net_100m >= 0 else ""
            lines.append(f"투자자 수급 {investor}: 순매수 {sign}{net_100m:,.0f}억원")

    return "\n".join(lines)


def generate_ai_commentary(
    data: dict,
    date: str,
    api_key: Optional[str] = None,
) -> str:
    """시장 데이터를 바탕으로 Gemini API로 AI 시황 코멘트를 생성합니다.

    Args:
        data: fetch_all_data()의 반환값
        date: 날짜 문자열 (YYYY-MM-DD)
        api_key: Gemini API 키 직접 전달 (없으면 환경변수 / .env 파일 사용)

    Returns:
        AI가 작성한 한국어 시황 코멘트 문자열.
        API 키 미설정 또는 오류 시 안내 메시지 반환.
    """
    # API 키 우선순위: 직접 전달 > 환경변수(dotenv 로드 후)
    key = api_key or os.environ.get("GEMINI_API_KEY", "")

    if not key:
        return (
            "_AI 코멘트: GEMINI_API_KEY가 설정되지 않았습니다. "
            "프로젝트 루트에 .env 파일을 만들고 "
            "`GEMINI_API_KEY=your_key_here` 를 추가하세요._"
        )

    try:
        import google.generativeai as genai  # pip install google-generativeai
    except ImportError:
        return (
            "_AI 코멘트: google-generativeai 패키지가 설치되지 않았습니다. "
            "`pip install google-generativeai` 를 실행하세요._"
        )

    market_summary = _build_market_summary(data)

    prompt = f"""당신은 한국 주식 모니터링 시스템의 AI 에이전트입니다.
아래 {date} 글로벌 & 한국 시장 데이터를 바탕으로, 한국어로 짧은 시황 코멘트를 작성해주세요.

조건:
- 200자 이내로 작성 (마크다운 메모 스타일)
- 주요 시장 동향과 리스크 요인 1~3개를 간결하게 요약
- 투자 팁(TIP)이나 주의사항이 있다면 하나 더 추가
- 투자 권유는 하지 말 것
- 업무에만 집중 (매력적인 인사말 불필요)

시장 데이터:
{market_summary}
"""

    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"_AI 코멘트 생성 실패: {e}_"
