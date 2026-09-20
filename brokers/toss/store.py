"""SQLite store for Toss order history.

All SQL lives here. Tables:
- orders      : one row per orderId, upserted (status/execution fields always overwritten).
                Amounts/quantities are decimal strings -> stored as TEXT as-is.
- sync_state  : per-query backfill progress (cursor) so an interrupted run can resume.
- splits, export_log : shared with every broker, see brokers/common/store.py.

Every public write method commits on its own. upsert_orders is idempotent by order_id, so
committing rows before advancing the cursor is safe: a crash in between just re-fetches
that page on the next run.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from brokers.common.models import Fill
from brokers.common.store import SplitStore, now_iso

__all__ = [
    "SCHEMA",
    "UPSERT",
    "Fill",
    "OrderStore",
    "OrderSummary",
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
class OrderSummary:
    total: int
    oldest: str | None
    newest: str | None
    filled: int
    by_status: list[tuple[str, int]]
    by_symbol: list[tuple[str, int]]


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


class OrderStore(SplitStore):
    SCHEMA = SCHEMA

    # --- orders ------------------------------------------------------------

    def upsert_orders(self, orders: list[dict], account_seq: int) -> int:
        fetched_at = now_iso()
        rows = [_order_row(o, account_seq, fetched_at) for o in orders]
        with self._conn:
            self._conn.executemany(UPSERT, rows)
        return len(rows)

    def account_seqs(self) -> list[int]:
        return [r[0] for r in self._conn.execute("SELECT DISTINCT account_seq FROM orders ORDER BY account_seq")]

    def accounts(self) -> list[str]:
        """Account ids as the shared pipeline sees them: the accountSeq as a string."""
        return [str(seq) for seq in self.account_seqs()]

    def fills(self, account: int | str, *, currency: str | None = None) -> list[Fill]:
        """Orders with filled_quantity > 0, oldest first. Filtered by status is wrong here:
        a CANCELED order can still carry a partial fill."""
        sql = """SELECT order_id, symbol, side, filled_quantity, average_filled_price, currency, filled_at,
                        commission, tax
                 FROM orders
                 WHERE account_seq = ? AND CAST(filled_quantity AS REAL) > 0"""
        params: list = [int(account)]
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
        now = now_iso()
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
                (cursor, pages_done, orders_done, now_iso(), key),
            )

    def complete_sync(self, key: str) -> None:
        now = now_iso()
        with self._conn:
            self._conn.execute(
                "UPDATE sync_state SET cursor = NULL, completed_at = ?, updated_at = ? WHERE key = ?",
                (now, now, key),
            )

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
