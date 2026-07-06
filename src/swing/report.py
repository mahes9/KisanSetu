"""Backtest report — metrics, breakdowns, equity curve plot."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config


def metrics(result: dict) -> dict:
    eq: pd.Series = result["equity"]
    trades = result["trades"]
    cap0 = result["capital0"]
    years = max((eq.index[-1] - eq.index[0]).days / 365.25, 1e-9)
    cagr = (eq.iloc[-1] / cap0) ** (1 / years) - 1
    peak = eq.cummax()
    dd = (eq / peak - 1.0)
    rets = eq.pct_change().dropna()
    sharpe = rets.mean() / rets.std() * np.sqrt(252) if rets.std() > 0 else 0.0

    n = len(trades)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    win_rate = len(wins) / n * 100 if n else 0.0
    avg_r = np.mean([t.r_result for t in trades]) if n else 0.0
    gross_p = sum(t.pnl for t in wins)
    gross_l = -sum(t.pnl for t in losses)
    pf = gross_p / gross_l if gross_l > 0 else float("inf")
    expectancy = np.mean([t.pnl for t in trades]) if n else 0.0

    nifty = result["nifty"].dropna()
    bench_cagr = (nifty.iloc[-1] / nifty.iloc[0]) ** (1 / years) - 1

    return {
        "period": f"{eq.index[0].date()} → {eq.index[-1].date()}",
        "symbols": result["n_symbols"],
        "final_equity": eq.iloc[-1],
        "CAGR_%": cagr * 100,
        "Nifty_CAGR_%": bench_cagr * 100,
        "max_drawdown_%": dd.min() * 100,
        "sharpe": sharpe,
        "trades": n,
        "win_rate_%": win_rate,
        "avg_R": avg_r,
        "profit_factor": pf,
        "expectancy_₹": expectancy,
    }


def per_setup(result: dict) -> pd.DataFrame:
    rows = []
    df = pd.DataFrame(
        [
            {"setup": t.setup, "pnl": t.pnl, "r": t.r_result, "bars": t.bars_held,
             "win": t.pnl > 0, "reason": t.exit_reason}
            for t in result["trades"]
        ]
    )
    if df.empty:
        return df
    g = df.groupby("setup")
    out = pd.DataFrame(
        {
            "trades": g.size(),
            "win_%": (g["win"].mean() * 100).round(1),
            "avg_R": g["r"].mean().round(2),
            "total_pnl": g["pnl"].sum().round(0),
            "avg_bars": g["bars"].mean().round(1),
        }
    )
    return out


def per_year(result: dict) -> pd.DataFrame:
    eq = result["equity"]
    yearly = eq.resample("YE").last()
    prev = eq.iloc[0]
    rows = []
    for d, v in yearly.items():
        rows.append({"year": d.year, "return_%": round((v / prev - 1) * 100, 1)})
        prev = v
    n = result["nifty"].dropna().resample("YE").last()
    pn = result["nifty"].dropna().iloc[0]
    for k, (d, v) in enumerate(n.items()):
        if k < len(rows):
            rows[k]["nifty_%"] = round((v / pn - 1) * 100, 1)
        pn = v
    return pd.DataFrame(rows)


def save_outputs(result: dict) -> tuple[str, str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = config.PROJECT_ROOT / "journal"
    out_dir.mkdir(exist_ok=True)

    eq = result["equity"]
    nifty = result["nifty"].dropna()
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True, height_ratios=[3, 1]
    )
    ax1.plot(eq.index, eq / eq.iloc[0], label="Strategy", lw=1.6)
    ax1.plot(nifty.index, nifty / nifty.iloc[0], label="Nifty 50", lw=1.2, alpha=0.8)
    ax1.set_title("Equity curve (normalised)")
    ax1.legend()
    ax1.grid(alpha=0.3)
    dd = eq / eq.cummax() - 1
    ax2.fill_between(dd.index, dd * 100, 0, color="tab:red", alpha=0.4)
    ax2.set_ylabel("DD %")
    ax2.grid(alpha=0.3)
    png = out_dir / "equity_curve.png"
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    plt.close(fig)

    tdf = pd.DataFrame(
        [
            {
                "symbol": t.symbol, "setup": t.setup,
                "entry_date": t.entry_date.date(), "exit_date": t.exit_date.date(),
                "entry": round(t.entry, 2), "exit_avg": round(t.exit_avg, 2),
                "qty": t.qty, "pnl": round(t.pnl, 0), "R": round(t.r_result, 2),
                "bars": t.bars_held, "exit_reason": t.exit_reason,
                "regime": t.regime_at_entry,
            }
            for t in result["trades"]
        ]
    )
    csv = out_dir / "backtest_trades.csv"
    tdf.to_csv(csv, index=False, encoding="utf-8-sig")
    return str(png), str(csv)


def render(result: dict) -> str:
    m = metrics(result)
    lines = ["=" * 70, "  BACKTEST REPORT — structural core (S1–S3 + gates)", "=" * 70]
    lines.append(f"  period            {m['period']}   ({m['symbols']} symbols)")
    lines.append(f"  final equity      ₹{m['final_equity']:,.0f}  (from ₹{result['capital0']:,.0f})")
    lines.append(f"  CAGR              {m['CAGR_%']:.1f}%   vs Nifty {m['Nifty_CAGR_%']:.1f}%")
    lines.append(f"  max drawdown      {m['max_drawdown_%']:.1f}%")
    lines.append(f"  sharpe (daily)    {m['sharpe']:.2f}")
    lines.append(f"  trades            {m['trades']}  | win rate {m['win_rate_%']:.1f}%"
                 f"  | avg R {m['avg_R']:.2f}  | PF {m['profit_factor']:.2f}")
    lines.append(f"  expectancy        ₹{m['expectancy_₹']:,.0f} / trade")
    lines.append("-" * 70)
    ps = per_setup(result)
    if not ps.empty:
        lines.append("  per setup:")
        for setup, row in ps.iterrows():
            lines.append(
                f"    {setup}: {int(row['trades'])} trades, win {row['win_%']}%, "
                f"avg R {row['avg_R']}, pnl ₹{row['total_pnl']:,.0f}, {row['avg_bars']} bars"
            )
    py = per_year(result)
    if not py.empty:
        lines.append("  per year (strategy vs nifty):")
        for _, r in py.iterrows():
            lines.append(f"    {int(r['year'])}: {r['return_%']:+.1f}%  vs  {r.get('nifty_%', float('nan')):+.1f}%")
    lines.append("-" * 70)
    lines.append("  caveats: current constituents (survivorship bias); fundamentals,")
    lines.append("  delivery %, OI and FII layers are live-only filters not in this test.")
    lines.append("=" * 70)
    return "\n".join(lines)
