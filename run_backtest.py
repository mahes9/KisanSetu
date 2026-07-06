"""Backtest CLI.

Usage:
    python run_backtest.py --start 2018-01-01
"""

import argparse
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent / "src"))

from swing import backtest, report  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Nifty 200 swing backtest")
    ap.add_argument("--start", default=None, help="YYYY-MM-DD (default from config)")
    ap.add_argument("--end", default=None)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    result = backtest.run(start=args.start, end=args.end)
    print(report.render(result))
    png, csv = report.save_outputs(result)
    print(f"\nequity curve: {png}\ntrades:       {csv}")


if __name__ == "__main__":
    main()
