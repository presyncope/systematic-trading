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
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from brokers.toss import adjustments, auth, config, ledger, splits
from brokers.toss.client import TossApiError, TossClient
from brokers.toss.ledger import AdjustedFill, Finding, Mismatch
from brokers.toss.store import OrderStore, Split

__all__ = [
    "COLUMNS",
    "DEFAULT_TZ",
    "TARGET",
    "ExportResult",
    "export_csv",
    "main",
    "to_row",
]

log = logging.getLogger("toss.export_tradesviz")

TARGET = "tradesviz"  # export_log key
DEFAULT_TZ = "Asia/Seoul"

# Column order of the written CSV. Required by TradesViz: date, symbol, asset_type, price, currency, quantity.
COLUMNS = ["date", "time", "symbol", "asset_type", "quantity", "price", "currency", "commission", "fees"]


@dataclass(frozen=True)
class ExportResult:
    rows: int
    path: Path
    collisions: list[tuple[str, str, str, int]]  # (symbol, date, time, count) for timestamp+symbol duplicates


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


def export_csv(fills: list[AdjustedFill], out: Path, tz: ZoneInfo) -> ExportResult:
    rows = [to_row(f, tz) for f in fills]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    seen = Counter((r["symbol"], r["date"], r["time"]) for r in rows)
    collisions = [(*key, n) for key, n in sorted(seen.items()) if n > 1]
    return ExportResult(rows=len(rows), path=out, collisions=collisions)


# --- reporting -------------------------------------------------------------


def _describe(f: Finding) -> str:
    af = f.fill
    amount = _fmt(af.amount.quantize(Decimal("0.01")))
    return (
        f"{af.symbol:6} {af.trading_date}  {_fmt(af.quantity):>12} @ {_fmt(af.price)} (~{amount} {af.fill.currency})"
        f"  short by {_fmt(f.shortfall)}  order {af.order_id}"
    )


def print_findings(findings: list[Finding], adj_path: Path) -> None:
    print("\n=== Sells without an opening fill: decision required ===")
    for f in findings:
        print("  " + _describe(f))
    print(f"\nRecord a decision for each in {adj_path} (or re-run with --interactive):\n")
    for f in findings:
        print(adjustments.fill_block(f.order_id, "exclude", ""))


def decide_interactively(findings: list[Finding], adj_path: Path) -> int:
    """Ask exclude/keep/skip per finding and append the answers. Returns how many were recorded."""
    recorded = 0
    print("\n=== Sells without an opening fill ===")
    for f in findings:
        print("\n  " + _describe(f))
        try:
            while True:
                answer = input("  [e]xclude from exports / [k]eep as-is / [s]kip for now: ").strip().lower()
                if answer in ("e", "k", "s", ""):
                    break
            if answer in ("s", ""):
                continue
            action = "exclude" if answer == "e" else "keep"
            reason = input("  reason (optional): ").strip()
        except EOFError:  # Ctrl-D or exhausted stdin: leave the rest undecided
            print()
            break
        adjustments.append_fill_decision(adj_path, f.order_id, action, reason)
        recorded += 1
    return recorded


def print_reconciliation(net: dict[str, Decimal], mismatches: list[Mismatch], currency: str | None) -> None:
    label = currency or "all currencies"
    bad = {m.symbol for m in mismatches}
    print(f"\n=== Holdings reconciliation ({label}) ===")
    open_symbols = sorted(s for s, q in net.items() if q != 0)
    for symbol in open_symbols:
        if symbol not in bad:
            print(f"  {symbol:8} {_fmt(net[symbol]):>12}  ok")
    for m in mismatches:
        print(f"  {m.symbol:8} {_fmt(m.ours):>12}  MISMATCH: broker has {_fmt(m.broker)} {m.name}".rstrip())
    if mismatches:
        print(f"  {len(mismatches)} mismatch(es). Causes the order history cannot show: ticker changes, mergers,")
        print("  shares received outside the order flow. Check the symbol in the Toss app; fix via adjustments.toml.")
    else:
        print(f"  {len(open_symbols)} open position(s) match the broker.")


def _merge_splits(detected: list[Split], manual: list[Split]) -> list[Split]:
    """Manual entries override a detected split on the same (symbol, ex_date)."""
    merged = {(sp.symbol, sp.ex_date): sp for sp in detected}
    merged.update({(sp.symbol, sp.ex_date): sp for sp in manual})
    return sorted(merged.values(), key=lambda sp: (sp.symbol, sp.ex_date))


def _report_sync(report: splits.SyncReport) -> None:
    log.info(
        "Split check: %d symbols, %d new split(s), %d removed, %d unresolved, %d unverifiable, %d distribution(s)",
        len(report.detections),
        len(report.new),
        len(report.removed),
        len(report.unresolved),
        len(report.unverifiable),
        len(report.distributions),
    )
    for sp in report.removed:
        log.info("Split no longer detected, removed: %s %s ratio %s", sp.symbol, sp.ex_date, sp.ratio_text)
    for symbol, ex_date, measured in report.distributions:
        log.info(
            "%s: %s price jump on %s taken as a distribution, not a split",
            symbol,
            f"{(measured - 1) * 100:.1f}%",
            ex_date,
        )
    for sp in report.new:
        log.info(
            "New split stored: %s %s ratio %s (factor %s -> %s)",
            sp.symbol,
            sp.ex_date,
            sp.ratio_text,
            sp.factor_before,
            sp.factor_after,
        )
    for symbol, ex_date, measured in report.unresolved:
        log.warning(
            "%s: price factor jumped on %s by %s but no clean ratio matches; "
            "check the Toss app and add [[splits]] manually",
            symbol,
            ex_date,
            measured.quantize(Decimal("0.0001")),
        )
    for symbol in report.unverifiable:
        log.warning(
            "%s: splits could not be checked (delisted or ticker reused); only the holdings check covers it", symbol
        )


