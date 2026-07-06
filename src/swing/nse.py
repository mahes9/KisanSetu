"""Thin NSE web-API client with cookie warm-up and graceful degradation.

NSE's www endpoints want a browser-ish session (cookies from the homepage)
and will throttle/block bursts. Every helper returns None on failure — the
screener treats missing live layers as "unavailable", never as fatal.
"""

from __future__ import annotations

import logging
import time

import requests

log = logging.getLogger(__name__)

BASE = "https://www.nseindia.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json,text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


class NseSession:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update(HEADERS)
        self._warm = False

    def warmup(self) -> bool:
        if self._warm:
            return True
        try:
            r = self.s.get(BASE, timeout=15)
            # NSE sometimes 403s the homepage yet still sets the cookies the
            # API endpoints need — any response with cookies counts as warm.
            time.sleep(0.5)
            if not self.s.cookies:
                self.s.get(f"{BASE}/option-chain", timeout=15)
                time.sleep(0.5)
            self._warm = bool(self.s.cookies) or r.status_code == 200
        except Exception as e:  # noqa: BLE001
            log.warning("NSE warmup failed: %s", e)
        return self._warm

    def get_json(self, path: str, retries: int = 2) -> dict | list | None:
        if not self.warmup():
            return None
        url = f"{BASE}{path}"
        for attempt in range(retries + 1):
            try:
                r = self.s.get(url, timeout=20)
                if r.status_code in (401, 403):
                    self._warm = False  # cookies expired — re-warm once
                    if not self.warmup():
                        return None
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as e:  # noqa: BLE001
                if attempt == retries:
                    log.warning("NSE GET %s failed: %s", path, e)
                    return None
                time.sleep(1.0 + attempt)
        return None
