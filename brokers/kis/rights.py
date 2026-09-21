"""Read the KIS rights table (CTRGA011R) as dividends and corporate actions (pure functions).

rght_type_cd says what the row is; the full code list is in agent-docs/kis (period-rights.md).
What this handles:

- 03 배당 / 74 배당옵션 / 75 특별배당 with a cash amount -> Dividend. `last_alct_amt` is the gross
  amount for the whole holding (`cblc_qty` shares), `cash_dfrm_dt` the payment date. Rows whose
  payment date has not arrived are left out (they are announcements, not income yet).
- 14 액면분할 / 15 액면병합 / 02 무상증자 and other share-changing rights -> reported, not applied.
  The account has never had one, so the field arithmetic (is `tot_alct_qty` the new total or only
  the extra shares?) is unverified; guessing it would silently corrupt the share basis. They are
  listed with their raw numbers so a `[[splits]]` entry can be added to adjustments.toml by hand,
  and the holdings reconciliation flags the position either way.

Withholding tax: KIS reports `tax_amt` for a dividend that has not been paid yet and 0 for every
paid one (checked on four live rows: only the pending one carried 15.4% of the gross). Korean
dividend withholding is a flat 15.4% (14% income tax + 1.4% local), so a paid dividend with no
tax figure gets that estimate, flagged as estimated. `gross=True` keeps the API's own numbers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

from brokers.common.models import Dividend

__all__ = [
    "DIVIDEND_TYPES",
    "SHARE_CHANGE_TYPES",
    "WITHHOLDING_RATE",
    "ShareChange",
    "dividends",
    "share_changes",
]

log = logging.getLogger("kis.rights")

DIVIDEND_TYPES = {"03", "3", "74", "75"}  # 배당 / 배당옵션 / 특별배당
SHARE_CHANGE_TYPES = {  # rights that change the share count: reported, never applied automatically
    "02": "무상증자",
    "2": "무상증자",
    "14": "액면분할",
    "15": "액면병합",
    "17": "감자",
    "11": "합병",
    "12": "회사분할",
    "16": "종목변경",
}
# 소득세 14% + 지방소득세 1.4%
WITHHOLDING_RATE = Decimal("0.154")


def _date(yyyymmdd: str | None) -> date | None:
    if not yyyymmdd or len(yyyymmdd) != 8:
        return None
    return date(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))


def dividends(rows: list[dict], *, today: date, gross: bool = False) -> tuple[list[Dividend], list[dict]]:
    """(paid dividends, rows still pending) from the rights table, oldest first."""
    paid: list[Dividend] = []
    pending: list[dict] = []
    for r in rows:
        if r["rght_type_cd"] not in DIVIDEND_TYPES:
            continue
        amount = Decimal(r["alct_amt"] or "0")
        if amount <= 0:
            continue  # a stock dividend, not cash: it belongs to share_changes
        pay_date = _date(r["cash_dfrm_dt"])
        if pay_date is None or pay_date > today:
            pending.append(r)
            continue
        tax = Decimal(r["tax_amt"] or "0")
        estimated = False
        if tax == 0 and not gross:
            tax = (amount * WITHHOLDING_RATE).quantize(Decimal(1), ROUND_DOWN)
            estimated = True
        paid.append(
            Dividend(
                id=f"kis:{pay_date.isoformat()}:{r['pdno']}",
                symbol=r["pdno"],
                paid_on=pay_date,
                quantity=Decimal(r["cblc_qty"] or "0"),
                amount=amount,
                tax=tax,
                currency="KRW",
                name=r.get("name") or "",
                record_date=_date(r["bass_dt"]),
                estimated_tax=estimated,
            )
        )
    paid.sort(key=lambda d: (d.paid_on, d.symbol))
    return paid, pending


@dataclass(frozen=True)
class ShareChange:
    """A right that changes the share count. Never applied automatically, see the module docstring."""

    symbol: str
    record_date: date | None
    type_code: str
    type_name: str
    name: str
    holding: Decimal
    allocated: Decimal
    total_allocated: Decimal


def share_changes(rows: list[dict]) -> list[ShareChange]:
    out = [
        ShareChange(
            symbol=r["pdno"],
            record_date=_date(r["bass_dt"]),
            type_code=r["rght_type_cd"],
            type_name=SHARE_CHANGE_TYPES[r["rght_type_cd"]],
            name=r.get("name") or "",
            holding=Decimal(r["cblc_qty"] or "0"),
            allocated=Decimal(r["last_alct_qty"] or "0"),
            total_allocated=Decimal(r["tot_alct_qty"] or "0"),
        )
        for r in rows
        if r["rght_type_cd"] in SHARE_CHANGE_TYPES
    ]
    for c in out:
        log.warning(
            "%s %s %s (%s): holding %s, allocated %s/%s. Not applied automatically - add a [[splits]] "
            "entry to adjustments.toml if this changed the share basis",
            c.record_date,
            c.symbol,
            c.type_name,
            c.name,
            c.holding,
            c.allocated,
            c.total_allocated,
        )
    return out
