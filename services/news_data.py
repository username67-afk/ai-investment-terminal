"""
Financial news retrieval via free Google News RSS, scoped to India.
"""

import re
from urllib.parse import quote

import feedparser

from config.settings import NEWS_RSS_TEMPLATE, MAX_HEADLINES


def _clean_headline(title: str) -> str:
    title = re.sub(r"\s*-\s*[^-]+$", "", title).strip()
    return title


def get_company_news(company_name: str, max_headlines: int = MAX_HEADLINES) -> list:
    query = quote(f"{company_name} India stock NSE")
    url = NEWS_RSS_TEMPLATE.format(query=query)

    feed = feedparser.parse(url)
    headlines = []
    seen_titles = set()

    for entry in feed.entries:
        title = _clean_headline(entry.get("title", ""))
        if not title or title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())

        source = ""
        if "source" in entry and hasattr(entry.source, "title"):
            source = entry.source.title
        elif "source" in entry and isinstance(entry.source, dict):
            source = entry.source.get("title", "")

        headlines.append(
            {
                "title": title,
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": source,
            }
        )
        if len(headlines) >= max_headlines:
            break

    return headlines
