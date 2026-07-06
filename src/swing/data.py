"""EOD OHLCV data via yfinance with a local parquet cache.

All symbols are NSE (`.NS` suffix). Indices use Yahoo's caret tickers. The
cache is incremental: re-running only fetches bars after the last cached date.
"""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

from . import config

log = logging.getLogger(__name__)

NIFTY50 = "^NSEI"
INDIA_VIX = "^INDIAVIX"

# Yahoo tickers for NSE sectoral indices. Some occasionally go dark on Yahoo;
# fetch skips failures and sector ranking works with whatever loads.
SECTOR_INDICES = {
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Auto": "^CNXAUTO",
    "Nifty FMCG": "^CNXFMCG",
    "Nifty Metal": "^CNXMETAL",
    "Nifty Energy": "^CNXENERGY",
    "Nifty Realty": "^CNXREALTY",
    "Nifty Infra": "^CNXINFRA",
    "Nifty PSU Bank": "^CNXPSUBANK",
    "Nifty Media": "^CNXMEDIA",
    "Nifty Fin Service": "NIFTY_FIN_SERVICE.NS",
}

OHLCV_COLS = ["Open", "High", "Low", "Close", "Volume"]


def _ohlcv_dir() -> Path:
    d = config.cache_dir() / "ohlcv"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cache_path(ticker: str) -> Path:
    safe = ticker.replace("^", "_idx_").replace(".", "_")
    return _ohlcv_dir() / f"{safe}.parquet"


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=OHLCV_COLS)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[[c for c in OHLCV_COLS if c in df.columns]].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=["Close"])
    return df


def load_cached(ticker: str) -> pd.DataFrame:
    p = _cache_path(ticker)
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame(columns=OHLCV_COLS)


def fetch(ticker: str, lookback_days: int | None = None) -> pd.DataFrame:
    """Return cached + freshly-fetched daily bars for one ticker."""
    lookback = lookback_days or config.load()["data"]["ohlcv_lookback_days"]
    cached = load_cached(ticker)
    today = pd.Timestamp(dt.date.today())
    if not cached.empty and cached.index[-1] >= today - pd.Timedelta(days=1):
        return cached
    start = (
        cached.index[-1] + pd.Timedelta(days=1)
        if not cached.empty
        else today - pd.Timedelta(days=lookback)
    )
    try:
        fresh = yf.download(
            ticker, start=start.date(), auto_adjust=True, progress=False, threads=False
        )
        fresh = _clean(fresh)
    except Exception as e:  # noqa: BLE001
        log.warning("yfinance fetch failed for %s: %s", ticker, e)
        fresh = pd.DataFrame(columns=OHLCV_COLS)
    if not fresh.empty:
        merged = _clean(pd.concat([cached, fresh]))
        merged.to_parquet(_cache_path(ticker))
        return merged
    return cached


def fetch_many(tickers: list[str], lookback_days: int | None = None) -> dict[str, pd.DataFrame]:
    """Batch-download missing history for many tickers, then serve from cache.

    Tickers already fresh in cache are skipped. Returns {ticker: df} with empty
    frames for symbols Yahoo couldn't serve (caller filters)."""
    lookback = lookback_days or config.load()["data"]["ohlcv_lookback_days"]
    today = pd.Timestamp(dt.date.today())
    stale: list[str] = []
    out: dict[str, pd.DataFrame] = {}
    for t in tickers:
        c = load_cached(t)
        if not c.empty and c.index[-1] >= today - pd.Timedelta(days=1):
            out[t] = c
        else:
            stale.append(t)

    if stale:
        start = (today - pd.Timedelta(days=lookback)).date()
        log.info("downloading %d tickers from yahoo…", len(stale))
        try:
            raw = yf.download(
                stale, start=start, auto_adjust=True, progress=False,
                group_by="ticker", threads=True,
            )
        except Exception as e:  # noqa: BLE001
            log.warning("batch download failed: %s", e)
            raw = None
        for t in stale:
            cached = load_cached(t)
            fresh = pd.DataFrame(columns=OHLCV_COLS)
            if raw is not None and not raw.empty:
                try:
                    sub = raw[t] if isinstance(raw.columns, pd.MultiIndex) else raw
                    fresh = _clean(sub)
                except KeyError:
                    pass
            if not fresh.empty:
                merged = _clean(pd.concat([cached, fresh]))
                merged.to_parquet(_cache_path(t))
                out[t] = merged
            else:
                out[t] = cached
                if cached.empty:
                    log.warning("no data for %s", t)
    return out


def weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Resample daily bars to weekly (W-FRI)."""
    if df.empty:
        return df
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
    return df.resample("W-FRI").agg(agg).dropna(subset=["Close"])
