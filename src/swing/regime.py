"""Market regime gate — structure-based, no indicators.

GREEN  : Nifty daily structure UP + breadth > threshold + VIX calm
AMBER  : exactly one leg broken, or FII positioning hostile
RED    : Nifty structure DOWN (confirmed lower-low) or VIX panic
"""

from __future__ import annotations

from dataclasses import dataclass

from . import structure
from .structure import StockFrame


@dataclass
class Regime:
    state: str            # GREEN | AMBER | RED
    nifty_trend: str
    breadth_pct: float | None
    vix: float | None
    fii_bias: str | None  # "long" | "short" | None (unknown)
    notes: str = ""

    @property
    def size_factor(self) -> float:
        return {"GREEN": 1.0, "AMBER": 0.5, "RED": 0.0}[self.state]

    def allows(self, setup: str) -> bool:
        if self.state == "GREEN":
            return True
        if self.state == "AMBER":
            return setup in ("S2", "S4")
        return False


def classify(
    nifty: StockFrame,
    i: int,
    breadth_pct: float | None,
    vix: float | None,
    fii_bias: str | None = None,
    cfg: dict | None = None,
) -> Regime:
    from . import config

    c = (cfg or config.load())["regime"]
    trend, _ = structure.trend_state(nifty.pivots, i)
    notes = []

    if trend == "DOWN" or (vix is not None and vix >= c["vix_red"]):
        notes.append("nifty structure broken" if trend == "DOWN" else f"VIX {vix:.1f} panic")
        return Regime("RED", trend, breadth_pct, vix, fii_bias, "; ".join(notes))

    legs_ok = 0
    legs_total = 0

    legs_total += 1
    if trend == "UP":
        legs_ok += 1
    else:
        notes.append(f"nifty trend {trend}")

    if breadth_pct is not None:
        legs_total += 1
        if breadth_pct > c["breadth_green_pct"]:
            legs_ok += 1
        else:
            notes.append(f"breadth {breadth_pct:.0f}%")

    if vix is not None:
        legs_total += 1
        if vix < c["vix_amber"]:
            legs_ok += 1
        else:
            notes.append(f"VIX {vix:.1f} elevated")

    if fii_bias == "short":
        notes.append("FII net short index futures")
        return Regime("AMBER", trend, breadth_pct, vix, fii_bias, "; ".join(notes))

    state = "GREEN" if legs_ok == legs_total else ("AMBER" if legs_total - legs_ok == 1 else "RED")
    return Regime(state, trend, breadth_pct, vix, fii_bias, "; ".join(notes))
