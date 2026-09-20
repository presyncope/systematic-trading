"""Export Toss fills from SQLite as a Ghostfolio activities JSON file.

Ghostfolio (deploy/ghostfolio) imports activities under Settings > Import. JSON, not CSV, on
purpose: the CSV path only carries a date, the browser stamps every row at local midnight and
the portfolio calculator then processes same-day activities in random order. A sell that runs
before its buy is booked against an empty position, which turns day trades into phantom gains.
JSON activities keep the fill timestamp, so the order is right (verified against 3.71.0:
apps/api/src/app/activities/activities.service.ts orders by date, then id).

File layout (test/import/ok/sample.json upstream):

    accounts    one entry named --account (default "Toss"). Ghostfolio reuses the user's existing
                account with the same name and currency and books the activities into it, so the
                account must exist before importing; its id here is a stable UUID5 of the name.
    activities  date       fill timestamp (execution.filledAt) in UTC; valued on that UTC day
                symbol     ticker as Yahoo Finance knows it (Toss US tickers match; KRX codes do not)
                dataSource YAHOO
                type       BUY / SELL
                quantity   filled quantity, current share basis
                unitPrice  average fill price, current share basis
                fee        commission + tax
                comment    "toss:<orderId>" with --with-order-id, else null

Split normalization matters here even more than for TradesViz: Ghostfolio values holdings at
today's Yahoo price, so quantities must be in today's share basis or a pre-split position is
worth 3x too little (SCHD) or 2000x too much (TANH).

Ghostfolio flags an imported activity as a duplicate when date (to the second), symbol, type,
quantity, price, fee and comment all match an existing one, so re-importing the full file only
adds what is new. --from YYYY-MM-DD exports only sessions on or after that date instead.
Dividends, deposits and withdrawals are not in the Toss API; add them in Ghostfolio by hand.

Usage:
    uv run toss-export-ghostfolio                       # USD fills -> data/toss/ghostfolio_activities.json
    uv run toss-export-ghostfolio --from 2026-09-18     # only newer sessions
    uv run toss-export-ghostfolio --account "Toss US"   # book into a differently named account
    uv run toss-export-ghostfolio --offline             # stored splits only, no API calls
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from brokers.toss import config, pipeline
from brokers.toss.ledger import AdjustedFill
from brokers.toss.pipeline import Prepared

__all__ = [
    "ACCOUNT_NAMESPACE",
    "DATA_SOURCE",
    "DEFAULT_ACCOUNT",
    "TARGET",
    "account_id",
    "export_json",
    "main",
    "to_activity",
]

log = logging.getLogger("toss.export_ghostfolio")

TARGET = "ghostfolio"  # export_log key
DEFAULT_ACCOUNT = "Toss"
DATA_SOURCE = "YAHOO"
# Namespace for the UUID5 account ids, so the same account name always maps to the same id.
ACCOUNT_NAMESPACE = uuid.UUID("6f1c2a7e-9b1d-4c0e-8f3a-2d5b7e9c1a44")


def account_id(name: str) -> str:
    return str(uuid.uuid5(ACCOUNT_NAMESPACE, name))


def _utc_iso(filled_at: str) -> str:
    dt = datetime.fromisoformat(filled_at).astimezone(UTC)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def to_activity(af: AdjustedFill, account: str, *, with_order_id: bool = False) -> dict:
    return {
        "accountId": account_id(account),
        "comment": f"toss:{af.order_id}" if with_order_id else None,
        "currency": af.fill.currency,
        "dataSource": DATA_SOURCE,
        "date": _utc_iso(af.fill.filled_at),
        "fee": float(Decimal(af.fill.commission) + Decimal(af.fill.tax)),
        "quantity": float(abs(af.quantity)),
        "symbol": af.symbol,
        "tags": [],
        "type": "BUY" if af.quantity > 0 else "SELL",
        "unitPrice": float(af.price),
    }


def export_json(
    fills: list[AdjustedFill], out: Path, account: str, *, currency: str, with_order_id: bool = False
) -> pipeline.ExportResult:
    doc = {
        "meta": {"date": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"), "version": "dev"},
        "accounts": [
            {
                "balances": [],
                "comment": None,
                "currency": currency,
                "id": account_id(account),
                "name": account,
                "platformId": None,
            }
        ],
        "activities": [to_activity(f, account, with_order_id=with_order_id) for f in fills],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    return pipeline.ExportResult(rows=len(doc["activities"]), path=out)


def _iso_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Date must be in YYYY-MM-DD format: {s!r}") from e


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export Toss fills as a Ghostfolio activities JSON file")
    pipeline.add_arguments(p)
    p.add_argument("--out", type=Path, default=None, help="output file (default: toss.ghostfolio_json in config.toml)")
    p.add_argument("--account", default=DEFAULT_ACCOUNT, help=f"Ghostfolio account name (default {DEFAULT_ACCOUNT!r})")
    p.add_argument(
        "--from",
        dest="from_date",
        type=_iso_date,
        default=None,
        help="only fills whose session date is on or after this date (YYYY-MM-DD, exchange local)",
    )
    p.add_argument("--with-order-id", action="store_true", help="put toss:<orderId> in each activity's comment")
    args = p.parse_args(argv)
    out: Path = args.out or config.ghostfolio_json_path()

    def write(prepared: Prepared) -> pipeline.ExportResult:
        fills = prepared.fills
        if args.from_date:
            fills = [f for f in fills if f.trading_date >= args.from_date]
        if prepared.currency != "USD":
            log.warning("Symbols are written as-is; non-US tickers may need Yahoo suffixes (e.g. 005930.KS)")
        result = export_json(
            fills, out, args.account, currency=prepared.currency or "USD", with_order_id=args.with_order_id
        )
        if fills:
            log.info(
                "Wrote %d activities (%s ~ %s, %s, %d excluded%s) -> %s",
                result.rows,
                fills[0].trading_date,
                fills[-1].trading_date,
                prepared.currency or "ALL",
                len(prepared.excluded),
                f", from {args.from_date}" if args.from_date else "",
                result.path,
            )
        else:
            log.warning("No fills on or after %s; wrote an empty file -> %s", args.from_date, result.path)
        print(f"Import in Ghostfolio: Settings > Import, account {args.account!r} must exist")
        return result

    return pipeline.run(args, target=TARGET, product="Ghostfolio", write=write)


if __name__ == "__main__":
    sys.exit(main())
