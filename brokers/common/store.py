"""SQLite pieces every broker store shares.

- splits      : stock splits, detected from candles (splits.py) or taken from a corporate-actions
                feed. A row's detected_at is the first time we saw it, which exporters use to warn
                about newly found splits; rows that a later detection no longer finds are removed.
- export_log  : one row per successful export, so the next run knows what "new since last export" means.

A broker store subclasses SplitStore, adds its own tables in its SCHEMA, and implements the
FillSource methods (accounts, fills) the pipeline reads through.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, date, datetime
from fractions import Fraction
from pathlib import Path
from typing import Protocol, Self

from brokers.common.models import Fill, Split

__all__ = ["COMMON_SCHEMA", "FillSource", "SplitStore", "now_iso"]

COMMON_SCHEMA = """
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


def now_iso() -> str:
    # Microseconds: export_log and splits.detected_at are compared as strings, and a split can be
    # stored in the same second as the export that follows it.
    return datetime.now(UTC).isoformat(timespec="microseconds")


class FillSource(Protocol):
    """What the export pipeline needs from a broker store."""

    def __enter__(self) -> Self: ...
    def __exit__(self, *exc) -> None: ...
    def accounts(self) -> list[str]: ...
    def fills(self, account: str, *, currency: str | None = None) -> list[Fill]: ...
    def get_splits(self, symbol: str | None = None) -> list[Split]: ...
    def replace_splits(self, symbol: str, splits: list[Split]) -> tuple[list[Split], list[Split]]: ...
    def record_export(self, target: str, rows: int) -> None: ...
    def last_export(self, target: str) -> str | None: ...


class SplitStore:
    """Opens the database, creates the shared tables, and implements the splits/export_log methods."""

    SCHEMA = ""  # a subclass's own tables, created after COMMON_SCHEMA

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(COMMON_SCHEMA)
        if self.SCHEMA:
            self._conn.executescript(self.SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # --- splits ------------------------------------------------------------

    def upsert_splits(self, splits: list[Split]) -> int:
        """Insert splits not seen before. Existing rows keep their detected_at. Returns the number inserted."""
        now = now_iso()
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

    # --- export_log --------------------------------------------------------

    def record_export(self, target: str, rows: int) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO export_log (target, exported_at, rows) VALUES (?, ?, ?)", (target, now_iso(), rows)
            )

    def last_export(self, target: str) -> str | None:
        row = self._conn.execute("SELECT MAX(exported_at) FROM export_log WHERE target = ?", (target,)).fetchone()
        return row[0] if row else None
