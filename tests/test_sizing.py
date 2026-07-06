"""Risk sizing and portfolio caps — hand-computed cases."""

import pytest

from swing import config, sizing

CFG = config.load()
CAP = 1_000_000.0


def test_basic_risk_sizing():
    # S2, grade B, GREEN: 1% of 10L = ₹10,000 risk; entry 100, stop 95 → 2000 sh
    t = sizing.size_trade(100.0, 95.0, "S2", "B", "GREEN", CAP, CFG)
    assert t.qty == 2000
    assert t.risk_amount == pytest.approx(10_000)


def test_notional_cap_binds():
    # tight stop would imply huge notional; capped at 20% of capital
    t = sizing.size_trade(100.0, 99.5, "S2", "B", "GREEN", CAP, CFG)
    assert t.notional <= CAP * 0.20 + 100
    assert t.qty == 2000  # 200k / 100


def test_stop_cap_skips():
    t = sizing.size_trade(100.0, 88.0, "S2", "B", "GREEN", CAP, CFG)  # 12% stop
    assert t.qty == 0 and "cap" in t.skip_reason


def test_amber_and_grade_haircuts():
    full = sizing.size_trade(100.0, 95.0, "S2", "B", "GREEN", CAP, CFG)
    amber = sizing.size_trade(100.0, 95.0, "S2", "B", "AMBER", CAP, CFG)
    c_grade = sizing.size_trade(100.0, 95.0, "S2", "C", "GREEN", CAP, CFG)
    assert amber.qty == full.qty // 2
    assert c_grade.qty == full.qty // 2


def test_swing_risk_lower():
    s1 = sizing.size_trade(100.0, 96.0, "S1", "B", "GREEN", CAP, CFG)
    assert s1.risk_amount == pytest.approx(CAP * 0.0075, rel=0.01)


def test_futures_only_a_grade_s2():
    kw = dict(capital=CAP, cfg=CFG, lot_size=500)
    a = sizing.size_trade(100.0, 95.0, "S2", "A", "GREEN", **kw)
    b = sizing.size_trade(100.0, 95.0, "S2", "B", "GREEN", **kw)
    s1 = sizing.size_trade(100.0, 95.0, "S1", "A", "GREEN", **kw)
    assert a.futures_ok and a.futures_lots == 1   # lot risk 2500 ≤ 1.25% (12.5k)
    assert not b.futures_ok
    assert not s1.futures_ok


def test_futures_lot_too_big():
    # lot risk = 5000 × (100-95) = 25k > 1.25% of 10L (12.5k)
    t = sizing.size_trade(100.0, 95.0, "S2", "A", "GREEN", CAP, CFG, lot_size=5000)
    assert not t.futures_ok


def test_portfolio_caps():
    caps = sizing.PortfolioCaps(CAP, CFG)
    for k in range(2):
        assert caps.reject_reason("IT", 10_000) is None
        caps.admit("IT", 10_000)
    assert "sector cap" in caps.reject_reason("IT", 10_000)
    # heat: 2 × 10k admitted; cap is 4% = 40k → a 25k trade breaches
    assert caps.reject_reason("Auto", 25_000) == "portfolio heat cap"
    # position count cap
    for s in ["A", "B", "C", "D", "E", "F"]:
        if caps.reject_reason(s, 1000) is None:
            caps.admit(s, 1000)
    assert caps.n == CFG["risk"]["max_positions"]
    assert caps.reject_reason("Z", 1000) == "max positions reached"
