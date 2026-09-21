"""KIS as a brokers.common.broker.Broker: what the shared pipeline and exporters call.

Two currencies live in one KIS account (USD for US stocks, KRW for KRX), so the Ghostfolio side
gets one account per currency ("KIS", "KIS KRW") and per-currency export files. Holdings come
from TTTS3012R (overseas, USD) and TTTC8434R (domestic); cash from CTRP6504R (foreign
currencies) and TTTC8434R (KRW 예수금); KRW dividends from the rights table (CTRGA011R, see
brokers/kis/rights.py). Split detection has no candle source yet.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from brokers.common.broker import AuthError
from brokers.common.models import Dividend, Holding
from brokers.common.store import FillSource
from brokers.kis import auth, config, rights
from brokers.kis.client import KisApiError, KisClient
from brokers.kis.store import KisStore, account_key

__all__ = ["KIS", "KisBroker"]

log = logging.getLogger("kis.broker")

KST = ZoneInfo("Asia/Seoul")


def _currency_path(path: Path, currency: str | None) -> Path:
    """data/kis/x.json -> data/kis/x_krw.json for a non-USD export (one file per currency)."""
    if currency in (None, "USD"):
        return path
    return path.with_name(f"{path.stem}_{currency.lower()}{path.suffix}")


class KisBroker:
    name = "kis"
    label = "KIS"
    backfill_command = "kis-backfill"
    account_flag = "--kis-account"
    account_help = "CANO-PRDT such as 12345678-01. Auto-selected if the DB has only one"
    holdings_source = "TTTS3012R / TTTC8434R"

    def db_path(self) -> Path:
        return config.db_path()

    def adjustments_path(self) -> Path:
        return config.adjustments_path()

    def tradesviz_csv_path(self, currency: str | None) -> Path:
        return _currency_path(config.tradesviz_csv_path(), currency)

    def ghostfolio_json_path(self, currency: str | None) -> Path:
        return _currency_path(config.ghostfolio_json_path(), currency)

    def ghostfolio_account(self, currency: str) -> str:
        return "KIS" if currency == "USD" else f"KIS {currency}"

    def ghostfolio_symbol(self, store: FillSource, symbol: str, currency: str) -> str:
        if currency != "KRW":
            return symbol
        assert isinstance(store, KisStore)
        info = store.instruments().get(symbol)
        return info["yahoo_symbol"] if info else f"{symbol}.KS"

    def open_store(self, path: Path) -> KisStore:
        return KisStore(path)

    def normalize_account(self, requested: str) -> str:
        return account_key(config.parse_account(requested))

    def connect(self) -> KisClient:
        try:
            return KisClient()
        except auth.KisAuthError as e:
            raise AuthError(str(e)) from e

    def close(self, client: KisClient) -> None:
        client.close()

    def is_api_error(self, exc: BaseException) -> bool:
        return isinstance(exc, KisApiError)

    def candle_source(self, client: KisClient) -> None:
        return None  # no split detection for KIS yet: the holdings check is the only guard

    def session_date(self, filled_at: str) -> date:
        # Every KIS fill states its session date (ord_dt); this is only a fallback.
        return datetime.fromisoformat(filled_at).astimezone(KST).date()

    def holdings(self, client: KisClient, account: str) -> list[Holding]:
        acct = config.parse_account(account)
        out: list[Holding] = []
        for page in client.overseas_balance(acct):
            for h in page.get("output1") or []:
                qty = Decimal(h.get("ovrs_cblc_qty") or "0")
                if qty:
                    out.append(Holding(h["ovrs_pdno"], qty, h.get("tr_crcy_cd", "USD"), h.get("ovrs_item_name", "")))
        for page in client.domestic_balance(acct):
            for h in page.get("output1") or []:
                qty = Decimal(h.get("hldg_qty") or "0")
                if qty:
                    out.append(Holding(h["pdno"], qty, "KRW", h.get("prdt_name", "")))
        return out

    def dividends(self, store: FillSource, account: str, currency: str) -> list[Dividend]:
        if currency != "KRW":
            return []  # CTRGA011R is domestic; the API has no overseas dividend record
        assert isinstance(store, KisStore)
        paid, pending = rights.dividends(store.rights(account), today=date.today())
        for r in pending:
            log.info(
                "%s %s dividend of %s KRW is not payable until %s; not exported",
                r["bass_dt"],
                r["pdno"],
                r["alct_amt"],
                r["cash_dfrm_dt"],
            )
        estimated = [d for d in paid if d.estimated_tax]
        if estimated:
            log.warning(
                "%d dividend(s) had no tax figure from KIS; withholding estimated at %s%%: %s",
                len(estimated),
                rights.WITHHOLDING_RATE * 100,
                ", ".join(f"{d.paid_on} {d.symbol} {d.amount}-{d.tax}" for d in estimated),
            )
        return paid

    def cash(self, client: KisClient, account: str, currency: str) -> Decimal:
        acct = config.parse_account(account)
        if currency == "KRW":
            pages = client.domestic_balance(acct)
            totals = (pages[-1].get("output2") or [{}])[0] if pages else {}
            return Decimal(totals.get("dnca_tot_amt") or "0")
        for row in client.overseas_present_balance(acct).get("output2") or []:
            if row.get("crcy_cd") == currency:
                return Decimal(row.get("frcr_dncl_amt_2") or "0")
        raise KisApiError(0, "no-balance", f"CTRP6504R has no {currency} balance row", "CTRP6504R")


KIS = KisBroker()
