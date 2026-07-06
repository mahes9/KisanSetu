"""Layer 5 — derivatives flow read: futures OI + option positioning.

Primary source: the daily NSE F&O bhavcopy (UDiFF format) — one cookie-free
zip per trading day carrying futures OI/OI-change and every option strike's
OI. From it we compute, per symbol:

* futures buildup (long_buildup / short_covering / short_buildup / …),
* PCR(OI), put-OI wall below spot, call-OI wall above spot, max pain.

IV is not in the bhavcopy; the web option-chain API is tried once as optional
enrichment and silently skipped if NSE blocks it.
"""

from __future__ import annotations

import datetime as dt
import io
import logging
import zipfile
from dataclasses import dataclass

import pandas as pd
import requests

from . import config
from .nse import HEADERS, NseSession

log = logging.getLogger(__name__)

BHAV_URL = (
    "https://nsearchives.nseindia.com/content/fo/"
    "BhavCopy_NSE_FO_0_0_0_{d}_F_0000.csv.zip"
)


@dataclass
class OptionRead:
    pcr: float | None = None
    put_wall: float | None = None
    call_wall: float | None = None
    atm_iv: float | None = None
    max_pain: float | None = None
    expiry: str | None = None

    def summary(self) -> str:
        bits = []
        if self.pcr is not None:
            bits.append(f"PCR {self.pcr:.2f}")
        if self.put_wall:
            bits.append(f"put-wall {self.put_wall:g}")
        if self.call_wall:
            bits.append(f"call-wall {self.call_wall:g}")
        if self.atm_iv:
            bits.append(f"IV {self.atm_iv:.0f}%")
        return ", ".join(bits) if bits else "n/a"


@dataclass
class FuturesRead:
    buildup: str | None = None
    oi: float | None = None
    oi_chg_pct: float | None = None
    px_chg_pct: float | None = None

    def confirms_long(self) -> bool | None:
        if self.buildup is None:
            return None
        return self.buildup == "long_buildup"


def _bhav_dir():
    d = config.cache_dir() / "fo"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_bhavcopy(day: dt.date) -> pd.DataFrame | None:
    """Download + cache one day's F&O bhavcopy (None on holidays/weekends)."""
    p = _bhav_dir() / f"{day:%Y%m%d}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    try:
        r = requests.get(BHAV_URL.format(d=f"{day:%Y%m%d}"), headers=HEADERS, timeout=40)
        if r.status_code != 200:
            return None
        z = zipfile.ZipFile(io.BytesIO(r.content))
        df = pd.read_csv(z.open(z.namelist()[0]), low_memory=False)
    except Exception as e:  # noqa: BLE001
        log.debug("bhavcopy %s failed: %s", day, e)
        return None
    keep = df[df["FinInstrmTp"].isin(["STF", "STO", "IDF", "IDO"])][
        ["TradDt", "FinInstrmTp", "TckrSymb", "XpryDt", "StrkPric", "OptnTp",
         "ClsPric", "PrvsClsgPric", "UndrlygPric", "OpnIntrst", "ChngInOpnIntrst",
         "TtlTradgVol"]
    ].copy()
    keep.to_parquet(p, index=False)
    return keep


def latest_bhavcopy(max_back: int = 7) -> tuple[pd.DataFrame, dt.date] | None:
    day = dt.date.today()
    for _ in range(max_back):
        if day.weekday() < 5:
            df = fetch_bhavcopy(day)
            if df is not None and not df.empty:
                return df, day
        day -= dt.timedelta(days=1)
    return None


