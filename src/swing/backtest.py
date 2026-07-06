"""Portfolio-level backtest of the structural core (S1–S3 + gates).

What it tests: market-structure setups, weekly alignment, overhead supply,
relative strength, sector rotation, regime gating, risk sizing, structural
trailing — the layers computable point-in-time.

What it cannot test (free data doesn't exist): fundamentals as they stood on
each date, option-chain OI, delivery %, FII flows. Those are live confirmation
filters. S4 runs on its volume-surge signature (the proxy for results days).

Mechanics:
* signals are computed on bar t's close; entry is bar t+1's open (+slippage);
  if t+1 opens below the stop, the entry is skipped;
* stops are hit intraday at the stop price (gap-downs fill at the open);
* 50% scales out intraday at the first target; stop then moves to breakeven;
* stop trails below each new confirmed higher-low; time stops per playbook;
* costs: round-trip pct + per-side slippage from config.

Survivorship caveat: universe = current Nifty 200 constituents.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config, data, rules, sector, sizing, structure, universe
from . import regime as regime_mod
from .structure import StockFrame

log = logging.getLogger(__name__)

WARMUP_BARS = 260


@dataclass
class Position:
    symbol: str
    setup: str
    sector: str
    entry_date: pd.Timestamp
    entry: float          # cost-adjusted entry price (costs applied once here)
    stop: float
    init_stop: float
    qty: int
    init_qty: int
    target1: float
    scaled: bool = False
    realized: float = 0.0
    bars_held: int = 0
    grade: str = "C"
    adds: int = 0
    last_add_hl: float = 0.0

    @property
    def risk_per_share(self) -> float:
        return self.entry - self.init_stop


@dataclass
class Trade:
    symbol: str
    setup: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry: float
    exit_avg: float
    qty: int
    pnl: float
    r_result: float
    bars_held: int
    exit_reason: str
    regime_at_entry: str


@dataclass
class SymbolCtx:
    sf: StockFrame
    wf: StockFrame
    pos_map: np.ndarray          # master-calendar position -> symbol bar index (-1 = absent)
    bench: np.ndarray            # nifty close aligned to symbol bars
    trend: np.ndarray            # per-bar trend state
    turnover_ok: np.ndarray      # per-bar liquidity flag
    week_end_dates: np.ndarray   # week-end timestamps for the weekly frame
    stock: universe.Stock


def _cost_side(cfg: dict) -> float:
    b = cfg["backtest"]
    return (b["cost_roundtrip_pct"] / 2 + b["slippage_per_side_pct"]) / 100.0


def _build_ctx(stk: universe.Stock, df: pd.DataFrame, master: pd.DatetimeIndex,
               nifty_close: pd.Series, cfg: dict) -> SymbolCtx | None:
    if len(df) < WARMUP_BARS + 40:
        return None
    sf = StockFrame(df, span=cfg["structure"]["pivot_span_daily"])
    wdf = data.weekly(df)
    wf = StockFrame(wdf, span=cfg["structure"]["pivot_span_weekly"])
    # master-calendar alignment
    pos_map = np.full(len(master), -1, dtype=int)
    sym_pos = {d: k for k, d in enumerate(df.index)}
    for m, d in enumerate(master):
        k = sym_pos.get(d)
        if k is not None:
            pos_map[m] = k
    bench = nifty_close.reindex(df.index).ffill().to_numpy(float)
    trend = structure.trend_states(sf)
    to = pd.Series(sf.c * sf.v).rolling(20).mean().to_numpy() / 1e7
    turnover_ok = to >= cfg["filters"]["min_turnover_cr"]
    return SymbolCtx(sf, wf, pos_map, bench, trend, turnover_ok,
                     wdf.index.to_numpy(), stk)


def _deep_merge(base: dict, over: dict) -> dict:
    out = {k: (v.copy() if isinstance(v, dict) else v) for k, v in base.items()}
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def run(start: str | None = None, end: str | None = None,
        overrides: dict | None = None) -> dict:
    cfg = config.load()
    if overrides:
        cfg = _deep_merge(cfg, overrides)
    capital0 = float(cfg["capital"])
    en = cfg.get("entries", {})
    start = pd.Timestamp(start or cfg["backtest"]["start"])
    end = pd.Timestamp(end) if end else None
    cost = _cost_side(cfg)
    ex = cfg["exits"]

    stocks = universe.stocks()
    nifty_df = data.load_cached(data.NIFTY50)
    vix_df = data.load_cached(data.INDIA_VIX)
    if nifty_df.empty:
        raise RuntimeError("No cached Nifty data — run the screener once first.")
    if end is not None:
        nifty_df = nifty_df[nifty_df.index <= end]
    master = nifty_df.index
    nifty_close = nifty_df["Close"]
    nifty_sf = StockFrame(nifty_df, span=cfg["structure"]["pivot_span_daily"])
    vix = vix_df["Close"].reindex(master).ffill() if not vix_df.empty else None

    log.info("building symbol contexts…")
    ctxs: dict[str, SymbolCtx] = {}
    closes_panel: dict[str, pd.Series] = {}
    for stk in stocks:
        df = data.load_cached(stk.yahoo)
        if df.empty:
            continue
        if end is not None:
            df = df[df.index <= end]
        ctx = _build_ctx(stk, df, master, nifty_close, cfg)
        if ctx is not None:
            ctxs[stk.symbol] = ctx
            closes_panel[stk.symbol] = df["Close"]
    panel = pd.DataFrame(closes_panel).reindex(master).ffill(limit=3)
    sectors = {s.symbol: s.sector for s in stocks}
    log.info("symbols in test: %d", len(ctxs))

    start_m = max(int(master.searchsorted(start)), WARMUP_BARS)
    equity = capital0
    cash = capital0
    positions: dict[str, Position] = {}
    trades: list[Trade] = []
    curve: list[tuple[pd.Timestamp, float]] = []
    regime_log: list[str] = []

    sector_cache_day = -1
    top_sectors: set[str] = set()

    for m in range(start_m, len(master)):
        today = master[m]

        # ── regime as of yesterday's close (no lookahead into today) ──
        mb = m - 1
        active = [c for c in ctxs.values() if c.pos_map[mb] >= 0]
        if active:
            up = sum(1 for c in active if c.trend[c.pos_map[mb]] == "UP")
            breadth = up / len(active) * 100.0
        else:
            breadth = None
        vix_y = float(vix.iloc[mb]) if vix is not None and np.isfinite(vix.iloc[mb]) else None
        reg = regime_mod.classify(nifty_sf, mb, breadth, vix_y, None, cfg)
        regime_log.append(reg.state)

        # weekly sector RS refresh (computed on data through yesterday)
        if m - sector_cache_day >= 5:
            rs_table = sector.industry_rs_table(
                panel.iloc[: mb + 1], nifty_close.iloc[: mb + 1], sectors, master[mb]
            )
            top_sectors = sector.top_industries(rs_table, cfg["filters"]["top_sectors"])
            sector_cache_day = m

        # ── manage open positions on today's bar ──
        for sym in list(positions):
            ctx = ctxs[sym]
            i = ctx.pos_map[m]
            if i < 0:
                continue
            p = positions[sym]
            p.bars_held += 1
            sf = ctx.sf
            o, h, l, c = sf.o[i], sf.h[i], sf.l[i], sf.c[i]
            exit_px, reason = None, None

            trail_buf = 1 - ex["trail_buffer_pct"] / 100.0
            # stop (gap-down fills at open)
            if l <= p.stop:
                exit_px = min(p.stop, o) if o < p.stop else p.stop
                reason = "stop"
            else:
                # scale-out at target1 (scale_fraction = 0 → ride the full position)
                frac = ex["scale_fraction"]
                if frac > 0 and not p.scaled and h >= p.target1:
                    qsell = int(p.qty * frac)
                    if qsell > 0:
                        px = max(p.target1, o) * (1 - cost)
                        cash += qsell * px
                        p.realized += qsell * (px - p.entry)
                        p.qty -= qsell
                        p.scaled = True
                        p.stop = max(p.stop, p.entry)  # breakeven
                # structural trail: below newest confirmed higher-low
                last_hl = None
                lows = structure.pivots_asof(sf.pivots, i, "L")
                if lows:
                    last_hl = lows[-1].price
                    if last_hl > p.stop and last_hl < c:
                        p.stop = max(p.stop, last_hl * trail_buf)
                # pyramiding: add to S2 winners on each new higher-low
                if (
                    ex["pyramid"] and p.setup == "S2" and p.scaled is False
                    and last_hl is not None and last_hl > p.entry
                    and p.adds < ex["pyramid_max_adds"]
                    and last_hl != p.last_add_hl
                ):
                    add_risk = p.risk_per_share * p.init_qty * ex["pyramid_add_fraction"]
                    per_share_now = c - p.stop
                    add_qty = int(add_risk / per_share_now) if per_share_now > 0 else 0
                    add_px = c * (1 + cost)
                    if add_qty > 0 and add_qty * add_px <= cash:
                        cash -= add_qty * add_px
                        # weighted-average the entry; keep R measured on initial risk
                        p.entry = (p.entry * p.qty + add_px * add_qty) / (p.qty + add_qty)
                        p.qty += add_qty
                        p.adds += 1
                        p.last_add_hl = last_hl
                # real structure break = close below the last confirmed higher-low
                broke = (last_hl is not None and c < last_hl) if not ex["trend_state_exit"] \
                    else (ctx.trend[i] == "DOWN")
                if broke:
                    exit_px, reason = c, "structure break"
                # time stops
                elif p.setup in ("S1",) and p.bars_held >= ex["s1_time_stop_days"]:
                    exit_px, reason = c, "time stop"
                elif p.setup == "S4" and p.bars_held >= ex["s4_time_stop_days"]:
                    exit_px, reason = c, "time stop"
                elif (
                    p.setup == "S2"
                    and p.bars_held >= ex["s2_review_days"]
                    and (c - p.entry) < ex["s2_review_min_r"] * p.risk_per_share
                ):
                    exit_px, reason = c, "review recycle"

            if exit_px is not None:
                px = exit_px * (1 - cost)
                cash += p.qty * px
                p.realized += p.qty * (px - p.entry)
                # R measured against the initial full-position risk
                init_risk = p.risk_per_share * p.init_qty
                rr = p.realized / init_risk if init_risk > 0 else 0.0
                trades.append(Trade(sym, p.setup, p.entry_date, today, p.entry, px,
                                    p.init_qty, p.realized, rr, p.bars_held, reason,
                                    regime_log[-1]))
                del positions[sym]

        # ── new entries from yesterday's signals, executed at today's open ──
        if reg.state != "RED":
            caps = sizing.PortfolioCaps(
                equity, cfg,
                [{"sector": positions[s].sector,
                  "open_risk": positions[s].qty * positions[s].risk_per_share}
                 for s in positions],
            )
            allowed = {"S1", "S2", "S3", "S4"} if reg.state == "GREEN" else {"S2", "S4"}
            allowed -= set(en.get("disabled_setups", []))
            for sym, ctx in ctxs.items():
                if sym in positions:
                    continue
                iy, i = ctx.pos_map[mb], ctx.pos_map[m]
                if iy < 0 or i < 0 or iy < WARMUP_BARS - 10:
                    continue
                if not ctx.turnover_ok[iy]:
                    continue
                if ctx.stock.sector not in top_sectors:
                    continue
                wi = int(np.searchsorted(ctx.week_end_dates, np.datetime64(today)) - 1)
                if wi < 8:
                    continue
                got = rules.structural_candidate(
                    ctx.sf, ctx.wf, iy, wi, ctx.bench, cfg, allowed_setups=allowed
                )
                if got is None:
                    continue
                sig, _card = got
                # entry refinements
                if en.get("s1_retest_only") and sig.setup == "S1" \
                        and sig.meta.get("mode") == "breakout":
                    continue
                if en.get("s4_require_uptrend") and sig.setup == "S4" \
                        and ctx.trend[iy] != "UP":
                    continue
                o = ctx.sf.o[i]
                if o <= sig.stop:  # gapped through the stop overnight
                    continue
                # never chase: signal invalid if today opens too far above trigger
                gap_pct = (o / sig.entry - 1.0) * 100.0
                if gap_pct > cfg["filters"]["entry_gap_skip_pct"]:
                    continue
                entry_px = o * (1 + cost)
                stop_pct = (entry_px - sig.stop) / entry_px * 100.0
                if stop_pct > sizing.stop_cap_for(sig.setup, cfg):
                    continue
                # grade "B": fundamentals aren't point-in-time testable, so the
                # backtest sizes at the playbook's standard risk, not C-grade half
                sized = sizing.size_trade(entry_px, sig.stop, sig.setup, "B",
                                          reg.state, equity, cfg)
                if sized.qty <= 0:
                    continue
                why = caps.reject_reason(ctx.stock.sector, sized.risk_amount)
                if why:
                    continue
                need_cash = sized.qty * entry_px
                if need_cash > cash:
                    continue
                r_mult = ex["s2_scale_r"] if sig.setup == "S2" else ex["s1_scale_r"]
                t1 = entry_px + r_mult * (entry_px - sig.stop)
                cash -= need_cash
                caps.admit(ctx.stock.sector, sized.risk_amount)
                positions[sym] = Position(sym, sig.setup, ctx.stock.sector, today,
                                          entry_px, sig.stop, sig.stop,
                                          sized.qty, sized.qty, t1)

        # mark to market
        mtm = cash
        for sym, p in positions.items():
            ctx = ctxs[sym]
            i = ctx.pos_map[m]
            px = ctx.sf.c[i] if i >= 0 else p.entry
            mtm += p.qty * px
        equity = mtm
        curve.append((today, equity))

    eq = pd.Series(dict(curve)).sort_index()
    return {
        "equity": eq,
        "trades": trades,
        "capital0": capital0,
        "nifty": nifty_close.reindex(eq.index),
        "regimes": pd.Series(regime_log, index=eq.index),
        "n_symbols": len(ctxs),
    }
