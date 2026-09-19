"""Toss Securities Open API order history backfill -> SQLite.

Per the spec (agent-docs/toss/openapi.json, GET /api/v1/orders):
- status=CLOSED: limit (max 100) + nextCursor cursor pagination. from/to filter on orderedAt (KST);
  unspecified means the full period.
- status=OPEN: returns everything (limit/cursor ignored).
- Only orders placed with order types the Open API supports (limit, market, limit-on-close)
  are returned. Orders such as after-hours closing-price orders are invisible to every query.
- Execution info is an order-level aggregate (execution) only; there is no per-fill list.

Behavior:
- Lists accounts -> auto-selects when there is exactly one, otherwise --account-seq is required.
- Upserts each page into the orders table (keyed by orderId), then saves the cursor to
  sync_state -> re-running with the same parameters resumes after an interruption.
- HTTP retries (401 re-issue, 429, 5xx, network) are handled by client.TossClient.

Usage:
    uv run toss-backfill-orders                       # CLOSED, full period
    uv run toss-backfill-orders --status ALL          # CLOSED + OPEN
    uv run toss-backfill-orders --from 2025-01-01 --to 2025-12-31
    uv run toss-backfill-orders --symbol 005930
    uv run toss-backfill-orders --restart             # ignore the saved cursor and start over
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date
from pathlib import Path

from brokers.toss import auth, config
from brokers.toss.client import OrderQuery, OrderStatus, TossApiError, TossClient
from brokers.toss.store import OrderStore, OrderSummary

__all__ = [
    "backfill",
    "main",
    "print_summary",
    "select_account",
    "sync_key",
]

log = logging.getLogger("toss.backfill")


def sync_key(account_seq: int, query: OrderQuery) -> str:
    # The cursor is bound to the filter combination, so every parameter goes into the key.
    return f"orders|{account_seq}|{query.status}|{query.from_date or ''}|{query.to_date or ''}|{query.symbol or ''}"


def backfill(
    client: TossClient,
    store: OrderStore,
    account_seq: int,
    query: OrderQuery,
    *,
    restart: bool = False,
    page_sleep: float = 0.2,
) -> tuple[int, int]:
    """Fetch one status group to the end. Returns: (page count, order count)."""
    key = sync_key(account_seq, query)
    cursor: str | None = None
    pages_done = orders_done = 0
    if query.paginated and not restart:
        prev = store.get_sync_state(key)
        if prev and prev.resumable:
            cursor, pages_done, orders_done = prev.cursor, prev.pages_done, prev.orders_done
            log.info("Resuming previous run from %d pages / %d orders completed", pages_done, orders_done)
    store.begin_sync(key, cursor=cursor, pages_done=pages_done, orders_done=orders_done)

    seen_cursors: set[str] = set()
    while True:
        page = client.get_orders_page(account_seq, query, cursor)
        orders = page.get("orders") or []
        next_cursor = page.get("nextCursor")
        has_next = bool(page.get("hasNext"))

        # Rows first, cursor second: upsert is idempotent, so a crash in between is safe.
        n = store.upsert_orders(orders, account_seq)
        pages_done += 1
        orders_done += n
        if query.paginated:
            store.advance_sync(
                key, cursor=next_cursor if has_next else None, pages_done=pages_done, orders_done=orders_done
            )

        first = orders[0]["orderedAt"] if orders else "-"
        last = orders[-1]["orderedAt"] if orders else "-"
        log.info("[%s] page %d: %d orders (%s ~ %s) hasNext=%s", query.status, pages_done, n, first, last, has_next)

        if not query.paginated or not has_next or not next_cursor:
            break
        if next_cursor in seen_cursors or next_cursor == cursor:
            log.warning("nextCursor repeated. Stopping to avoid an infinite loop: %s", next_cursor[:40])
            break
        seen_cursors.add(next_cursor)
        cursor = next_cursor
        if page_sleep > 0:
            time.sleep(page_sleep)

    store.complete_sync(key)
    return pages_done, orders_done


def print_summary(summary: OrderSummary, account_seq: int) -> None:
    print(f"\n=== DB summary (account_seq={account_seq}) ===")
    print(f"Total orders        : {summary.total}")
    if summary.total == 0:
        return
    print(f"Oldest order        : {summary.oldest}")
    print(f"Newest order        : {summary.newest}")
    print(f"Orders w/ fills > 0 : {summary.filled}")
    print("By status:")
    for status, count in summary.by_status:
        print(f"  {status:18} {count}")
    print("By symbol (top 10):")
    for symbol, count in summary.by_symbol:
        print(f"  {symbol:10} {count}")


def _iso_date(s: str) -> str:
    try:
        return date.fromisoformat(s).isoformat()
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Date must be in YYYY-MM-DD format: {s!r}") from e


def select_account(client: TossClient, requested: int | None) -> int:
    accounts = client.list_accounts()
    if not accounts:
        raise SystemExit("No accounts found (GET /api/v1/accounts returned an empty array).")
    if requested is not None:
        if not any(a["accountSeq"] == requested for a in accounts):
            raise SystemExit(
                f"--account-seq {requested} is not in the account list: "
                + ", ".join(f"{a['accountSeq']}({a['accountType']}, {a['accountNo']})" for a in accounts)
            )
        return requested
    if len(accounts) == 1:
        a = accounts[0]
        log.info("Auto-selected account: accountSeq=%s (%s, %s)", a["accountSeq"], a["accountType"], a["accountNo"])
        return a["accountSeq"]
    raise SystemExit(
        "Multiple accounts found. Specify one with --account-seq: "
        + ", ".join(f"{a['accountSeq']}({a['accountType']}, {a['accountNo']})" for a in accounts)
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Backfill Toss Securities order history -> SQLite")
    p.add_argument(
        "--status",
        choices=["CLOSED", "OPEN", "ALL"],
        default="CLOSED",
        help="CLOSED (default): finished orders, OPEN: in-progress orders, ALL: both",
    )
    p.add_argument(
        "--from",
        dest="from_date",
        type=_iso_date,
        default=None,
        help="start date YYYY-MM-DD (orderedAt, KST). Unset means the full period",
    )
    p.add_argument(
        "--to",
        dest="to_date",
        type=_iso_date,
        default=None,
        help="end date YYYY-MM-DD (orderedAt, KST). Unset means the full period",
    )
    p.add_argument("--symbol", default=None, help="symbol (6-digit KRX code or US ticker)")
    p.add_argument(
        "--account-seq", type=int, default=None, help="account accountSeq. Auto-selected if there is only one"
    )
    p.add_argument("--limit", type=int, default=100, help="page size 1-100 (default 100)")
    p.add_argument("--sleep", type=float, default=0.2, help="seconds to wait between pages (default 0.2)")
    p.add_argument("--db", type=Path, default=None, help="SQLite path (default: toss.db in config.toml)")
    p.add_argument("--restart", action="store_true", help="ignore the saved cursor and start over")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    if not 1 <= args.limit <= 100:
        p.error("--limit must be between 1 and 100")
    if args.from_date and args.to_date and args.from_date > args.to_date:
        p.error("--from cannot be later than --to")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not args.verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        client = TossClient()
    except auth.TossAuthError as e:
        log.error("%s", e)
        return 2

    db_path = args.db or config.db_path()
    log.info("DB: %s", db_path)
    # argparse choices guarantees args.status is one of CLOSED / OPEN / ALL.
    statuses: list[OrderStatus] = ["CLOSED", "OPEN"] if args.status == "ALL" else [args.status]
    try:
        with client, OrderStore(db_path) as store:
            account_seq = select_account(client, args.account_seq)
            for status in statuses:
                query = OrderQuery(
                    status=status,
                    symbol=args.symbol,
                    from_date=args.from_date,
                    to_date=args.to_date,
                    limit=args.limit,
                )
                pages, n = backfill(client, store, account_seq, query, restart=args.restart, page_sleep=args.sleep)
                log.info("[%s] done: %d pages, %d orders upserted", status, pages, n)
            print_summary(store.summary(account_seq), account_seq)
    except KeyboardInterrupt:
        log.warning("Interrupted. Re-run with the same parameters to resume from the last page.")
        return 130
    except TossApiError as e:
        log.error("API error: %s", e)
        return 1
    except auth.TossAuthError as e:
        log.error("%s", e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
