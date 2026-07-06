"""Market-structure engine: swing pivots, trend state, zones, bases, setups.

Pure price action — no oscillators. Every detector is evaluated *as of* a bar
index ``i`` and uses only information available at that bar:

* a pivot formed at bar ``p`` with span ``s`` is only *confirmed* (usable) from
  bar ``p + s`` onward — no lookahead;
* all rolling statistics are computed on bars ``<= i``.

The same functions drive the live screener (i = last bar) and the backtest
(i iterating), which is what makes the backtest honest.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# ── primitives ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Pivot:
    idx: int            # bar position of the extreme
    price: float
    kind: str           # "H" or "L"
    confirmed_at: int   # first bar index at which this pivot is known


@dataclass
class StockFrame:
    """Precomputed arrays + pivots for one symbol. Build once, query per bar."""

    df: pd.DataFrame
    span: int = 3

    o: np.ndarray = field(init=False)
    h: np.ndarray = field(init=False)
    l: np.ndarray = field(init=False)
    c: np.ndarray = field(init=False)
    v: np.ndarray = field(init=False)
    vol20: np.ndarray = field(init=False)   # 20-bar avg volume, shifted 1 (as-of prior close)
    hi52: np.ndarray = field(init=False)    # rolling 252-bar high of High, inclusive
    pivots: list[Pivot] = field(init=False)

    def __post_init__(self) -> None:
        d = self.df
        self.o = d["Open"].to_numpy(float)
        self.h = d["High"].to_numpy(float)
        self.l = d["Low"].to_numpy(float)
        self.c = d["Close"].to_numpy(float)
        self.v = d["Volume"].to_numpy(float)
        vol = pd.Series(self.v)
        self.vol20 = vol.rolling(20, min_periods=5).mean().shift(1).to_numpy()
        self.hi52 = pd.Series(self.h).rolling(252, min_periods=60).max().to_numpy()
        self.pivots = find_pivots(self.h, self.l, self.span)

    def __len__(self) -> int:
        return len(self.c)


def find_pivots(high: np.ndarray, low: np.ndarray, span: int) -> list[Pivot]:
    """Swing pivots: a pivot high at p has the highest High of the 2*span+1
    window centred on p (strictly higher than later bars to break ties).
    Alternation is enforced — consecutive same-kind pivots keep the extreme."""
    n = len(high)
    raw: list[Pivot] = []
    for p in range(span, n - span):
        win_h = high[p - span : p + span + 1]
        if high[p] >= win_h.max() and high[p] > high[p + 1 : p + span + 1].max():
            raw.append(Pivot(p, float(high[p]), "H", p + span))
        win_l = low[p - span : p + span + 1]
        if low[p] <= win_l.min() and low[p] < low[p + 1 : p + span + 1].min():
            raw.append(Pivot(p, float(low[p]), "L", p + span))
    raw.sort(key=lambda x: (x.idx, x.kind))
    # enforce H/L alternation keeping the more extreme of same-kind runs
    out: list[Pivot] = []
    for piv in raw:
        if out and out[-1].kind == piv.kind:
            prev = out[-1]
            better = (piv.kind == "H" and piv.price >= prev.price) or (
                piv.kind == "L" and piv.price <= prev.price
            )
            if better:
                out[-1] = piv
        else:
            out.append(piv)
    return out


def pivots_asof(pivots: list[Pivot], i: int, kind: str | None = None) -> list[Pivot]:
    return [p for p in pivots if p.confirmed_at <= i and (kind is None or p.kind == kind)]


def trend_states(sf: "StockFrame") -> np.ndarray:
    """Vectorized precompute of trend_state(...)[0] for every bar.
    Returns an array of 'UP'/'DOWN'/'RANGE' — used by backtest breadth."""
    n = len(sf)
    out = np.array(["RANGE"] * n, dtype=object)
    events = sorted(sf.pivots, key=lambda p: p.confirmed_at)
    state = "RANGE"
    highs: list[float] = []
    lows: list[float] = []
    e = 0
    for i in range(n):
        changed = False
        while e < len(events) and events[e].confirmed_at <= i:
            p = events[e]
            (highs if p.kind == "H" else lows).append(p.price)
            e += 1
            changed = True
        if changed and len(highs) >= 2 and len(lows) >= 2:
            hh, hl = highs[-1] > highs[-2], lows[-1] > lows[-2]
            lh, ll = highs[-1] < highs[-2], lows[-1] < lows[-2]
            state = "UP" if (hh and hl) else ("DOWN" if (lh and ll) else "RANGE")
        out[i] = state
    return out


def trend_state(pivots: list[Pivot], i: int) -> tuple[str, int]:
    """('UP'|'DOWN'|'RANGE', completed HH/HL sequence count) as of bar i."""
    ps = pivots_asof(pivots, i)
    highs = [p for p in ps if p.kind == "H"]
    lows = [p for p in ps if p.kind == "L"]
    if len(highs) < 2 or len(lows) < 2:
        return "RANGE", 0
    hh = highs[-1].price > highs[-2].price
    hl = lows[-1].price > lows[-2].price
    lh = highs[-1].price < highs[-2].price
    ll = lows[-1].price < lows[-2].price
    if hh and hl:
        # count consecutive completed HH+HL pairs walking back
        seq = 0
        k = len(highs) - 1
        j = len(lows) - 1
        while k >= 1 and j >= 1 and highs[k].price > highs[k - 1].price and lows[j].price > lows[j - 1].price:
            seq += 1
            k -= 1
            j -= 1
        return "UP", seq
    if lh and ll:
        return "DOWN", 0
    return "RANGE", 0


# ── shared signal payload ─────────────────────────────────────────────────


@dataclass
class Signal:
    setup: str           # "S1" | "S2" | "S3" | "S4"
    entry: float         # reference entry (trigger close)
    stop: float          # structural stop
    note: str = ""
    meta: dict = field(default_factory=dict)

    @property
    def stop_pct(self) -> float:
        return (self.entry - self.stop) / self.entry * 100.0


# ── bases & S1 breakout–retest ────────────────────────────────────────────


@dataclass(frozen=True)
class Base:
    start: int
    end: int             # last bar inside the base (exclusive of breakout bar)
    high: float
    low: float
    range_pct: float
    tight: bool


def detect_base(sf: StockFrame, i: int, cfg: dict) -> Base | None:
    """Longest consolidation ending at bar i-1 that satisfies the base rules,
    evaluated as of bar i (the would-be breakout bar)."""
    s = cfg["structure"]
    min_len = int(s["base_min_sessions"])
    max_len = 60
    if i < min_len + 1:
        return None
    best: Base | None = None
    tight_found = False
    for L in range(min_len, min(max_len, i) + 1):
        lo = float(sf.l[i - L : i].min())
        hi = float(sf.h[i - L : i].max())
        rng = (hi - lo) / lo * 100.0
        if rng <= s["tight_base_range_pct"]:
            tight_found = True  # a tight core base exists even if we extend further
        if rng <= s["base_max_range_pct"]:
            best = Base(i - L, i - 1, hi, lo, rng, tight_found)
        elif best is not None:
            break  # window grew past a valid base — keep the longest found
    if best is None:
        return None
    hi52 = sf.hi52[i - 1]
    if not np.isfinite(hi52):
        return None
    if (hi52 - best.high) / hi52 * 100.0 > s["base_max_dist_52wh_pct"]:
        return None
    return best


def is_breakout_bar(sf: StockFrame, i: int, base: Base, cfg: dict) -> bool:
    s = cfg["structure"]
    if not np.isfinite(sf.vol20[i]) or sf.vol20[i] <= 0:
        return False
    rng = sf.h[i] - sf.l[i]
    if rng <= 0:
        return False
    close_pos = (sf.h[i] - sf.c[i]) / rng  # 0 = closed at high
    return (
        sf.c[i] > base.high
        and sf.v[i] >= s["breakout_vol_mult"] * sf.vol20[i]
        and close_pos <= s["breakout_close_top_frac"]
    )


def detect_s1(sf: StockFrame, i: int, cfg: dict) -> Signal | None:
    """S1 at bar i: either a tight-base breakout close (enter now), or a valid
    retest trigger after a recent breakout."""
    s = cfg["structure"]
    # (a) breakout today
    base = detect_base(sf, i, cfg)
    if base is not None and is_breakout_bar(sf, i, base, cfg):
        gap_pct = (sf.o[i] / sf.c[i - 1] - 1.0) * 100.0
        if base.tight and gap_pct <= s["gap_chase_limit_pct"]:
            # stop below the breakout-day low: the level itself is noise distance
            stop = float(min(sf.l[i], base.high) * 0.995)
            return Signal("S1", float(sf.c[i]), stop,
                          "tight-base breakout", {"base": base, "mode": "breakout"})
        # wide base or gap — only the retest is tradeable; fall through
    # (b) retest trigger today after a breakout in the lookback window
    win = int(s["retest_window_sessions"])
    for b in range(max(1, i - win), i):
        bb = detect_base(sf, b, cfg)
        if bb is None or not is_breakout_bar(sf, b, bb, cfg):
            continue
        level = bb.high
        # price must have come back near the level after the breakout…
        touched = (sf.l[b + 1 : i + 1].min() <= level * (1 + s["retest_proximity_pct"] / 100.0))
        # …without closing back below it (failed breakout)
        held = (sf.c[b + 1 : i + 1].min() >= level * 0.995) if i > b else True
        trigger = sf.c[i] > sf.h[i - 1] and sf.c[i] > level
        if touched and held and trigger:
            trap_stop = float(min(sf.l[b + 1 : i + 1].min(), level * 0.995))
            return Signal("S1", float(sf.c[i]), trap_stop,
                          "breakout retest hold", {"base": bb, "mode": "retest"})
    return None


# ── S2 pullback to demand ─────────────────────────────────────────────────


def demand_zone(sf: StockFrame, i: int) -> tuple[float, float, Pivot] | None:
    """Zone = consolidation at the origin of the most recent completed up-leg:
    bars around the last confirmed higher-low pivot."""
    lows = pivots_asof(sf.pivots, i, "L")
    highs = pivots_asof(sf.pivots, i, "H")
    if len(lows) < 2 or len(highs) < 1:
        return None
    hl = lows[-1]
    if hl.price <= lows[-2].price:
        return None
    a, b = max(0, hl.idx - 3), min(i, hl.idx + 3)
    zone_low = float(sf.l[a : b + 1].min())
    zone_high = float(max(np.maximum(sf.o[a : b + 1], sf.c[a : b + 1]).max(), hl.price))
    return zone_low, zone_high, hl


def detect_s2(sf: StockFrame, i: int, cfg: dict) -> Signal | None:
    s = cfg["structure"]
    state, seqs = trend_state(sf.pivots, i)
    if state != "UP" or seqs < int(s["uptrend_min_sequences"]):
        return None
    z = demand_zone(sf, i)
    if z is None:
        return None
    zone_low, zone_high, hl = z
    highs = pivots_asof(sf.pivots, i, "H")
    last_hh = highs[-1]
    if last_hh.idx <= hl.idx:
        return None  # leg not completed: need HL -> HH then pullback
    # pullback: price has retraced from the HH into/near the zone
    touched = sf.l[i] <= zone_high or sf.l[i - 1] <= zone_high
    if not touched:
        return None
    if sf.c[i] <= zone_low:  # zone failed
        return None
    # volume dryness: pullback vol < dry_mult × rally-leg vol
    rally_v = sf.v[hl.idx : last_hh.idx + 1].mean()
    pull_bars = sf.v[last_hh.idx + 1 : i + 1]
    if len(pull_bars) < 2 or rally_v <= 0:
        return None
    if pull_bars.mean() > s["pullback_vol_dry_mult"] * rally_v:
        return None
    # reversal trigger
    if not (sf.c[i] > sf.h[i - 1] and sf.c[i] > sf.o[i]):
        return None
    return Signal("S2", float(sf.c[i]), zone_low, "pullback to demand zone",
                  {"zone": (zone_low, zone_high), "hl_idx": hl.idx, "hh_idx": last_hh.idx})


# ── S3 failed-breakdown reclaim ───────────────────────────────────────────


def detect_s3(sf: StockFrame, i: int, cfg: dict) -> Signal | None:
    s = cfg["structure"]
    win = int(s["reclaim_window_sessions"])
    lows = pivots_asof(sf.pivots, i, "L")
    if len(lows) < 2:
        return None
    # support = two pivot lows within 1.5% of each other (tested level)
    support = None
    for a in range(len(lows) - 1, 0, -1):
        for b in range(a - 1, -1, -1):
            if abs(lows[a].price / lows[b].price - 1.0) <= 0.015:
                support = min(lows[a].price, lows[b].price)
                break
        if support:
            break
    if not support:
        return None
    # breakdown then reclaim within `win` sessions, reclaim close today
    bd = None
    for j in range(max(1, i - win), i):
        if sf.c[j] < support * 0.995:
            bd = j
            break
    if bd is None:
        return None
    if any(sf.c[j] > support for j in range(bd + 1, i)):  # already reclaimed earlier
        return None
    if sf.c[i] <= support:
        return None
    trap_low = float(sf.l[bd : i + 1].min())
    return Signal("S3", float(sf.c[i]), trap_low, "failed-breakdown reclaim",
                  {"support": support, "breakdown_idx": bd})


# ── S4 post-results / surge momentum ──────────────────────────────────────


def detect_surge_day(sf: StockFrame, j: int, cfg: dict) -> bool:
    s = cfg["structure"]
    if j < 1 or not np.isfinite(sf.vol20[j]) or sf.vol20[j] <= 0:
        return False
    gain = (sf.c[j] / sf.c[j - 1] - 1.0) * 100.0
    return gain >= s["s4_min_gain_pct"] and sf.v[j] >= s["s4_vol_mult"] * sf.vol20[j]


def detect_s4(sf: StockFrame, i: int, cfg: dict) -> Signal | None:
    """Entry trigger within 5 sessions after a surge day: pullback holding the
    upper half of the surge bar, then a close above the prior day's high."""
    for j in range(max(1, i - 5), i):
        if not detect_surge_day(sf, j, cfg):
            continue
        mid = (sf.h[j] + sf.l[j]) / 2.0
        if sf.l[j + 1 : i + 1].min() < mid:  # gave back too much
            continue
        if sf.c[i] > sf.h[i - 1] and sf.c[i] >= sf.c[j]:
            return Signal("S4", float(sf.c[i]), float(mid), "post-surge momentum",
                          {"surge_idx": j})
    return None


