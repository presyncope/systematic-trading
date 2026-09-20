"""Toss daily candles as a CandleSource for brokers.common.splits.

GET /api/v1/candles serves both adjusted and raw prices (adjusted=true|false). Toss's adjusted
price reflects splits and large return-of-capital distributions but not ordinary dividends
(checked on SCHD, a quarterly payer, over two years), which is what the detector assumes.
Ticker reuse is told from GET /api/v1/stocks listDate.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from decimal import Decimal

from brokers.common.ledger import ET
from brokers.toss.client import TossApiError, TossClient

__all__ = ["NOT_FOUND", "TossCandleSource"]

log = logging.getLogger("toss.candles")

NOT_FOUND = "stock-not-found"


class TossCandleSource:
    def __init__(self, client: TossClient):
        self.client = client

    def _closes(self, symbol: str, since: date, *, adjusted: bool) -> dict[date, Decimal]:
        """Daily closes from today back to `since` (inclusive, possibly a little earlier)."""
        out: dict[date, Decimal] = {}
        before: str | None = None
        seen: set[str] = set()
        while True:
            page = self.client.get_candles(symbol, interval="1d", count=200, before=before, adjusted=adjusted)
            candles = page.get("candles") or []
            for c in candles:
                out[date.fromisoformat(c["timestamp"][:10])] = Decimal(c["closePrice"])
            before = page.get("nextBefore")
            if not candles or not before or before in seen:
                break
            seen.add(before)
            if date.fromisoformat(candles[-1]["timestamp"][:10]) <= since:
                break
        return out

    def daily_factors(self, symbol: str, since: date) -> dict[date, Decimal] | None:
        """raw_close / adjusted_close per trading day from `since` to today. None if the symbol is unknown."""
        try:
            adj = self._closes(symbol, since, adjusted=True)
            raw = self._closes(symbol, since, adjusted=False)
        except TossApiError as e:
            if e.code == NOT_FOUND:
                return None
            raise
        return {d: raw[d] / adj[d] for d in sorted(adj.keys() & raw.keys()) if adj[d] != 0}

    def factor_on(self, symbol: str, on: date) -> Decimal | None:
        """Factor of the last candle on or before `on`, from two one-candle calls. None if unavailable."""
        # Noon local time: includes that day's candle (stamped at local midnight) and excludes the next.
        before = datetime.combine(on, time(12), tzinfo=ET).isoformat()
        try:
            adj = self.client.get_candles(symbol, interval="1d", count=1, before=before, adjusted=True)
            raw = self.client.get_candles(symbol, interval="1d", count=1, before=before, adjusted=False)
        except TossApiError as e:
            if e.code == NOT_FOUND:
                return None  # daily_factors will report the symbol as unverifiable
            raise
        adj_c = adj.get("candles") or []
        raw_c = raw.get("candles") or []
        if (
            not adj_c
            or not raw_c
            or adj_c[0]["timestamp"] != raw_c[0]["timestamp"]
            or Decimal(adj_c[0]["closePrice"]) == 0
        ):
            return None
        log.debug("%s: candle on/before %s is %s", symbol, on, adj_c[0]["timestamp"])
        if date.fromisoformat(adj_c[0]["timestamp"][:10]) > on:
            # The server stamped the candle in a timezone we did not expect and handed us the next day.
            # A split on `on + 1` would then read as factor 1, so let the full series decide instead.
            return None
        return Decimal(raw_c[0]["closePrice"]) / Decimal(adj_c[0]["closePrice"])

    def reused_tickers(self, first_dates: dict[str, date]) -> set[str]:
        """Symbols whose current listing started after our first fill in them (ticker reuse)."""
        symbols = sorted(first_dates)
        reused: set[str] = set()
        for i in range(0, len(symbols), 200):
            chunk = symbols[i : i + 200]
            try:
                infos = self.client.get_stocks(chunk)
            except TossApiError as e:
                # A rejected request (e.g. one symbol the endpoint does not know) only costs this check;
                # server/network failures have already been retried and would fail every candle call too.
                if e.status == 0 or e.status >= 500:
                    raise
                log.warning("Stock info lookup failed for %d symbols, skipping ticker-reuse check: %s", len(chunk), e)
                continue
            for info in infos:
                listed = info.get("listDate")
                if listed and date.fromisoformat(listed) > first_dates.get(info["symbol"], date.max):
                    reused.add(info["symbol"])
        return reused
