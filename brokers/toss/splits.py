"""Detect stock splits from Toss daily candles.

Toss has no corporate-actions endpoint, but GET /api/v1/candles serves both adjusted and raw
prices. raw_close / adjusted_close on a date is the cumulative split multiplier from that date
to today (3.0 before a 3:1 split, 1.0 after) and only changes on a split's ex-date: Toss's
adjusted price ignores dividends (checked on SCHD, a quarterly payer, over two years).

Detection walks that factor series and snaps each jump to a clean ratio. Jumps are snapped one
at a time because a single jump (3, 1/40) is unambiguous, while a cumulative factor such as
1/2000 sits within 0.05% of its neighbours.

Not every jump is a split. Toss also adjusts for large return-of-capital distributions (YieldMax
funds pay 9-14% a month; SCHD's ordinary dividends are left alone). A distribution looks exactly
like a small forward split, so only ratios real splits use are accepted (see SPLIT_RATIOS) and
other jumps between 1x and 2x are logged as distributions and ignored. A distribution of exactly
25% or 50% would still pass as 5:4 or 2:1; the holdings reconciliation is what catches that, and
a `[[splits]]` entry with ratio "1/1" in adjustments.toml cancels a wrong detection.

Cost: two one-candle calls per symbol tell whether anything happened since the first fill
(factor == 1 means no). Only symbols with a non-unit factor need the full daily series.

Not visible here: ticker changes, mergers, spin-offs. A delisted ticker reused by another
company would produce a plausible-looking series, so symbols whose listDate is after our first
fill are reported as unverifiable instead. The holdings reconciliation (ledger.reconcile) is
the safety net for everything this cannot see.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from fractions import Fraction
from itertools import chain

from brokers.toss.client import TossApiError, TossClient
from brokers.toss.ledger import ET, trading_date
from brokers.toss.store import Fill, OrderStore, Split

__all__ = [
    "JUMP_THRESHOLD",
    "SNAP_TOLERANCE",
    "Detection",
    "SyncReport",
    "daily_factors",
    "detect_splits",
    "snap_ratio",
    "sync_splits",
]

log = logging.getLogger("toss.splits")

# Relative change of the raw/adjusted factor between consecutive candles worth looking at.
JUMP_THRESHOLD = Decimal("0.005")
# A jump is accepted when a clean ratio lies within this relative distance of the measured value.
SNAP_TOLERANCE = Fraction(1, 200)
# Uneven ratios that occur in practice. Anything else must be n:1 or 1:k.
SPLIT_RATIOS = (Fraction(3, 2), Fraction(4, 3), Fraction(5, 4), Fraction(5, 2), Fraction(2, 3), Fraction(3, 4))
NOT_FOUND = "stock-not-found"


def snap_ratio(measured: Decimal | Fraction) -> Fraction | None:
    """Nearest split ratio (n:1, 1:k, or one of SPLIT_RATIOS) within SNAP_TOLERANCE, else None."""
    r = Fraction(measured)
    candidates = chain(
        (Fraction(n) for n in range(2, 101)),
        (Fraction(1, k) for k in range(2, 1001)),
        SPLIT_RATIOS,
    )
    best: Fraction | None = None
    best_err: Fraction | None = None
    for c in candidates:
        err = abs(c / r - 1)
        if best_err is None or err < best_err:
            best, best_err = c, err
    return best if best_err is not None and best_err <= SNAP_TOLERANCE else None


def _closes(client: TossClient, symbol: str, since: date, *, adjusted: bool) -> dict[date, Decimal]:
    """Daily closes from today back to `since` (inclusive, possibly a little earlier)."""
    out: dict[date, Decimal] = {}
    before: str | None = None
    seen: set[str] = set()
    while True:
        page = client.get_candles(symbol, interval="1d", count=200, before=before, adjusted=adjusted)
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


def daily_factors(client: TossClient, symbol: str, since: date) -> dict[date, Decimal] | None:
    """raw_close / adjusted_close per trading day from `since` to today. None if the symbol is unknown."""
    try:
        adj = _closes(client, symbol, since, adjusted=True)
        raw = _closes(client, symbol, since, adjusted=False)
    except TossApiError as e:
        if e.code == NOT_FOUND:
            return None
        raise
    return {d: raw[d] / adj[d] for d in sorted(adj.keys() & raw.keys()) if adj[d] != 0}


def _factor_on(client: TossClient, symbol: str, on: date) -> Decimal | None:
    """Factor of the last candle on or before `on`, from two one-candle calls. None if unavailable."""
    # Noon local time: includes that day's candle (stamped at local midnight) and excludes the next.
    before = datetime.combine(on, time(12), tzinfo=ET).isoformat()
    adj = client.get_candles(symbol, interval="1d", count=1, before=before, adjusted=True).get("candles") or []
    raw = client.get_candles(symbol, interval="1d", count=1, before=before, adjusted=False).get("candles") or []
    if not adj or not raw or adj[0]["timestamp"] != raw[0]["timestamp"] or Decimal(adj[0]["closePrice"]) == 0:
        return None
    log.debug("%s: candle on/before %s is %s", symbol, on, adj[0]["timestamp"])
    if date.fromisoformat(adj[0]["timestamp"][:10]) > on:
        # The server stamped the candle in a timezone we did not expect and handed us the next day.
        # A split on `on + 1` would then read as factor 1, so let the full series decide instead.
        return None
    return Decimal(raw[0]["closePrice"]) / Decimal(adj[0]["closePrice"])


@dataclass(frozen=True)
class Detection:
    symbol: str
    splits: list[Split]
    unresolved: list[tuple[date, Decimal]]  # jumps that did not snap to a clean ratio: (ex_date, measured ratio)
    unverifiable: bool  # no candle data (delisted) or ticker reused since our first fill
    distributions: list[tuple[date, Decimal]] = field(default_factory=list)  # 1x-2x jumps taken as payouts


def _looks_like_distribution(measured: Decimal) -> bool:
    return 1 < measured < 2


def detect_splits(client: TossClient, symbol: str, since: date) -> Detection:
    """Splits of `symbol` with ex_date after `since` (the symbol's first trading date)."""
    try:
        f0 = _factor_on(client, symbol, since)
        if f0 is not None and abs(f0 - 1) <= JUMP_THRESHOLD:
            return Detection(symbol, [], [], False)
        factors = daily_factors(client, symbol, since)
    except TossApiError as e:
        if e.code == NOT_FOUND:
            return Detection(symbol, [], [], True)
        raise
    if factors is None:
        return Detection(symbol, [], [], True)

    splits: list[Split] = []
    unresolved: list[tuple[date, Decimal]] = []
    distributions: list[tuple[date, Decimal]] = []
    prev: date | None = None
    for d in sorted(factors):
        if prev is not None and d > since:  # jumps on or before the first fill affect nothing
            f_prev, f = factors[prev], factors[d]
            if abs(f / f_prev - 1) > JUMP_THRESHOLD:
                measured = f_prev / f  # new shares per old share
                ratio = snap_ratio(measured)
                if ratio is None and _looks_like_distribution(measured):
                    distributions.append((d, measured))
                elif ratio is None:
                    unresolved.append((d, measured))
                else:
                    splits.append(
                        Split(
                            symbol,
                            d,
                            ratio,
                            str(f_prev.quantize(Decimal("0.000001"))),
                            str(f.quantize(Decimal("0.000001"))),
                        )
                    )
        prev = d
    return Detection(symbol, splits, unresolved, False, distributions)


@dataclass(frozen=True)
class SyncReport:
    detections: list[Detection]
    new: list[Split]  # inserted into the store by this run
    removed: list[Split]  # stored earlier but no longer detected (e.g. after a detection rule change)

    @property
    def unresolved(self) -> list[tuple[str, date, Decimal]]:
        return [(d.symbol, ex, measured) for d in self.detections for ex, measured in d.unresolved]

    @property
    def unverifiable(self) -> list[str]:
        return [d.symbol for d in self.detections if d.unverifiable]

    @property
    def distributions(self) -> list[tuple[str, date, Decimal]]:
        return [(d.symbol, ex, measured) for d in self.detections for ex, measured in d.distributions]


def _reused_tickers(client: TossClient, first_dates: dict[str, date]) -> set[str]:
    """Symbols whose current listing started after our first fill in them (ticker reuse)."""
    symbols = sorted(first_dates)
    reused: set[str] = set()
    for i in range(0, len(symbols), 200):
        chunk = symbols[i : i + 200]
        try:
            infos = client.get_stocks(chunk)
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


def sync_splits(client: TossClient, store: OrderStore, fills: list[Fill]) -> SyncReport:
    """Detect splits for every symbol in `fills` since its first fill and store the new ones."""
    first_dates: dict[str, date] = {}
    for f in fills:
        td = trading_date(f.filled_at)
        if f.symbol not in first_dates or td < first_dates[f.symbol]:
            first_dates[f.symbol] = td

    reused = _reused_tickers(client, first_dates)
    detections: list[Detection] = []
    new: list[Split] = []
    removed: list[Split] = []
    for symbol in sorted(first_dates):
        if symbol in reused:
            log.warning("%s was listed after our first fill (ticker reuse): splits cannot be verified", symbol)
            detections.append(Detection(symbol, [], [], True))
            continue
        det = detect_splits(client, symbol, first_dates[symbol])
        detections.append(det)
        if not det.unverifiable:
            added, dropped = store.replace_splits(symbol, det.splits)
            new.extend(added)
            removed.extend(dropped)
        log.debug(
            "%s: %d splits, %d unresolved, %d distributions, unverifiable=%s",
            symbol,
            len(det.splits),
            len(det.unresolved),
            len(det.distributions),
            det.unverifiable,
        )
    return SyncReport(detections, new, removed)