# ── context filters ───────────────────────────────────────────────────────


def dist_from_52wh_pct(sf: StockFrame, i: int) -> float:
    hi = sf.hi52[i]
    if not np.isfinite(hi) or hi <= 0:
        return 100.0
    return (hi - sf.c[i]) / hi * 100.0


def relative_strength(sf: StockFrame, bench_close: np.ndarray, i: int, lookback: int) -> float:
    """Stock return minus benchmark return over `lookback` bars, in % points.
    `bench_close` must be aligned to the same bar index as sf."""
    j = max(0, i - lookback)
    if sf.c[j] <= 0 or bench_close[j] <= 0:
        return 0.0
    return (sf.c[i] / sf.c[j] - bench_close[i] / bench_close[j]) * 100.0


def weekly_alignment(wf: StockFrame, wi: int, cfg: dict) -> bool:
    """Weekly agrees: weekly uptrend, or weekly range while within 10% of 52w high."""
    state, _ = trend_state(wf.pivots, wi)
    if state == "UP":
        return True
    if state == "RANGE" and dist_from_52wh_pct(wf, wi) <= 10.0:
        return True
    return False


def detect_all(sf: StockFrame, i: int, cfg: dict) -> list[Signal]:
    out = []
    for fn in (detect_s1, detect_s2, detect_s3, detect_s4):
        sig = fn(sf, i, cfg)
        if sig is not None and sig.entry > sig.stop:
            out.append(sig)
    return out
