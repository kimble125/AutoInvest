---
date: {{ month.month_str }}
category: economy-monthly
tags: [KOSPI, KOSDAQ, US-market, monthly-review]
---

# {{ month.month_str }} Monthly Briefing
> {{ month.year }}년 {{ month.month }}월 전체 ({{ month.start_date.strftime("%m/%d") }} ~ {{ month.end_date.strftime("%m/%d") }})

## 월간 차트

{% for chart in charts %}![[{{ chart }}]]
{% endfor %}

---

## 1. 글로벌 지수

| 지수 | 월초 | 월말 | 월간 등락 | 전월 대비 | 고가/저가 | RSI |
|------|------|------|----------|----------|----------|-----|
{% for name, d in data.us_indices.items() %}{% if d %}| **{{ name }}** | {{ d.month_open | num }} | {{ d.month_close | num }} | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} | {{ d.month_high | num }} / {{ d.month_low | num }} | {{ d.rsi if d.rsi else "N/A" }} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

---

## 2. 국내 시장

| 지수 | 월초 | 월말 | 월간 등락 | 전월 대비 | 고가/저가 | RSI |
|------|------|------|----------|----------|----------|-----|
{% for name, d in data.korean_indices.items() %}{% if d %}| **{{ name }}** | {{ d.month_open | num }} | {{ d.month_close | num }} | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} | {{ d.month_high | num }} / {{ d.month_low | num }} | {{ d.rsi if d.rsi else "N/A" }} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

---

## 3. 핵심 종목

### 국내
| 종목 | 월초 | 월말 | 월간 등락 | 고가/저가 | RSI |
|------|------|------|----------|----------|-----|
{% for name, d in data.korean_stocks.items() %}{% if d %}| **{{ name }}** | {{ d.month_open | num(0) }}원 | {{ d.month_close | num(0) }}원 | {{ d.month_change_pct | pct }} | {{ d.month_high | num(0) }} / {{ d.month_low | num(0) }} | {{ d.rsi if d.rsi else "N/A" }} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

### 미국
| 종목 | 월초 | 월말 | 월간 등락 | 고가/저가 | RSI |
|------|------|------|----------|----------|-----|
{% for name, d in data.us_stocks.items() %}{% if d %}| **{{ name }}** | ${{ d.month_open | num }} | ${{ d.month_close | num }} | {{ d.month_change_pct | pct }} | ${{ d.month_high | num }} / ${{ d.month_low | num }} | {{ d.rsi if d.rsi else "N/A" }} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

---

## 4. 매크로 & 원자재

| 지표 | 월초 | 월말 | 월간 등락 | 전월 대비 |
|------|------|------|----------|----------|
{% for name, d in data.fx.items() %}{% if d %}| 💵 {{ name }} | {{ d.month_open | num }} | {{ d.month_close | num }} | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} |
{% endif %}{% endfor %}
{% for name, d in data.bonds.items() %}{% if d %}| 🏛️ {{ name }} | {{ d.month_open | num }}% | {{ d.month_close | num }}% | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} |
{% endif %}{% endfor %}
{% for name, d in data.commodities.items() %}{% if d %}| {{ name }} | ${{ d.month_open | num }} | ${{ d.month_close | num }} | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} |
{% endif %}{% endfor %}
{% for name, d in data.crypto.items() %}{% if d %}| {{ name }} | ${{ d.month_open | num }} | ${{ d.month_close | num }} | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} |
{% endif %}{% endfor %}
{% for name, d in data.volatility.items() %}{% if d %}| 😱 {{ name }} | {{ d.month_open | num }} | {{ d.month_close | num }} | {{ d.month_change_pct | pct }} | {% if d.vs_prev_month_pct is defined %}{{ d.vs_prev_month_pct | pct }}{% else %}N/A{% endif %} |
{% endif %}{% endfor %}

---

## 5. 주차별 등락률 (%)

| 종목/지수 | 1w | 2w | 3w | 4w |
|----------|-----|-----|-----|-----|
{% for name in weekly[1].keys() %}| {{ name }} | {% for w in range(1, 5) %}{% if weekly[w][name] is defined %}{% if weekly[w][name] >= 0 %}🔴 +{{ weekly[w][name] }}%{% else %}🔵 {{ weekly[w][name] }}%{% endif %}{% else %}N/A{% endif %} | {% endfor %}
{% endfor %}

---

## 6. 메모
> 아래에 수동으로 메모를 추가하세요.

-
