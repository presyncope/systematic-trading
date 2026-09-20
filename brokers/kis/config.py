"""KIS settings: the [kis] section of config.toml plus KIS_* secrets from .env.

- KIS_APP_KEY / KIS_APP_SECRET : live-trading app key pair from KIS Developers
- KIS_ACCOUNT                  : "12345678-01" = 종합계좌번호(CANO) - 계좌상품코드(ACNT_PRDT_CD)
"""

from __future__ import annotations

import re
from pathlib import Path

from brokers.common import config as common

__all__ = [
    "DEFAULTS",
    "SECTION",
    "Account",
    "account",
    "adjustments_path",
    "base_url",
    "credentials",
    "db_path",
    "ghostfolio_json_path",
    "load",
    "parse_account",
    "token_cache_path",
    "tradesviz_csv_path",
]

SECTION = "kis"

DEFAULTS: dict[str, str] = {
    "base_url": "https://openapi.koreainvestment.com:9443",
    "token_cache": ".kis_token.json",
    "db": "data/kis/kis.sqlite",
    "tradesviz_csv": "data/kis/tradesviz_executions.csv",
    "ghostfolio_json": "data/kis/ghostfolio_activities.json",
    "adjustments": "data/kis/adjustments.toml",
}

# (CANO, ACNT_PRDT_CD): every account API takes the two halves as separate parameters.
type Account = tuple[str, str]

_ACCOUNT_RE = re.compile(r"^(\d{8})-?(\d{2})$")


def load(path: Path | None = None) -> dict[str, str]:
    """(Re)read config.toml and return the [kis] settings over DEFAULTS."""
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


def adjustments_path() -> Path:
    return common.resolve(_get("adjustments"))


def credentials() -> tuple[str | None, str | None]:
    """(app key, app secret) from .env. Each is None if unset."""
    return common.env("KIS_APP_KEY"), common.env("KIS_APP_SECRET")


def parse_account(text: str) -> Account:
    """ "12345678-01" (or "1234567801") -> ("12345678", "01"). Raises ValueError otherwise."""
    m = _ACCOUNT_RE.match(text.strip())
    if not m:
        raise ValueError(f"KIS account must look like 12345678-01, got {text!r}")
    return m.group(1), m.group(2)


def account() -> Account | None:
    """KIS_ACCOUNT from .env as (CANO, ACNT_PRDT_CD). None if unset."""
    value = common.env("KIS_ACCOUNT")
    return parse_account(value) if value else None
