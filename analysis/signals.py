"""
Rule-based chart analysis: turns the latest indicator values into plain-English
readings of trend, momentum, volatility and volume.

These are descriptive readings of PAST price behaviour using standard textbook
thresholds - they are not predictions or investment advice.
"""

import pandas as pd

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
SMA_CROSS_LOOKBACK = 10     # a 50/200-day crossover counts as "fresh" within this many days
MACD_CROSS_LOOKBACK = 5
HIGH_VOLUME_RATIO = 1.5
LOW_VOLUME_RATIO = 0.5


def _valid(x):
    """False for None/NaN."""
    return x is not None and x == x


def _recent_cross(a: pd.Series, b: pd.Series, lookback: int):
    """
    Did series `a` cross above or below series `b` within the last `lookback` rows?
    Returns ("up" | "down", days_ago) for the most recent crossover, or None.
    """
    diff = (a - b).dropna()
    if len(diff) < 2:
        return None
    signs = [(1 if d > 0 else -1 if d < 0 else 0) for d in diff.iloc[-(lookback + 1):]]
    for i in range(len(signs) - 1, 0, -1):
        if signs[i] != signs[i - 1] and signs[i] != 0:
            return ("up" if signs[i] > 0 else "down", len(signs) - 1 - i)
    return None


def analyze_signals(df: pd.DataFrame) -> dict:
    """
    df: price history after analysis.technical.compute_all_indicators().
    Returns {"signals": [{indicator, stance, detail}, ...], "bullish", "bearish",
             "neutral", "bias"}.
    """
    signals = []

    def add(indicator, stance, detail):
        signals.append({"indicator": indicator, "stance": stance, "detail": detail})

    if df is None or df.empty:
        return {"signals": [], "bullish": 0, "bearish": 0, "neutral": 0, "bias": "No data"}

    last = df.iloc[-1]
    close = last["Close"]

    # --- Trend: price versus its moving averages ---
    for col, label in (("SMA_50", "50-day"), ("SMA_200", "200-day")):
        name = f"Trend ({label})"
        if col in df.columns and _valid(last[col]):
            if close > last[col]:
                add(name, "bullish", f"Price {close:.2f} is above its {label} average ({last[col]:.2f}).")
            else:
                add(name, "bearish", f"Price {close:.2f} is below its {label} average ({last[col]:.2f}).")
        else:
            add(name, "neutral", "Not enough price history to calculate this yet.")

    # --- 50/200-day crossover (golden / death cross) ---
    if ("SMA_50" in df.columns and "SMA_200" in df.columns
            and _valid(last["SMA_50"]) and _valid(last["SMA_200"])):
        cross = _recent_cross(df["SMA_50"], df["SMA_200"], SMA_CROSS_LOOKBACK)
        if cross and cross[0] == "up":
            add("50/200-day cross", "bullish",
                f"Golden cross: 50-day crossed above 200-day {cross[1]} day(s) ago.")
        elif cross:
            add("50/200-day cross", "bearish",
                f"Death cross: 50-day crossed below 200-day {cross[1]} day(s) ago.")
        elif last["SMA_50"] > last["SMA_200"]:
            add("50/200-day cross", "bullish", "50-day average is above the 200-day average.")
        else:
            add("50/200-day cross", "bearish", "50-day average is below the 200-day average.")

    # --- Momentum: RSI ---
    if "RSI_14" in df.columns and _valid(last["RSI_14"]):
        rsi = last["RSI_14"]
        if rsi >= RSI_OVERBOUGHT:
            add("RSI (14)", "bearish", f"RSI {rsi:.1f} is above 70 (overbought) - may be stretched.")
        elif rsi <= RSI_OVERSOLD:
            add("RSI (14)", "bullish", f"RSI {rsi:.1f} is below 30 (oversold) - selling may be overdone.")
        else:
            add("RSI (14)", "neutral", f"RSI {rsi:.1f} is between 30 and 70 - no extreme.")

    # --- Momentum: MACD ---
    if ("MACD" in df.columns and "MACD_signal" in df.columns
            and _valid(last["MACD"]) and _valid(last["MACD_signal"])):
        macd, sig = last["MACD"], last["MACD_signal"]
        cross = _recent_cross(df["MACD"], df["MACD_signal"], MACD_CROSS_LOOKBACK)
        if cross and cross[0] == "up":
            add("MACD", "bullish", f"MACD crossed above its signal line {cross[1]} day(s) ago.")
        elif cross:
            add("MACD", "bearish", f"MACD crossed below its signal line {cross[1]} day(s) ago.")
        elif macd > sig:
            add("MACD", "bullish", f"MACD ({macd:.2f}) is above its signal line ({sig:.2f}).")
        else:
            add("MACD", "bearish", f"MACD ({macd:.2f}) is below its signal line ({sig:.2f}).")

    # --- Volatility: Bollinger Bands ---
    if ("BB_upper" in df.columns and "BB_lower" in df.columns
            and _valid(last["BB_upper"]) and _valid(last["BB_lower"])
            and last["BB_upper"] > last["BB_lower"]):
        upper, lower = last["BB_upper"], last["BB_lower"]
        if close > upper:
            add("Bollinger Bands", "bearish", "Price is above the upper band - stretched to the upside.")
        elif close < lower:
            add("Bollinger Bands", "bullish", "Price is below the lower band - stretched to the downside.")
        else:
            pct = (close - lower) / (upper - lower) * 100
            add("Bollinger Bands", "neutral", f"Price is inside the bands ({pct:.0f}% of the way up).")

    # --- Volume context (informational) ---
    if "Volume" in df.columns and len(df) >= 21:
        avg20 = df["Volume"].iloc[-21:-1].mean()
        vol = last["Volume"]
        if _valid(avg20) and avg20 > 0 and _valid(vol):
            ratio = vol / avg20
            if ratio >= HIGH_VOLUME_RATIO:
                add("Volume", "neutral", f"Latest volume is {ratio:.1f}x its 20-day average - unusually active.")
            elif ratio <= LOW_VOLUME_RATIO:
                add("Volume", "neutral", f"Latest volume is {ratio:.1f}x its 20-day average - quiet trading.")
            else:
                add("Volume", "neutral", f"Latest volume is {ratio:.1f}x its 20-day average - normal.")

    bullish = sum(1 for s in signals if s["stance"] == "bullish")
    bearish = sum(1 for s in signals if s["stance"] == "bearish")
    neutral = sum(1 for s in signals if s["stance"] == "neutral")

    if bullish - bearish >= 2:
        bias = "Bullish-leaning"
    elif bearish - bullish >= 2:
        bias = "Bearish-leaning"
    else:
        bias = "Mixed / neutral"

    return {"signals": signals, "bullish": bullish, "bearish": bearish,
            "neutral": neutral, "bias": bias}
