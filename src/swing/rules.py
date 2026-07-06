"""Setup assembly — the shared brain of screener and backtest.

`structural_candidate` applies the layers that are computable point-in-time
(structure setups, weekly alignment, overhead supply, relative strength).
The screener adds the live-only layers (delivery, OI, vetoes) on top via
`Scorecard`; the backtest runs on the structural core alone and says so.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import structure
from .structure import Signal, StockFrame

RS_LOOKBACK = {"S1": 21, "S2": 42, "S3": 21, "S4": 21}


@dataclass
class Scorecard:
    """Layer-by-layer record for one candidate. hard_fail kills the trade;
    soft entries adjust the note/grade."""

    checks: dict[str, str] = field(default_factory=dict)  # name -> "pass"/"fail"/"n/a"/detail
    vetoes: list[str] = field(default_factory=list)

    def hard_fail(self) -> bool:
        return bool(self.vetoes)

    def add(self, name: str, value: str) -> None:
        self.checks[name] = value

    def veto(self, reason: str) -> None:
        self.vetoes.append(reason)

    def summary(self) -> str:
        return "; ".join(f"{k}:{v}" for k, v in self.checks.items())


@dataclass
class Candidate:
    symbol: str
    signal: Signal
    sector: str
    grade: str
    card: Scorecard
    rs: float = 0.0


def structural_candidate(
    sf: StockFrame,
    wf: StockFrame | None,
    i: int,
    wi: int,
    bench_close: np.ndarray,
    cfg: dict,
    allowed_setups: set[str] | None = None,
) -> tuple[Signal, Scorecard] | None:
    """Best structural setup at bar i after the point-in-time gates.

    bench_close must be aligned to sf's bar index. Returns None when no setup
    fires or every fired setup fails a hard gate."""
    signals = structure.detect_all(sf, i, cfg)
    if allowed_setups is not None:
        signals = [s for s in signals if s.setup in allowed_setups]
    if not signals:
        return None
    # hard gates shared by all setups
    card = Scorecard()
    d52 = structure.dist_from_52wh_pct(sf, i)
    if d52 > cfg["filters"]["max_dist_52wh_reject_pct"]:
        return None
    card.add("52wh_dist", f"{d52:.0f}%")
    if wf is not None:
        if not structure.weekly_alignment(wf, wi, cfg):
            return None
        card.add("weekly", "pass")
    else:
        card.add("weekly", "n/a")
    # pick the strongest setup that passes leg RS (priority: S2 > S4 > S1 > S3)
    priority = {"S2": 0, "S4": 1, "S1": 2, "S3": 3}
    for sig in sorted(signals, key=lambda s: priority[s.setup]):
        rs = structure.relative_strength(sf, bench_close, i, RS_LOOKBACK[sig.setup])
        if rs <= 0:
            continue
        c = Scorecard(checks=dict(card.checks))
        c.add("leg_RS", f"+{rs:.1f}%")
        return sig, c
    return None


def liquidity_ok(sf: StockFrame, i: int, cfg: dict) -> bool:
    """20-day average turnover above the configured floor (₹ crore)."""
    if i < 20:
        return False
    turnover = (sf.c[i - 20 : i] * sf.v[i - 20 : i]).mean() / 1e7  # ₹ cr
    return turnover >= cfg["filters"]["min_turnover_cr"]


def first_target(sig: Signal, call_wall: float | None, r_mult: float) -> float:
    """Scale-out level: call-OI wall if it sits beyond +1R, else the R target."""
    r_target = sig.entry + r_mult * (sig.entry - sig.stop)
    if call_wall and call_wall > sig.entry + (sig.entry - sig.stop):
        return min(r_target, call_wall) if call_wall < r_target else r_target
    return r_target
