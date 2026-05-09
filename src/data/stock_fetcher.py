from __future__ import annotations

import time
import threading
import yfinance as yf
import pandas as pd
from typing import Optional

_cache: dict[str, tuple[dict, float]] = {}
_cache_lock = threading.Lock()
_TTL = 60  # seconds


def get_stock_info(ticker: str) -> dict:
    now = time.time()
    with _cache_lock:
        if ticker in _cache:
            data, ts = _cache[ticker]
            if now - ts < _TTL:
                return data

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or info.get("trailingPegRatio") is None and not info.get("currentPrice") and not info.get("regularMarketPrice"):
            # minimal fallback — try fast_info
            fi = stock.fast_info
            current_price = getattr(fi, "last_price", 0) or 0
            prev_close = getattr(fi, "previous_close", current_price) or current_price
            change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            result = {
                "ticker": ticker,
                "name": ticker,
                "current_price": current_price,
                "prev_close": prev_close,
                "change_pct": round(change_pct, 2),
                "volume": getattr(fi, "three_month_average_volume", 0),
                "avg_volume": 0,
                "market_cap": getattr(fi, "market_cap", 0),
                "pe_ratio": None,
                "pb_ratio": None,
                "roe": None,
                "debt_to_equity": None,
                "free_cashflow": None,
                "week_52_high": getattr(fi, "year_high", None),
                "week_52_low": getattr(fi, "year_low", None),
                "sector": "",
                "industry": "",
                "summary": "",
                "history": pd.DataFrame(),
            }
        else:
            current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            prev_close = info.get("previousClose", current_price)
            change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            try:
                hist = stock.history(period="1y")
            except Exception:
                hist = pd.DataFrame()
            result = {
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
    except Exception as e:
        raise RuntimeError(f"{ticker} 데이터 조회 실패: {e}") from e

    with _cache_lock:
        _cache[ticker] = (result, time.time())
    return result


def get_multiple_stocks(tickers: list[str]) -> list[dict]:
    results = []
    for ticker in tickers:
        try:
            results.append(get_stock_info(ticker))
        except Exception:
            pass
    return results


def search_ticker(query: str) -> list[dict]:
    try:
        ticker = yf.Ticker(query.upper())
        info = ticker.info
        if info.get("longName"):
            return [{"ticker": query.upper(), "name": info["longName"]}]
    except Exception:
        pass
    return []


def get_price_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period)
    except Exception:
        return pd.DataFrame()
