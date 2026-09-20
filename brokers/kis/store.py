"""SQLite store for KIS account history.

Tables (all keyed by account = "CANO-PRDT"):
- overseas_orders : filled orders from TTTS3035R, one row per odno (upserted).
- overseas_trans  : daily transaction records from CTOS4001R, the only place the API states
                    fees. One row per (trad_dt, pdno, side) as KIS aggregates them; no id of
                    their own, so a fetched date range replaces what was stored for it.
- fills           : what the exporters read (brokers.common.models.Fill), rebuilt from the raw
                    tables by brokers.kis.fills after every backfill. fill_id is the odno for
                    order-based fills and "trans:<date>:<symbol>:<side>" for transaction rows
                    that no order explains (fractional-share trades, which TTTS3035R omits).
- fetch_log       : which date ranges were fetched when, for the summary.
- splits, export_log : shared with every broker, see brokers/common/store.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from brokers.common.models import Fill
from brokers.common.store import SplitStore, now_iso

__all__ = ["SCHEMA", "FillRow", "KisStore", "account_key"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS overseas_orders (
    odno          TEXT PRIMARY KEY,   -- 주문번호
    account       TEXT NOT NULL,
    ord_dt        TEXT NOT NULL,      -- 주문일자, exchange local (YYYYMMDD)
    dmst_ord_dt   TEXT NOT NULL,      -- 국내주문일자 (KST)
    thco_ord_tmd  TEXT NOT NULL,      -- 당사주문시각 (KST, HHMMSS)
    pdno          TEXT NOT NULL,
    excg          TEXT NOT NULL,      -- ovrs_excg_cd: NASD / NYSE / AMEX ...
    side          TEXT NOT NULL,      -- BUY / SELL
    ccld_qty      TEXT NOT NULL,      -- ft_ccld_qty
    ccld_unpr     TEXT NOT NULL,      -- ft_ccld_unpr3
    ccld_amt      TEXT NOT NULL,      -- ft_ccld_amt3
    crcy          TEXT NOT NULL,
    orgn_odno     TEXT,
    rvse_cncl     TEXT,               -- rvse_cncl_dvsn: 00 none / 01 modified / 02 cancelled
    prcs_stat     TEXT,
    raw_json      TEXT NOT NULL,
    fetched_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_overseas_orders_account_dt ON overseas_orders(account, ord_dt);

CREATE TABLE IF NOT EXISTS overseas_trans (
    account       TEXT NOT NULL,
    trad_dt       TEXT NOT NULL,      -- 매매일자, exchange local
    pdno          TEXT NOT NULL,
    side          TEXT NOT NULL,
    seq           INTEGER NOT NULL,   -- position among rows with the same key in one response
    sttl_dt       TEXT,
    ccld_qty      TEXT NOT NULL,
    amt_unit_qty  TEXT,               -- amt_unit_ccld_qty (fractional quantity)
    unpr          TEXT NOT NULL,      -- ft_ccld_unpr2
    frcr_amt      TEXT NOT NULL,      -- tr_frcr_amt2
    dmst_fee      TEXT NOT NULL,      -- dmst_frcr_fee1: KIS commission in the trade currency
    frcr_fee      TEXT NOT NULL,      -- frcr_fee1: foreign fees/taxes (SEC fee etc.)
    crcy          TEXT NOT NULL,
    std_pdno      TEXT,               -- ISIN: stable across ticker changes (FI -> FISV)
    erlm_exrt     TEXT,
    raw_json      TEXT NOT NULL,
    fetched_at    TEXT NOT NULL,
    PRIMARY KEY (account, trad_dt, pdno, side, seq)
);

CREATE TABLE IF NOT EXISTS fills (
    fill_id       TEXT NOT NULL,
    account       TEXT NOT NULL,
    market        TEXT NOT NULL,      -- overseas / domestic
    symbol        TEXT NOT NULL,
    side          TEXT NOT NULL,
    quantity      TEXT NOT NULL,
    price         TEXT NOT NULL,
    currency      TEXT NOT NULL,
    filled_at     TEXT NOT NULL,      -- ISO 8601 KST
    trading_date  TEXT NOT NULL,      -- exchange local session date
    commission    TEXT NOT NULL,
    tax           TEXT NOT NULL,
    source        TEXT NOT NULL,      -- order / trans
    flags         TEXT NOT NULL,      -- JSON list: synthetic, unsettled, qty_mismatch, renamed
    isin          TEXT,
    PRIMARY KEY (account, fill_id)
);
CREATE INDEX IF NOT EXISTS idx_fills_account_filled_at ON fills(account, filled_at);

CREATE TABLE IF NOT EXISTS fetch_log (
    account     TEXT NOT NULL,
    what        TEXT NOT NULL,        -- overseas / domestic / rights
    from_date   TEXT NOT NULL,
    to_date     TEXT NOT NULL,
    rows        INTEGER NOT NULL,
    fetched_at  TEXT NOT NULL
);
"""

