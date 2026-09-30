"""
Portfolio-level analysis: current value, returns, correlation across holdings.
"""

import pandas as pd

from services.market_data import get_quote, get_history


def portfolio_summary(holdings: list) -> dict:
    rows = []
    total_invested = 0.0
    total_current = 0.0

    for h in holdings:
        ticker = h["ticker"]
        qty = float(h["quantity"])
        buy_price = float(h["purchase_price"])
        invested = qty * buy_price

        try:
            quote = get_quote(ticker)
            current_price = quote["price"]
            current_value = qty * current_price
            gain_pct = round(100 * (current_price - buy_price) / buy_price, 2)
            error = None
        except Exception as exc:
            current_price, current_value, gain_pct = None, None, None
            error = str(exc)

        rows.append(
            {
                "ticker": ticker,
                "quantity": qty,
                "purchase_price": buy_price,
                "invested": round(invested, 2),
                "current_price": current_price,
                "current_value": round(current_value, 2) if current_value is not None else None,
                "gain_pct": gain_pct,
                "error": error,
            }
        )
        total_invested += invested
        if current_value is not None:
            total_current += current_value

    total_gain_pct = (
        round(100 * (total_current - total_invested) / total_invested, 2)
        if total_invested > 0 else None
    )

    return {
        "holdings": rows,
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "total_gain_pct": total_gain_pct,
    }


def correlation_matrix(tickers: list, period: str = "6mo") -> pd.DataFrame:
    price_series = {}
    for ticker in tickers:
        try:
            hist = get_history(ticker, period=period)
            price_series[ticker] = hist.set_index("Date")["Close"]
        except Exception:
            continue

    if len(price_series) < 2:
        return pd.DataFrame()

    combined = pd.DataFrame(price_series).dropna()
    returns = combined.pct_change().dropna()
    return returns.corr().round(2)
