"""Export Toss fills from SQLite as a TradesViz "Custom" (execution-level) CSV.

Format: agent-docs/tradesviz/custom-csv-format.md. One row per execution; the Toss API only
exposes an order-level aggregate, so one order with fills -> one row (average price, total
filled quantity, time of the last fill).

Pipeline:
1. fills          store.fills(): orders with filled_quantity > 0 regardless of status (a CANCELED
                  order can carry a partial fill). USD only by default (ROADMAP: US equities).
2. splits         Unless --offline, splits.sync_splits() detects stock splits from Toss candles and
                  stores them. ledger.apply_splits() then rewrites pre-split fills into the current
                  share basis (quantity x ratio, price / ratio) so buys and sells add up and open
                  positions match the broker.
3. adjustments    data/toss/adjustments.toml: excluded fills and manually entered splits.
4. checks         A sell that takes the running position below zero has no opening fill in the data
                  (e.g. fractional shares received as a gift). Each one needs a recorded decision
                  (exclude / keep) in adjustments.toml; until then no CSV is written (exit 3).
                  --interactive asks per finding and records the answer.
5. csv            Written, and the export logged so the next run can tell which splits are new.
6. reconcile      Unless --offline, net positions are compared with GET /api/v1/holdings.
                  Mismatches are printed and the exit code is 4 (the CSV is still written).

Mapping:
- date/time   : execution.filledAt in --tz (default Asia/Seoul, as Toss reports it). Select the
                same timezone on the TradesViz import page. --tz America/New_York gives exchange
                time instead; a 10:53 KST fill is the *previous* calendar day there, so the two
                settings must agree.
- quantity    : signed (buy > 0, sell < 0), current share basis. The side column is deliberately
                not written so that the direction has exactly one source.
- price       : execution.averageFilledPrice, current share basis
- commission  : execution.commission (per order, unaffected by splits)
- fees        : execution.tax (SEC fee etc. for US sells)
- asset_type  : stock (TradesViz treats ETFs as stock)

Re-exporting the full history is safe: TradesViz de-duplicates on timestamp + symbol, so a
file with rows it has already seen only adds the new ones. The flip side: rows that *changed*
(a newly detected split rewrites that symbol's earlier rows) are ignored too, so for those
symbols delete the trades in TradesViz and re-import. The exporter says which symbols need it.

Exit codes: 0 ok / 1 nothing to export / 2 auth or config error / 3 undecided findings (no CSV)
/ 4 holdings mismatch (CSV written).

Usage:
    uv run toss-export-tradesviz                        # USD fills -> data/toss/tradesviz_executions.csv
    uv run toss-export-tradesviz --interactive          # decide flagged fills on the spot
    uv run toss-export-tradesviz --offline              # stored splits only, no API calls
    uv run toss-export-tradesviz --currency ALL         # include KRW (KRX symbols are 6-digit codes)
    uv run toss-export-tradesviz --tz America/New_York  # exchange time; select US/Eastern when importing
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from brokers.toss import config, pipeline
from brokers.toss.ledger import AdjustedFill
from brokers.toss.pipeline import Prepared

__all__ = [
    "COLUMNS",
    "DEFAULT_TZ",
    "TARGET",
    "export_csv",
    "main",
    "to_row",
]

log = logging.getLogger("toss.export_tradesviz")

TARGET = "tradesviz"  # export_log key
DEFAULT_TZ = "Asia/Seoul"

# Column order of the written CSV. Required by TradesViz: date, symbol, asset_type, price, currency, quantity.
COLUMNS = ["date", "time", "symbol", "asset_type", "quantity", "price", "currency", "commission", "fees"]


def _fmt(d: Decimal) -> str:
    return format(d, "f")


def to_row(af: AdjustedFill, tz: ZoneInfo) -> dict[str, str]:
    filled_at = datetime.fromisoformat(af.fill.filled_at).astimezone(tz)
    return {
        "date": filled_at.strftime("%Y%m%d"),
        "time": filled_at.strftime("%H:%M:%S"),
        "symbol": af.symbol,
        "asset_type": "stock",
        "quantity": _fmt(af.quantity),
        "price": _fmt(af.price),
        "currency": af.fill.currency,
        "commission": _fmt(Decimal(af.fill.commission)),
        "fees": _fmt(Decimal(af.fill.tax)),
    }


def export_csv(fills: list[AdjustedFill], out: Path, tz: ZoneInfo) -> pipeline.ExportResult:
    rows = [to_row(f, tz) for f in fills]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    seen = Counter((r["symbol"], r["date"], r["time"]) for r in rows)
    for (symbol, date_, time_), n in sorted(seen.items()):
        if n > 1:
            log.warning(
                "%d fills of %s at %s %s share a timestamp; TradesViz de-duplicates on timestamp+symbol "
                "and will keep only one",
                n,
                symbol,
                date_,
                time_,
            )
    return pipeline.ExportResult(rows=len(rows), path=out)


# --- CLI -------------------------------------------------------------------


def _zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as e:
        raise argparse.ArgumentTypeError(f"Unknown timezone: {name!r}") from e


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export Toss fills as a TradesViz Custom (execution-level) CSV")
    pipeline.add_arguments(p)
    p.add_argument("--out", type=Path, default=None, help="output CSV (default: toss.tradesviz_csv in config.toml)")
    p.add_argument(
        "--tz",
        type=_zone,
        default=DEFAULT_TZ,
        help=f"timezone for date/time columns; select the same one on the import page (default {DEFAULT_TZ})",
    )
    args = p.parse_args(argv)
    tz: ZoneInfo = args.tz  # argparse runs type= on the string default too
    out: Path = args.out or config.tradesviz_csv_path()

    def write(prepared: Prepared) -> pipeline.ExportResult:
        result = export_csv(prepared.fills, out, tz)
        fills = prepared.fills
        log.info(
            "Wrote %d executions (%s ~ %s, %s, %d excluded) -> %s",
            result.rows,
            fills[0].trading_date,
            fills[-1].trading_date,
            prepared.currency or "ALL",
            len(prepared.excluded),
            result.path,
        )
        print(f"Import on TradesViz with platform=Custom, timezone={tz.key}, currency={prepared.currency or 'per row'}")
        return result

    return pipeline.run(args, target=TARGET, product="TradesViz", write=write)


if __name__ == "__main__":
    sys.exit(main())
