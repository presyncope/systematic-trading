"""Toss as a brokers.common.broker.Broker: what the shared pipeline and exporters call."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from brokers.common import ledger
from brokers.common.broker import AuthError
from brokers.common.models import Holding
from brokers.toss import auth, config
from brokers.toss.candles import TossCandleSource
from brokers.toss.client import TossApiError, TossClient
from brokers.toss.store import OrderStore

__all__ = ["TOSS", "TossBroker"]


class TossBroker:
    name = "toss"
    label = "Toss"
    backfill_command = "toss-backfill-orders"
    account_flag = "--account-seq"
    account_help = "accountSeq. Auto-selected if the DB has only one"
    holdings_source = "GET /api/v1/holdings"
    ghostfolio_account = "Toss"

    def db_path(self) -> Path:
        return config.db_path()

    def adjustments_path(self) -> Path:
        return config.adjustments_path()

    def tradesviz_csv_path(self) -> Path:
        return config.tradesviz_csv_path()

    def ghostfolio_json_path(self) -> Path:
        return config.ghostfolio_json_path()

    def open_store(self, path: Path) -> OrderStore:
        return OrderStore(path)

    def normalize_account(self, requested: str) -> str:
        return str(int(requested))

    def connect(self) -> TossClient:
        try:
            return TossClient()
        except auth.TossAuthError as e:
            raise AuthError(str(e)) from e

    def close(self, client: TossClient) -> None:
        client.close()

    def is_api_error(self, exc: BaseException) -> bool:
        return isinstance(exc, TossApiError)

    def candle_source(self, client: TossClient) -> TossCandleSource:
        return TossCandleSource(client)

    def session_date(self, filled_at: str) -> date:
        return ledger.us_session_date(filled_at)

    def holdings(self, client: TossClient, account: str) -> list[Holding]:
        items = client.get_holdings(int(account)).get("items") or []
        return [Holding(h["symbol"], Decimal(h["quantity"]), h.get("currency", ""), h.get("name", "")) for h in items]

    def cash(self, client: TossClient, account: str, currency: str) -> Decimal:
        return client.get_buying_power(int(account), currency)


TOSS = TossBroker()
