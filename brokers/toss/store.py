"""SQLite store for Toss order history.

All SQL lives here. Tables:
- orders      : one row per orderId, upserted (status/execution fields always overwritten).
                Amounts/quantities are decimal strings -> stored as TEXT as-is.
- sync_state  : per-query backfill progress (cursor) so an interrupted run can resume.
- splits      : stock splits detected from candles (splits.py). A row's detected_at is the first
                time we saw it, which exporters use to warn about newly found splits; rows that a
                later detection no longer finds are removed.
- export_log  : one row per successful export, so the next run knows what "new since last export" means.

Every public write method commits on its own. upsert_orders is idempotent by order_id, so
committing rows before advancing the cursor is safe: a crash in between just re-fetches
that page on the next run.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, date, datetime
from fractions import Fraction
from pathlib import Path

__all__ = [
    "SCHEMA",
    "UPSERT",
    "Fill",
    "OrderStore",
    "OrderSummary",
    "Split",
    "SyncState",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id             TEXT PRIMARY KEY,
    account_seq          INTEGER NOT NULL,
    symbol               TEXT NOT NULL,
    side                 TEXT NOT NULL,
    order_type           TEXT NOT NULL,
    time_in_force        TEXT NOT NULL,
    status               TEXT NOT NULL,
    price                TEXT,
    quantity             TEXT NOT NULL,
    order_amount         TEXT,
    currency             TEXT NOT NULL,
    ordered_at           TEXT NOT NULL,
    canceled_at          TEXT,
    filled_quantity      TEXT,
    average_filled_price TEXT,
    filled_amount        TEXT,
    commission           TEXT,
    tax                  TEXT,
    filled_at            TEXT,
    settlement_date      TEXT,
    raw_json             TEXT NOT NULL,
    fetched_at           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_account_ordered_at ON orders(account_seq, ordered_at);
CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);

CREATE TABLE IF NOT EXISTS sync_state (
    key          TEXT PRIMARY KEY,
    cursor       TEXT,
    pages_done   INTEGER NOT NULL DEFAULT 0,
    orders_done  INTEGER NOT NULL DEFAULT 0,
    started_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS splits (
    symbol        TEXT NOT NULL,
    ex_date       TEXT NOT NULL,   -- first candle date (exchange local) traded on the new share basis
    ratio         TEXT NOT NULL,   -- new shares per old share as "n/m": "3/1" forward, "1/40" reverse
    factor_before TEXT NOT NULL,   -- measured raw/adjusted close the day before, for debugging
    factor_after  TEXT NOT NULL,
    detected_at   TEXT NOT NULL,
    PRIMARY KEY (symbol, ex_date)
);

CREATE TABLE IF NOT EXISTS export_log (
    target      TEXT NOT NULL,
    exported_at TEXT NOT NULL,
    rows        INTEGER NOT NULL
);
"""

UPSERT = """
INSERT INTO orders (
    order_id, account_seq, symbol, side, order_type, time_in_force, status,
    price, quantity, order_amount, currency, ordered_at, canceled_at,
    filled_quantity, average_filled_price, filled_amount, commission, tax, filled_at, settlement_date,
    raw_json, fetched_at
) VALUES (
    :order_id, :account_seq, :symbol, :side, :order_type, :time_in_force, :status,
    :price, :quantity, :order_amount, :currency, :ordered_at, :canceled_at,
    :filled_quantity, :average_filled_price, :filled_amount, :commission, :tax, :filled_at, :settlement_date,
    :raw_json, :fetched_at
)
ON CONFLICT(order_id) DO UPDATE SET
    status = excluded.status,
    price = excluded.price,
    quantity = excluded.quantity,
    order_amount = excluded.order_amount,
    canceled_at = excluded.canceled_at,
    filled_quantity = excluded.filled_quantity,
    average_filled_price = excluded.average_filled_price,
    filled_amount = excluded.filled_amount,
    commission = excluded.commission,
    tax = excluded.tax,
    filled_at = excluded.filled_at,
    settlement_date = excluded.settlement_date,
    raw_json = excluded.raw_json,
    fetched_at = excluded.fetched_at
"""


@dataclass(frozen=True)
class SyncState:
    key: str
    cursor: str | None
    pages_done: int
    orders_done: int
    started_at: str
    updated_at: str
    completed_at: str | None

    @property
    def resumable(self) -> bool:
        """True if a previous run stopped mid-way and left a cursor to continue from."""
        return self.completed_at is None and self.cursor is not None


