"""Evening screener CLI.

Usage:
    python run_screener.py                       # daily scan
    python run_screener.py --refresh-fundamentals  # quarterly focus-list rebuild
"""

import argparse
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent / "src"))

from swing import screener  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Nifty 200 swing screener")
    ap.add_argument("--refresh-fundamentals", action="store_true",
                    help="rebuild the focus list from live fundamentals (slow, quarterly)")
    ap.add_argument("--delivery-days", type=int, default=45,
                    help="rolling delivery-cache window")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    result = screener.run(
        refresh_fundamentals=args.refresh_fundamentals,
        delivery_days=args.delivery_days,
    )
    print(screener.render(result))
    saved = screener.save_journal(result)
    if saved:
        print(f"\ncandidates journalled to {saved}")


if __name__ == "__main__":
    main()
