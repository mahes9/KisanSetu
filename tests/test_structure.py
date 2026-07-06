"""Structure-engine tests on hand-built synthetic series."""

import numpy as np
import pandas as pd
import pytest

from swing import config, structure
from swing.structure import StockFrame


CFG = config.load()


def make_df(closes, highs=None, lows=None, opens=None, volumes=None):
    closes = np.asarray(closes, dtype=float)
    n = len(closes)
    highs = np.asarray(highs, dtype=float) if highs is not None else closes * 1.01
    lows = np.asarray(lows, dtype=float) if lows is not None else closes * 0.99
    opens = np.asarray(opens, dtype=float) if opens is not None else closes
    volumes = np.asarray(volumes, dtype=float) if volumes is not None else np.full(n, 1e6)
    idx = pd.bdate_range("2024-01-01", periods=n)
    return pd.DataFrame(
        {"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": volumes},
        index=idx,
    )


def zigzag(levels, leg=5):
    """Linear interpolation through the given turning-point levels."""
    pts = []
    for a, b in zip(levels[:-1], levels[1:]):
        pts.extend(np.linspace(a, b, leg, endpoint=False))
    pts.append(levels[-1])
    return np.array(pts)


# ── pivots ────────────────────────────────────────────────────────────────


def test_pivots_alternate_and_confirm():
    closes = zigzag([100, 110, 104, 116, 108, 122], leg=6)
    sf = StockFrame(make_df(closes), span=3)
    kinds = [p.kind for p in sf.pivots]
    for a, b in zip(kinds[:-1], kinds[1:]):
        assert a != b, "pivots must alternate H/L"
    for p in sf.pivots:
        assert p.confirmed_at == p.idx + 3, "pivot usable only span bars later"


def test_no_lookahead():
    closes = zigzag([100, 110, 104, 116], leg=6)
    sf = StockFrame(make_df(closes), span=3)
    piv = sf.pivots[0]
    before = structure.pivots_asof(sf.pivots, piv.confirmed_at - 1)
    after = structure.pivots_asof(sf.pivots, piv.confirmed_at)
    assert piv not in before
    assert piv in after


def test_trend_state_up_down():
    up = zigzag([100, 112, 106, 120, 113, 130, 122, 140], leg=6)
    sf = StockFrame(make_df(up), span=3)
    state, seqs = structure.trend_state(sf.pivots, len(sf) - 1)
    assert state == "UP"
    assert seqs >= 2

    down = zigzag([140, 122, 130, 113, 120, 106, 112, 100], leg=6)
    sfd = StockFrame(make_df(down), span=3)
    stated, _ = structure.trend_state(sfd.pivots, len(sfd) - 1)
    assert stated == "DOWN"


# ── S1 base & breakout ────────────────────────────────────────────────────


def s1_frame(base_len=25, breakout_vol=2.0, gap=0.0, base_range=0.05):
    """Uptrend into a flat base near highs, then a breakout bar."""
    rally = zigzag([70, 100], leg=50)
    rng = np.random.default_rng(7)
    base = 100 + (rng.random(base_len) - 0.5) * 100 * base_range * 0.8
    closes = np.concatenate([rally, base])
    n = len(closes)
    vols = np.full(n, 1e6)
    # breakout bar
    bo_open = closes[-1] * (1 + gap / 100)
    bo_close = max(closes.max() * 1.025, bo_open * 1.01)
    closes = np.append(closes, bo_close)
    highs = closes * 1.005
    lows = closes * 0.995
    opens = closes.copy()
    opens[-1] = bo_open
    lows[-1] = min(bo_open, bo_close) * 0.995
    highs[-1] = bo_close * 1.002  # close near the top of the bar
    vols = np.append(vols, breakout_vol * 1e6)
    return make_df(closes, highs, lows, opens, vols)


def test_s1_tight_base_breakout_fires():
    df = s1_frame(breakout_vol=2.0)
    sf = StockFrame(df, span=3)
    sig = structure.detect_s1(sf, len(sf) - 1, CFG)
    assert sig is not None and sig.setup == "S1"
    assert sig.meta["mode"] == "breakout"
    assert sig.stop < sig.entry


def test_s1_needs_volume():
    df = s1_frame(breakout_vol=1.1)  # below 1.5x
    sf = StockFrame(df, span=3)
    assert structure.detect_s1(sf, len(sf) - 1, CFG) is None


def test_s1_gap_up_blocks_breakout_entry():
    df = s1_frame(breakout_vol=2.0, gap=3.0)  # >2% gap-up: no chase
    sf = StockFrame(df, span=3)
    sig = structure.detect_s1(sf, len(sf) - 1, CFG)
    assert sig is None or sig.meta["mode"] == "retest"


