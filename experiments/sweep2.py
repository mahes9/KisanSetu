"""Confirmation sweep: clean combination of the two robust levers
(ride_full + s4_uptrend), and whether cutting the loss-making S1 helps.
Validated on two windows to check the gain isn't a single-period artifact.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from swing import backtest, report  # noqa: E402

RIDE = {"exits": {"scale_fraction": 0.0}}
S4UP = {"entries": {"s4_require_uptrend": True}}


def merge(*ds):
    out: dict = {}
    for d in ds:
        for k, v in d.items():
            out.setdefault(k, {}).update(v)
    return out


VARIANTS = {
    "baseline": {},
    "ride+s4up": merge(RIDE, S4UP),
    "ride+s4up_noS1": merge(RIDE, S4UP, {"entries": {"disabled_setups": ["S1"]}}),
    "ride+s4up_noS1_notrend": merge(
        RIDE, S4UP,
        {"entries": {"disabled_setups": ["S1"]}, "exits": {"trend_state_exit": False}},
    ),
}

WINDOWS = ["2019-06-01", "2021-06-01"]  # full + out-of-the-COVID-rebound subperiod


def main() -> None:
    rows = []
    for start in WINDOWS:
        for name, ov in VARIANTS.items():
            res = backtest.run(start=start, overrides=ov)
            m = report.metrics(res)
            rows.append(
                {
                    "window": start,
                    "variant": name,
                    "CAGR%": round(m["CAGR_%"], 1),
                    "maxDD%": round(m["max_drawdown_%"], 1),
                    "sharpe": round(m["sharpe"], 2),
                    "PF": round(m["profit_factor"], 2),
                    "win%": round(m["win_rate_%"], 1),
                    "avgR": round(m["avg_R"], 2),
                    "exp₹": int(m["expectancy_₹"]),
                    "trades": m["trades"],
                }
            )
    df = pd.DataFrame(rows)
    print("\n" + "=" * 96)
    print("CONFIRMATION SWEEP — two windows (Nifty full-window CAGR ≈ 9.7%)")
    print("=" * 96)
    print(df.to_string(index=False))
    df.to_csv(Path(__file__).parent / "sweep2_results.csv", index=False)


if __name__ == "__main__":
    main()