SIDES = {"01": "SELL", "02": "BUY"}


def account_key(account: tuple[str, str]) -> str:
    return f"{account[0]}-{account[1]}"


@dataclass(frozen=True)
class FillRow:
    """One fills-table row; brokers.kis.fills builds these from the raw tables."""

    fill_id: str
    market: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    currency: str
    filled_at: str
    trading_date: date
    commission: Decimal
    tax: Decimal
    source: str
    flags: tuple[str, ...] = ()
    isin: str | None = None


def _order_row(r: dict, account: str, fetched_at: str) -> dict:
    return {
        "odno": r["odno"],
        "account": account,
        "ord_dt": r["ord_dt"],
        "dmst_ord_dt": r.get("dmst_ord_dt") or r["ord_dt"],
        "thco_ord_tmd": r.get("thco_ord_tmd") or r.get("ord_tmd") or "000000",
        "pdno": r["pdno"],
        "excg": r.get("ovrs_excg_cd", ""),
        "side": SIDES.get(r.get("sll_buy_dvsn_cd", ""), r.get("sll_buy_dvsn_cd", "")),
        "ccld_qty": r.get("ft_ccld_qty", "0"),
        "ccld_unpr": r.get("ft_ccld_unpr3", "0"),
        "ccld_amt": r.get("ft_ccld_amt3", "0"),
        "crcy": r.get("tr_crcy_cd", ""),
        "orgn_odno": r.get("orgn_odno") or None,
        "rvse_cncl": r.get("rvse_cncl_dvsn"),
        "prcs_stat": r.get("prcs_stat_name"),
        "raw_json": json.dumps(r, ensure_ascii=False, sort_keys=True),
        "fetched_at": fetched_at,
    }


def _trans_row(r: dict, account: str, seq: int, fetched_at: str) -> dict:
    return {
        "account": account,
        "trad_dt": r["trad_dt"],
        "pdno": r["pdno"],
        "side": SIDES.get(r.get("sll_buy_dvsn_cd", ""), r.get("sll_buy_dvsn_cd", "")),
        "seq": seq,
        "sttl_dt": r.get("sttl_dt"),
        "ccld_qty": r.get("ccld_qty", "0"),
        "amt_unit_qty": r.get("amt_unit_ccld_qty"),
        "unpr": r.get("ft_ccld_unpr2", "0"),
        "frcr_amt": r.get("tr_frcr_amt2", "0"),
        "dmst_fee": r.get("dmst_frcr_fee1", "0"),
        "frcr_fee": r.get("frcr_fee1", "0"),
        "crcy": r.get("crcy_cd", ""),
        "std_pdno": r.get("std_pdno") or None,
        "erlm_exrt": r.get("erlm_exrt"),
        "raw_json": json.dumps(r, ensure_ascii=False, sort_keys=True),
        "fetched_at": fetched_at,
    }