# ── S2 pullback to demand ─────────────────────────────────────────────────


def s2_frame():
    """Clean uptrend (2+ HH/HL legs), then a low-volume pullback into the
    origin of the last leg, ending with a reversal bar."""
    path = zigzag([100, 112, 105, 120, 113, 132, 124, 145], leg=8)  # 2+ HH/HL legs
    pull = np.linspace(145, 127, 7)[1:]                    # pullback toward 124 zone
    closes = np.concatenate([path, pull])
    vols = np.concatenate([np.full(len(path), 1.2e6), np.full(len(pull), 0.5e6)])
    # reversal trigger bar inside the zone
    closes = np.append(closes, 131.0)
    vols = np.append(vols, 0.9e6)
    highs = closes * 1.008
    lows = closes * 0.992
    opens = np.append(closes[:-1].copy(), 127.5)  # trigger bar opens low, closes high
    lows[-1] = 126.5
    highs[-1] = 131.4
    return make_df(closes, highs, lows, opens, vols)


def test_s2_pullback_fires():
    df = s2_frame()
    sf = StockFrame(df, span=3)
    sig = structure.detect_s2(sf, len(sf) - 1, CFG)
    assert sig is not None and sig.setup == "S2"
    assert sig.stop < sig.entry
    zlow, zhigh = sig.meta["zone"]
    assert zlow < zhigh


def test_s2_rejects_heavy_volume_pullback():
    df = s2_frame()
    df.loc[df.index[-7]:, "Volume"] = 2.0e6  # distribution-style pullback
    sf = StockFrame(df, span=3)
    assert structure.detect_s2(sf, len(sf) - 1, CFG) is None


# ── S3 failed-breakdown reclaim ───────────────────────────────────────────


def test_s3_reclaim_fires():
    # support ~100 tested twice, breakdown to 97, reclaim to 101.5
    path = zigzag([100, 110, 100.5, 109, 100.2, 106], leg=7)
    closes = np.concatenate([path, [98.5, 97.4, 101.5]])
    highs = closes * 1.006
    lows = closes * 0.994
    lows[-2] = 96.8  # trap low
    sf = StockFrame(make_df(closes, highs, lows), span=3)
    sig = structure.detect_s3(sf, len(sf) - 1, CFG)
    assert sig is not None and sig.setup == "S3"
    assert sig.stop == pytest.approx(96.8, abs=0.2)


# ── S4 surge momentum ─────────────────────────────────────────────────────


def test_s4_surge_then_trigger():
    flat = np.full(40, 100.0) + np.linspace(-1, 1, 40)
    surge_close = 106.0
    closes = np.concatenate([flat, [surge_close], [105.2, 104.8, 106.5]])
    vols = np.full(len(closes), 1e6)
    vols[40] = 3.0e6  # surge volume
    highs = closes * 1.004
    lows = closes * 0.996
    lows[40] = 100.5
    highs[40] = 106.2
    sf = StockFrame(make_df(closes, highs, lows, volumes=vols), span=3)
    sig = structure.detect_s4(sf, len(sf) - 1, CFG)
    assert sig is not None and sig.setup == "S4"
    mid = (106.2 + 100.5) / 2
    assert sig.stop == pytest.approx(mid, rel=0.01)


def test_s4_rejects_deep_giveback():
    flat = np.full(40, 100.0)
    closes = np.concatenate([flat, [106.0], [102.0, 101.0, 106.5]])  # fell below mid
    vols = np.full(len(closes), 1e6)
    vols[40] = 3.0e6
    highs = closes * 1.004
    lows = closes * 0.996
    lows[40] = 100.5
    highs[40] = 106.2
    sf = StockFrame(make_df(closes, highs, lows, volumes=vols), span=3)
    assert structure.detect_s4(sf, len(sf) - 1, CFG) is None


# ── context helpers ───────────────────────────────────────────────────────


def test_relative_strength():
    stock = np.linspace(100, 120, 60)   # +20%
    bench = np.linspace(100, 105, 60)   # +5%
    sf = StockFrame(make_df(stock), span=3)
    rs = structure.relative_strength(sf, bench, 59, 59)
    assert rs == pytest.approx(15.0, abs=0.5)


def test_dist_52wh():
    closes = np.concatenate([np.linspace(100, 200, 260), np.full(20, 150.0)])
    sf = StockFrame(make_df(closes), span=3)
    d = structure.dist_from_52wh_pct(sf, len(sf) - 1)
    assert 24 < d < 27  # 150 vs ~202 high
