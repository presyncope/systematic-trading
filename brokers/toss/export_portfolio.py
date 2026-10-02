"""Write today's USD holdings and USD cash as a TradingAgents portfolio file.

    uv run toss-export-portfolio                 # → data/toss/portfolio.json
    uv run toss-export-portfolio --account-seq 1

The file follows TradingAgents' PortfolioContext (`cash`, `currency`, `positions[]` with `ticker`,
`quantity`, `average_price`), plus `source`, `synced_at` and `account_seq` for whoever reads it
(tradingagents-web picks it up through TRADINGAGENTS_WEB_PORTFOLIO_FILE). Only USD-traded holdings
are written: their Toss symbols are the Yahoo tickers TradingAgents prices. Quantities and prices
are what GET /api/v1/holdings and GET /api/v1/buying-power report now; the file is a snapshot, not
a history. It is replaced atomically, so a reader never sees half a file.

Exit codes: 0 written · 2 auth/config error.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from brokers.toss import auth, config
from brokers.toss.backfill_orders import select_account
from brokers.toss.client import TossApiError, TossClient

log = logging.getLogger("toss.export_portfolio")

CURRENCY = "USD"


def build_portfolio(holdings: dict, cash: Decimal, *, account_seq: int, now: datetime | None = None) -> dict:
    """The portfolio document from a HoldingsOverview and the USD cash balance."""
    positions = []
    for item in holdings.get("items") or []:
        if item.get("currency") != CURRENCY:
            continue
        quantity = Decimal(item["quantity"])
        if quantity == 0:
            continue
        average = item.get("averagePurchasePrice")
        positions.append({
            "ticker": item["symbol"].strip().upper(),
            "quantity": float(quantity),
            "average_price": float(Decimal(average)) if average not in (None, "") else None,
        })
    positions.sort(key=lambda p: p["ticker"])
    return {
        "cash": float(cash),
        "currency": CURRENCY,
        "positions": positions,
        "source": "toss",
        "synced_at": (now or datetime.now(UTC)).isoformat(timespec="seconds"),
        "account_seq": account_seq,
    }


def write_atomic(doc: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="toss-export-portfolio", description=__doc__.splitlines()[0])
    p.add_argument("--account-seq", type=int, help="accountSeq. Auto-selected if there is only one")
    p.add_argument("--out", type=Path, help="output file (default: [toss] portfolio_json in config.toml)")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    out = args.out or config.portfolio_json_path()
    try:
        with TossClient() as client:
            account_seq = select_account(client, args.account_seq)
            doc = build_portfolio(client.get_holdings(account_seq),
                                  client.get_buying_power(account_seq, CURRENCY), account_seq=account_seq)
    except auth.TossAuthError as e:
        print(f"auth error: {e}", file=sys.stderr)
        return 2
    except TossApiError as e:
        print(f"Toss API error: {e}", file=sys.stderr)
        return 2
    write_atomic(doc, out)
    print(f"{len(doc['positions'])} USD positions and USD cash → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
