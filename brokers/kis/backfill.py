"""KIS account history -> SQLite (data/kis/kis.sqlite).

Overseas (--market overseas): TTTS3035R filled orders and CTOS4001R daily transactions for the
date range, then the fills table is rebuilt from everything stored (brokers/kis/fills.py joins
the two and spreads the fees).

Date range: --from/--to, exchange-local dates. Without --from the first run starts at
FIRST_DATE (KIS returned the account's whole history for a 2015-2026 range); later runs go
back RECENT_DAYS before the newest stored date so that transaction rows registered after the
previous run (settlement is T+1/T+2) and modified orders are picked up. --restart fetches the
whole history again.

Usage:
    uv run kis-backfill                          # overseas, incremental
    uv run kis-backfill --from 2025-07-01        # explicit range start
    uv run kis-backfill --restart                # full history again
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from brokers.common.config import resolve
from brokers.kis import auth, config, fills
from brokers.kis.client import KisApiError, KisClient
from brokers.kis.config import Account
from brokers.kis.store import KisStore, account_key

__all__ = ["FIRST_DATE", "RECENT_DAYS", "backfill_overseas", "main", "print_summary"]

log = logging.getLogger("kis.backfill")

FIRST_DATE = date(2015, 1, 1)
RECENT_DAYS = 45


def _yyyymmdd(d: date) -> str:
    return d.strftime("%Y%m%d")


def _range(store: KisStore, account: str, what: str, from_date: date | None, to_date: date | None, restart: bool):
    end = to_date or date.today()
    if from_date:
        start = from_date
    elif restart or (last := store.last_fetch(account, what)) is None:
        start = FIRST_DATE
    else:
        start = min(date.fromisoformat(last[1]) - timedelta(days=RECENT_DAYS), end)
        if end < date.fromisoformat(last[1]):
            log.warning(
                "--to %s is before the last fetched date %s; only %s ~ %s is refreshed", end, last[1], start, end
            )
    if start > end:
        raise SystemExit(f"--from {start} is after --to {end}")
    return start, end


def backfill_overseas(
    client: KisClient,
    store: KisStore,
    account: Account,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    restart: bool = False,
) -> tuple[int, int, int]:
    """Fetch, store, rebuild fills. Returns (orders, transactions, fills)."""
    key = account_key(account)
    start, end = _range(store, key, "overseas", from_date, to_date, restart)
    log.info("Overseas history %s ~ %s (account %s)", start, end, key)

    orders = client.overseas_orders(account, _yyyymmdd(start), _yyyymmdd(end))
    filled = [o for o in orders if Decimal(o.get("ft_ccld_qty") or "0") > 0]
    n_orders = store.upsert_overseas_orders(filled, key)
    log.info("TTTS3035R: %d rows, %d with fills stored", len(orders), n_orders)

    trans = client.overseas_trans(account, _yyyymmdd(start), _yyyymmdd(end))
    n_trans = store.replace_overseas_trans(trans, key, _yyyymmdd(start), _yyyymmdd(end))
    log.info("CTOS4001R: %d rows stored", n_trans)
    store.record_fetch(key, "overseas", start.isoformat(), end.isoformat(), n_orders + n_trans)

    rows = fills.join_overseas(store.overseas_orders(key), store.overseas_trans(key))
    n_fills = store.replace_fills(key, "overseas", rows)
    log.info("fills (overseas): %d rows rebuilt", n_fills)
    return n_orders, n_trans, n_fills


def print_summary(store: KisStore, account: str, market: str) -> None:
    rows = store.fills(account, market=market)  # all currencies
    print(f"\n=== fills summary (account {account}, {market}) ===")
    if not rows:
        print("no fills")
        return
    dates = [f.trading_date for f in rows if f.trading_date]
    print(f"Fills               : {len(rows)}  ({min(dates)} ~ {max(dates)})")
    by_ccy: dict[str, dict[str, Decimal]] = {}
    for f in rows:
        d = by_ccy.setdefault(f.currency, {"BUY": Decimal(0), "SELL": Decimal(0), "fees": Decimal(0)})
        d[f.side] += Decimal(f.quantity) * Decimal(f.price)
        d["fees"] += Decimal(f.commission) + Decimal(f.tax)
    for ccy, d in sorted(by_ccy.items()):
        print(f"  {ccy}: bought {d['BUY']:,.2f}  sold {d['SELL']:,.2f}  fees {d['fees']:,.4f}")
    flagged = store.flagged_fills(account, market)
    flags = Counter(flag for r in flagged for flag in json.loads(r["flags"]))
    print(f"Flagged             : {dict(flags) if flags else 'none'}")
    for r in flagged[:10]:
        line = f"  {r['trading_date']} {r['side']:4} {r['symbol']:6} {r['quantity']} @ {r['price']}"
        print(f"{line}  {r['flags']}  {r['fill_id']}")
    symbols = Counter(f.symbol for f in rows)
    print("By symbol (top 10):")
    for symbol, n in symbols.most_common(10):
        print(f"  {symbol:10} {n}")
    print("Latest 5:")
    for f in rows[-5:]:
        print(
            f"  {f.filled_at} {f.trading_date} {f.side:4} {f.symbol:6} {f.quantity} @ {f.price} "
            f"fee {f.commission}+{f.tax} {f.currency}  {f.order_id}"
        )


def _iso_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Date must be in YYYY-MM-DD format: {s!r}") from e


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fetch KIS account history into SQLite")
    p.add_argument("--market", choices=["overseas"], default="overseas", help="which history to fetch")
    p.add_argument("--from", dest="from_date", type=_iso_date, default=None, help="start date (YYYY-MM-DD)")
    p.add_argument("--to", dest="to_date", type=_iso_date, default=None, help="end date (default today)")
    p.add_argument("--restart", action="store_true", help="fetch the whole history again")
    p.add_argument("--kis-account", default=None, help="CANO-PRDT (default KIS_ACCOUNT from .env)")
    p.add_argument("--db", type=Path, default=None, help="SQLite path (default: kis.db in config.toml)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not args.verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        account = config.parse_account(args.kis_account) if args.kis_account else config.account()
    except ValueError as e:
        log.error("%s", e)
        return 2
    if account is None:
        log.error("KIS_ACCOUNT is not set in .env (or pass --kis-account 12345678-01)")
        return 2

    try:
        client = KisClient()
    except auth.KisAuthError as e:
        log.error("%s", e)
        return 2
    try:
        with client, KisStore(resolve(str(args.db)) if args.db else config.db_path()) as store:
            backfill_overseas(
                client, store, account, from_date=args.from_date, to_date=args.to_date, restart=args.restart
            )
            print_summary(store, account_key(account), "overseas")
    except KisApiError as e:
        log.error("API error: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
