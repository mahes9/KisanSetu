"""Evening screener — runs the full 6-layer funnel on live data.

Output: regime banner, then ranked candidates with entry/stop/target/qty,
layer scorecard, and (for F&O names) futures-OI + option-chain reads and an
instrument suggestion. Appends candidates to journal/candidates_<date>.csv.
"""

from __future__ import annotations

import datetime as dt
import logging

import pandas as pd

from . import (
    config,
    data,
    delivery,
    flows,
    fundamentals,
    options_flow,
    regime as regime_mod,
    rules,
    sector,
    sizing,
    structure,
    universe,
)
from .nse import NseSession

log = logging.getLogger(__name__)


def _close_panel(tickers: dict[str, str]) -> pd.DataFrame:
    """dates × symbols close panel from the local cache. {symbol: yahoo}."""
    cols = {}
    for sym, yh in tickers.items():
        df = data.load_cached(yh)
        if not df.empty:
            cols[sym] = df["Close"]
    return pd.DataFrame(cols).sort_index().ffill(limit=3)


def run(refresh_fundamentals: bool = False, delivery_days: int = 45) -> dict:
    cfg = config.load()
    capital = float(cfg["capital"])
    stocks = universe.stocks()
    by_symbol = {s.symbol: s for s in stocks}

    log.info("building focus list…")
    focus = fundamentals.build_focus_list(stocks, refresh=refresh_fundamentals)
    if not focus:
        raise RuntimeError("Focus list is empty — run with --refresh-fundamentals first.")

    log.info("loading prices…")
    need = [by_symbol[s].yahoo for s in focus if s in by_symbol]
    frames = data.fetch_many(need + [data.NIFTY50, data.INDIA_VIX])
    nifty_df = frames[data.NIFTY50]
    nifty = structure.StockFrame(nifty_df, span=cfg["structure"]["pivot_span_daily"])
    vix_df = frames.get(data.INDIA_VIX, pd.DataFrame())
    vix = float(vix_df["Close"].iloc[-1]) if not vix_df.empty else None

    # per-symbol frames aligned to the Nifty calendar
    sframes: dict[str, structure.StockFrame] = {}
    wframes: dict[str, structure.StockFrame] = {}
    bench: dict[str, pd.Series] = {}
    for sym in focus:
        st = by_symbol.get(sym)
        if st is None:
            continue
        df = frames.get(st.yahoo, pd.DataFrame())
        if df.empty or len(df) < 120:
            continue
        aligned_n = nifty_df["Close"].reindex(df.index).ffill()
        sframes[sym] = structure.StockFrame(df, span=cfg["structure"]["pivot_span_daily"])
        wframes[sym] = structure.StockFrame(data.weekly(df), span=cfg["structure"]["pivot_span_weekly"])
        bench[sym] = aligned_n

    # regime
    up = sum(
        1 for sf in sframes.values()
        if structure.trend_state(sf.pivots, len(sf) - 1)[0] == "UP"
    )
    breadth = up / len(sframes) * 100.0 if sframes else None

    ns = NseSession()
    fii = flows.fii_dii(ns)
    fii_bias = "short" if fii and fii.get("fii", 0) < -2000 else None
    reg = regime_mod.classify(nifty, len(nifty) - 1, breadth, vix, fii_bias, cfg)

    # live layers
    veto_set, veto_reasons = flows.veto_symbols(ns)
    log.info("updating delivery cache…")
    dview = delivery.DeliveryView(delivery.update(days=delivery_days))
    fno = options_flow.FnOView()
    deals = flows.bulk_deals(ns) or []
    deal_syms = {d["symbol"] for d in deals if d.get("side", "").startswith("B")}

    # full-universe close panel for sector RS (uses whatever is cached)
    panel = _close_panel({s.symbol: s.yahoo for s in stocks})
    nifty_aligned = nifty_df["Close"].reindex(panel.index).ffill()
    asof = panel.index[-1]
    rs_table = sector.industry_rs_table(
        panel, nifty_aligned, {s.symbol: s.sector for s in stocks}, asof
    )
    top = sector.top_industries(rs_table, cfg["filters"]["top_sectors"])

    candidates = []
    for sym, sf in sframes.items():
        st = by_symbol[sym]
        i = len(sf) - 1
        wi = len(wframes[sym]) - 1
        if not rules.liquidity_ok(sf, i, cfg):
            continue
        allowed = {"S1", "S2", "S3", "S4"} - set(cfg.get("entries", {}).get("disabled_setups", []))
        got = rules.structural_candidate(
            sf, wframes[sym], i, wi, bench[sym].to_numpy(float), cfg,
            allowed_setups=allowed,
        )
        if got is None:
            continue
        sig, card = got
        if not reg.allows(sig.setup):
            card.add("regime", f"{reg.state} blocks {sig.setup}")
            continue
        if cfg.get("entries", {}).get("s4_require_uptrend") and sig.setup == "S4" \
                and structure.trend_state(sf.pivots, i)[0] != "UP":
            continue
        # sector gate
        if st.sector in top:
            card.add("sector", f"top4 ({st.sector})")
        else:
            continue
        # hard live vetoes
        if sym in veto_set:
            card.veto(f"surveillance: {veto_reasons.get(sym)}")
        fut = fno.futures(sym) if st.in_fo else None
        if fut and fut.buildup == "short_buildup":
            card.veto("futures short buildup")
        if card.hard_fail():
            continue
        # soft layers
        grade = focus[sym].get("grade", "C")
        dstat = dview.stats(sym) if dview.available() else None
        if dstat:
            card.add(
                "delivery",
                f"{dstat['deliv_pct']:.0f}% vs {dstat['deliv_20d_avg']:.0f}% avg"
                + (" ✓" if dstat["high_delivery"] else " ✗"),
            )
            if dstat["churn"]:
                grade = "C"
                card.add("note", "churn delivery — downgraded")
        if fut:
            card.add("futures_OI", fut.buildup or "n/a")
        opt = fno.options(sym, sf.c[i], iv_session=None) if st.in_fo else None
        if opt:
            card.add("options", opt.summary())
        if sym in deal_syms:
            card.add("bulk_deal", "institutional buy today ✓")

        sized = sizing.size_trade(
            sig.entry, sig.stop, sig.setup, grade, reg.state, capital, cfg,
            lot_size=st.lot_size,
        )
        if sized.qty <= 0:
            card.add("sizing", sized.skip_reason)
            continue
        r_mult = cfg["exits"]["s2_scale_r"] if sig.setup == "S2" else cfg["exits"]["s1_scale_r"]
        target = rules.first_target(sig, opt.call_wall if opt else None, r_mult)
        instrument = "cash"
        if sized.futures_ok and fut and fut.confirms_long():
            instrument = f"futures 1 lot ({st.lot_size}) or cash"
        elif st.in_fo and grade in ("A", "B") and sig.setup in ("S1", "S4"):
            instrument = f"cash or {options_flow.suggest_spread(sf.c[i], target, opt)}"
        candidates.append(
            {
                "symbol": sym,
                "setup": sig.setup,
                "grade": grade,
                "sector": st.sector,
                "entry": round(sig.entry, 2),
                "stop": round(sig.stop, 2),
                "stop_%": round(sig.stop_pct, 1),
                "target1": round(target, 2),
                "qty": sized.qty,
                "risk_₹": int(sized.risk_amount),
                "notional_₹": int(sized.notional),
                "instrument": instrument,
                "note": sig.note,
                "scorecard": card.summary(),
            }
        )

    candidates.sort(key=lambda c: ({"A": 0, "B": 1, "C": 2}[c["grade"]], c["stop_%"]))

    # portfolio caps on today's picks (positions already open are the user's
    # ledger — the playbook's heat rules apply on top)
    caps = sizing.PortfolioCaps(capital, cfg)
    admitted = []
    for c in candidates:
        why = caps.reject_reason(c["sector"], c["risk_₹"])
        if why:
            c["note"] = f"{c['note']} [not sized: {why}]"
        else:
            caps.admit(c["sector"], c["risk_₹"])
            admitted.append(c)

    return {
        "asof": str(asof.date()),
        "regime": reg,
        "fii": fii,
        "vix": vix,
        "breadth": breadth,
        "top_sectors": rs_table.head(cfg["filters"]["top_sectors"]).to_dict("records"),
        "sector_table": rs_table,
        "focus_count": len(focus),
        "scanned": len(sframes),
        "candidates": admitted,
        "all_candidates": candidates,
        "fno_date": fno.date,
        "delivery_available": dview.available(),
    }


