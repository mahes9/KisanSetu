"""Load config.yaml from the project root."""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@functools.lru_cache(maxsize=1)
def load(path: str | Path | None = None) -> dict:
    cfg_path = Path(path) if path else PROJECT_ROOT / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cache_dir() -> Path:
    d = PROJECT_ROOT / load()["data"]["cache_dir"]
    d.mkdir(parents=True, exist_ok=True)
    return d
