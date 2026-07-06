"""Generate a complete human-readable backtest trade report from the saved
ledger (journal/backtest_trades.csv). Run after a backtest:
    python run_backtest.py --start 2019-06-01
    python run_trade_report.py
Writes journal/trade_report.md and prints a summary.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LEDGER = Path("journal/backtest_trades.csv")
OUT = Path("journal/trade_report.md")

SETUP_WHY = {
    "S2": "Pullback-to-demand — an established uptrend pulled back into a demand zone "
          "(prior breakout/higher-low) on drying volume, then printed a reversal close. "
          "The system's positional engine.",
    "S3": "Failed-breakdown reclaim — price broke a support pivot then closed back above "
          "it within 3 sessions (bear trap). Countertrend, taken at half size.",
    "S4": "Post-results momentum (PEAD) — a results-day surge on heavy volume while the "
          "stock was already in a confirmed daily uptrend. Drift continuation trade.",
    "S1": "Breakout-retest (disabled by default in backtest — needs live delivery/OI).",
}

EXIT_WHY = {
    "stop": "hit the structural stop",
    "structure break": "closed below the last confirmed higher-low (trend broke)",
    "time stop": "hit the max-holding-period time stop",
    "review recycle": "≤1R after 6 weeks — capital recycled",
}


def inr(x: float) -> str:
    return f"₹{x:,.0f}"


def main() -> None:
    if not LEDGER.exists():
        raise SystemExit("No ledger — run run_backtest.py first.")
    df = pd.read_csv(LEDGER, parse_dates=["entry_date", "exit_date"])
    df["year"] = df["entry_date"].dt.year
    df["win"] = df["pnl"] > 0
    df["hold_days"] = (df["exit_date"] - df["entry_date"]).dt.days

    wins, losses = df[df.win], df[~df.win]
    gross_p, gross_l = wins.pnl.sum(), losses.pnl.sum()
    L = []
    w = L.append
    w("# KisanSetu — Complete Backtest Trade Report")
    w("")
    w(f"Source: `{LEDGER}` · {len(df)} trades · "
      f"{df.entry_date.min():%Y-%m-%d} → {df.exit_date.max():%Y-%m-%d}")
    w("")
    w("> Validated config: ride full position on structural trail, S4 uptrend-gated, "
      "S1 disabled. Costs (0.15% round-trip + 0.05%/side slippage) already deducted "
      "from every P&L below. Current-constituent universe (survivorship bias); live "
      "fundamental/delivery/OI confirmation layers are NOT in these numbers.")
    w("")

    # ---- headline ----
    w("## 1. Headline")
    w("")
    w("| Metric | Value |")
    w("|---|---|")
    w(f"| Net P&L | **{inr(df.pnl.sum())}** on ₹10,00,000 |")
    w(f"| Trades | {len(df)}  ({df.win.sum()} wins / {(~df.win).sum()} losses) |")
    w(f"| Win rate | {df.win.mean()*100:.1f}% |")
    w(f"| Avg win | {inr(wins.pnl.mean())}  ·  Avg loss {inr(losses.pnl.mean())} |")
    w(f"| Avg R / trade | {df.R.mean():.2f} |")
    w(f"| Profit factor | {gross_p/abs(gross_l):.2f}  (gross +{inr(gross_p)} / {inr(gross_l)}) |")
    w(f"| Best trade | {wins.loc[wins.pnl.idxmax(),'symbol']} {inr(wins.pnl.max())} |")
    w(f"| Worst trade | {losses.loc[losses.pnl.idxmin(),'symbol']} {inr(losses.pnl.min())} |")
    w(f"| Avg holding | {df.hold_days.mean():.0f} calendar days |")
    w("")
    w("**The shape of the edge:** a minority of trades win, but winners are far larger "
      "than losers — classic positive-expectancy trend-following. The top 5 trades below "
      "carry the whole result; the discipline is surviving the many small losses to be "
      "holding when a big one runs.")
    w("")

    # ---- concentration ----
    top5 = df.nlargest(5, "pnl")
    w(f"Top 5 trades = {inr(top5.pnl.sum())} "
      f"({top5.pnl.sum()/df.pnl.sum()*100:.0f}% of net P&L).")
    w("")

    # ---- by setup ----
    w("## 2. By setup type (why each trade was taken)")
    w("")
    for s in ["S2", "S4", "S3"]:
        sd = df[df.setup == s]
        if sd.empty:
            continue
        w(f"### {s} — {SETUP_WHY[s]}")
        w(f"- {len(sd)} trades · win {sd.win.mean()*100:.0f}% · "
          f"avg R {sd.R.mean():.2f} · net **{inr(sd.pnl.sum())}**")
        w("")

    # ---- by year ----
    w("## 3. By year")
    w("")
    w("| Year | Trades | Win% | Net P&L |")
    w("|---|---|---|---|")
    for y, yd in df.groupby("year"):
        w(f"| {y} | {len(yd)} | {yd.win.mean()*100:.0f}% | {inr(yd.pnl.sum())} |")
    w("")

    # ---- by regime ----
    w("## 4. By regime at entry")
    w("")
    w("| Regime | Trades | Win% | Net P&L |")
    w("|---|---|---|---|")
    for r, rd in df.groupby("regime"):
        w(f"| {r} | {len(rd)} | {rd.win.mean()*100:.0f}% | {inr(rd.pnl.sum())} |")
    w("")

    # ---- winners ----
    w("## 5. Every winning trade")
    w("")
    w("| # | Symbol | Setup | In → Out | Days | Qty | P&L | R | Exit |")
    w("|---|---|---|---|---|---|---|---|---|")
    for n, (_, t) in enumerate(wins.sort_values("pnl", ascending=False).iterrows(), 1):
        w(f"| {n} | {t.symbol} | {t.setup} | {t.entry_date:%Y-%m-%d} → {t.exit_date:%Y-%m-%d} "
          f"| {t.hold_days} | {t.qty} | **{inr(t.pnl)}** | {t.R:.2f} "
          f"| {EXIT_WHY.get(t.exit_reason, t.exit_reason)} |")
    w("")

    # ---- losers ----
    w("## 6. Every losing trade")
    w("")
    w("| # | Symbol | Setup | In → Out | Days | Qty | P&L | R | Exit |")
    w("|---|---|---|---|---|---|---|---|---|")
    for n, (_, t) in enumerate(losses.sort_values("pnl").iterrows(), 1):
        w(f"| {n} | {t.symbol} | {t.setup} | {t.entry_date:%Y-%m-%d} → {t.exit_date:%Y-%m-%d} "
          f"| {t.hold_days} | {t.qty} | {inr(t.pnl)} | {t.R:.2f} "
          f"| {EXIT_WHY.get(t.exit_reason, t.exit_reason)} |")
    w("")
    w("---")
    w("*Losses are capped by structural stops near −1R; the right tail is left uncapped "
      "by the trailing exit. That asymmetry — small bounded losses, large open-ended wins — "
      "is the entire engine.*")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {OUT}  ({len(df)} trades)")
    print(f"Net P&L {inr(df.pnl.sum())} | win {df.win.mean()*100:.1f}% | "
          f"PF {gross_p/abs(gross_l):.2f}")
    print(f"Top 5 trades = {top5.pnl.sum()/df.pnl.sum()*100:.0f}% of net P&L")


if __name__ == "__main__":
    main()
