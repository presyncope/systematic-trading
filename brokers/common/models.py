"""Broker-neutral records the exporters work on. Each broker's store produces them."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from fractions import Fraction

__all__ = ["Dividend", "Fill", "Holding", "Split"]


@dataclass(frozen=True)
class Fill:
    """One execution as far as exporters are concerned.

    Brokers that only expose an order-level aggregate (average price, total filled quantity) map
    one order to one Fill. Decimals stay as strings exactly as the API sent them.
    """

    order_id: str
    symbol: str
    side: str  # BUY / SELL
    quantity: str  # filled quantity, always positive
    price: str  # average filled price
    currency: str
    filled_at: str  # ISO 8601 with offset
    commission: str
    tax: str
    # Exchange-local session date when the broker states it; None means the ledger derives it
    # from filled_at with the broker's session rule.
    trading_date: date | None = None


@dataclass(frozen=True)
class Split:
    """A stock split: fills with trading_date < ex_date are in the old share basis.

    ratio is new shares per old share (3 for a 3:1 split, 1/40 for a 1-for-40 reverse split).
    factor_before/after are the measured raw/adjusted close ratios around ex_date; None for
    manually entered splits. detected_at is None until the split has been stored.
    """

    symbol: str
    ex_date: date
    ratio: Fraction
    factor_before: str | None = None
    factor_after: str | None = None
    detected_at: str | None = None

    @property
    def ratio_text(self) -> str:
        return f"{self.ratio.numerator}/{self.ratio.denominator}"


@dataclass(frozen=True)
class Holding:
    """One position as the broker reports it today."""

    symbol: str
    quantity: Decimal
    currency: str
    name: str = ""


@dataclass(frozen=True)
class Dividend:
    """A cash dividend the broker paid into the account.

    amount and tax are totals in `currency`; quantity is the holding the payment was based on, so
    amount / quantity is the per-share dividend. estimated_tax marks a tax figure this code worked
    out because the broker reported none.
    """

    id: str  # stable across runs: "<broker>:<pay date>:<symbol>"
    symbol: str
    paid_on: date
    quantity: Decimal
    amount: Decimal
    tax: Decimal
    currency: str
    name: str = ""
    record_date: date | None = None
    estimated_tax: bool = False

    @property
    def per_share(self) -> Decimal:
        return self.amount / self.quantity if self.quantity else Decimal(0)

    @property
    def net(self) -> Decimal:
        return self.amount - self.tax
