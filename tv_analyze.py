"""TradingView chart screenshot tool for SMC swing analysis.

Login (one-time):  python tv_analyze.py --login

Single pair:       python tv_analyze.py EURGBP
                   python tv_analyze.py EURGBP --tf 4h

SMC workflow:      python tv_analyze.py EURUSD --smc
                   (captures W1, D1, H4 for the pair)

All pairs:         python tv_analyze.py --scan
                   (captures W1, D1, H4 for all watchlist pairs)

Custom watchlist:  python tv_analyze.py --scan --pairs EURUSD,GBPUSD,XAUUSD

Analyze image:     python tv_analyze.py --image path/to/chart.png
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SCREENSHOTS_DIR = PROJECT_ROOT / "data" / "tv_screenshots"
PW_PROFILE = PROJECT_ROOT / "data" / "tv_browser"

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

TIMEFRAME_MAP = {
    "1m": "1", "3m": "3", "5m": "5", "15m": "15", "30m": "30", "45m": "45",
    "1h": "60", "2h": "120", "3h": "180", "4h": "240",
    "1d": "D", "1w": "W", "1M": "M",
    "D": "D", "W": "W", "M": "M",
}

SMC_TIMEFRAMES = ["1w", "1d", "4h", "1h", "15m"]

DEFAULT_WATCHLIST = [
    # Major pairs
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD",
    "AUDUSD", "NZDUSD",
    # Crosses
    "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "EURCAD",
    "GBPCAD", "AUDCAD", "AUDJPY", "NZDJPY", "CADJPY", "CHFJPY",
    # Metals
    "XAUUSD",
    # Indices
    "US30USD", "NAS100USD",
]

DEFAULT_PROMPT = """Analyze this TradingView chart with Luxalgo Smart Money Concepts indicator.

Identify and describe:
1. **Market Structure** -- current trend (HH/HL or LH/LL), any CHoCH or BOS
2. **Order Blocks** -- active bullish/bearish OBs visible on chart
3. **Fair Value Gaps (FVGs)** -- any unfilled imbalances
4. **Liquidity** -- buy-side/sell-side liquidity pools, equal highs/lows
5. **Key Levels** -- support/resistance, premium/discount zones
6. **Bias** -- overall directional bias with reasoning
7. **Trade Setup** -- if a clean setup exists, specify entry zone, stop loss, and targets

