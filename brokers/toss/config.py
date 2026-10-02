"""Toss settings: the [toss] section of config.toml plus TOSS_* secrets from .env.

Shared settings (Ghostfolio, TradesViz, notifications) live in brokers/common/config.py and are
re-exported here for the modules that still import them from this package.
"""

from __future__ import annotations

from pathlib import Path

from brokers.common import config as common
from brokers.common.config import (
    CONFIG_PATH,
    REPO_ROOT,
    ghostfolio_access_token,
    ghostfolio_url,
    notify_webhook_url,
    section,
    telegram_credentials,
    tradesviz_sync_dir,
)

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
    "portfolio_json_path",
    "notify_webhook_url",
    "section",
    "telegram_credentials",
    "token_cache_path",
    "tradesviz_csv_path",
    "tradesviz_sync_dir",
]

SECTION = "toss"

DEFAULTS: dict[str, str] = {
    "base_url": "https://openapi.tossinvest.com",
    "token_cache": ".toss_token.json",
    "db": "data/toss/orders.sqlite",
    "tradesviz_csv": "data/toss/tradesviz_executions.csv",
    "ghostfolio_json": "data/toss/ghostfolio_activities.json",
    "adjustments": "data/toss/adjustments.toml",
    "portfolio_json": "data/toss/portfolio.json",
}


def load(path: Path | None = None) -> dict[str, str]:
    """(Re)read config.toml and return the [toss] settings over DEFAULTS."""
    common.load(path)
    return common.broker_settings(SECTION, DEFAULTS)


def _get(key: str) -> str:
    return common.broker_settings(SECTION, DEFAULTS)[key]


def base_url() -> str:
    return _get("base_url").rstrip("/")


def token_cache_path() -> Path:
    return common.resolve(_get("token_cache"))


def db_path() -> Path:
    return common.resolve(_get("db"))


def tradesviz_csv_path() -> Path:
    return common.resolve(_get("tradesviz_csv"))


def ghostfolio_json_path() -> Path:
    return common.resolve(_get("ghostfolio_json"))


def portfolio_json_path() -> Path:
    return common.resolve(_get("portfolio_json"))


def adjustments_path() -> Path:
    return common.resolve(_get("adjustments"))


def credentials() -> tuple[str | None, str | None]:
    """(client_id, client_secret) from .env. Each is None if unset."""
    return common.env("TOSS_CLIENT_ID"), common.env("TOSS_CLIENT_SECRET")