class FnOView:
    """Per-symbol derivative reads from the latest bhavcopy."""

    def __init__(self) -> None:
        got = latest_bhavcopy()
        self.df: pd.DataFrame | None = got[0] if got else None
        self.date: dt.date | None = got[1] if got else None
        self._ns: NseSession | None = None
        if self.df is not None:
            self.df["XpryDt"] = pd.to_datetime(self.df["XpryDt"])

    def available(self) -> bool:
        return self.df is not None

    def futures(self, symbol: str) -> FuturesRead | None:
        if self.df is None:
            return None
        rows = self.df[(self.df.TckrSymb == symbol) & (self.df.FinInstrmTp == "STF")]
        if rows.empty:
            return None
        near = rows.sort_values("XpryDt").iloc[0]
        oi = float(near.OpnIntrst or 0)
        oi_chg = float(near.ChngInOpnIntrst or 0)
        prev_close = float(near.PrvsClsgPric or 0)
        close = float(near.ClsPric or 0)
        if prev_close <= 0 or oi <= 0:
            return None
        px_chg = (close / prev_close - 1.0) * 100.0
        oi_prev = oi - oi_chg
        oi_chg_pct = (oi_chg / oi_prev * 100.0) if oi_prev > 0 else 0.0
        if px_chg >= 0 and oi_chg_pct > 0.5:
            buildup = "long_buildup"
        elif px_chg >= 0 and oi_chg_pct < -0.5:
            buildup = "short_covering"
        elif px_chg < 0 and oi_chg_pct > 0.5:
            buildup = "short_buildup"
        elif px_chg < 0 and oi_chg_pct < -0.5:
            buildup = "long_unwinding"
        else:
            buildup = "neutral"
        return FuturesRead(buildup, oi, oi_chg_pct, px_chg)

    def options(self, symbol: str, spot: float, iv_session: NseSession | None = None) -> OptionRead | None:
        if self.df is None:
            return None
        rows = self.df[(self.df.TckrSymb == symbol) & (self.df.FinInstrmTp == "STO")]
        if rows.empty:
            return None
        expiry = rows["XpryDt"].min()
        rows = rows[rows.XpryDt == expiry]
        calls = rows[rows.OptnTp == "CE"].set_index("StrkPric")["OpnIntrst"].astype(float)
        puts = rows[rows.OptnTp == "PE"].set_index("StrkPric")["OpnIntrst"].astype(float)
        calls, puts = calls[calls > 0], puts[puts > 0]
        if calls.empty and puts.empty:
            return None
        pcr = float(puts.sum() / calls.sum()) if calls.sum() > 0 else None
        below = puts[puts.index <= spot]
        above = calls[calls.index >= spot]
        put_wall = float(below.idxmax()) if not below.empty else None
        call_wall = float(above.idxmax()) if not above.empty else None
        import numpy as np

        strikes = sorted(set(calls.index) | set(puts.index))
        ck, cv = calls.index.to_numpy(float), calls.to_numpy(float)
        pk, pv = puts.index.to_numpy(float), puts.to_numpy(float)
        max_pain, best = None, None
        for s in strikes:
            cost = float((np.clip(s - ck, 0, None) * cv).sum()
                         + (np.clip(pk - s, 0, None) * pv).sum())
            if best is None or cost < best:
                best, max_pain = cost, float(s)
        read = OptionRead(pcr, put_wall, call_wall, None, max_pain,
                          expiry.date().isoformat())
        if iv_session is not None:
            read.atm_iv = _try_iv(iv_session, symbol, spot)
        return read


def _try_iv(ns: NseSession, symbol: str, spot: float) -> float | None:
    js = ns.get_json(f"/api/option-chain-equities?symbol={symbol}")
    if not isinstance(js, dict):
        return None
    rows = (js.get("records") or {}).get("data") or []
    best = None
    for r in rows:
        k = float(r.get("strikePrice", 0) or 0)
        iv = (r.get("CE") or {}).get("impliedVolatility")
        if iv:
            d = abs(k - spot)
            if best is None or d < best[0]:
                best = (d, float(iv))
    return best[1] if best else None


def suggest_spread(spot: float, target: float, read: OptionRead | None) -> str:
    lo = round(spot * 0.99, -1)
    hi = read.call_wall if read and read.call_wall and read.call_wall > spot else round(target, -1)
    iv_note = ""
    if read and read.atm_iv:
        iv_note = " — IV elevated, prefer credit structures" if read.atm_iv > 40 else ""
    return f"buy ~{lo:g} call / sell {hi:g} call, next-month expiry{iv_note}"
