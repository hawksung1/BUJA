from __future__ import annotations

import yfinance as yf
import pandas as pd
from typing import Optional


def get_stock_info(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")

    current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev_close = info.get("previousClose", current_price)
    change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0

    return {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName", ticker),
        "current_price": current_price,
        "prev_close": prev_close,
        "change_pct": round(change_pct, 2),
        "volume": info.get("volume", 0),
        "avg_volume": info.get("averageVolume", 0),
        "market_cap": info.get("marketCap", 0),
        "pe_ratio": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "roe": info.get("returnOnEquity"),
        "debt_to_equity": info.get("debtToEquity"),
        "free_cashflow": info.get("freeCashflow"),
        "week_52_high": info.get("fiftyTwoWeekHigh"),
        "week_52_low": info.get("fiftyTwoWeekLow"),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "summary": info.get("longBusinessSummary", ""),
        "history": hist,
    }


def get_multiple_stocks(tickers: list[str]) -> list[dict]:
    results = []
    for ticker in tickers:
        try:
            results.append(get_stock_info(ticker))
        except Exception:
            pass
    return results


def search_ticker(query: str) -> list[dict]:
    """티커 심볼 검색 (yfinance 기반)"""
    try:
        ticker = yf.Ticker(query.upper())
        info = ticker.info
        if info.get("longName"):
            return [{"ticker": query.upper(), "name": info["longName"]}]
    except Exception:
        pass
    return []


def get_price_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    return stock.history(period=period)
