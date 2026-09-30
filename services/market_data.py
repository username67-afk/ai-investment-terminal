"""
Online market data layer. Prices are never hard-coded - fetched live via yfinance.
"""

from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from config.settings import HISTORY_PERIOD_DEFAULT, HISTORY_INTERVAL_DEFAULT, BENCHMARK_TICKER
from utils.storage import cached


class MarketDataError(Exception):
    pass


@cached(namespace="history")
def get_history(ticker: str, period: str = HISTORY_PERIOD_DEFAULT,
                 interval: str = HISTORY_INTERVAL_DEFAULT) -> pd.DataFrame:
    try:
        data = yf.Ticker(ticker).history(period=period, interval=interval)
    except Exception as exc:
        raise MarketDataError(f"Could not fetch history for {ticker}: {exc}") from exc

    if data.empty:
        raise MarketDataError(
            f"No historical data returned for '{ticker}'. "
            "Check that it is a valid NSE-listed ticker (must end in .NS)."
        )
    data = data.reset_index()
    return data


@cached(namespace="quote")
def get_quote(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    try:
        info = t.info
    except Exception as exc:
        raise MarketDataError(f"Could not fetch quote for {ticker}: {exc}") from exc

    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        hist = t.history(period="5d")
        if hist.empty:
            raise MarketDataError(f"No quote data available for '{ticker}'.")
        last_row = hist.iloc[-1]
        return {
            "ticker": ticker,
            "price": round(float(last_row["Close"]), 2),
            "open": round(float(last_row["Open"]), 2),
            "high": round(float(last_row["High"]), 2),
            "low": round(float(last_row["Low"]), 2),
            "previous_close": None,
            "volume": int(last_row["Volume"]),
            "market_cap": None,
            "week52_high": None,
            "week52_low": None,
            "currency": "INR",
            "as_of": datetime.now(timezone.utc).isoformat(),
            "data_freshness": "delayed_or_historical",
        }

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    return {
        "ticker": ticker,
        "price": price,
        "open": info.get("open"),
        "high": info.get("dayHigh"),
        "low": info.get("dayLow"),
        "previous_close": info.get("previousClose"),
        "volume": info.get("volume"),
        "market_cap": info.get("marketCap"),
        "week52_high": info.get("fiftyTwoWeekHigh"),
        "week52_low": info.get("fiftyTwoWeekLow"),
        "currency": info.get("currency", "INR"),
        "as_of": datetime.now(timezone.utc).isoformat(),
        "data_freshness": "live_or_near_live",
    }


@cached(namespace="fundamentals")
def get_fundamentals(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    try:
        info = t.info
    except Exception as exc:
        raise MarketDataError(f"Could not fetch fundamentals for {ticker}: {exc}") from exc

    return {
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "revenue": info.get("totalRevenue"),
        "revenue_growth": info.get("revenueGrowth"),
        "profit_margin": info.get("profitMargins"),
        "roe": info.get("returnOnEquity"),
        "debt_to_equity": info.get("debtToEquity"),
        "dividend_yield": info.get("dividendYield"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }


@cached(namespace="benchmark")
def get_benchmark_history(period: str = HISTORY_PERIOD_DEFAULT) -> pd.DataFrame:
    return get_history(BENCHMARK_TICKER, period=period)
