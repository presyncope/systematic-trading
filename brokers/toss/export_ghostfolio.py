"""Export Toss fills from SQLite as a Ghostfolio activities CSV.

Ghostfolio (deploy/ghostfolio) imports activities from CSV under Settings > Import. The header
names it recognizes (apps/client/src/app/services/import-activities.service.ts, 3.71.0) and what
this file writes:

    Date        yyyy-MM-dd. Ghostfolio activities are dated, not timed, and are valued against
                daily market data, so the exchange session date is used (ledger.trading_date:
                after-close and weekend overnight fills belong to the next session).
    Code        ticker as Yahoo Finance knows it. Toss US tickers match; KRX codes would not.
    DataSource  YAHOO
    Currency    USD
    Price       average fill price in the current share basis
    Quantity    filled quantity, current share basis (direction comes from Action)
    Action      buy / sell
    Fee         commission + tax
    Note        toss:<orderId>, which also makes Ghostfolio's duplicate check exact: it flags an
                imported activity as a duplicate only when date, symbol, type, quantity, price,
                fee and comment all match an existing one.
    Account     name of the Ghostfolio account to book into (--account, default "Toss"); it must
                exist before importing.

Split normalization matters here even more than for TradesViz: Ghostfolio values holdings at
today's Yahoo price, so quantities must be in today's share basis or a pre-split position is
worth 3x too little (SCHD) or 2000x too much (TANH).

Re-importing the full file works but shows every already-imported row as a duplicate to skip;
--from YYYY-MM-DD exports only sessions on or after that date for incremental imports.
Dividends, deposits and withdrawals are not in the Toss API; add them in Ghostfolio by hand.

Usage:
    uv run toss-export-ghostfolio                       # USD fills -> data/toss/ghostfolio_activities.csv
    uv run toss-export-ghostfolio --from 2026-09-18     # only newer sessions
    uv run toss-export-ghostfolio --account "Toss US"   # book into a differently named account
    uv run toss-export-ghostfolio --offline             # stored splits only, no API calls
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from brokers.toss import config, pipeline
from brokers.toss.ledger import AdjustedFill
from brokers.toss.pipeline import Prepared

__all__ = [
    "COLUMNS",
    "DATA_SOURCE",
    "DEFAULT_ACCOUNT",
    "TARGET",
    "export_csv",
    "main",
    "to_row",
]

log = logging.getLogger("toss.export_ghostfolio")

TARGET = "ghostfolio"  # export_log key
DEFAULT_ACCOUNT = "Toss"
DATA_SOURCE = "YAHOO"

COLUMNS = ["Date", "Code", "DataSource", "Currency", "Price", "Quantity", "Action", "Fee", "Note", "Account"]


def _fmt(d: Decimal) -> str:
    return format(d, "f")


def to_row(af: AdjustedFill, account: str) -> dict[str, str]:
    return {
        "Date": af.trading_date.isoformat(),
        "Code": af.symbol,
        "DataSource": DATA_SOURCE,
        "Currency": af.fill.currency,
        "Price": _fmt(af.price),
        "Quantity": _fmt(abs(af.quantity)),
        "Action": "buy" if af.quantity > 0 else "sell",
        "Fee": _fmt(Decimal(af.fill.commission) + Decimal(af.fill.tax)),
        "Note": f"toss:{af.order_id}",
        "Account": account,
    }


def export_csv(fills: list[AdjustedFill], out: Path, account: str) -> pipeline.ExportResult:
    rows = [to_row(f, account) for f in fills]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return pipeline.ExportResult(rows=len(rows), path=out)


def _iso_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Date must be in YYYY-MM-DD format: {s!r}") from e


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export Toss fills as a Ghostfolio activities CSV")
    pipeline.add_arguments(p)
    p.add_argument("--out", type=Path, default=None, help="output CSV (default: toss.ghostfolio_csv in config.toml)")
    p.add_argument("--account", default=DEFAULT_ACCOUNT, help=f"Ghostfolio account name (default {DEFAULT_ACCOUNT!r})")
    p.add_argument(
        "--from",
        dest="from_date",
        type=_iso_date,
        default=None,
        help="only fills whose session date is on or after this date (YYYY-MM-DD, exchange local)",
    )
    args = p.parse_args(argv)
    out: Path = args.out or config.ghostfolio_csv_path()

    def write(prepared: Prepared) -> pipeline.ExportResult:
        fills = prepared.fills
        if args.from_date:
            fills = [f for f in fills if f.trading_date >= args.from_date]
        if prepared.currency != "USD":
            log.warning("Symbols are written as-is; non-US tickers may need Yahoo suffixes (e.g. 005930.KS)")
        result = export_csv(fills, out, args.account)
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
