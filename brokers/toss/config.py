"""Settings loading: secrets from .env, everything else from config.toml.

- .env            : TOSS_CLIENT_ID / TOSS_CLIENT_SECRET, GHOSTFOLIO_ACCESS_TOKEN (gitignored)
- config.toml     : non-secret settings: [toss] base_url, token_cache, db, export paths;
                    [ghostfolio] url (committed)

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
    "ghostfolio_access_token",
    "ghostfolio_json_path",
    "ghostfolio_url",
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
    "ghostfolio_json": "data/toss/ghostfolio_activities.json",
    "adjustments": "data/toss/adjustments.toml",
}

GHOSTFOLIO_DEFAULTS: dict[str, str] = {"url": "http://127.0.0.1:3333"}

_settings: dict[str, str] = {}
_ghostfolio: dict[str, str] = {}


def load(path: Path | None = None) -> dict[str, str]:
    """Read config.toml: [toss] over DEFAULTS, [ghostfolio] over GHOSTFOLIO_DEFAULTS.
    Falls back to the defaults if the file is missing. Returns the [toss] settings."""
    global _settings, _ghostfolio
    path = path or CONFIG_PATH
    merged = dict(DEFAULTS)
    gf = dict(GHOSTFOLIO_DEFAULTS)
    if path.exists():
        with path.open("rb") as f:
            doc = tomllib.load(f)
        merged.update(doc.get("toss", {}))
        gf.update(doc.get("ghostfolio", {}))
    _settings, _ghostfolio = merged, gf
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


def ghostfolio_json_path() -> Path:
    return _resolve(_get("ghostfolio_json"))


def adjustments_path() -> Path:
    return _resolve(_get("adjustments"))


def credentials() -> tuple[str | None, str | None]:
    """Load .env and return (client_id, client_secret). Each is None if unset."""
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get("TOSS_CLIENT_ID"), os.environ.get("TOSS_CLIENT_SECRET")


def ghostfolio_url() -> str:
    if not _ghostfolio:
        load()
    return _ghostfolio["url"].rstrip("/")


def ghostfolio_access_token() -> str | None:
    """The security token Ghostfolio showed at first login, from .env. None if unset."""
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get("GHOSTFOLIO_ACCESS_TOKEN")
