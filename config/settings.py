"""
Central configuration for the AI Investment Research Terminal.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMPANY_MAPPING_PATH = os.path.join(BASE_DIR, "data", "company_mapping.csv")
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")
STORAGE_PATH = os.path.join(BASE_DIR, "data", "user_data.json")

DEFAULT_EXCHANGE_SUFFIX = ".NS"
BENCHMARK_TICKER = "^NSEI"
HISTORY_PERIOD_DEFAULT = "1y"
HISTORY_INTERVAL_DEFAULT = "1d"

NEWS_RSS_TEMPLATE = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
MAX_HEADLINES = 10

CACHE_TTL_SECONDS = 900

RISK_FREE_RATE = 0.065
