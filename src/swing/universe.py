"""Nifty 200 constituents (with sector mapping) and F&O lot sizes.

Primary source: NSE archives CSVs. Everything is cached locally so the system
keeps working when NSE throttles. If neither the live fetch nor a cache is
available we fail loudly — trading on a wrong universe is worse than stopping.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass

import pandas as pd
import requests

from . import config

log = logging.getLogger(__name__)

NIFTY200_URL = "https://archives.nseindia.com/content/indices/ind_nifty200list.csv"
FO_LOTS_URL = "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/csv,application/csv,*/*",
    "Referer": "https://www.nseindia.com/",
}


@dataclass(frozen=True)
class Stock:
    symbol: str          # NSE symbol, e.g. "RELIANCE"
    name: str
    sector: str          # NSE "Industry" field
    in_fo: bool = False
    lot_size: int = 0

    @property
    def yahoo(self) -> str:
        return f"{self.symbol}.NS"


def _fetch_csv(url: str) -> pd.DataFrame | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return pd.read_csv(io.StringIO(r.text), on_bad_lines="skip", skipinitialspace=True)
    except Exception as e:  # noqa: BLE001 — any network/parse failure → cache fallback
        log.warning("fetch failed for %s: %s", url, e)
        return None


def nifty200(refresh: bool = False) -> pd.DataFrame:
    """Return DataFrame with columns: symbol, name, sector."""
    cache = config.cache_dir() / "nifty200.csv"
    df = None
    if refresh or not cache.exists():
        raw = _fetch_csv(NIFTY200_URL)
        if raw is not None and "Symbol" in raw.columns:
            df = pd.DataFrame(
                {
                    "symbol": raw["Symbol"].str.strip(),
                    "name": raw["Company Name"].str.strip(),
                    "sector": raw["Industry"].str.strip(),
                }
            )
            # NSE inserts DUMMY* placeholder rows for pending corporate actions
            df = df[~df["symbol"].str.upper().str.startswith("DUMMY")].reset_index(drop=True)
            df.to_csv(cache, index=False)
            log.info("nifty200 list refreshed: %d names", len(df))
    if df is None:
        if not cache.exists():
            raise RuntimeError(
                "Could not fetch the Nifty 200 list from NSE and no local cache exists "
                f"({cache}). Check connectivity and retry."
            )
        df = pd.read_csv(cache)
    return df


def fo_lot_sizes(refresh: bool = False) -> dict[str, int]:
    """Symbol -> current-month lot size for F&O stocks. Empty dict if unavailable
    (derivative features then degrade gracefully)."""
    cache = config.cache_dir() / "fo_lots.csv"
    df = None
    if refresh or not cache.exists():
        raw = _fetch_csv(FO_LOTS_URL)
        if raw is not None and raw.shape[1] >= 3:
            raw.columns = [c.strip() for c in raw.columns]
            sym_col = next((c for c in raw.columns if c.upper() == "SYMBOL"), raw.columns[1])
            lot_col = raw.columns[2]  # nearest-month column
            df = pd.DataFrame(
                {
                    "symbol": raw[sym_col].astype(str).str.strip(),
                    "lot": pd.to_numeric(raw[lot_col], errors="coerce"),
                }
            ).dropna()
            df = df[df["symbol"].str.upper() != "SYMBOL"]
            df.to_csv(cache, index=False)
    if df is None and cache.exists():
        df = pd.read_csv(cache)
    if df is None:
        log.warning("F&O lot sizes unavailable — futures/options suggestions disabled")
        return {}
    return {r.symbol: int(r.lot) for r in df.itertuples() if r.lot and r.lot > 0}


def stocks(refresh: bool = False) -> list[Stock]:
    uni = nifty200(refresh=refresh)
    lots = fo_lot_sizes(refresh=refresh)
    return [
        Stock(
            symbol=r.symbol,
            name=r.name,
            sector=r.sector,
            in_fo=r.symbol in lots,
            lot_size=lots.get(r.symbol, 0),
        )
        for r in uni.itertuples()
    ]