@dataclass(frozen=True)
class Fill:
    """An order with a non-zero fill, i.e. one execution as far as exporters are concerned.

    The API only exposes an order-level aggregate (average price, total filled quantity), so one
    order maps to exactly one Fill even if it was filled in several pieces. Decimals stay as
    strings exactly as the API sent them.
    """

    order_id: str
    symbol: str
    side: str  # BUY / SELL
    quantity: str  # filled quantity, always positive
    price: str  # average filled price
    currency: str
    filled_at: str  # ISO 8601 with offset (KST)
    commission: str
    tax: str


@dataclass(frozen=True)
class Split:
    """A stock split: fills with trading_date < ex_date are in the old share basis.

    ratio is new shares per old share (3 for a 3:1 split, 1/40 for a 1-for-40 reverse split).
    factor_before/after are the measured raw/adjusted close ratios around ex_date; None for
    manually entered splits. detected_at is None until the split has been stored.
    """

    symbol: str
    ex_date: date
    ratio: Fraction
    factor_before: str | None = None
    factor_after: str | None = None
    detected_at: str | None = None

    @property
    def ratio_text(self) -> str:
        return f"{self.ratio.numerator}/{self.ratio.denominator}"


@dataclass(frozen=True)
class OrderSummary:
    total: int
    oldest: str | None
    newest: str | None
    filled: int
    by_status: list[tuple[str, int]]
    by_symbol: list[tuple[str, int]]


def _now_iso() -> str:
    # Microseconds: export_log and splits.detected_at are compared as strings, and a split can be
    # stored in the same second as the export that follows it.
    return datetime.now(UTC).isoformat(timespec="microseconds")


def _order_row(order: dict, account_seq: int, fetched_at: str) -> dict:
    ex = order.get("execution") or {}
    return {
        "order_id": order["orderId"],
        "account_seq": account_seq,
        "symbol": order["symbol"],
        "side": order["side"],
        "order_type": order["orderType"],
        "time_in_force": order["timeInForce"],
        "status": order["status"],
        "price": order.get("price"),
        "quantity": order["quantity"],
        "order_amount": order.get("orderAmount"),
        "currency": order["currency"],
        "ordered_at": order["orderedAt"],
        "canceled_at": order.get("canceledAt"),
        "filled_quantity": ex.get("filledQuantity"),
        "average_filled_price": ex.get("averageFilledPrice"),
        "filled_amount": ex.get("filledAmount"),
        "commission": ex.get("commission"),
        "tax": ex.get("tax"),
        "filled_at": ex.get("filledAt"),
        "settlement_date": ex.get("settlementDate"),
        "raw_json": json.dumps(order, ensure_ascii=False, sort_keys=True),
        "fetched_at": fetched_at,
    }


class OrderStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> OrderStore:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # --- orders ------------------------------------------------------------

    def upsert_orders(self, orders: list[dict], account_seq: int) -> int:
        fetched_at = _now_iso()
        rows = [_order_row(o, account_seq, fetched_at) for o in orders]
        with self._conn:
            self._conn.executemany(UPSERT, rows)
        return len(rows)

    def account_seqs(self) -> list[int]:
        return [r[0] for r in self._conn.execute("SELECT DISTINCT account_seq FROM orders ORDER BY account_seq")]

    def fills(self, account_seq: int, *, currency: str | None = None) -> list[Fill]:
        """Orders with filled_quantity > 0, oldest first. Filtered by status is wrong here:
        a CANCELED order can still carry a partial fill."""
        sql = """SELECT order_id, symbol, side, filled_quantity, average_filled_price, currency, filled_at,
                        commission, tax
                 FROM orders
                 WHERE account_seq = ? AND CAST(filled_quantity AS REAL) > 0"""
        params: list = [account_seq]
        if currency:
            sql += " AND currency = ?"
            params.append(currency)
        sql += " ORDER BY filled_at, order_id"
        return [
            Fill(
                order_id=r["order_id"],
                symbol=r["symbol"],
                side=r["side"],
                quantity=r["filled_quantity"],
                price=r["average_filled_price"],
                currency=r["currency"],
                filled_at=r["filled_at"],
                commission=r["commission"] or "0",
                tax=r["tax"] or "0",
            )
            for r in self._conn.execute(sql, params)
        ]

    # --- sync_state --------------------------------------------------------

    def get_sync_state(self, key: str) -> SyncState | None:
        row = self._conn.execute("SELECT * FROM sync_state WHERE key = ?", (key,)).fetchone()
        return SyncState(**dict(row)) if row else None

    def begin_sync(self, key: str, *, cursor: str | None = None, pages_done: int = 0, orders_done: int = 0) -> None:
        """Mark a sync as in progress. Pass the previous state's cursor/counters to resume."""
        now = _now_iso()
        with self._conn:
            self._conn.execute(
                """INSERT INTO sync_state (key, cursor, pages_done, orders_done, started_at, updated_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, NULL)
                   ON CONFLICT(key) DO UPDATE SET cursor = excluded.cursor, pages_done = excluded.pages_done,
                       orders_done = excluded.orders_done, started_at = excluded.started_at,
                       updated_at = excluded.updated_at, completed_at = NULL""",
                (key, cursor, pages_done, orders_done, now, now),
            )

    def advance_sync(self, key: str, *, cursor: str | None, pages_done: int, orders_done: int) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE sync_state SET cursor = ?, pages_done = ?, orders_done = ?, updated_at = ? WHERE key = ?",
                (cursor, pages_done, orders_done, _now_iso(), key),
            )

    def complete_sync(self, key: str) -> None:
        now = _now_iso()
        with self._conn:
            self._conn.execute(
                "UPDATE sync_state SET cursor = NULL, completed_at = ?, updated_at = ? WHERE key = ?",
                (now, now, key),
            )

    # --- splits / export_log -----------------------------------------------

    def upsert_splits(self, splits: list[Split]) -> int:
        """Insert splits not seen before. Existing rows keep their detected_at. Returns the number inserted."""
        now = _now_iso()
        inserted = 0
        with self._conn:
            for sp in splits:
                cur = self._conn.execute(
                    """INSERT INTO splits (symbol, ex_date, ratio, factor_before, factor_after, detected_at)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(symbol, ex_date) DO NOTHING""",
                    (
                        sp.symbol,
                        sp.ex_date.isoformat(),
                        sp.ratio_text,
                        sp.factor_before or "",
                        sp.factor_after or "",
                        now,
                    ),
                )
                inserted += cur.rowcount
        return inserted

    def replace_splits(self, symbol: str, splits: list[Split]) -> tuple[list[Split], list[Split]]:
        """Make the stored splits of `symbol` equal to `splits`, keeping detected_at of the ones already
        there. Returns (added, removed)."""
        before = {sp.ex_date: sp for sp in self.get_splits(symbol)}
        wanted = {sp.ex_date: sp for sp in splits if sp.symbol == symbol}
        removed = [sp for ex, sp in before.items() if ex not in wanted]
        with self._conn:
            for sp in removed:
                self._conn.execute(
                    "DELETE FROM splits WHERE symbol = ? AND ex_date = ?", (symbol, sp.ex_date.isoformat())
                )
        added = [sp for ex, sp in wanted.items() if ex not in before]
        self.upsert_splits(added)
        return added, removed

    def get_splits(self, symbol: str | None = None) -> list[Split]:
        sql = "SELECT * FROM splits"
        params: tuple = ()
        if symbol:
            sql += " WHERE symbol = ?"
            params = (symbol,)
        sql += " ORDER BY symbol, ex_date"
        return [
            Split(
                symbol=r["symbol"],
                ex_date=date.fromisoformat(r["ex_date"]),
                ratio=Fraction(r["ratio"]),
                factor_before=r["factor_before"] or None,
                factor_after=r["factor_after"] or None,
                detected_at=r["detected_at"],
            )
            for r in self._conn.execute(sql, params)
        ]

    def record_export(self, target: str, rows: int) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO export_log (target, exported_at, rows) VALUES (?, ?, ?)", (target, _now_iso(), rows)
            )

    def last_export(self, target: str) -> str | None:
        row = self._conn.execute("SELECT MAX(exported_at) FROM export_log WHERE target = ?", (target,)).fetchone()
        return row[0] if row else None

    # --- reporting ---------------------------------------------------------

    def summary(self, account_seq: int, *, top_symbols: int = 10) -> OrderSummary:
        q = self._conn.execute
        total = q("SELECT COUNT(*) FROM orders WHERE account_seq = ?", (account_seq,)).fetchone()[0]
        if total == 0:
            return OrderSummary(0, None, None, 0, [], [])
        oldest, newest = q(
            "SELECT MIN(ordered_at), MAX(ordered_at) FROM orders WHERE account_seq = ?", (account_seq,)
        ).fetchone()
        filled = q(
            "SELECT COUNT(*) FROM orders WHERE account_seq = ? AND CAST(filled_quantity AS REAL) > 0", (account_seq,)
        ).fetchone()[0]
        by_status = [
            (r["status"], r["c"])
            for r in q(
                "SELECT status, COUNT(*) c FROM orders WHERE account_seq = ? GROUP BY status ORDER BY c DESC",
                (account_seq,),
            )
        ]
        by_symbol = [
            (r["symbol"], r["c"])
            for r in q(
                "SELECT symbol, COUNT(*) c FROM orders WHERE account_seq = ? GROUP BY symbol ORDER BY c DESC LIMIT ?",
                (account_seq, top_symbols),
            )
        ]
        return OrderSummary(total, oldest, newest, filled, by_status, by_symbol)
