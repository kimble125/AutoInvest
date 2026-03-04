---
date: {{ week.week_str }}
category: economy-weekly
tags: [KOSPI, KOSDAQ, US-market, weekly-review]
---

# {{ week.week_str }} Weekly Briefing
> {{ week.year }}년 {{ week.month }}월 {{ week.week_num }}째주 ({{ week.start_date.strftime("%m/%d") }} ~ {{ week.end_date.strftime("%m/%d") }})

## 주간 차트

{% for chart in charts %}![[{{ chart }}]]
{% endfor %}


---

## 1. 글로벌 지수

| 지수 | 주초 | 주말 | 주간 등락 | 전주 대비 | RSI |
|------|------|------|----------|----------|-----|
{% for name, d in data.us_indices.items() %}{% if d %}| **{{ name }}** | {{ d.week_open | num }} | {{ d.week_close | num }} | {{ d.week_change_pct | pct }} | {% if d.vs_prev_week_pct is defined %}{{ d.vs_prev_week_pct | pct }}{% else %}N/A{% endif %} | {{ d.rsi if d.rsi else "N/A" }} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

---

## 2. 국내 시장

| 지수 | 주초 | 주말 | 주간 등락 | 전주 대비 | RSI |
|------|------|------|----------|----------|-----|
{% for name, d in data.korean_indices.items() %}{% if d %}| **{{ name }}** | {{ d.week_open | num }} | {{ d.week_close | num }} | {{ d.week_change_pct | pct }} | {% if d.vs_prev_week_pct is defined %}{{ d.vs_prev_week_pct | pct }}{% else %}N/A{% endif %} | {{ d.rsi if d.rsi else "N/A" }} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

---

## 3. 핵심 종목

### 국내
| 종목 | 주초 | 주말 | 주간 등락 | 주간 고/저 | RSI | 비고 |
|------|------|------|----------|-----------|-----|------|
{% for name, d in data.korean_stocks.items() %}{% if d %}| **{{ name }}** | {{ d.week_open | num(0) }}원 | {{ d.week_close | num(0) }}원 | {{ d.week_change_pct | pct }} | {{ d.week_high | num(0) }} / {{ d.week_low | num(0) }} | {{ d.rsi if d.rsi else "N/A" }} | {% if d.rsi and d.rsi >= 70 %}⚠️ 과매수{% elif d.rsi and d.rsi <= 30 %}⚠️ 과매도{% endif %} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A | |
{% endif %}{% endfor %}

### 미국
| 종목 | 주초 | 주말 | 주간 등락 | 주간 고/저 | RSI | 비고 |
|------|------|------|----------|-----------|-----|------|
{% for name, d in data.us_stocks.items() %}{% if d %}| **{{ name }}** | ${{ d.week_open | num }} | ${{ d.week_close | num }} | {{ d.week_change_pct | pct }} | ${{ d.week_high | num }} / ${{ d.week_low | num }} | {{ d.rsi if d.rsi else "N/A" }} | {% if d.rsi and d.rsi >= 70 %}⚠️ 과매수{% elif d.rsi and d.rsi <= 30 %}⚠️ 과매도{% endif %} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A | |
{% endif %}{% endfor %}

---

## 4. 매크로 & 원자재

| 지표 | 주초 | 주말 | 주간 등락 |
|------|------|------|----------|
{% for name, d in data.fx.items() %}{% if d %}| 💵 {{ name }} | {{ d.week_open | num }} | {{ d.week_close | num }} | {{ d.week_change_pct | pct }} |
{% endif %}{% endfor %}
{% for name, d in data.bonds.items() %}{% if d %}| 🏛️ {{ name }} | {{ d.week_open | num }}% | {{ d.week_close | num }}% | {{ d.week_change_pct | pct }} |
{% endif %}{% endfor %}
{% for name, d in data.commodities.items() %}{% if d %}| {{ name }} | ${{ d.week_open | num }} | ${{ d.week_close | num }} | {{ d.week_change_pct | pct }} |
{% endif %}{% endfor %}
{% for name, d in data.crypto.items() %}{% if d %}| {{ name }} | ${{ d.week_open | num }} | ${{ d.week_close | num }} | {{ d.week_change_pct | pct }} |
{% endif %}{% endfor %}
{% for name, d in data.volatility.items() %}{% if d %}| 😱 {{ name }} | {{ d.week_open | num }} | {{ d.week_close | num }} | {{ d.week_change_pct | pct }} |
{% endif %}{% endfor %}

---

## 5. 메모
> 아래에 수동으로 메모를 추가하세요.

-
