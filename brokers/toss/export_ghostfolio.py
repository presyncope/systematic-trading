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

--cash also records today's USD cash balance (GET /api/v1/buying-power, which matches the app)
on the Ghostfolio account. The import ignores balances for an account that already exists, so
this goes through Ghostfolio's API (POST /api/v1/account-balance) and needs [ghostfolio] url in
config.toml and GHOSTFOLIO_ACCESS_TOKEN in .env. The balance is also written into the file, which
covers the case where the import creates the account.

Usage:
    uv run toss-export-ghostfolio                       # USD fills -> data/toss/ghostfolio_activities.json
    uv run toss-export-ghostfolio --cash                # ...and push today's cash balance to Ghostfolio
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
from brokers.toss.client import TossClient
from brokers.toss.ledger import AdjustedFill
from brokers.toss.pipeline import Prepared
from ghostfolio.client import GhostfolioClient, GhostfolioError

__all__ = [
    "ACCOUNT_NAMESPACE",
    "DATA_SOURCE",
    "DEFAULT_ACCOUNT",
    "TARGET",
    "account_id",
    "export_json",
    "main",
    "push_cash_balance",
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


def _midnight(on: date) -> str:
    return f"{on.isoformat()}T00:00:00.000Z"


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
    fills: list[AdjustedFill],
    out: Path,
    account: str,
    *,
    currency: str,
    with_order_id: bool = False,
    cash: Decimal | None = None,
) -> pipeline.ExportResult:
    now = datetime.now(UTC)
    balances = [{"date": _midnight(now.date()), "value": float(cash)}] if cash is not None else []
    doc = {
        "meta": {"date": now.isoformat(timespec="milliseconds").replace("+00:00", "Z"), "version": "dev"},
        "accounts": [
            {
                "balances": balances,
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


def push_cash_balance(account: str, cash: Decimal, on: date) -> bool:
    """Record `cash` as the account's balance for `on` via the Ghostfolio API. False if not configured."""
    token = config.ghostfolio_access_token()
    if not token:
        log.warning("GHOSTFOLIO_ACCESS_TOKEN is not set in .env; cash balance not pushed to Ghostfolio")
        return False
    try:
        with GhostfolioClient(config.ghostfolio_url(), token) as gf:
            acct = gf.account_by_name(account)
            if not acct:
                log.warning("Ghostfolio has no account named %r; create it first. Cash balance not pushed", account)
                return False
            gf.set_cash_balance(acct["id"], cash, on)
    except (GhostfolioError, OSError) as e:
        log.warning("Cash balance not pushed to Ghostfolio: %s", e)
        return False
    log.info("Ghostfolio account %r cash balance set to %s for %s", account, cash, on)
    return True


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
    p.add_argument(
        "--cash", action="store_true", help="record today's cash balance (buying power) on the Ghostfolio account"
    )
    args = p.parse_args(argv)
    out: Path = args.out or config.ghostfolio_json_path()
    if args.cash and args.offline:
        p.error("--cash needs the Toss API; drop --offline")

    def write(prepared: Prepared, client: TossClient | None) -> pipeline.ExportResult:
        fills = prepared.fills
        if args.from_date:
            fills = [f for f in fills if f.trading_date >= args.from_date]
        currency = prepared.currency or "USD"
        if currency != "USD":
            log.warning("Symbols are written as-is; non-US tickers may need Yahoo suffixes (e.g. 005930.KS)")
        cash = client.get_buying_power(prepared.account_seq, currency) if args.cash and client else None
        result = export_json(fills, out, args.account, currency=currency, with_order_id=args.with_order_id, cash=cash)
        if cash is not None:
            log.info("Cash balance (%s buying power): %s", currency, cash)
            push_cash_balance(args.account, cash, datetime.now(UTC).date())
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
