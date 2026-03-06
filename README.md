# AutoInvest

> **AI 기반 투자 데이터 파이프라인 & 자동 브리핑 시스템**

글로벌 시장 지표를 자동으로 수집하고, 기술적 지표를 계산하며, AI가 요약 리포트를 생성하는 **End-to-End 데이터 파이프라인**입니다.

---

## Problem

매일 아침 글로벌 시장 상황을 파악하려면 여러 사이트를 돌아다니며 수동으로 데이터를 수집하고 정리해야 합니다. 이 과정은 비효율적이고, 일관된 포맷으로 기록을 남기기 어렵습니다.

## Solution

**데이터 수집 → 기술 지표 계산 → AI 분석 → 리포트 생성**의 전 과정을 자동화했습니다.

```
[yfinance / pykrx]  →  [RSI 계산]  →  [Gemini AI 분석]  →  [Markdown 브리핑]
     수집                  분석              해석                 출력
```

## Key Features

| 기능 | 설명 |
|------|------|
| **멀티마켓 데이터 수집** | KOSPI, S&P500, NASDAQ, 개별 종목, 환율, 원자재, 암호화폐, 채권 금리 등 |
| **기술적 지표 자동 계산** | RSI(14일), 거래량 변화율, 5일 평균 거래량 대비 |
| **외국인/기관 수급 추적** | pykrx 기반 KOSPI 섹터별 수급 데이터 |
| **AI 시황 분석** | Gemini API로 시장 데이터 기반 자동 코멘터리 생성 |
| **일간/주간/월간 브리핑** | 템플릿 기반 Markdown 리포트 자동 생성 |
| **GitHub Actions 자동화** | 매일 아침 자동 실행 (cron 스케줄링) |
| **YAML 설정** | 추적 종목, 지표, 출력 경로 등 설정 파일로 관리 |

## Architecture

```
AutoInvest/
├── config.yaml                 # 추적 종목 및 설정
├── data_collector.py           # yfinance/pykrx 데이터 수집 + RSI 계산
├── ai_analyst.py               # Gemini API 기반 AI 시황 분석
├── formatter.py                # Jinja2 템플릿 기반 Markdown 렌더링
├── chart_generator.py          # 차트 생성 (확장용)
├── generate_daily_briefing.py  # 일간 브리핑 생성 엔트리포인트
├── generate_weekly_briefing.py # 주간 브리핑 생성
├── generate_monthly_briefing.py# 월간 브리핑 생성
├── notify_summary.py           # 알림 발송
├── templates/                  # Markdown 브리핑 템플릿
└── .github/workflows/          # GitHub Actions 자동화
```

## Tech Stack

| 카테고리 | 기술 |
|----------|------|
| **언어** | Python 3.11+ |
| **데이터 수집** | yfinance, pykrx |
| **AI 분석** | Google Gemini API (gemini-1.5-flash) |
| **자동화** | GitHub Actions (cron), YAML config |
| **출력** | Markdown (Obsidian Vault 연동) |

## Output Example

일간 브리핑에는 다음 정보가 포함됩니다:

- **글로벌 매크로**: S&P500, NASDAQ, Dow, 신흥국 ETF, USD/KRW, 미국 10년물, VIX
- **국내 시장**: KOSPI, KOSDAQ 지수 + 거래량 + 5일 평균 대비
- **핵심 종목**: 삼성전자, SK하이닉스, Apple, Nvidia, Microsoft, Tesla (RSI 포함)
- **원자재/암호화폐**: WTI, Brent, Gold, Silver, Bitcoin
- **외국인/기관 수급**: 섹터별 순매수 현황
- **AI 시황 분석**: Gemini가 생성한 시장 코멘터리

## Quick Start

```bash
# 1. 클론
git clone https://github.com/kimble125/AutoInvest.git
cd AutoInvest

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 입력

# 4. 일간 브리핑 생성
python generate_daily_briefing.py

# 5. 주간/월간 브리핑
python generate_weekly_briefing.py
python generate_monthly_briefing.py
```

## What I Learned

이 프로젝트를 통해 다음 역량을 실전으로 익혔습니다:

- **데이터 파이프라인 설계**: 수집 → 가공 → 분석 → 출력의 End-to-End 흐름
- **API 통합**: yfinance, pykrx, Gemini API 등 다중 데이터 소스 통합
- **자동화**: GitHub Actions cron을 활용한 무인 운영
- **설정 관리**: YAML config로 유연한 종목/지표 관리

> 이 경험은 **유저 행동 데이터 수집 → 집계 → 리포팅** 자동화와 동일한 구조이며, 그로스 마케팅에서의 데이터 파이프라인 구축에 직접 적용 가능합니다.

## License

MIT License
el.