def _warn_stale_rows(store: OrderStore, kept: list[AdjustedFill]) -> None:
    """Splits detected after the last export change rows TradesViz already has and will ignore."""
    last = store.last_export(TARGET)
    for sp in store.get_splits():
        is_new = sp.detected_at is not None and (last is None or sp.detected_at > last)
        if is_new and ledger.position_before(kept, sp.symbol, sp.ex_date) != 0:
            log.warning(
                "%s: split %s (%s) detected since the last export while the position was open. "
                "Delete %s trades in TradesViz, then import this file.",
                sp.symbol,
                sp.ex_date,
                sp.ratio_text,
                sp.symbol,
            )


# --- CLI -------------------------------------------------------------------


def _select_account(store: OrderStore, requested: int | None) -> int:
    seqs = store.account_seqs()
    if not seqs:
        raise SystemExit("The DB has no orders. Run toss-backfill-orders first.")
    if requested is not None:
        if requested not in seqs:
            raise SystemExit(f"--account-seq {requested} is not in the DB: {seqs}")
        return requested
    if len(seqs) == 1:
        return seqs[0]
    raise SystemExit(f"Multiple accounts in the DB. Specify one with --account-seq: {seqs}")


def _zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as e:
        raise argparse.ArgumentTypeError(f"Unknown timezone: {name!r}") from e


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export Toss fills as a TradesViz Custom (execution-level) CSV")
    p.add_argument("--db", type=Path, default=None, help="SQLite path (default: toss.db in config.toml)")
    p.add_argument("--out", type=Path, default=None, help="output CSV (default: toss.tradesviz_csv in config.toml)")
    p.add_argument(
        "--adjustments",
        type=Path,
        default=None,
        help="manual corrections TOML (default: toss.adjustments in config.toml)",
    )
    p.add_argument("--account-seq", type=int, default=None, help="accountSeq. Auto-selected if the DB has only one")
    p.add_argument(
        "--currency",
        default="USD",
        help="only export fills in this currency, or ALL for every currency (default USD)",
    )
    p.add_argument(
        "--tz",
        type=_zone,
        default=DEFAULT_TZ,
        help=f"timezone for date/time columns; select the same one on the import page (default {DEFAULT_TZ})",
    )
    p.add_argument("--offline", action="store_true", help="no API calls: use stored splits, skip the holdings check")
    p.add_argument("--interactive", action="store_true", help="ask for a decision on each flagged fill")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not args.verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
    tz: ZoneInfo = args.tz  # argparse runs type= on the string default too
    currency = None if args.currency.upper() == "ALL" else args.currency.upper()
    db_path = args.db or config.db_path()
    out = args.out or config.tradesviz_csv_path()
    adj_path = args.adjustments or config.adjustments_path()

    try:
        adj = adjustments.load(adj_path)
    except ValueError as e:
        log.error("%s", e)
        return 2

    client: TossClient | None = None
    if not args.offline:
        try:
            client = TossClient()
        except auth.TossAuthError as e:
            log.error("%s", e)
            return 2

    try:
        with OrderStore(db_path) as store:
            account_seq = _select_account(store, args.account_seq)
            fills = store.fills(account_seq, currency=currency)
            if not fills:
                log.warning("No fills to export (account_seq=%s, currency=%s)", account_seq, currency or "ALL")
                return 1

            if client:
                _report_sync(splits.sync_splits(client, store, fills))
            all_splits = _merge_splits(store.get_splits(), adj.splits)
            adjusted = ledger.apply_splits(fills, all_splits)

            def undecided() -> tuple[list[AdjustedFill], list[Finding]]:
                kept, _ = ledger.apply_exclusions(adjusted, adj.exclude_ids)
                return kept, [f for f in ledger.unmatched_sells(kept) if f.order_id not in adj.fills]

            kept, findings = undecided()
            if findings and args.interactive and decide_interactively(findings, adj_path):
                adj = adjustments.load(adj_path)
                kept, findings = undecided()
            if findings:
                print_findings(findings, adj_path)
                return 3

            for af in kept:
                if af.inexact:
                    log.warning(
                        "%s %s: adjusted quantity rounded to %s (factor %s)",
                        af.symbol,
                        af.trading_date,
                        af.quantity,
                        af.factor,
                    )
                if af.near_split:
                    log.warning(
                        "%s %s: filled within a day of a split ex-date; check the share basis of this row by hand",
                        af.symbol,
                        af.trading_date,
                    )
            _warn_stale_rows(store, kept)

            result = export_csv(kept, out, tz)
            store.record_export(TARGET, result.rows)
            log.info(
                "Wrote %d executions (%s ~ %s, %s, %d excluded) -> %s",
                result.rows,
                kept[0].trading_date,
                kept[-1].trading_date,
                currency or "ALL",
                len(adjusted) - len(kept),
                result.path,
            )
            for symbol, date_, time_, n in result.collisions:
                log.warning(
                    "%d fills of %s at %s %s share a timestamp; TradesViz de-duplicates on timestamp+symbol "
                    "and will keep only one",
                    n,
                    symbol,
                    date_,
                    time_,
                )
            print(f"Import on TradesViz with platform=Custom, timezone={tz.key}, currency={currency or 'per row'}")

            if client:
                holdings = client.get_holdings(account_seq).get("items") or []
                net = ledger.net_positions(kept)
                mismatches = ledger.reconcile(net, holdings, currency)
                print_reconciliation(net, mismatches, currency)
                if mismatches:
                    return 4
    except TossApiError as e:
        log.error("API error: %s", e)
        return 1
    finally:
        if client:
            client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
