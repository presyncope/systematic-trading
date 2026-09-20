"""Settings loading: secrets from .env, everything else from config.toml.

- .env            : TOSS_CLIENT_ID / TOSS_CLIENT_SECRET (gitignored)
- config.toml     : non-secret settings such as base_url, token_cache, db, export paths (committed)

Both are located from the repo root, independent of cwd.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

__all__ = [
    "CONFIG_PATH",
    "DEFAULTS",
    "REPO_ROOT",
    "adjustments_path",
    "base_url",
    "credentials",
    "db_path",
    "load",
    "token_cache_path",
    "tradesviz_csv_path",
]

# brokers/toss/config.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config.toml"

DEFAULTS: dict[str, str] = {
    "base_url": "https://openapi.tossinvest.com",
    "token_cache": ".toss_token.json",
    "db": "data/toss/orders.sqlite",
    "tradesviz_csv": "data/toss/tradesviz_executions.csv",
    "adjustments": "data/toss/adjustments.toml",
}

_settings: dict[str, str] = {}


def load(path: Path | None = None) -> dict[str, str]:
    """Read the [toss] section of config.toml over DEFAULTS. Falls back to DEFAULTS if the file is missing."""
    global _settings
    path = path or CONFIG_PATH
    merged = dict(DEFAULTS)
    if path.exists():
        with path.open("rb") as f:
            merged.update(tomllib.load(f).get("toss", {}))
    _settings = merged
    return _settings


def _get(key: str) -> str:
    if not _settings:
        load()
    return _settings[key]


def _resolve(p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else REPO_ROOT / path


def base_url() -> str:
    return _get("base_url").rstrip("/")


def token_cache_path() -> Path:
    return _resolve(_get("token_cache"))


def db_path() -> Path:
    return _resolve(_get("db"))


def tradesviz_csv_path() -> Path:
    return _resolve(_get("tradesviz_csv"))


def adjustments_path() -> Path:
    return _resolve(_get("adjustments"))


def credentials() -> tuple[str | None, str | None]:
    """Load .env and return (client_id, client_secret). Each is None if unset."""
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get("TOSS_CLIENT_ID"), os.environ.get("TOSS_CLIENT_SECRET")
