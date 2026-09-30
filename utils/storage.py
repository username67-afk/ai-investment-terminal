"""
Caching decorator + JSON storage for watchlist/portfolio.

Cache-read failures of any kind are handled by deleting the bad cache file and
fetching fresh data, so a cache problem can never crash the app.
"""

import functools
import hashlib
import io
import json
import os
import time

import pandas as pd

from config.settings import CACHE_DIR, CACHE_TTL_SECONDS, STORAGE_PATH


def _cache_key(namespace: str, args, kwargs) -> str:
    raw = namespace + str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(raw.encode()).hexdigest()


def cached(namespace: str):
    """Decorator: cache a function's return value to disk for CACHE_TTL_SECONDS."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            os.makedirs(CACHE_DIR, exist_ok=True)
            key = _cache_key(namespace, args, kwargs)
            path = os.path.join(CACHE_DIR, f"{key}.json")

            if os.path.exists(path):
                age = time.time() - os.path.getmtime(path)
                if age < CACHE_TTL_SECONDS:
                    try:
                        with open(path, "r") as f:
                            payload = json.load(f)
                        return _from_jsonable(payload)
                    except Exception:
                        # Unreadable cache file: delete it and fetch fresh data below.
                        try:
                            os.remove(path)
                        except OSError:
                            pass

            result = func(*args, **kwargs)
            try:
                with open(path, "w") as f:
                    json.dump(_to_jsonable(result), f)
            except Exception:
                pass  # failing to write the cache must never break the app
            return result

        return wrapper

    return decorator


def _to_jsonable(obj):
    if isinstance(obj, pd.DataFrame):
        return {"__type__": "dataframe", "data": obj.to_json(orient="split", date_format="iso")}
    return {"__type__": "plain", "data": obj}


def _from_jsonable(payload):
    if payload.get("__type__") == "dataframe":
        json_str = payload["data"]
        if not json_str:
            raise ValueError("Empty cached dataframe payload")
        # Wrapped in StringIO: newer pandas treats a bare string as a FILE PATH,
        # which is what caused the old "FileNotFoundError: File {...} does not exist" crash.
        return pd.read_json(io.StringIO(json_str), orient="split")
    return payload["data"]


def _load_store() -> dict:
    if not os.path.exists(STORAGE_PATH):
        return {"watchlist": [], "portfolio": []}
    try:
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"watchlist": [], "portfolio": []}


def _save_store(store: dict):
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    with open(STORAGE_PATH, "w") as f:
        json.dump(store, f, indent=2)


def add_to_watchlist(ticker: str):
    store = _load_store()
    if ticker not in store["watchlist"]:
        store["watchlist"].append(ticker)
        _save_store(store)


def get_watchlist() -> list:
    return _load_store()["watchlist"]


def add_holding(ticker: str, quantity: float, purchase_price: float):
    store = _load_store()
    store["portfolio"].append(
        {"ticker": ticker, "quantity": quantity, "purchase_price": purchase_price}
    )
    _save_store(store)


def get_portfolio() -> list:
    return _load_store()["portfolio"]


def clear_portfolio():
    store = _load_store()
    store["portfolio"] = []
    _save_store(store)
