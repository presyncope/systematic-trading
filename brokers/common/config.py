"""Settings shared by every broker: config.toml sections and .env secrets.

- .env         : secrets (gitignored). Broker credentials plus GHOSTFOLIO_ACCESS_TOKEN,
                 NOTIFY_WEBHOOK_URL, TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID.
- config.toml  : non-secret settings (committed). One section per broker ([toss]) read via
                 broker_settings(); [ghostfolio] url; [tradesviz] sync_dir.

Both are located from the repo root, independent of cwd. A broker's config module wraps
broker_settings() with typed getters for its own section.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

__all__ = [
    "CONFIG_PATH",
    "GHOSTFOLIO_DEFAULTS",
    "REPO_ROOT",
    "broker_settings",
    "env",
    "ghostfolio_access_token",
    "ghostfolio_url",
    "load",
    "notify_webhook_url",
    "resolve",
    "section",
    "telegram_credentials",
    "tradesviz_sync_dir",
]

# brokers/common/config.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config.toml"

GHOSTFOLIO_DEFAULTS: dict[str, str] = {"url": "http://127.0.0.1:3333"}

_doc: dict | None = None


def load(path: Path | None = None) -> dict:
    """Read config.toml (an absent file means no settings) and return the whole document."""
    global _doc
    path = path or CONFIG_PATH
    doc: dict = {}
    if path.exists():
        with path.open("rb") as f:
            doc = tomllib.load(f)
    _doc = doc
    return doc


def section(name: str) -> dict:
    """A raw section of config.toml ({} if absent)."""
    if _doc is None:
        load()
    assert _doc is not None
    return dict(_doc.get(name, {}))


def broker_settings(name: str, defaults: dict[str, str]) -> dict[str, str]:
    """[name] section over its defaults."""
    merged = dict(defaults)
    merged.update(section(name))
    return merged


def resolve(p: str) -> Path:
    """A config path: relative ones are taken from the repo root."""
    path = Path(p)
    return path if path.is_absolute() else REPO_ROOT / path


def env(key: str) -> str | None:
    """A .env / environment value, None when unset or empty."""
    load_dotenv(REPO_ROOT / ".env")
    return os.environ.get(key) or None


def ghostfolio_url() -> str:
    gf = dict(GHOSTFOLIO_DEFAULTS)
    gf.update(section("ghostfolio"))
    return gf["url"].rstrip("/")


def ghostfolio_access_token() -> str | None:
    """The security token Ghostfolio showed at first login, from .env. None if unset."""
    return env("GHOSTFOLIO_ACCESS_TOKEN")


def tradesviz_sync_dir() -> Path | None:
    """Folder the TradesViz CSV is copied to (e.g. a Google Drive sync folder). None if unset."""
    value = section("tradesviz").get("sync_dir")
    return resolve(value) if value else None


def notify_webhook_url() -> str | None:
    """Discord or Slack incoming-webhook URL for job notifications, from .env. None if unset."""
    return env("NOTIFY_WEBHOOK_URL")


def telegram_credentials() -> tuple[str | None, str | None]:
    """(bot token, chat id) for Telegram notifications, from .env. Each is None if unset."""
    return env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_CHAT_ID")
