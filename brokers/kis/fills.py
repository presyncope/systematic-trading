"""Build fills from the raw KIS tables (pure functions, no I/O).

Overseas: TTTS3035R (orders) has the order id, KST time and fill quantity/price but no fees;
CTOS4001R (daily transactions) has the fees but no order id, aggregated per (trade date,
symbol, side). The two are joined on that key and each transaction row's fees are spread over
the orders in its group in proportion to their filled amount, the rounding remainder going to
the last order so the group's fees add up exactly.

- dmst_frcr_fee1 (국내외화수수료) -> commission; frcr_fee1 (외화수수료: SEC fee etc.) -> tax
- a transaction group with no orders is a trade the order endpoint does not report (it omits
  fractional-share trades): it becomes one synthetic fill timed at the session close, flag
  "synthetic"
- an order group with no transaction row has not been settled/registered yet: fees 0, flag
  "unsettled" (the next backfill re-fetches recent days and fills them in)
- quantities that differ between the two sides are flagged "qty_mismatch" and the order side
  is trusted. One way this happens: a fractional trade on the same day, symbol and side as a
  whole-share order is folded into that order's transaction row, so the flagged fill's fees
  cover both. Investigate by hand.
- a ticker change shows up as one ISIN (std_pdno on the transaction rows) under two symbols
  (Fiserv: FI, then FISV). Every fill of that ISIN is written under the symbol used most
  recently, flag "renamed", so the position adds up and matches today's holdings

Timestamps: ord_dt is the exchange-local session date (KIS states it, so it goes straight into
Fill.trading_date); dmst_ord_dt + thco_ord_tmd is the KST order-acceptance time, the closest
thing to a fill time the API offers.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, datetime, time
from decimal import ROUND_HALF_EVEN, Decimal
from zoneinfo import ZoneInfo

from brokers.common.ledger import CLOSE_HOUR, ET
from brokers.kis.store import FillRow

__all__ = ["FEE_PLACES", "KST", "join_overseas", "kst_timestamp", "session_close_kst", "ticker_aliases"]

log = logging.getLogger("kis.fills")

KST = ZoneInfo("Asia/Seoul")
FEE_PLACES = 4
_FEE_QUANTUM = Decimal(1).scaleb(-FEE_PLACES)


def kst_timestamp(yyyymmdd: str, hhmmss: str) -> str:
    """ "20260804", "233732" -> "2026-08-04T23:37:32+09:00"."""
    return datetime.strptime(yyyymmdd + hhmmss.ljust(6, "0"), "%Y%m%d%H%M%S").replace(tzinfo=KST).isoformat()


def session_close_kst(session: date) -> str:
    """The US close (16:00 ET) of `session` expressed in KST, for fills with no time of their own."""
    return datetime.combine(session, time(CLOSE_HOUR), tzinfo=ET).astimezone(KST).isoformat()


def _date(yyyymmdd: str) -> date:
    return date(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))


def _strip(d: Decimal) -> Decimal:
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return Decimal(s)


def _allocate(total: Decimal, weights: list[Decimal]) -> list[Decimal]:
    """Split `total` in proportion to `weights`, rounded to FEE_PLACES, remainder on the last item."""
    if not weights:
        return []
    denom = sum(weights)
    if denom == 0:  # no amounts to weigh by: equal shares
        weights = [Decimal(1)] * len(weights)
        denom = Decimal(len(weights))
    parts = [(total * w / denom).quantize(_FEE_QUANTUM, ROUND_HALF_EVEN) for w in weights[:-1]]
    parts.append(total - sum(parts, Decimal(0)))
    return parts


def ticker_aliases(trans: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
    """(old ticker -> current ticker, ticker -> ISIN) from the transaction rows' std_pdno."""
    latest: dict[str, tuple[str, str]] = {}  # isin -> (trad_dt, pdno)
    tickers: dict[str, set[str]] = defaultdict(set)
    isin_of: dict[str, str] = {}
    for t in trans:
        isin = t.get("std_pdno")
        if not isin:
            continue
        tickers[isin].add(t["pdno"])
        isin_of[t["pdno"]] = isin
        if isin not in latest or t["trad_dt"] > latest[isin][0]:
            latest[isin] = (t["trad_dt"], t["pdno"])
    aliases: dict[str, str] = {}
    for isin, symbols in tickers.items():
        if len(symbols) > 1:
            current = latest[isin][1]
            for old in symbols - {current}:
                aliases[old] = current
                log.info("%s: ticker %s is now %s (ISIN %s); fills renamed", current, old, current, isin)
    return aliases, isin_of