def render(result: dict) -> str:
    reg = result["regime"]
    lines = []
    lines.append("=" * 78)
    lines.append(f"  NIFTY 200 SWING SCREENER — {result['asof']}")
    lines.append("=" * 78)
    fii = result.get("fii") or {}
    lines.append(
        f"REGIME: {reg.state}  (nifty {reg.nifty_trend}, breadth "
        f"{reg.breadth_pct:.0f}%, VIX {reg.vix:.1f})"
        if reg.breadth_pct is not None and reg.vix is not None
        else f"REGIME: {reg.state}"
    )
    if reg.notes:
        lines.append(f"  notes: {reg.notes}")
    if fii:
        lines.append(f"  FII cash: ₹{fii.get('fii', 0):,.0f} cr | DII: ₹{fii.get('dii', 0):,.0f} cr")
    lines.append(
        f"  focus list: {result['focus_count']} | scanned: {result['scanned']}"
        f" | F&O data: {result['fno_date']} | delivery: "
        + ("ok" if result["delivery_available"] else "n/a")
    )
    lines.append(f"  top sectors: " + ", ".join(
        f"{r['industry']} ({r['rs']:+.1f})" for r in result["top_sectors"]))
    lines.append("-" * 78)
    cands = result["candidates"]
    if not cands:
        lines.append(
            "  No qualifying setups today."
            + ("  (RED regime — no new longs.)" if reg.state == "RED" else
               "  The correct trade is no trade.")
        )
    for c in cands:
        lines.append(
            f"  {c['symbol']:<12} {c['setup']} {c['grade']}  entry {c['entry']:>9}  "
            f"stop {c['stop']:>9} ({c['stop_%']}%)  T1 {c['target1']:>9}  qty {c['qty']}"
        )
        lines.append(f"      {c['instrument']}  | risk ₹{c['risk_₹']:,} | {c['note']}")
        lines.append(f"      {c['scorecard']}")
    lines.append("=" * 78)
    return "\n".join(lines)


def save_journal(result: dict) -> str | None:
    cands = result["all_candidates"]
    if not cands:
        return None
    jdir = config.PROJECT_ROOT / "journal"
    jdir.mkdir(exist_ok=True)
    day = result["asof"].replace("-", "")
    path = jdir / f"candidates_{day}.csv"
    df = pd.DataFrame(cands)
    df.insert(0, "date", result["asof"])
    df.insert(2, "regime", result["regime"].state)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)
