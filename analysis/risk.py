"""
Descriptive risk metrics - historical, not predictive.
"""

import numpy as np
import pandas as pd

from config.settings import RISK_FREE_RATE

TRADING_DAYS_PER_YEAR = 252


def daily_returns(df: pd.DataFrame) -> pd.Series:
    return df["Close"].pct_change().dropna()


def historical_volatility(df: pd.DataFrame) -> float:
    r = daily_returns(df)
    if r.empty:
        return None
    return round(float(r.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100), 2)


def max_drawdown(df: pd.DataFrame) -> float:
    closes = df["Close"]
    if closes.empty:
        return None
    running_max = closes.cummax()
    drawdown = (closes - running_max) / running_max
    return round(float(drawdown.min() * 100), 2)


def sharpe_ratio(df: pd.DataFrame, risk_free_rate: float = RISK_FREE_RATE) -> float:
    r = daily_returns(df)
    if r.empty or r.std() == 0:
        return None
    daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR
    excess = r - daily_rf
    return round(float((excess.mean() / r.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)), 2)


def downside_volatility(df: pd.DataFrame) -> float:
    r = daily_returns(df)
    downside = r[r < 0]
    if downside.empty:
        return None
    return round(float(downside.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100), 2)


def beta_vs_benchmark(stock_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> float:
    stock_r = daily_returns(stock_df).reset_index(drop=True)
    bench_r = daily_returns(benchmark_df).reset_index(drop=True)

    n = min(len(stock_r), len(bench_r))
    if n < 2:
        return None
    stock_r, bench_r = stock_r.iloc[-n:], bench_r.iloc[-n:]

    covariance = np.cov(stock_r, bench_r)[0][1]
    variance = np.var(bench_r)
    if variance == 0:
        return None
    return round(float(covariance / variance), 2)


def correlation_with_benchmark(stock_df: pd.DataFrame, benchmark_df: pd.DataFrame) -> float:
    stock_r = daily_returns(stock_df).reset_index(drop=True)
    bench_r = daily_returns(benchmark_df).reset_index(drop=True)
    n = min(len(stock_r), len(bench_r))
    if n < 2:
        return None
    return round(float(np.corrcoef(stock_r.iloc[-n:], bench_r.iloc[-n:])[0][1]), 2)


def risk_summary(stock_df: pd.DataFrame, benchmark_df: pd.DataFrame = None) -> dict:
    summary = {
        "historical_volatility_pct": historical_volatility(stock_df),
        "max_drawdown_pct": max_drawdown(stock_df),
        "sharpe_ratio": sharpe_ratio(stock_df),
        "downside_volatility_pct": downside_volatility(stock_df),
        "methodology": f"Annualized over {TRADING_DAYS_PER_YEAR} trading days; "
                        f"risk-free rate assumed {RISK_FREE_RATE * 100:.1f}%.",
    }
    if benchmark_df is not None:
        summary["beta_vs_nifty50"] = beta_vs_benchmark(stock_df, benchmark_df)
        summary["correlation_vs_nifty50"] = correlation_with_benchmark(stock_df, benchmark_df)
    return summary