Be specific about price levels. Reference what the SMC indicator is showing."""


def load_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    print("ERROR: Set ANTHROPIC_API_KEY env var or add it to .env")
    sys.exit(1)


VIEWPORT_W = 1920
VIEWPORT_H = 1080
DEVICE_SCALE = 2          # 2× DPR → effective 3840×2160 pixels saved to disk


def _make_context(pw):
    PW_PROFILE.mkdir(parents=True, exist_ok=True)
    return pw.chromium.launch_persistent_context(
        str(PW_PROFILE),
        executable_path=CHROME_EXE,
        headless=False,
        viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
        device_scale_factor=DEVICE_SCALE,
        args=["--disable-extensions"],
    )


def login_flow() -> None:
    from playwright.sync_api import sync_playwright

    print("Opening TradingView sign-in page...")
    print(">>> Use EMAIL login, NOT 'Continue with Google'")
    print(">>> Close the browser when logged in.")

    with sync_playwright() as pw:
        ctx = _make_context(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.tradingview.com/accounts/signin/", wait_until="networkidle")
        print("\nWaiting for you to log in and close the browser...")
        try:
            page.wait_for_event("close", timeout=300_000)
        except Exception:
            pass
        ctx.close()
    print("Session saved!")


def get_exchange(symbol: str) -> str:
    if symbol in ("XAUUSD", "XAGUSD"):
        return "OANDA"
    if symbol in ("US30USD", "NAS100USD", "SPX500USD"):
        return "OANDA"
    return "FX"


def capture_batch(
    pairs_timeframes: list[tuple[str, str]],
    wait: int,
) -> list[tuple[str, str, Path]]:
    """Capture multiple pair+timeframe combos in a single browser session.

    Saves one file per chart at 2× DPR (effective 3840×2160 on disk).
    Returns list of (symbol, tf_label, screenshot_path).
    """
    from playwright.sync_api import sync_playwright

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    total = len(pairs_timeframes)
    print(f"\nCapturing {total} charts (2x resolution)...")

    with sync_playwright() as pw:
        ctx = _make_context(pw)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for idx, (symbol, tf) in enumerate(pairs_timeframes, 1):
            tf_key = tf.lower() if tf.lower() in TIMEFRAME_MAP else tf
            tv_tf = TIMEFRAME_MAP.get(tf_key, tf)
            exchange = get_exchange(symbol)
            tv_symbol = f"{exchange}:{symbol}"
            url = f"https://www.tradingview.com/chart/?symbol={tv_symbol}&interval={tv_tf}"

            ts = time.strftime("%Y%m%d_%H%M%S")
            shot_path = SCREENSHOTS_DIR / f"{symbol}_{tv_tf}_{ts}.png"

            print(f"  [{idx}/{total}] {symbol} @ {tf} ...", end=" ", flush=True)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(wait * 1000)

            page.evaluate("""() => {
                document.querySelectorAll('[class*="cookie"], [class*="consent"], [class*="banner"]')
                    .forEach(el => { try { el.remove(); } catch {} });
            }""")
            page.wait_for_timeout(500)

            # Close any open dialogs, then zoom in slightly via mouse wheel
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
            # Hover over chart center (left third to avoid right panel) and scroll up to zoom in
            page.mouse.move(VIEWPORT_W // 3, VIEWPORT_H // 2)
            page.mouse.wheel(0, -300)   # scroll up = zoom in (fewer candles, larger labels)
            page.mouse.wheel(0, -300)
            page.mouse.wheel(0, -300)
            page.mouse.wheel(0, -300)
            page.wait_for_timeout(400)

            page.screenshot(path=str(shot_path), full_page=False)
            print(f"saved")

            results.append((symbol, tf, shot_path))

        ctx.close()

    return results


def analyze_chart(image_path: Path, prompt: str, api_key: str) -> str:
    import anthropic

    img_bytes = image_path.read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode()
    client = anthropic.Anthropic(api_key=api_key)

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return resp.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(description="TradingView chart -> SMC analysis")
    parser.add_argument("symbol", nargs="?", help="Symbol (e.g. EURGBP, XAUUSD)")
    parser.add_argument("--tf", default="1D", help="Timeframe (default: 1D)")
    parser.add_argument("--exchange", help="Exchange prefix (auto-detected if omitted)")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Analysis prompt")
    parser.add_argument("--wait", type=int, default=18, help="Seconds to wait for chart load (default: 18)")
    parser.add_argument("--screenshot-only", action="store_true", help="Just capture, skip analysis")
    parser.add_argument("--image", type=str, help="Analyze an existing screenshot")
    parser.add_argument("--all-tf", action="store_true", help="Capture 15m, 1H, 4H, 1D")
    parser.add_argument("--smc", action="store_true", help="SMC workflow: capture W1, D1, H4")
    parser.add_argument("--scan", action="store_true", help="Scan all watchlist pairs (W1, D1, H4 each)")
    parser.add_argument("--pairs", type=str, help="Comma-separated pair list for --scan")
    parser.add_argument("--login", action="store_true", help="Open browser for TradingView login")
    args = parser.parse_args()

    if args.login:
        login_flow()
        return

    if args.image:
        img_path = Path(args.image)
        if not img_path.exists():
            print(f"ERROR: Image not found: {args.image}")
            sys.exit(1)
        api_key = load_api_key()
        analysis = analyze_chart(img_path, args.prompt, api_key)
        print("\n" + "=" * 70)
        print(f"  CHART ANALYSIS -- {img_path.stem}")
        print("=" * 70)
        print(analysis)
        print("=" * 70)
        return

    # Build the capture list
    jobs: list[tuple[str, str]] = []

    if args.scan:
        pairs = args.pairs.split(",") if args.pairs else DEFAULT_WATCHLIST
        pairs = [p.strip().upper() for p in pairs]
        for pair in pairs:
            for tf in SMC_TIMEFRAMES:
                jobs.append((pair, tf))
    elif args.symbol:
        symbol = args.symbol.upper()
        if args.smc:
            for tf in SMC_TIMEFRAMES:
                jobs.append((symbol, tf))
        elif args.all_tf:
            for tf in ["15m", "1h", "4h", "1d"]:
                jobs.append((symbol, tf))
        else:
            jobs.append((symbol, args.tf))
    else:
        parser.print_help()
        sys.exit(1)

    results = capture_batch(jobs, args.wait)

    if args.screenshot_only:
        print(f"\nDone. {len(results)} screenshots captured.")
        current_pair = None
        for symbol, tf, path in results:
            if symbol != current_pair:
                print(f"\n  {symbol}:")
                current_pair = symbol
            print(f"    {tf}: {path}")
        return

    api_key = load_api_key()
    for symbol, tf, img_path in results:
        analysis = analyze_chart(img_path, args.prompt, api_key)
        print("\n" + "=" * 70)
        print(f"  CHART ANALYSIS -- {symbol} @ {tf}")
        print("=" * 70)
        print(analysis)
        print("=" * 70)
        print()


if __name__ == "__main__":
    main()
