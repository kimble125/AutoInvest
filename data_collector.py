"""Market data collection module using yfinance and pykrx."""

import warnings
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)

KST = timezone(timedelta(hours=9))


def compute_rsi(closes: pd.Series, period: int = 14) -> Optional[float]:
    """Calculate RSI from a series of closing prices."""
    if len(closes) < period + 1:
        return None
    delta = closes.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    last_loss = loss.iloc[-1]
    if last_loss == 0:
        return 100.0
    rs = gain.iloc[-1] / last_loss
    return round(100 - (100 / (1 + rs)), 1)


def _extract_ticker_data(
    ticker_symbol: str, period: str = "1mo", rsi_period: int = 14, calc_rsi: bool = False
) -> Optional[dict]:
    """Fetch and extract data for a single ticker."""
    try:
        df = yf.Ticker(ticker_symbol).history(period=period, auto_adjust=True)
        if df.empty or len(df) < 2:
            return None

        current = df["Close"].iloc[-1]
        prev = df["Close"].iloc[-2]
        change_pct = ((current - prev) / prev) * 100

        result = {
            "price": round(current, 2),
            "change_pct": round(change_pct, 2),
        }

        if "Volume" in df.columns and not df["Volume"].isna().all():
            vol_today = df["Volume"].iloc[-1]
            vol_prev = df["Volume"].iloc[-2]
            result["volume"] = int(vol_today)
            if vol_prev > 0:
                result["volume_change_pct"] = round(
                    ((vol_today - vol_prev) / vol_prev) * 100, 1
                )
            # 5일 평균 거래량 대비
            if len(df) >= 6:
                avg_5d = df["Volume"].iloc[-6:-1].mean()
                if avg_5d > 0:
                    result["volume_vs_5d_avg_pct"] = round(
                        ((vol_today - avg_5d) / avg_5d) * 100, 1
                    )

        if calc_rsi:
            rsi = compute_rsi(df["Close"], rsi_period)
            result["rsi"] = rsi

        return result
    except Exception:
        return None


def fetch_yfinance_data(config: dict) -> dict:
    """Fetch all yfinance-based market data."""
    tickers_config = config["tickers"]
    rsi_period = config.get("rsi_period", 14)
    rsi_alert = config.get("rsi_alert", {"overbought": 70, "oversold": 30})

    # Categories that need RSI
    rsi_categories = {"korean_stocks", "us_stocks"}

    result = {}
    for category, tickers in tickers_config.items():
        result[category] = {}
        calc_rsi = category in rsi_categories
        for name, symbol in tickers.items():
            data = _extract_ticker_data(
                symbol, period="1mo", rsi_period=rsi_period, calc_rsi=calc_rsi
            )
            if data and calc_rsi and data.get("rsi") is not None:
                rsi = data["rsi"]
                if rsi >= rsi_alert["overbought"]:
                    data["rsi_alert"] = f"과매수 구간 (RSI {rsi})"
                elif rsi <= rsi_alert["oversold"]:
                    data["rsi_alert"] = f"과매도 구간 (RSI {rsi})"
            result[category][name] = data

    return result


def fetch_pykrx_data(config: dict, date_str: str) -> dict:
    """Fetch Korean market-specific data using pykrx.

    Args:
        config: Configuration dict with pykrx settings.
        date_str: Date string in YYYY-MM-DD format.
    """
    result = {
        "investor_flows": None,
        "sectors": None,
    }

    try:
        from pykrx import stock
    except ImportError:
        return result

    # pykrx uses YYYYMMDD format
    date_fmt = date_str.replace("-", "")

    # Try today, then go back up to 5 days to find last trading day
    for offset in range(6):
        check_date = datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=offset)
        check_fmt = check_date.strftime("%Y%m%d")
        try:
            # Test if this is a trading day by checking if we get data
            test = stock.get_market_trading_volume_by_investor(check_fmt, check_fmt, "KOSPI")
            if not test.empty:
                date_fmt = check_fmt
                break
        except Exception:
            continue

    # 1. Foreign/institutional investor flows
    try:
        investor_df = stock.get_market_trading_volume_by_investor(
            date_fmt, date_fmt, "KOSPI"
        )
        if not investor_df.empty:
            flows = {}
            for investor_type in ["외국인", "기관합계"]:
                if investor_type in investor_df.index:
                    row = investor_df.loc[investor_type]
                    buy = row.get("매수", 0)
                    sell = row.get("매도", 0)
                    net = buy - sell
                    flows[investor_type] = {
                        "buy": int(buy),
                        "sell": int(sell),
                        "net": int(net),
                    }
            if flows:
                result["investor_flows"] = flows
    except Exception:
        pass

    # 2. Sector performance
    pykrx_config = config.get("pykrx", {})
    target_sectors = pykrx_config.get("sectors", [])

    try:
        sector_df = stock.get_index_ticker_list(date_fmt, market="KOSPI")
        # Get all sector indices and their returns
        sectors = {}
        for sector_name in target_sectors:
            try:
                # Find matching index
                for idx_code in stock.get_index_ticker_list(date_fmt, market="KOSPI"):
                    idx_name = stock.get_index_ticker_name(idx_code)
                    if sector_name in idx_name:
                        # Get index OHLCV for change calculation
                        prev_date = (datetime.strptime(date_fmt, "%Y%m%d") - timedelta(days=7)).strftime("%Y%m%d")
                        idx_df = stock.get_index_ohlcv(prev_date, date_fmt, idx_code)
                        if len(idx_df) >= 2:
                            curr = idx_df["종가"].iloc[-1]
                            prev = idx_df["종가"].iloc[-2]
                            change = ((curr - prev) / prev) * 100
                            sectors[sector_name] = {
                                "price": round(curr, 2),
                                "change_pct": round(change, 2),
                            }
                        break
            except Exception:
                continue
        if sectors:
            result["sectors"] = sectors
    except Exception:
        pass

    return result


def fetch_period_data(config: dict, start_date: str, end_date: str) -> dict:
    """Fetch daily OHLCV data for all tickers over a date range.

    Returns dict of {category: {name: DataFrame}} with daily data.
    Used by weekly/monthly briefing generators for aggregation and charts.
    """
    tickers_config = config["tickers"]
    result = {}

    for category, tickers in tickers_config.items():
        result[category] = {}
        for name, symbol in tickers.items():
            try:
                df = yf.Ticker(symbol).history(start=start_date, end=end_date, auto_adjust=True)
                if not df.empty:
                    result[category][name] = df
            except Exception:
                result[category][name] = pd.DataFrame()

    return result


def fetch_all_data(config: dict, date_str: str) -> dict:
    """Fetch all market data from both yfinance and pykrx."""
    data = fetch_yfinance_data(config)

    pykrx_data = fetch_pykrx_data(config, date_str)
    data["investor_flows"] = pykrx_data["investor_flows"]
    data["sectors"] = pykrx_data["sectors"]

    # Detect if market was closed (KOSPI didn't move)
    kospi = data.get("korean_indices", {}).get("KOSPI")
    data["market_closed"] = kospi is None or (
        kospi is not None and kospi.get("change_pct") == 0.0
    )

    return data