def join_overseas(orders: list[dict], trans: list[dict]) -> list[FillRow]:
    """Rows of the overseas_orders and overseas_trans tables -> fills, oldest first."""
    aliases, isin_of = ticker_aliases(trans)
    by_key_orders: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for o in orders:
        if Decimal(o["ccld_qty"]) > 0 and o["side"] in ("BUY", "SELL"):
            by_key_orders[(o["ord_dt"], aliases.get(o["pdno"]) or o["pdno"], o["side"])].append(o)
    by_key_trans: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for t in trans:
        if t["side"] in ("BUY", "SELL"):
            by_key_trans[(t["trad_dt"], aliases.get(t["pdno"]) or t["pdno"], t["side"])].append(t)

    out: list[FillRow] = []
    for key in sorted(set(by_key_orders) | set(by_key_trans)):
        trad_dt, pdno, side = key
        group_orders = by_key_orders.get(key, [])
        group_trans = by_key_trans.get(key, [])
        commission = sum((Decimal(t["dmst_fee"]) for t in group_trans), Decimal(0))
        tax = sum((Decimal(t["frcr_fee"]) for t in group_trans), Decimal(0))
        session = _date(trad_dt)
        isin = isin_of.get(pdno)

        if not group_orders:
            qty = sum((Decimal(t["amt_unit_qty"] or t["ccld_qty"]) for t in group_trans), Decimal(0))
            amount = sum((Decimal(t["frcr_amt"]) for t in group_trans), Decimal(0))
            price = _strip((amount / qty).quantize(Decimal("0.000001"))) if qty else Decimal(0)
            log.warning(
                "%s %s %s %s @ %s has no order (fractional trade?): synthetic fill", trad_dt, side, pdno, qty, price
            )
            renamed = any(t["pdno"] != pdno for t in group_trans)
            out.append(
                FillRow(
                    fill_id=f"trans:{trad_dt}:{pdno}:{side}",
                    market="overseas",
                    symbol=pdno,
                    side=side,
                    quantity=_strip(qty),
                    price=price,
                    currency=group_trans[0]["crcy"],
                    filled_at=session_close_kst(session),
                    trading_date=session,
                    commission=commission,
                    tax=tax,
                    source="trans",
                    flags=("synthetic", "renamed") if renamed else ("synthetic",),
                    isin=isin,
                )
            )
            continue

        flags: list[str] = []
        if not group_trans:
            flags.append("unsettled")
        else:
            order_qty = sum((Decimal(o["ccld_qty"]) for o in group_orders), Decimal(0))
            trans_qty = sum((Decimal(t["ccld_qty"]) for t in group_trans), Decimal(0))
            if order_qty != trans_qty:
                log.warning(
                    "%s %s %s: orders filled %s but transactions show %s; fees spread over the orders anyway",
                    trad_dt,
                    side,
                    pdno,
                    order_qty,
                    trans_qty,
                )
                flags.append("qty_mismatch")
        amounts = [Decimal(o["ccld_qty"]) * Decimal(o["ccld_unpr"]) for o in group_orders]
        commissions = _allocate(commission, amounts)
        taxes = _allocate(tax, amounts)
        for o, c, t in zip(group_orders, commissions, taxes, strict=True):
            row_flags = (*flags, "renamed") if o["pdno"] != pdno else tuple(flags)
            out.append(
                FillRow(
                    fill_id=o["odno"],
                    market="overseas",
                    symbol=pdno,
                    side=side,
                    quantity=_strip(Decimal(o["ccld_qty"])),
                    price=_strip(Decimal(o["ccld_unpr"])),
                    currency=o["crcy"],
                    filled_at=kst_timestamp(o["dmst_ord_dt"], o["thco_ord_tmd"]),
                    trading_date=session,
                    commission=_strip(c),
                    tax=_strip(t),
                    source="order",
                    flags=row_flags,
                    isin=isin,
                )
            )
    out.sort(key=lambda f: (f.filled_at, f.fill_id))
    return out
