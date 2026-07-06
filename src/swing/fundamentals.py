"""Layer 1 — fundamental engine: quant screen → Focus List with grades.

Quant metrics come from yfinance (`Ticker.info` + quarterly statements where
available). The 10-point conviction checklist is inherently manual — scores
live in ``conviction.yaml`` at the project root::

    RELIANCE: 7
    TATAMOTORS: 5

Grades (playbook §1.4):
  A = quant pass + conviction >= 7
  B = quant pass + conviction 4–6
  C = quant pass + conviction < 4 or unscored
Results are cached to data/fundamentals.json (refresh quarterly).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass

import yaml
import yfinance as yf

from . import config
from .universe import Stock

log = logging.getLogger(__name__)

FINANCIAL_SECTORS = {"Financial Services"}


@dataclass
class Fundamentals:
    symbol: str
    revenue_growth: float | None = None   # % quarterly YoY
    pat_growth: float | None = None       # % quarterly YoY
    roe: float | None = None              # %
    de: float | None = None               # ratio
    ocf_positive: bool | None = None
    accelerating: bool | None = None
    passed: bool = False
    reasons: str = ""


def _pct(x) -> float | None:
    try:
        return None if x is None else float(x) * 100.0
    except (TypeError, ValueError):
        return None


def fetch_one(stock: Stock) -> Fundamentals:
    f = Fundamentals(symbol=stock.symbol)
    try:
        t = yf.Ticker(stock.yahoo)
        info = t.info or {}
    except Exception as e:  # noqa: BLE001
        f.reasons = f"fetch failed: {e}"
        return f
    f.revenue_growth = _pct(info.get("revenueGrowth"))
    f.pat_growth = _pct(info.get("earningsQuarterlyGrowth"))
    f.roe = _pct(info.get("returnOnEquity"))
    de = info.get("debtToEquity")
    f.de = float(de) / 100.0 if de is not None else None
    ocf = info.get("operatingCashflow")
    f.ocf_positive = (ocf > 0) if isinstance(ocf, (int, float)) else None
    # earnings acceleration: latest quarterly YoY PAT growth vs the one before
    try:
        q = t.quarterly_income_stmt
        ni = q.loc["Net Income"].dropna() if q is not None and "Net Income" in q.index else None
        if ni is not None and len(ni) >= 6:
            ni = ni.sort_index()
            g_now = ni.iloc[-1] / abs(ni.iloc[-5]) - 1.0
            g_prev = ni.iloc[-2] / abs(ni.iloc[-6]) - 1.0
            f.accelerating = bool(g_now > g_prev)
    except Exception:  # noqa: BLE001 — statements often missing; acceleration stays None
        pass
    return f


def evaluate(f: Fundamentals, sector: str, cfg: dict) -> Fundamentals:
    th = cfg["filters"]["fundamentals"]
    fails: list[str] = []
    is_fin = sector in FINANCIAL_SECTORS

    def chk(name: str, value, minimum=None, maximum=None) -> None:
        if value is None:
            return  # missing data is neutral, not a fail (Yahoo NSE coverage varies)
        if minimum is not None and value < minimum:
            fails.append(f"{name} {value:.1f} < {minimum}")
        if maximum is not None and value > maximum:
            fails.append(f"{name} {value:.1f} > {maximum}")

    chk("revenue_growth", f.revenue_growth, minimum=th["revenue_growth_min"])
    chk("pat_growth", f.pat_growth, minimum=th["pat_growth_min"])
    chk("roe", f.roe, minimum=th["roe_min"])
    if not is_fin:
        chk("de", f.de, maximum=th["de_max"])
    if f.ocf_positive is False and not is_fin:
        fails.append("negative operating cash flow")
    # must have at least growth evidence to make the focus list
    if f.pat_growth is None and f.revenue_growth is None:
        fails.append("no growth data")
    f.passed = not fails
    f.reasons = "; ".join(fails)
    return f


def conviction_scores() -> dict[str, int]:
    p = config.PROJECT_ROOT / "conviction.yaml"
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return {str(k).upper(): int(v) for k, v in raw.items()}


def grade(symbol: str, passed: bool, scores: dict[str, int]) -> str | None:
    if not passed:
        return None
    s = scores.get(symbol.upper())
    if s is None or s < 4:
        return "C"
    return "A" if s >= 7 else "B"


def build_focus_list(stocks: list[Stock], refresh: bool = False) -> dict[str, dict]:
    """{symbol: {fundamentals…, grade}} for stocks passing the quant screen."""
    cfg = config.load()
    cache = config.cache_dir() / "fundamentals.json"
    rows: dict[str, dict] = {}
    if not refresh and cache.exists():
        rows = json.loads(cache.read_text(encoding="utf-8"))
    else:
        sectors = {s.symbol: s.sector for s in stocks}
        for k, s in enumerate(stocks):
            f = evaluate(fetch_one(s), sectors[s.symbol], cfg)
            rows[s.symbol] = asdict(f)
            if (k + 1) % 25 == 0:
                log.info("fundamentals %d/%d", k + 1, len(stocks))
            time.sleep(0.15)  # be polite to yahoo
        cache.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    scores = conviction_scores()
    out: dict[str, dict] = {}
    for sym, row in rows.items():
        g = grade(sym, row.get("passed", False), scores)
        if g:
            row["grade"] = g
            out[sym] = row
    return out
