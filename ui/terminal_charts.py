"""
Terminal chart rendering - pure Python, zero external dependencies.

Draws price/indicator charts as plain ASCII text, so there is no charting
library to break between versions (an earlier plotext-based version did).
Missing values (None/NaN, e.g. the first rows of a rolling average) are
skipped instead of crashing the chart.
"""

import pandas as pd


def _is_missing(v):
    """True for None or NaN (rolling indicators are NaN for their first rows)."""
    return v is None or v != v


def _sample_indices(n, max_points):
    """Evenly spaced row indices (always including the newest point) to fit the chart width."""
    if n <= max_points:
        return list(range(n))
    return [round(i * (n - 1) / (max_points - 1)) for i in range(max_points)]


def _format_date(d):
    try:
        return pd.to_datetime(d).strftime("%d %b %Y")
    except Exception:
        return None


def _date_axis(dates, idx, plot_width):
    """Bottom label line: first date at the left edge, last date at the right edge."""
    if not dates:
        left, right = "Oldest", "Newest"
    else:
        left = _format_date(dates[idx[0]]) or "Oldest"
        right = _format_date(dates[idx[-1]]) or "Newest"
    gap = max(plot_width - len(left) - len(right), 1)
    return left + " " * gap + right


def _compact(n):
    for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= limit:
            return f"{n / limit:.1f}{suffix}"
    return f"{n:.0f}"


def plot_lines(series, title, dates=None, y_label="", width=90, height=18,
               reference_lines=None, y_min=None, y_max=None, decimals=2,
               include_reference_in_range=False):
    """
    Draw one or more lines on a shared Y axis.

    series          list of (values, marker_character, legend_label); the first
                    series is drawn on top where lines overlap
    reference_lines {value: label} horizontal dotted guides (e.g. RSI 70 / 30)
    y_min / y_max   force the Y range (RSI is always drawn on 0-100)
    """
    print()
    print(f"=== {title} ===")

    n = max((len(vals) for vals, _, _ in series), default=0)
    if n == 0:
        print("No data to draw.")
        print()
        return

    idx = _sample_indices(n, width)
    sampled = [([vals[i] if i < len(vals) else None for i in idx], ch, label)
               for vals, ch, label in series]

    present = [v for vals, _, _ in sampled for v in vals if not _is_missing(v)]
    if not present:
        print("Not enough data to draw this chart yet.")
        print()
        return

    lo = y_min if y_min is not None else min(present)
    hi = y_max if y_max is not None else max(present)
    if include_reference_in_range and reference_lines:
        lo = min([lo] + list(reference_lines))
        hi = max([hi] + list(reference_lines))
    if hi == lo:
        hi = lo + 1
    span = hi - lo

    def row_of(v):
        r = int(round((v - lo) / span * (height - 1)))
        return min(max(r, 0), height - 1)

    m = len(idx)
    grid = [[" "] * m for _ in range(height)]

    if reference_lines:
        for ref_value in reference_lines:
            if lo <= ref_value <= hi:
                r = row_of(ref_value)
                for c in range(m):
                    grid[r][c] = "."

    for vals, ch, _ in reversed(sampled):  # first series is drawn last, so it stays visible
        for c, v in enumerate(vals):
            if not _is_missing(v):
                grid[row_of(v)][c] = ch

    for r in range(height - 1, -1, -1):
        value = lo + (r / (height - 1)) * span
        print(f"{value:>10.{decimals}f} | " + "".join(grid[r]))

    print(" " * 11 + "+" + "-" * m)
    print(" " * 12 + _date_axis(dates, idx, m))
    print("Legend: " + "   ".join(f"{ch} {label}" for _, ch, label in series))
    if reference_lines:
        print("Dotted lines: " + ", ".join(f"{k} = {v}" for k, v in reference_lines.items()))
    if y_label:
        print(f"Y-axis: {y_label}")
    print()


