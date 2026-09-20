"""KIS account history -> SQLite (data/kis/kis.sqlite).

Overseas: TTTS3035R filled orders and CTOS4001R daily transactions for the date range.
Domestic: TTTC0081R (orders of the last three months) / CTSC9215R (older, in chunks of at most
a year, as the API requires) plus TTTC8715R daily P&L rows (fees and taxes, at most ten years
per call) from the first stored order on, and CTPF1002R once per new symbol (name, market,
ISIN -> instruments). After fetching, the fills table is rebuilt from everything stored
(brokers/kis/fills.py joins orders with the fee rows and spreads the fees).

Date range: --from/--to, exchange-local dates. Without --from the first run starts at
FIRST_DATE (the live account answered a 2015-2026 range with its whole history); later runs go
back RECENT_DAYS before the last fetched date so that rows registered after the previous run
(overseas settlement is T+1/T+2) and modified orders are picked up. --restart fetches the whole
history again.

Usage:
    uv run kis-backfill                          # both markets, incremental
    uv run kis-backfill --market domestic        # one market
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

__all__ = [
    "FIRST_DATE",
    "MARKETS",
    "OLD_TR_CHUNK_DAYS",
    "RECENT_DAYS",
    "RECENT_TR_DAYS",
    "backfill_domestic",
    "backfill_overseas",
    "main",
    "print_summary",
]

log = logging.getLogger("kis.backfill")

MARKETS = ("overseas", "domestic")
FIRST_DATE = date(2015, 1, 1)
RECENT_DAYS = 45
# Domestic orders: TTTC0081R covers "the last three months", CTSC9215R everything before. The two
# overlap by a month here so the boundary cannot leave a gap (rows are upserted by order id).
RECENT_TR_DAYS = 91
OLD_TR_OVERLAP_DAYS = 30
OLD_TR_CHUNK_DAYS = 365  # CTSC9215R: "조회기간은 1년 이내이어야 합니다"
TRADE_PROFIT_MAX_DAYS = 3650  # TTTC8715R: "조회기간은 10년 이내이어야 합니다"


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


def backfill_domestic(
    client: KisClient,
    store: KisStore,
    account: Account,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    restart: bool = False,
) -> tuple[int, int, int]:
    """Fetch, store, rebuild fills. Returns (orders, daily P&L rows, fills)."""
    key = account_key(account)
    start, end = _range(store, key, "domestic", from_date, to_date, restart)
    log.info("Domestic history %s ~ %s (account %s)", start, end, key)
    today = date.today()

    orders: list[dict] = []
    recent_start = max(start, today - timedelta(days=RECENT_TR_DAYS))
    if end >= recent_start:
        orders += client.domestic_orders(account, _yyyymmdd(recent_start), _yyyymmdd(end), recent=True)
    if start < recent_start:  # the range reaches beyond the recent TR's window: older rows come from CTSC9215R
        chunk_end = min(end, recent_start + timedelta(days=OLD_TR_OVERLAP_DAYS))
        while chunk_end >= start:
            chunk_start = max(start, chunk_end - timedelta(days=OLD_TR_CHUNK_DAYS - 1))
            orders += client.domestic_orders(account, _yyyymmdd(chunk_start), _yyyymmdd(chunk_end), recent=False)
            chunk_end = chunk_start - timedelta(days=1)
    filled = {(o["ord_dt"], o["odno"]): o for o in orders if Decimal(o.get("tot_ccld_qty") or "0") > 0}
    n_orders = store.upsert_domestic_orders(list(filled.values()), key)
    log.info("TTTC0081R/CTSC9215R: %d rows (the two TRs overlap), %d distinct with fills stored", len(orders), n_orders)

    pl_start = max(start, end - timedelta(days=TRADE_PROFIT_MAX_DAYS - 1))
    pl = client.domestic_trade_profit(account, _yyyymmdd(pl_start), _yyyymmdd(end))
    n_pl = store.replace_domestic_daily_pl(pl, key, _yyyymmdd(pl_start), _yyyymmdd(end))
    log.info("TTTC8715R: %d rows stored", n_pl)
    store.record_fetch(key, "domestic", start.isoformat(), end.isoformat(), n_orders + n_pl)

    known = store.instruments()
    for pdno in sorted({o["pdno"] for o in store.domestic_orders(key)} - set(known)):
        info = client.stock_info(pdno)
        if not info.get("prdt_name"):
            log.warning("%s: CTPF1002R returned nothing; Yahoo symbol defaults to .KS", pdno)
        store.upsert_instrument(pdno, info.get("prdt_name") or pdno, info.get("mket_id_cd") or "", info.get("std_pdno"))
        log.info(
            "Instrument %s: %s (%s, %s)", pdno, info.get("prdt_name"), info.get("mket_id_cd"), info.get("std_pdno")
        )

    rows = fills.join_domestic(store.domestic_orders(key), store.domestic_daily_pl(key))
    n_fills = store.replace_fills(key, "domestic", rows)
    log.info("fills (domestic): %d rows rebuilt", n_fills)
    return n_orders, n_pl, n_fills


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
    p.add_argument("--market", choices=[*MARKETS, "all"], default="all", help="which history to fetch (default all)")
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
            markets = MARKETS if args.market == "all" else (args.market,)
            for market in markets:
                fn = backfill_overseas if market == "overseas" else backfill_domestic
                fn(client, store, account, from_date=args.from_date, to_date=args.to_date, restart=args.restart)
            for market in markets:
                print_summary(store, account_key(account), market)
    except KisApiError as e:
        log.error("API error: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
