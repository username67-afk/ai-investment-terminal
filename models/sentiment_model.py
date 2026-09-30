"""
Lightweight financial-news sentiment model (VADER + finance lexicon).
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

_FINANCE_LEXICON = {
    "beat estimates": 2.5,
    "beats estimates": 2.5,
    "misses estimates": -2.5,
    "profit surge": 2.5,
    "profit jumps": 2.2,
    "profit falls": -2.2,
    "profit declines": -2.2,
    "revenue growth": 1.8,
    "downgrade": -2.0,
    "upgrade": 2.0,
    "buyback": 1.3,
    "dividend": 1.0,
    "fraud": -3.0,
    "probe": -1.8,
    "investigation": -1.5,
    "record high": 2.3,
    "record low": -2.0,
    "layoffs": -2.2,
    "expansion": 1.2,
    "acquisition": 1.0,
    "default": -2.8,
    "delisting": -2.5,
    "rating cut": -2.3,
    "rating upgrade": 2.3,
}
_analyzer.lexicon.update(_FINANCE_LEXICON)


def analyze_headline(text: str) -> dict:
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.15:
        label = "positive"
    elif compound <= -0.15:
        label = "negative"
    else:
        label = "neutral"

    return {
        "text": text,
        "positive": scores["pos"],
        "neutral": scores["neu"],
        "negative": scores["neg"],
        "compound": compound,
        "label": label,
    }


def analyze_headlines(headlines: list) -> list:
    return [analyze_headline(h["title"]) for h in headlines]


def aggregate_sentiment(analyzed: list) -> dict:
    if not analyzed:
        return {"positive_pct": 0.0, "neutral_pct": 0.0, "negative_pct": 0.0,
                "n_headlines": 0, "overall_label": "no_data"}

    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for item in analyzed:
        counts[item["label"]] += 1

    n = len(analyzed)
    positive_pct = round(100 * counts["positive"] / n, 1)
    neutral_pct = round(100 * counts["neutral"] / n, 1)
    negative_pct = round(100 * counts["negative"] / n, 1)

    if positive_pct >= negative_pct and positive_pct >= neutral_pct:
        overall = "positive"
    elif negative_pct >= positive_pct and negative_pct >= neutral_pct:
        overall = "negative"
    else:
        overall = "neutral"

    return {
        "positive_pct": positive_pct,
        "neutral_pct": neutral_pct,
        "negative_pct": negative_pct,
        "n_headlines": n,
        "overall_label": overall,
    }