class KisStore(SplitStore):
    SCHEMA = SCHEMA

    # --- raw tables --------------------------------------------------------

    def upsert_overseas_orders(self, rows: list[dict], account: str) -> int:
        """Store TTTS3035R rows (only those with a filled quantity are useful; the caller filters)."""
        fetched_at = now_iso()
        data = [_order_row(r, account, fetched_at) for r in rows]
        cols = list(data[0]) if data else []
        if data:
            sql = (
                f"INSERT INTO overseas_orders ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)}) "
                "ON CONFLICT(odno) DO UPDATE SET " + ", ".join(f"{c} = excluded.{c}" for c in cols if c != "odno")
            )
            with self._conn:
                self._conn.executemany(sql, data)
        return len(data)

    def replace_overseas_trans(self, rows: list[dict], account: str, from_date: str, to_date: str) -> int:
        """Replace the stored CTOS4001R rows whose trad_dt is within [from_date, to_date] (YYYYMMDD)."""
        fetched_at = now_iso()
        seq: dict[tuple[str, str, str], int] = {}
        data = []
        for r in rows:
            key = (r["trad_dt"], r["pdno"], SIDES.get(r.get("sll_buy_dvsn_cd", ""), ""))
            seq[key] = seq.get(key, -1) + 1
            data.append(_trans_row(r, account, seq[key], fetched_at))
        with self._conn:
            self._conn.execute(
                "DELETE FROM overseas_trans WHERE account = ? AND trad_dt BETWEEN ? AND ?",
                (account, from_date, to_date),
            )
            if data:
                cols = list(data[0])
                self._conn.executemany(
                    f"INSERT INTO overseas_trans ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})", data
                )
        return len(data)

    def overseas_orders(self, account: str) -> list[dict]:
        return [
            dict(r)
            for r in self._conn.execute(
                "SELECT * FROM overseas_orders WHERE account = ? ORDER BY ord_dt, dmst_ord_dt, thco_ord_tmd, odno",
                (account,),
            )
        ]

    def overseas_trans(self, account: str) -> list[dict]:
        return [
            dict(r)
            for r in self._conn.execute(
                "SELECT * FROM overseas_trans WHERE account = ? ORDER BY trad_dt, pdno, side, seq", (account,)
            )
        ]

    def record_fetch(self, account: str, what: str, from_date: str, to_date: str, rows: int) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO fetch_log (account, what, from_date, to_date, rows, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
                (account, what, from_date, to_date, rows, now_iso()),
            )

    def last_fetch(self, account: str, what: str) -> tuple[str, str] | None:
        """(from_date, to_date) of the latest fetch of `what`, None if never fetched."""
        row = self._conn.execute(
            "SELECT from_date, to_date FROM fetch_log WHERE account = ? AND what = ? ORDER BY fetched_at DESC LIMIT 1",
            (account, what),
        ).fetchone()
        return (row[0], row[1]) if row else None

    # --- fills -------------------------------------------------------------

    def replace_fills(self, account: str, market: str, rows: list[FillRow]) -> int:
        with self._conn:
            self._conn.execute("DELETE FROM fills WHERE account = ? AND market = ?", (account, market))
            self._conn.executemany(
                """INSERT INTO fills (fill_id, account, market, symbol, side, quantity, price, currency, filled_at,
                                      trading_date, commission, tax, source, flags, isin)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        f.fill_id,
                        account,
                        f.market,
                        f.symbol,
                        f.side,
                        format(f.quantity, "f"),
                        format(f.price, "f"),
                        f.currency,
                        f.filled_at,
                        f.trading_date.isoformat(),
                        format(f.commission, "f"),
                        format(f.tax, "f"),
                        f.source,
                        json.dumps(list(f.flags)),
                        f.isin,
                    )
                    for f in rows
                ],
            )
        return len(rows)

    def accounts(self) -> list[str]:
        return [r[0] for r in self._conn.execute("SELECT DISTINCT account FROM fills ORDER BY account")]

    def fills(self, account: str, *, currency: str | None = None, market: str | None = None) -> list[Fill]:
        sql = "SELECT * FROM fills WHERE account = ?"
        params: list = [account]
        if currency:
            sql += " AND currency = ?"
            params.append(currency)
        if market:
            sql += " AND market = ?"
            params.append(market)
        sql += " ORDER BY filled_at, fill_id"
        return [
            Fill(
                order_id=r["fill_id"],
                symbol=r["symbol"],
                side=r["side"],
                quantity=r["quantity"],
                price=r["price"],
                currency=r["currency"],
                filled_at=r["filled_at"],
                commission=r["commission"],
                tax=r["tax"],
                trading_date=date.fromisoformat(r["trading_date"]),
            )
            for r in self._conn.execute(sql, params)
        ]

    def flagged_fills(self, account: str, market: str) -> list[dict]:
        return [
            dict(r)
            for r in self._conn.execute(
                "SELECT * FROM fills WHERE account = ? AND market = ? AND flags != '[]' ORDER BY filled_at",
                (account, market),
            )
        ]
