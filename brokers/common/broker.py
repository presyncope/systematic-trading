"""What the shared export pipeline needs from a broker integration.

A broker package implements Broker once (brokers/toss/broker.py) and hands it to
pipeline.run() and the exporters' main(); everything else in brokers/common is written
against this interface only.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

from brokers.common.models import Holding
from brokers.common.splits import CandleSource
from brokers.common.store import FillSource

__all__ = ["AuthError", "Broker"]


class AuthError(RuntimeError):
    """Credentials missing or rejected; the message says what to fix."""


class Broker(Protocol):
    name: str  # config section and data directory: "toss"
    label: str  # in messages: "Toss"
    backfill_command: str  # what to run when the DB is empty: "toss-backfill-orders"
    # CLI option that selects the broker account: "--account-seq". Not "--account", which the
    # Ghostfolio exporter uses for the Ghostfolio account name.
    account_flag: str
    account_help: str
    holdings_source: str  # in messages: "GET /api/v1/holdings"
    ghostfolio_account: str  # default Ghostfolio account name

    def db_path(self) -> Path: ...
    def adjustments_path(self) -> Path: ...
    def tradesviz_csv_path(self) -> Path: ...
    def ghostfolio_json_path(self) -> Path: ...

    def open_store(self, path: Path) -> FillSource: ...

    def normalize_account(self, requested: str) -> str:
        """The account id as the store spells it ("01" -> "1" for Toss). Raises ValueError if malformed."""
        ...

    def connect(self) -> Any:
        """An authenticated API client (closed by the caller). Raises AuthError."""
        ...

    def close(self, client: Any) -> None: ...

    def is_api_error(self, exc: BaseException) -> bool:
        """True for the client's API error type (reported as exit 1 rather than a traceback)."""
        ...

    def candle_source(self, client: Any) -> CandleSource | None:
        """Daily candles for split detection; None when the broker has no usable price feed."""
        ...

    def session_date(self, filled_at: str) -> date:
        """Exchange-local session date of a fill, for fills that do not state one."""
        ...

    def holdings(self, client: Any, account: str) -> list[Holding]: ...

    def cash(self, client: Any, account: str, currency: str) -> Decimal:
        """Cash balance in `currency` (buying power / deposit), for the Ghostfolio account balance."""
        ...
