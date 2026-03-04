---
date: {{ date }}
category: economy-daily
tags: [KOSPI, KOSDAQ, US-market, FX, commodities, crypto]
---

# {{ date }} Daily Briefing
{% if data.market_closed %}
> **시장 휴장일** — 아래 데이터는 최근 거래일 기준입니다.
{% endif %}

## 1. 글로벌 & 매크로

### 미국 시장 (전일 종가)
| 지수 | 현재가 | 등락률 |
|------|--------|--------|
{% for name, d in data.us_indices.items() %}{% if d %}| **{{ name }}** | {{ d.price | num }} | {{ d.change_pct | pct }} |
{% else %}| **{{ name }}** | N/A | N/A |
{% endif %}{% endfor %}

### 핵심 매크로 지표
| 지표 | 현재가 | 등락률 |
|------|--------|--------|
{% for name, d in data.fx.items() %}{% if d %}| 💵 {{ name }} | {{ d.price | num }} | {{ d.change_pct | pct }} |
{% else %}| 💵 {{ name }} | N/A | N/A |
{% endif %}{% endfor %}
{% for name, d in data.bonds.items() %}{% if d %}| 🏛️ {{ name }} | {{ d.price | num }}% | {{ d.change_pct | pct }} |
{% else %}| 🏛️ {{ name }} | N/A | N/A |
{% endif %}{% endfor %}
{% for name, d in data.volatility.items() %}{% if d %}| 😱 {{ name }} | {{ d.price | num }} | {{ d.change_pct | pct }} |
{% else %}| 😱 {{ name }} | N/A | N/A |
{% endif %}{% endfor %}

---

## 2. 국내 시장

### 지수
| 지표 | 현재가 | 등락률 | 거래량 (전일비) | 5일 평균 대비 |
|------|--------|--------|----------------|-------------|
{% for name, d in data.korean_indices.items() %}{% if d %}| **{{ name }}** | {{ d.price | num }} | {{ d.change_pct | pct }} | {{ d.volume | vol }}{% if d.volume_change_pct is defined %} ({{ d.volume_change_pct }}%){% endif %} | {% if d.volume_vs_5d_avg_pct is defined %}{{ d.volume_vs_5d_avg_pct }}%{% else %}N/A{% endif %} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A |
{% endif %}{% endfor %}

{% if data.investor_flows %}
### 투자자 수급
| 투자자 | 매수 | 매도 | 순매수 |
|--------|------|------|--------|
{% for investor, flow in data.investor_flows.items() %}| **{{ investor }}** | {{ flow.buy | vol }} | {{ flow.sell | vol }} | {{ flow.net | flow }} |
{% endfor %}
{% endif %}

{% if data.sectors %}
### 섹터 동향
| 섹터 | 지수 | 등락률 |
|------|------|--------|
{% for name, d in data.sectors.items() %}| {{ name }} | {{ d.price | num }} | {{ d.change_pct | pct }} |
{% endfor %}
{% endif %}

---

## 3. 핵심 종목 포커스

### 국내
| 종목 | 현재가 | 등락률 | 거래량 (전일비) | RSI (14) | 비고 |
|------|--------|--------|----------------|----------|------|
{% for name, d in data.korean_stocks.items() %}{% if d %}| **{{ name }}** | {{ d.price | num(0) }}원 | {{ d.change_pct | pct }} | {{ d.volume | vol }}{% if d.volume_change_pct is defined %} ({{ d.volume_change_pct }}%){% endif %} | {{ d.rsi if d.rsi else "N/A" }} | {% if d.rsi_alert is defined %}⚠️ {{ d.rsi_alert }}{% endif %} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | |
{% endif %}{% endfor %}

### 미국
| 종목 | 현재가 | 등락률 | 거래량 (전일비) | RSI (14) | 비고 |
|------|--------|--------|----------------|----------|------|
{% for name, d in data.us_stocks.items() %}{% if d %}| **{{ name }}** | ${{ d.price | num }} | {{ d.change_pct | pct }} | {{ d.volume | vol }}{% if d.volume_change_pct is defined %} ({{ d.volume_change_pct }}%){% endif %} | {{ d.rsi if d.rsi else "N/A" }} | {% if d.rsi_alert is defined %}⚠️ {{ d.rsi_alert }}{% endif %} |
{% else %}| **{{ name }}** | N/A | N/A | N/A | N/A | |
{% endif %}{% endfor %}

---

## 4. 원자재 & 안전자산

| 자산 | 현재가 | 등락률 |
|------|--------|--------|
{% for name, d in data.commodities.items() %}{% if d %}| {{ name }} | ${{ d.price | num }} | {{ d.change_pct | pct }} |
{% else %}| {{ name }} | N/A | N/A |
{% endif %}{% endfor %}
{% for name, d in data.crypto.items() %}{% if d %}| {{ name }} | ${{ d.price | num }} | {{ d.change_pct | pct }} |
{% else %}| {{ name }} | N/A | N/A |
{% endif %}{% endfor %}

---

## 5. 메모
> 아래에 수동으로 메모를 추가하세요.

-
