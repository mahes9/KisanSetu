"""Compare principled strategy variants on expectancy. Run from repo root:
    python experiments/sweep.py
Each variant is a config override over the baseline. We report CAGR, max DD,
PF, win%, avg R, expectancy and trade count so trade-offs are visible — no
cherry-picking. Theory-driven changes only (let winners run, cut noise trades,
exit on real structure breaks), to limit overfitting.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from swing import backtest, report  # noqa: E402

START = "2019-06-01"

VARIANTS = {
    "baseline": {},
    "no_trend_exit": {"exits": {"trend_state_exit": False}},
    "ride_full": {"exits": {"scale_fraction": 0.0}},
    "scale_third": {"exits": {"scale_fraction": 0.33}},
    "s4_uptrend": {"entries": {"s4_require_uptrend": True}},
    "s1_retest_only": {"entries": {"s1_retest_only": True}},
    "pyramid": {"exits": {"pyramid": True}},
    # combined: the changes that should compound — let winners run + clean breaks
    # + cut the noisy S1/S4 trades
    "combined": {
        "exits": {"trend_state_exit": False, "scale_fraction": 0.0, "pyramid": True},
        "entries": {"s4_require_uptrend": True, "s1_retest_only": True},
    },
    "combined_no_pyramid": {
        "exits": {"trend_state_exit": False, "scale_fraction": 0.0},
        "entries": {"s4_require_uptrend": True, "s1_retest_only": True},
    },
}


def main() -> None:
    rows = []
    setup_rows = []
    for name, ov in VARIANTS.items():
        res = backtest.run(start=START, overrides=ov)
        m = report.metrics(res)
        rows.append(
            {
                "variant": name,
                "CAGR%": round(m["CAGR_%"], 1),
                "maxDD%": round(m["max_drawdown_%"], 1),
                "sharpe": round(m["sharpe"], 2),
                "PF": round(m["profit_factor"], 2),
                "win%": round(m["win_rate_%"], 1),
                "avgR": round(m["avg_R"], 2),
                "exp₹": int(m["expectancy_₹"]),
                "trades": m["trades"],
                "final₹": int(m["final_equity"]),
            }
        )
        ps = report.per_setup(res)
        for s, r in ps.iterrows():
            setup_rows.append({"variant": name, "setup": s, "trades": int(r["trades"]),
                               "win%": r["win_%"], "avgR": r["avg_R"], "pnl": int(r["total_pnl"])})
    df = pd.DataFrame(rows)
    print("\n" + "=" * 92)
    print("VARIANT COMPARISON  (Nifty CAGR over window ≈ 9.7%)")
    print("=" * 92)
    print(df.to_string(index=False))
    print("\nPer-setup detail:")
    print(pd.DataFrame(setup_rows).to_string(index=False))
    df.to_csv(Path(__file__).parent / "sweep_results.csv", index=False)


if __name__ == "__main__":
    main()
