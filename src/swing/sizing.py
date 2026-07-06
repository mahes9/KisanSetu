"""Layer 6 — risk-based position sizing and portfolio caps."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SizedTrade:
    qty: int
    risk_amount: float
    notional: float
    risk_pct: float
    futures_ok: bool = False
    futures_lots: int = 0
    skip_reason: str = ""


def risk_pct_for(setup: str, grade: str, regime_state: str, cfg: dict) -> float:
    r = cfg["risk"]
    base = r["positional_pct"] if setup == "S2" else r["swing_pct"]
    if setup == "S3" or grade == "C":
        base *= r["s3_factor"]
    if regime_state == "AMBER":
        base *= 0.5
    return base


def stop_cap_for(setup: str, cfg: dict) -> float:
    r = cfg["risk"]
    return {
        "S1": r["stop_cap_swing_pct"],
        "S2": r["stop_cap_positional_pct"],
        "S3": r["stop_cap_s3_pct"],
        "S4": r["stop_cap_s4_pct"],
    }[setup]


def size_trade(
    entry: float,
    stop: float,
    setup: str,
    grade: str,
    regime_state: str,
    capital: float,
    cfg: dict,
    lot_size: int = 0,
) -> SizedTrade:
    r = cfg["risk"]
    stop_pct = (entry - stop) / entry * 100.0
    cap = stop_cap_for(setup, cfg)
    if stop_pct > cap:
        return SizedTrade(0, 0, 0, 0, skip_reason=f"stop {stop_pct:.1f}% > {cap}% cap")
    pct = risk_pct_for(setup, grade, regime_state, cfg)
    risk_amount = capital * pct / 100.0
    per_share = entry - stop
    if per_share <= 0:
        return SizedTrade(0, 0, 0, 0, skip_reason="non-positive risk per share")
    qty = int(risk_amount // per_share)
    notional = qty * entry
    max_notional = capital * r["max_notional_pct"] / 100.0
    if notional > max_notional:
        qty = int(max_notional // entry)
        notional = qty * entry
    if qty <= 0:
        return SizedTrade(0, 0, 0, 0, skip_reason="capital too small for 1 share at this risk")
    # futures feasibility (suggestion only; cash qty above remains the default)
    futures_ok, lots = False, 0
    if lot_size > 0 and grade == "A" and setup == "S2":
        lot_risk = lot_size * per_share
        lot_notional = lot_size * entry
        if (
            lot_risk <= capital * r["futures_lot_risk_cap_pct"] / 100.0
            and lot_notional <= capital * r["max_futures_notional_pct"] / 100.0
        ):
            futures_ok, lots = True, 1
    return SizedTrade(qty, qty * per_share, notional, pct, futures_ok, lots)


class PortfolioCaps:
    """Tracks open-position constraints while admitting new candidates."""

    def __init__(self, capital: float, cfg: dict, open_positions: list[dict] | None = None):
        self.cfg = cfg["risk"]
        self.capital = capital
        self.n = 0
        self.heat = 0.0
        self.by_sector: dict[str, int] = {}
        for p in open_positions or []:
            self.admit(p.get("sector", "?"), p.get("open_risk", 0.0))

    def admit(self, sector: str, risk_amount: float) -> None:
        self.n += 1
        self.heat += risk_amount
        self.by_sector[sector] = self.by_sector.get(sector, 0) + 1

    def reject_reason(self, sector: str, risk_amount: float) -> str | None:
        if self.n >= self.cfg["max_positions"]:
            return "max positions reached"
        if self.by_sector.get(sector, 0) >= self.cfg["max_per_sector"]:
            return f"sector cap ({sector})"
        if (self.heat + risk_amount) / self.capital * 100.0 > self.cfg["max_heat_pct"]:
            return "portfolio heat cap"
        return None
