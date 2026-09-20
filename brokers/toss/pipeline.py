"""Steps shared by the exporters (TradesViz, Ghostfolio).

An export is: fills from SQLite -> split normalization -> manual adjustments -> checks -> the
product-specific file -> holdings reconciliation. Everything but the file is the same for every
product, so it lives here; an exporter supplies argparse extras and a `write` function.

    p = argparse.ArgumentParser(...)
    pipeline.add_arguments(p)
    args = p.parse_args(argv)
    return pipeline.run(args, target="tradesviz", product="TradesViz", write=my_write)

    def my_write(prepared: Prepared, client: TossClient | None) -> ExportResult: ...

Exit codes: 0 ok / 1 nothing to export or API error / 2 auth or config error /
3 undecided findings (nothing written) / 4 holdings mismatch (file written).
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from brokers.toss import adjustments, auth, config, ledger, splits
from brokers.toss.adjustments import Adjustments
from brokers.toss.client import TossApiError, TossClient
from brokers.toss.ledger import AdjustedFill, Finding, Mismatch
from brokers.toss.store import OrderStore, Split

__all__ = [
    "ExportAbort",
    "ExportResult",
    "Prepared",
    "add_arguments",
    "decide_interactively",
    "prepare",
    "print_findings",
    "print_reconciliation",
    "run",
    "select_account",
]

log = logging.getLogger("toss.pipeline")


class ExportAbort(Exception):
    """Stop the export with this exit code; the reason has already been printed/logged."""

    def __init__(self, code: int):
        super().__init__(f"export aborted with exit code {code}")
        self.code = code


@dataclass(frozen=True)
class Prepared:
    account_seq: int
    currency: str | None
    fills: list[AdjustedFill]  # normalized, exclusions applied, oldest first
    excluded: list[AdjustedFill]
    adjustments: Adjustments


@dataclass(frozen=True)
class ExportResult:
    rows: int
    path: Path


# --- argparse ----------------------------------------------------------------


def add_arguments(p: argparse.ArgumentParser) -> None:
    p.add_argument("--db", type=Path, default=None, help="SQLite path (default: toss.db in config.toml)")
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
    p.add_argument("--offline", action="store_true", help="no API calls: use stored splits, skip the holdings check")
    p.add_argument("--interactive", action="store_true", help="ask for a decision on each flagged fill")
    p.add_argument("-v", "--verbose", action="store_true")


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)


# --- steps -------------------------------------------------------------------


def select_account(store: OrderStore, requested: int | None) -> int:
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
        pct = f"{(measured - 1) * 100:.1f}%"
        log.info("%s: %s price jump on %s taken as a distribution, not a split", symbol, pct, ex_date)
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


def _fmt(d: Decimal) -> str:
    return format(d, "f")


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


def prepare(
    store: OrderStore,
    client: TossClient | None,
    *,
    account_seq: int | None,
    currency: str | None,
    adj: Adjustments,
    adj_path: Path,
    interactive: bool,
) -> Prepared:
    """Fills -> splits -> adjustments -> findings. Raises ExportAbort(1) with nothing to export and
    ExportAbort(3) when findings are left undecided (after printing them)."""
    account_seq = select_account(store, account_seq)
    fills = store.fills(account_seq, currency=currency)
    if not fills:
        log.warning("No fills to export (account_seq=%s, currency=%s)", account_seq, currency or "ALL")
        raise ExportAbort(1)

    if client:
        _report_sync(splits.sync_splits(client, store, fills))
    adjusted = ledger.apply_splits(fills, _merge_splits(store.get_splits(), adj.splits))

    def undecided(adj: Adjustments) -> tuple[list[AdjustedFill], list[AdjustedFill], list[Finding]]:
        kept, excluded = ledger.apply_exclusions(adjusted, adj.exclude_ids)
        return kept, excluded, [f for f in ledger.unmatched_sells(kept) if f.order_id not in adj.fills]

    kept, excluded, findings = undecided(adj)
    if findings and interactive and decide_interactively(findings, adj_path):
        adj = adjustments.load(adj_path)
        kept, excluded, findings = undecided(adj)
    if findings:
        print_findings(findings, adj_path)
        raise ExportAbort(3)

    for af in kept:
        if af.inexact:
            log.warning(
                "%s %s: adjusted quantity rounded to %s (factor %s)", af.symbol, af.trading_date, af.quantity, af.factor
            )
        if af.near_split:
            log.warning(
                "%s %s: filled within a day of a split ex-date; check the share basis of this row by hand",
                af.symbol,
                af.trading_date,
            )
    return Prepared(account_seq, currency, kept, excluded, adj)


def _warn_stale_rows(store: OrderStore, fills: list[AdjustedFill], target: str, product: str) -> None:
    """Splits detected after the last export change rows the product already has."""
    last = store.last_export(target)
    for sp in store.get_splits():
        is_new = sp.detected_at is not None and (last is None or sp.detected_at > last)
        if is_new and ledger.position_before(fills, sp.symbol, sp.ex_date) != 0:
            log.warning(
                "%s: split %s (%s) detected since the last %s export while the position was open. "
                "Delete %s activities in %s, then import this file.",
                sp.symbol,
                sp.ex_date,
                sp.ratio_text,
                product,
                sp.symbol,
                product,
            )


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


# --- runner ------------------------------------------------------------------


def run(
    args: argparse.Namespace,
    *,
    target: str,
    product: str,
    write: Callable[[Prepared, TossClient | None], ExportResult],
) -> int:
    """Run the whole export. `write` turns the prepared fills into the product's file; it gets the
    Toss client (None with --offline) for anything else it wants to look up."""
    _setup_logging(args.verbose)
    currency = None if args.currency.upper() == "ALL" else args.currency.upper()
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
        with OrderStore(args.db or config.db_path()) as store:
            prepared = prepare(
                store,
                client,
                account_seq=args.account_seq,
                currency=currency,
                adj=adj,
                adj_path=adj_path,
                interactive=args.interactive,
            )
            _warn_stale_rows(store, prepared.fills, target, product)
            result = write(prepared, client)
            store.record_export(target, result.rows)
            if client:
                holdings = client.get_holdings(prepared.account_seq).get("items") or []
                net = ledger.net_positions(prepared.fills)
                mismatches = ledger.reconcile(net, holdings, currency)
                print_reconciliation(net, mismatches, currency)
                if mismatches:
                    return 4
    except ExportAbort as e:
        return e.code
    except TossApiError as e:
        log.error("API error: %s", e)
        return 1
    finally:
        if client:
            client.close()
    return 0
