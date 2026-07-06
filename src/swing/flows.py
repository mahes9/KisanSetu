"""Layer 4 live data — FII/DII flows, veto lists, bulk deals.

All functions accept an NseSession and return None when NSE is unavailable;
the screener prints the layer as "n/a" and carries on (structure-only mode).
"""

from __future__ import annotations

import logging

from .nse import NseSession

log = logging.getLogger(__name__)


def fii_dii(ns: NseSession) -> dict | None:
    """Latest day FII/DII cash net buy (₹ cr): {'fii': x, 'dii': y}."""
    js = ns.get_json("/api/fiidiiTradeReact")
    if not isinstance(js, list):
        return None
    out = {}
    for row in js:
        cat = str(row.get("category", "")).upper()
        try:
            net = float(str(row.get("netValue", "0")).replace(",", ""))
        except ValueError:
            continue
        if "FII" in cat or "FPI" in cat:
            out["fii"] = net
        elif "DII" in cat:
            out["dii"] = net
    return out or None


def fo_ban_list(ns: NseSession) -> set[str] | None:
    """F&O ban list from the archives CSV (the /api endpoint was retired).
    Format: a title line, then `n,SYMBOL` rows."""
    import requests

    from .nse import HEADERS

    try:
        r = requests.get(
            "https://nsearchives.nseindia.com/content/fo/fo_secban.csv",
            headers=HEADERS, timeout=15,
        )
        r.raise_for_status()
    except Exception as e:  # noqa: BLE001
        log.warning("fo_secban fetch failed: %s", e)
        return None
    syms: set[str] = set()
    for line in r.text.splitlines()[1:]:
        parts = [p.strip().upper() for p in line.split(",") if p.strip()]
        if len(parts) >= 2 and parts[-1].isalpha():
            syms.add(parts[-1])
        elif len(parts) == 1 and parts[0].isalpha():
            syms.add(parts[0])
    return syms


def asm_list(ns: NseSession) -> set[str] | None:
    js = ns.get_json("/api/reportASM")
    if not isinstance(js, dict):
        return None
    syms: set[str] = set()
    for key in ("longterm", "shortterm"):
        section = js.get(key) or {}
        for r in section.get("data") or []:
            sym = str(r.get("symbol", "")).strip().upper()
            if sym:
                syms.add(sym)
    return syms


def gsm_list(ns: NseSession) -> set[str] | None:
    js = ns.get_json("/api/reportGSM")
    if isinstance(js, dict):
        rows = js.get("data") or []
        return {str(r.get("symbol", "")).strip().upper() for r in rows if r.get("symbol")}
    return None


def bulk_deals(ns: NseSession) -> list[dict] | None:
    """Today's large deals (bulk+block) — [{symbol, client, side, qty}]."""
    js = ns.get_json("/api/snapshot-capital-market-largedeal")
    if not isinstance(js, dict):
        return None
    out = []
    for section in ("BULK_DEALS_DATA", "BLOCK_DEALS_DATA", "bulkDeals", "blockDeals"):
        for r in js.get(section) or []:
            out.append(
                {
                    "symbol": str(r.get("symbol", "")).strip().upper(),
                    "client": r.get("name") or r.get("clientName"),
                    "side": (r.get("buySell") or r.get("transactionType") or "").upper(),
                    "qty": r.get("qty") or r.get("quantityTraded"),
                }
            )
    return out


def veto_symbols(ns: NseSession) -> tuple[set[str], dict[str, str]]:
    """Union of ASM/GSM/F&O-ban symbols + reason map. Empty if NSE is down
    (the playbook then requires a manual check)."""
    reasons: dict[str, str] = {}
    for name, fn in (("ASM", asm_list), ("GSM", gsm_list), ("F&O ban", fo_ban_list)):
        got = fn(ns)
        if got is None:
            log.warning("%s list unavailable", name)
            continue
        for s in got:
            reasons[s] = f"{reasons.get(s)} + {name}" if s in reasons else name
    return set(reasons), reasons
