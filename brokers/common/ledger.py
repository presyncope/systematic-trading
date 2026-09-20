"""Pure computations over fills: split normalization, running positions, reconciliation.

No I/O here, so every exporter (TradesViz, Ghostfolio) and every broker shares one set of rules.

Share basis: fills are normalized to the *current* share basis so that fills before and after a
split add up, and open positions match what the broker reports today. A fill on trading date d
is multiplied by the ratio of every split whose ex_date is after d.

Trading date: the exchange-local session date a fill belongs to. A broker that states it puts it
on the Fill (Fill.trading_date); otherwise it is derived from filled_at with the broker's session
rule (`session_date` argument of apply_splits). us_session_date is the rule for US listings:
fills after the 16:00 ET close belong to the next session (a split effective "after close"
already applies to them), and weekend overnight-session fills belong to Monday. Holidays need
no special handling: the only thing done with a trading date is comparing it to split ex_dates.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal
from fractions import Fraction
from zoneinfo import ZoneInfo

from brokers.common.models import Fill, Holding, Split

__all__ = [
    "CLOSE_HOUR",
    "ET",
    "PRICE_PLACES",
    "QUANTITY_PLACES",
    "AdjustedFill",
    "Finding",
    "Mismatch",
    "SessionRule",
    "apply_exclusions",
    "apply_splits",
    "net_positions",
    "position_before",
    "reconcile",
    "signed_quantity",
    "unmatched_sells",
    "us_session_date",
]

ET = ZoneInfo("America/New_York")
CLOSE_HOUR = 16
# Brokers report fractional quantities with up to 6 decimals (e.g. 0.000081); prices with up to 6.
QUANTITY_PLACES = 6
PRICE_PLACES = 6

SessionRule = Callable[[str], date]


def us_session_date(filled_at: str) -> date:
    """Session date of a US-market fill from its timestamp (see module docstring)."""
    dt = datetime.fromisoformat(filled_at).astimezone(ET)
    d = dt.date()
    if dt.hour >= CLOSE_HOUR:
        d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def signed_quantity(fill: Fill) -> Decimal:
    """Buy > 0, sell < 0, in the share basis the fill was reported in."""
    q = Decimal(fill.quantity)
    if fill.side == "SELL":
        return -q
    if fill.side == "BUY":
        return q
    raise ValueError(f"Unknown side {fill.side!r} on order {fill.order_id}")


def _to_decimal(fr: Fraction, places: int) -> tuple[Decimal, bool]:
    """Fraction -> Decimal. Exact when it terminates within `places` decimals, otherwise rounded (flagged)."""
    scaled = fr * 10**places
    if scaled.denominator == 1:
        return _strip(Decimal(scaled.numerator).scaleb(-places)), False
    approx = (Decimal(fr.numerator) / Decimal(fr.denominator)).quantize(Decimal(1).scaleb(-places), ROUND_HALF_EVEN)
    return _strip(approx), True


def _strip(d: Decimal) -> Decimal:
    """Drop trailing zeros without switching to exponent notation ("120.000" -> "120")."""
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return Decimal(s)


@dataclass(frozen=True)
class AdjustedFill:
    """A fill expressed in the current share basis."""

    fill: Fill
    trading_date: date
    factor: Fraction  # cumulative split ratio applied; 1 means quantity/price are the original strings
    quantity: Decimal  # signed (buy > 0, sell < 0)
    price: Decimal  # per share
    near_split: bool  # within one day of a split ex_date: the session boundary rule may be wrong, check by hand
    inexact: bool  # adjusted quantity did not terminate within QUANTITY_PLACES and was rounded

    @property
    def symbol(self) -> str:
        return self.fill.symbol

    @property
    def order_id(self) -> str:
        return self.fill.order_id

    @property
    def amount(self) -> Decimal:
        return abs(self.quantity) * self.price


def apply_splits(
    fills: list[Fill], splits: list[Split], *, session_date: SessionRule = us_session_date
) -> list[AdjustedFill]:
    """Normalize every fill to the current share basis. Order is preserved."""
    by_symbol: dict[str, list[Split]] = defaultdict(list)
    for sp in splits:
        by_symbol[sp.symbol].append(sp)

    out: list[AdjustedFill] = []
    for fill in fills:
        td = fill.trading_date or session_date(fill.filled_at)
        factor = Fraction(1)
        near = False
        for sp in by_symbol.get(fill.symbol, ()):
            if sp.ex_date > td:
                factor *= sp.ratio
            if abs((sp.ex_date - td).days) <= 1:
                near = True
        signed = signed_quantity(fill)
        if factor == 1:
            quantity, price, inexact = signed, Decimal(fill.price), False
        else:
            quantity, inexact = _to_decimal(Fraction(signed) * factor, QUANTITY_PLACES)
            price, _ = _to_decimal(Fraction(Decimal(fill.price)) / factor, PRICE_PLACES)
        out.append(AdjustedFill(fill, td, factor, quantity, price, near, inexact))
    return out


def apply_exclusions(fills: list[AdjustedFill], exclude_ids: set[str]) -> tuple[list[AdjustedFill], list[AdjustedFill]]:
    """Split into (kept, excluded) by order id."""
    kept = [f for f in fills if f.order_id not in exclude_ids]
    excluded = [f for f in fills if f.order_id in exclude_ids]
    return kept, excluded


@dataclass(frozen=True)
class Finding:
    """A sell that takes the running position below zero: its opening fill is not in the data.

    Typical causes: shares received outside the order flow (fractional gifts, transfers) or a
    corporate action the split check cannot see. shortfall is the part with no opening fill.
    """

    fill: AdjustedFill
    shortfall: Decimal

    @property
    def order_id(self) -> str:
        return self.fill.order_id


def unmatched_sells(fills: list[AdjustedFill]) -> list[Finding]:
    """Walk each symbol chronologically; the first sell that overshoots zero is reported and the
    running position is reset to zero so later fills of the same symbol are not re-flagged."""
    findings: list[Finding] = []
    running: dict[str, Decimal] = defaultdict(Decimal)
    for f in fills:
        running[f.symbol] += f.quantity
        if running[f.symbol] < 0:
            findings.append(Finding(f, -running[f.symbol]))
            running[f.symbol] = Decimal(0)
    return findings


def net_positions(fills: list[AdjustedFill]) -> dict[str, Decimal]:
    net: dict[str, Decimal] = defaultdict(Decimal)
    for f in fills:
        net[f.symbol] += f.quantity
    return dict(net)


def position_before(fills: list[AdjustedFill], symbol: str, ex_date: date) -> Decimal:
    """Net position (current basis) built from fills before ex_date. Non-zero means the position
    was open when the split happened, so rows exported earlier are now in the wrong basis."""
    return sum((f.quantity for f in fills if f.symbol == symbol and f.trading_date < ex_date), Decimal(0))


@dataclass(frozen=True)
class Mismatch:
    symbol: str
    ours: Decimal
    broker: Decimal
    name: str


def reconcile(net: dict[str, Decimal], holdings: list[Holding], currency: str | None) -> list[Mismatch]:
    """Compare net positions with what the broker holds today."""
    broker = {h.symbol: (h.quantity, h.name) for h in holdings if currency is None or h.currency == currency}
    out: list[Mismatch] = []
    for symbol in sorted(set(net) | set(broker)):
        ours = net.get(symbol, Decimal(0))
        theirs, name = broker.get(symbol, (Decimal(0), ""))
        if ours != theirs:
            out.append(Mismatch(symbol, ours, theirs, name))
    return out