def plot_columns(values, title, dates=None, y_label="", width=90, height=10):
    """Vertical bar chart over time (used for volume). Many days per column are averaged."""
    print()
    print(f"=== {title} ===")

    n = len(values)
    if n == 0:
        print("No data to draw.")
        print()
        return

    clean = [0 if _is_missing(v) else v for v in values]
    if n > width:
        cols = []
        for i in range(width):
            a = int(i * n / width)
            b = max(int((i + 1) * n / width), a + 1)
            chunk = clean[a:b]
            cols.append(sum(chunk) / len(chunk))
    else:
        cols = clean

    top = max(cols) or 1
    heights = [int(round(v / top * height)) for v in cols]

    for level in range(height, 0, -1):
        label = _compact(top * level / height)
        print(f"{label:>10} | " + "".join("#" if h >= level else " " for h in heights))

    print(" " * 11 + "+" + "-" * len(cols))
    print(" " * 12 + _date_axis(dates, [0, n - 1], len(cols)))
    if y_label:
        note = " (averaged where several days share a column)" if n > width else ""
        print(f"Y-axis: {y_label}{note}")
    print()


def plot_bar(labels, values, title, max_bar_width=50):
    """Horizontal bar chart (negative values drawn with '-')."""
    print()
    print(f"=== {title} ===")

    clean_values = [0 if _is_missing(v) else v for v in values]
    max_abs = max((abs(v) for v in clean_values), default=1) or 1
    label_width = max((len(str(l)) for l in labels), default=10)

    for label, value in zip(labels, clean_values):
        bar_len = int(round((abs(value) / max_abs) * max_bar_width))
        bar = ("#" if value >= 0 else "-") * bar_len
        print(f"{str(label).ljust(label_width)} | {bar} {value:.2f}")
    print()


# ---- Chart functions used by app.py -------------------------------------------------

def plot_price_history(df, ticker: str):
    """Closing price with 20-day and 50-day moving averages."""
    series = [(df["Close"].tolist(), "*", "Close")]
    if "SMA_20" in df.columns:
        series.append((df["SMA_20"].tolist(), "o", "20-day avg"))
    if "SMA_50" in df.columns:
        series.append((df["SMA_50"].tolist(), "+", "50-day avg"))
    plot_lines(series, f"{ticker} - Price History (last {len(df)} trading days)",
               dates=list(df["Date"]), y_label="Price (Rs.)")


def plot_rsi(df, ticker: str):
    """RSI(14) on a fixed 0-100 scale with overbought (70) / oversold (30) guides."""
    plot_lines([(df["RSI_14"].tolist(), "*", "RSI (14)")],
               f"{ticker} - RSI (14)", dates=list(df["Date"]), y_label="RSI",
               reference_lines={70: "Overbought", 30: "Oversold"}, y_min=0, y_max=100)


def plot_macd(df, ticker: str):
    """MACD line vs its signal line, with the zero line always visible."""
    plot_lines([(df["MACD"].tolist(), "*", "MACD"),
                (df["MACD_signal"].tolist(), "o", "Signal line")],
               f"{ticker} - MACD", dates=list(df["Date"]), y_label="MACD",
               reference_lines={0: "Zero line"}, include_reference_in_range=True)


def plot_volume(df, ticker: str):
    """Traded volume over time."""
    if "Volume" not in df.columns:
        print("\nNo volume data available for this stock.\n")
        return
    plot_columns(df["Volume"].tolist(), f"{ticker} - Trading Volume",
                 dates=list(df["Date"]), y_label="Shares traded")


def plot_sentiment_bar(aggregate: dict):
    plot_bar(["Positive", "Neutral", "Negative"],
             [aggregate["positive_pct"], aggregate["neutral_pct"], aggregate["negative_pct"]],
             title="News Sentiment Breakdown (%)")


def plot_comparison_bar(names: list, values: list, metric_label: str):
    plot_bar(names, values, title=metric_label)
