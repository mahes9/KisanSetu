"""Sector rotation gate — industry relative strength from constituents.

Rather than depending on Yahoo's sectoral index tickers, industry RS is the
equal-weight average of member-stock RS vs the Nifty (blended 1M + 3M). This
is computable point-in-time, so the same gate runs in backtest and live.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

LOOK_1M, LOOK_3M = 21, 63


def industry_rs_table(
    closes: pd.DataFrame, nifty: pd.Series, sectors: dict[str, str], asof: pd.Timestamp
) -> pd.DataFrame:
    """RS by industry as of a date.

    closes: dates × symbols close panel; nifty: aligned close series;
    sectors: symbol -> industry. Returns DataFrame(industry, rs) sorted desc."""
    idx = closes.index
    pos = idx.searchsorted(asof, side="right") - 1
    if pos < LOOK_3M:
        return pd.DataFrame(columns=["industry", "rs"])
    rows = []
    n_now, n_1m, n_3m = nifty.iloc[pos], nifty.iloc[pos - LOOK_1M], nifty.iloc[pos - LOOK_3M]
    c_now = closes.iloc[pos]
    c_1m = closes.iloc[pos - LOOK_1M]
    c_3m = closes.iloc[pos - LOOK_3M]
    rs_1m = (c_now / c_1m - n_now / n_1m) * 100
    rs_3m = (c_now / c_3m - n_now / n_3m) * 100
    blended = (rs_1m + rs_3m) / 2
    sec = pd.Series({s: sectors.get(s, "Other") for s in closes.columns})
    df = pd.DataFrame({"rs": blended, "industry": sec}).dropna()
    out = df.groupby("industry")["rs"].mean().sort_values(ascending=False).reset_index()
    return out


def top_industries(rs_table: pd.DataFrame, n: int) -> set[str]:
    return set(rs_table.head(n)["industry"]) if not rs_table.empty else set()


def stock_rs_rank(closes: pd.DataFrame, nifty: pd.Series, asof: pd.Timestamp) -> pd.Series:
    """Percentile rank (0-100) of each stock's blended RS as of a date."""
    idx = closes.index
    pos = idx.searchsorted(asof, side="right") - 1
    if pos < LOOK_3M:
        return pd.Series(dtype=float)
    n_now, n_1m, n_3m = nifty.iloc[pos], nifty.iloc[pos - LOOK_1M], nifty.iloc[pos - LOOK_3M]
    rs = (
        (closes.iloc[pos] / closes.iloc[pos - LOOK_1M] - n_now / n_1m)
        + (closes.iloc[pos] / closes.iloc[pos - LOOK_3M] - n_now / n_3m)
    ) / 2
    return rs.rank(pct=True) * 100
