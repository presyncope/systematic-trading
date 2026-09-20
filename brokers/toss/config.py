"""Settings loading: secrets from .env, everything else from config.toml.

- .env            : TOSS_CLIENT_ID / TOSS_CLIENT_SECRET, GHOSTFOLIO_ACCESS_TOKEN, NOTIFY_WEBHOOK_URL,
                    TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID (gitignored)
- config.toml     : non-secret settings: [toss] base_url, token_cache, db, export paths;
                    [ghostfolio] url; [tradesviz] sync_dir (committed)

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
    "notify_webhook_url",
    "section",
    "telegram_credentials",
    "token_cache_path",
    "tradesviz_csv_path",
    "tradesviz_sync_dir",
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
_doc: dict = {}


def load(path: Path | None = None) -> dict[str, str]:
    """Read config.toml: [toss] over DEFAULTS, [ghostfolio] over GHOSTFOLIO_DEFAULTS, other sections
    as-is. Falls back to the defaults if the file is missing. Returns the [toss] settings."""
    global _settings, _ghostfolio, _doc
    path = path or CONFIG_PATH
    merged = dict(DEFAULTS)
    gf = dict(GHOSTFOLIO_DEFAULTS)
    doc: dict = {}
    if path.exists():
        with path.open("rb") as f:
            doc = tomllib.load(f)
        merged.update(doc.get("toss", {}))
        gf.update(doc.get("ghostfolio", {}))
    _settings, _ghostfolio, _doc = merged, gf, doc
    return _settings


def section(name: str) -> dict:
    """A raw section of config.toml ({} if absent)."""
    if not _settings:
        load()
    return dict(_doc.get(name, {}))


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


def tradesviz_sync_dir() -> Path | None:
    """Folder the TradesViz CSV is copied to (e.g. a Google Drive sync folder). None if unset."""
    value = section("tradesviz").get("sync_dir")
    return _resolve(value) if value else None


def notify_webhook_url() -> str | None:
    """Discord or Slack incoming-webhook URL for job notifications, from .env. None if unset."""
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get("NOTIFY_WEBHOOK_URL")


def telegram_credentials() -> tuple[str | None, str | None]:
    """(bot token, chat id) for Telegram notifications, from .env. Each is None if unset."""
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get("TELEGRAM_BOT_TOKEN") or None, os.environ.get("TELEGRAM_CHAT_ID") or None
