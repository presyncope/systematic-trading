"""SQLite store for KIS account history.

Tables (all keyed by account = "CANO-PRDT"):
- overseas_orders : filled orders from TTTS3035R, one row per (KST order date, odno), upserted.
- overseas_trans  : daily transaction records from CTOS4001R, the only place the API states
                    overseas fees. One row per (trad_dt, pdno, side) as KIS aggregates them; no
                    id of their own, so a fetched date range replaces what was stored for it.
- domestic_orders : filled orders from TTTC0081R / CTSC9215R, one row per (order date, odno).
- domestic_daily_pl : TTTC8715R rows, one per (trad_dt, pdno) with that day's fee and tax for
                    the symbol (buys and sells together); replaced per fetched date range.
- rights          : CTRGA011R corporate actions on the account (dividends, splits, bonus issues),
                    replaced per fetched record-date range.
- instruments     : CTPF1002R per domestic symbol: name, market (STK = KOSPI, KSQ = KOSDAQ),
                    ISIN and the Yahoo symbol the Ghostfolio export uses.
- fills           : what the exporters read (brokers.common.models.Fill), rebuilt from the raw
                    tables by brokers.kis.fills after every backfill. fill_id is the odno (a
                    daily sequence; "@<KST date>" is appended when one recurs on another day), or
                    "trans:<date>:<symbol>:<side>" for transaction rows no order explains
                    (fractional-share trades, which TTTS3035R omits).
- fetch_log       : which date ranges were fetched when, so the next run knows where to resume.
- splits, export_log : shared with every broker, see brokers/common/store.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from brokers.common.models import Fill
from brokers.common.store import SplitStore, now_iso

__all__ = ["SCHEMA", "SIDES", "FillRow", "KisStore", "account_key", "short_code", "yahoo_symbol"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS overseas_orders (
    account       TEXT NOT NULL,
    dmst_ord_dt   TEXT NOT NULL,      -- 국내주문일자 (KST); odno is a sequence within this day
    odno          TEXT NOT NULL,      -- 주문번호
    ord_dt        TEXT NOT NULL,      -- 주문일자, exchange local (YYYYMMDD) = session date
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
    fetched_at    TEXT NOT NULL,
    PRIMARY KEY (account, dmst_ord_dt, odno)
);
CREATE INDEX IF NOT EXISTS idx_overseas_orders_account_dt ON overseas_orders(account, ord_dt);

CREATE TABLE IF NOT EXISTS domestic_orders (
    account       TEXT NOT NULL,
    ord_dt        TEXT NOT NULL,      -- 주문일자 (KST)
    odno          TEXT NOT NULL,
    ord_tmd       TEXT NOT NULL,      -- 주문시각 (KST, HHMMSS)
    pdno          TEXT NOT NULL,      -- 6-char KRX code
    side          TEXT NOT NULL,
    ccld_qty      TEXT NOT NULL,      -- tot_ccld_qty
    avg_prvs      TEXT NOT NULL,      -- average fill price
    ccld_amt      TEXT NOT NULL,      -- tot_ccld_amt
    excg_id       TEXT,               -- excg_id_dvsn_cd: KRX / NXT / SOR
    orgn_odno     TEXT,
    raw_json      TEXT NOT NULL,
    fetched_at    TEXT NOT NULL,
    PRIMARY KEY (account, ord_dt, odno)
);

CREATE TABLE IF NOT EXISTS domestic_daily_pl (
    account       TEXT NOT NULL,
    trad_dt       TEXT NOT NULL,
    pdno          TEXT NOT NULL,      -- 6-char KRX code (normalized)
    seq           INTEGER NOT NULL,
    buy_qty       TEXT NOT NULL,
    buy_amt       TEXT NOT NULL,
    sll_qty       TEXT NOT NULL,
    sll_amt       TEXT NOT NULL,
    fee           TEXT NOT NULL,      -- commission, buys and sells of the day together (KRW)
    tl_tax        TEXT NOT NULL,      -- transaction taxes, sells only (KRW)
    raw_json      TEXT NOT NULL,
    fetched_at    TEXT NOT NULL,
    PRIMARY KEY (account, trad_dt, pdno, seq)
);

CREATE TABLE IF NOT EXISTS rights (
    account       TEXT NOT NULL,
    bass_dt       TEXT NOT NULL,      -- 기준일자 (record date)
    pdno          TEXT NOT NULL,      -- 6-char KRX code (normalized)
    rght_type_cd  TEXT NOT NULL,      -- 03 배당, 14 액면분할, 15 액면병합, 02 무상증자, ...
    cblc_type_cd  TEXT NOT NULL,      -- 권리잔고유형코드
    name          TEXT,
    cblc_qty      TEXT,               -- holding the right was based on
    last_alct_qty TEXT,               -- shares allocated (bonus issues, splits)
    tot_alct_qty  TEXT,
    alct_amt      TEXT,               -- last_alct_amt: cash amount (gross)
    tax_amt       TEXT,
    cash_dfrm_dt  TEXT,               -- 현금지급일자 (payment date)
    raw_json      TEXT NOT NULL,
    fetched_at    TEXT NOT NULL,
    PRIMARY KEY (account, bass_dt, pdno, rght_type_cd, cblc_type_cd)
);

CREATE TABLE IF NOT EXISTS instruments (
    pdno          TEXT PRIMARY KEY,   -- 6-char KRX code
    name          TEXT NOT NULL,
    market        TEXT NOT NULL,      -- mket_id_cd: STK (KOSPI) / KSQ (KOSDAQ) / ...
    isin          TEXT,
    yahoo_symbol  TEXT NOT NULL,      -- 005930.KS / 035420.KQ
    fetched_at    TEXT NOT NULL
);

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


def short_code(pdno: str) -> str:
    """KRX code as the order endpoints spell it: 12-char "00000A005380" -> "005380", "00000Q500001"
    (ETN) -> "Q500001"; anything up to 7 chars is returned as-is."""
    p = pdno.strip()
    if len(p) <= 7:
        return p
    return p[-7:] if p[-7] == "Q" else p[-6:]


def yahoo_symbol(pdno: str, market: str) -> str:
    """Yahoo Finance spelling of a KRX code: .KS for the KOSPI market, .KQ for KOSDAQ."""
    return f"{pdno}.KQ" if market == "KSQ" else f"{pdno}.KS"


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
        "account": account,
        "dmst_ord_dt": r.get("dmst_ord_dt") or r["ord_dt"],
        "odno": r["odno"],
        "ord_dt": r["ord_dt"],
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


def _domestic_order_row(r: dict, account: str, fetched_at: str) -> dict:
    return {
        "account": account,
        "ord_dt": r["ord_dt"],
        "odno": r["odno"],
        "ord_tmd": r.get("ord_tmd") or "000000",
        "pdno": short_code(r["pdno"]),
        "side": SIDES.get(r.get("sll_buy_dvsn_cd", ""), r.get("sll_buy_dvsn_cd", "")),
        "ccld_qty": r.get("tot_ccld_qty", "0"),
        "avg_prvs": r.get("avg_prvs", "0"),
        "ccld_amt": r.get("tot_ccld_amt", "0"),
        "excg_id": r.get("excg_id_dvsn_cd"),
        "orgn_odno": r.get("orgn_odno") if (r.get("orgn_odno") or "").strip("0") else None,
        "raw_json": json.dumps(r, ensure_ascii=False, sort_keys=True),
        "fetched_at": fetched_at,
    }


def _rights_row(r: dict, account: str, fetched_at: str) -> dict:
    return {
        "account": account,
        "bass_dt": r["bass_dt"],
        "pdno": short_code(r.get("shtn_pdno") or r["pdno"]),
        "rght_type_cd": r.get("rght_type_cd", ""),
        "cblc_type_cd": r.get("rght_cblc_type_cd", ""),
        "name": r.get("prdt_name"),
        "cblc_qty": r.get("cblc_qty", "0"),
        "last_alct_qty": r.get("last_alct_qty", "0"),
        "tot_alct_qty": r.get("tot_alct_qty", "0"),
        "alct_amt": r.get("last_alct_amt", "0"),
        "tax_amt": r.get("tax_amt", "0"),
        "cash_dfrm_dt": r.get("cash_dfrm_dt") or None,
        "raw_json": json.dumps(r, ensure_ascii=False, sort_keys=True),
        "fetched_at": fetched_at,
    }


def _daily_pl_row(r: dict, account: str, seq: int, fetched_at: str) -> dict:
    return {
        "account": account,
        "trad_dt": r["trad_dt"],
        "pdno": short_code(r["pdno"]),
        "seq": seq,
        "buy_qty": r.get("buy_qty", "0"),
        "buy_amt": r.get("buy_amt", "0"),
        "sll_qty": r.get("sll_qty", "0"),
        "sll_amt": r.get("sll_amt", "0"),
        "fee": r.get("fee", "0"),
        "tl_tax": r.get("tl_tax", "0"),
        "raw_json": json.dumps(r, ensure_ascii=False, sort_keys=True),
        "fetched_at": fetched_at,
    }


class KisStore(SplitStore):
    SCHEMA = SCHEMA

    def _upsert(self, table: str, data: list[dict], key: tuple[str, ...]) -> int:
        if not data:
            return 0
        cols = list(data[0])
        sql = (
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)}) "
            f"ON CONFLICT({', '.join(key)}) DO UPDATE SET "
            + ", ".join(f"{c} = excluded.{c}" for c in cols if c not in key)
        )
        with self._conn:
            self._conn.executemany(sql, data)
        return len(data)

    # --- overseas ----------------------------------------------------------

    def upsert_overseas_orders(self, rows: list[dict], account: str) -> int:
        """Store TTTS3035R rows (only those with a filled quantity are useful; the caller filters)."""
        fetched_at = now_iso()
        return self._upsert(
            "overseas_orders", [_order_row(r, account, fetched_at) for r in rows], ("account", "dmst_ord_dt", "odno")
        )

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

    # --- domestic ----------------------------------------------------------

    def upsert_domestic_orders(self, rows: list[dict], account: str) -> int:
        fetched_at = now_iso()
        data = [_domestic_order_row(r, account, fetched_at) for r in rows]
        return self._upsert("domestic_orders", data, ("account", "ord_dt", "odno"))

    def replace_domestic_daily_pl(self, rows: list[dict], account: str, from_date: str, to_date: str) -> int:
        """Replace the stored TTTC8715R rows whose trad_dt is within [from_date, to_date] (YYYYMMDD)."""
        fetched_at = now_iso()
        seq: dict[tuple[str, str], int] = {}
        data = []
        for r in rows:
            key = (r["trad_dt"], short_code(r["pdno"]))
            seq[key] = seq.get(key, -1) + 1
            data.append(_daily_pl_row(r, account, seq[key], fetched_at))
        with self._conn:
            self._conn.execute(
                "DELETE FROM domestic_daily_pl WHERE account = ? AND trad_dt BETWEEN ? AND ?",
                (account, from_date, to_date),
            )
            if data:
                cols = list(data[0])
                self._conn.executemany(
                    f"INSERT INTO domestic_daily_pl ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})",
                    data,
                )
        return len(data)

    def domestic_orders(self, account: str) -> list[dict]:
        return [
            dict(r)
            for r in self._conn.execute(
                "SELECT * FROM domestic_orders WHERE account = ? ORDER BY ord_dt, ord_tmd, odno", (account,)
            )
        ]

    def domestic_daily_pl(self, account: str) -> list[dict]:
        return [
            dict(r)
            for r in self._conn.execute(
                "SELECT * FROM domestic_daily_pl WHERE account = ? ORDER BY trad_dt, pdno, seq", (account,)
            )
        ]

    def replace_rights(self, rows: list[dict], account: str, from_date: str, to_date: str) -> int:
        """Replace the stored CTRGA011R rows whose bass_dt is within [from_date, to_date] (YYYYMMDD)."""
        fetched_at = now_iso()
        data = [_rights_row(r, account, fetched_at) for r in rows]
        with self._conn:
            self._conn.execute(
                "DELETE FROM rights WHERE account = ? AND bass_dt BETWEEN ? AND ?", (account, from_date, to_date)
            )
            if data:
                cols = list(data[0])
                self._conn.executemany(
                    f"INSERT INTO rights ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})", data
                )
        return len(data)

    def rights(self, account: str) -> list[dict]:
        return [
            dict(r)
            for r in self._conn.execute(
                "SELECT * FROM rights WHERE account = ? ORDER BY bass_dt, pdno, rght_type_cd", (account,)
            )
        ]

    def upsert_instrument(self, pdno: str, name: str, market: str, isin: str | None) -> None:
        with self._conn:
            self._conn.execute(
                """INSERT INTO instruments (pdno, name, market, isin, yahoo_symbol, fetched_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(pdno) DO UPDATE SET name = excluded.name, market = excluded.market, isin = excluded.isin,
                       yahoo_symbol = excluded.yahoo_symbol, fetched_at = excluded.fetched_at""",
                (pdno, name, market, isin, yahoo_symbol(pdno, market), now_iso()),
            )

    def instruments(self) -> dict[str, dict]:
        return {r["pdno"]: dict(r) for r in self._conn.execute("SELECT * FROM instruments")}

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
