"""Layer 4 — NSE delivery-percentage data (the accumulation truth serum).

Source: NSE full bhavdata CSV per trading day
(`sec_bhavdata_full_DDMMYYYY.csv`). We keep a rolling local cache (default 90
calendar days) — enough for 20-day delivery baselines in the live screener.
Deep history isn't fetched (thousands of files); the backtest uses volume
signatures instead and says so.
"""

from __future__ import annotations

import datetime as dt
import io
import logging
import time

import pandas as pd
import requests

from . import config

log = logging.getLogger(__name__)

URL = "https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{d}.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://www.nseindia.com/",
}


def _cache_path():
    return config.cache_dir() / "delivery.parquet"


def fetch_day(day: dt.date) -> pd.DataFrame | None:
    url = URL.format(d=day.strftime("%d%m%Y"))
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200 or "SYMBOL" not in r.text[:200]:
            return None
        df = pd.read_csv(io.StringIO(r.text), skipinitialspace=True)
        df.columns = [c.strip() for c in df.columns]
        df = df[df["SERIES"].str.strip() == "EQ"]
        out = pd.DataFrame(
            {
                "date": pd.Timestamp(day),
                "symbol": df["SYMBOL"].str.strip(),
                "deliv_qty": pd.to_numeric(df["DELIV_QTY"], errors="coerce"),
                "deliv_pct": pd.to_numeric(df["DELIV_PER"], errors="coerce"),
            }
        ).dropna(subset=["deliv_pct"])
        return out
    except Exception as e:  # noqa: BLE001
        log.debug("delivery fetch failed for %s: %s", day, e)
        return None


def load_cache() -> pd.DataFrame:
    p = _cache_path()
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame(columns=["date", "symbol", "deliv_qty", "deliv_pct"])


def update(days: int = 90) -> pd.DataFrame:
    """Fill the rolling cache up to today. Skips weekends/holidays (404s)."""
    cache = load_cache()
    have = set(pd.to_datetime(cache["date"]).dt.date) if not cache.empty else set()
    today = dt.date.today()
    new: list[pd.DataFrame] = []
    fetched = 0
    for off in range(days, -1, -1):
        day = today - dt.timedelta(days=off)
        if day.weekday() >= 5 or day in have:
            continue
        df = fetch_day(day)
        if df is not None and not df.empty:
            new.append(df)
            fetched += 1
            time.sleep(0.35)
    if new:
        cache = pd.concat([cache] + new, ignore_index=True)
        cutoff = pd.Timestamp(today - dt.timedelta(days=days + 30))
        cache = cache[pd.to_datetime(cache["date"]) >= cutoff]
        cache.to_parquet(_cache_path(), index=False)
        log.info("delivery cache: +%d days, %d rows", fetched, len(cache))
    return cache


class DeliveryView:
    """Per-symbol delivery stats from the cache."""

    def __init__(self, cache: pd.DataFrame | None = None):
        c = cache if cache is not None else load_cache()
        self.by_symbol: dict[str, pd.DataFrame] = (
            {s: g.sort_values("date") for s, g in c.groupby("symbol")} if not c.empty else {}
        )

    def available(self) -> bool:
        return bool(self.by_symbol)

    def stats(self, symbol: str) -> dict | None:
        """Latest delivery % vs the symbol's 20-session average."""
        g = self.by_symbol.get(symbol)
        if g is None or len(g) < 5:
            return None
        last = g.iloc[-1]
        base = g["deliv_pct"].tail(21).head(20).mean()
        return {
            "deliv_pct": float(last["deliv_pct"]),
            "deliv_20d_avg": float(base),
            "high_delivery": bool(last["deliv_pct"] > base),
            "churn": bool(last["deliv_pct"] < 25.0),
            "date": pd.Timestamp(last["date"]).date().isoformat(),
        }
