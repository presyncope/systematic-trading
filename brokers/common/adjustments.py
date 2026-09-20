"""Manual corrections for the exporters, kept in a TOML file per broker (data/<broker>/adjustments.toml).

    [[splits]]                 # only for splits the candle check could not resolve
    symbol = "XYZ"
    ex_date = "2025-02-13"     # first session traded on the new share basis (exchange local)
    ratio = "1/40"             # new shares per old share

    [[fills]]                  # decision on a fill the exporter flagged (sell without an opening fill)
    order_id = "..."
    action = "exclude"         # exclude: drop from exports; keep: export as-is, stop asking
    reason = "0.000081 TSLA dust from a fractional gift; no opening fill in the API"

The file is read with tomllib and only ever appended to (tomllib cannot write), so comments and
hand edits survive. Values are written as JSON strings, which are valid TOML basic strings.
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Literal

from brokers.common.models import Split

__all__ = [
    "ACTIONS",
    "Action",
    "Adjustments",
    "Decision",
    "append_fill_decision",
    "fill_block",
    "load",
]

Action = Literal["exclude", "keep"]
ACTIONS: tuple[Action, ...] = ("exclude", "keep")

HEADER = "# Manual corrections applied by the exporters. Format: brokers/common/adjustments.py\n"


@dataclass(frozen=True)
class Decision:
    action: Action
    reason: str


@dataclass(frozen=True)
class Adjustments:
    fills: dict[str, Decision] = field(default_factory=dict)
    splits: list[Split] = field(default_factory=list)

    @property
    def exclude_ids(self) -> set[str]:
        return {oid for oid, d in self.fills.items() if d.action == "exclude"}


def load(path: Path) -> Adjustments:
    """Parse the file. A missing file means no adjustments. Raises ValueError on a bad entry."""
    if not path.exists():
        return Adjustments()
    with path.open("rb") as f:
        data = tomllib.load(f)

    fills: dict[str, Decision] = {}
    for i, entry in enumerate(data.get("fills") or []):
        try:
            order_id = str(entry["order_id"])
            action = entry["action"]
        except KeyError as e:
            raise ValueError(f"{path}: [[fills]] #{i + 1} is missing {e}") from e
        if action not in ACTIONS:
            raise ValueError(f"{path}: [[fills]] {order_id}: action must be one of {ACTIONS}, got {action!r}")
        if order_id in fills:
            raise ValueError(f"{path}: [[fills]] {order_id} appears more than once")
        fills[order_id] = Decision(action, str(entry.get("reason", "")))

    splits: list[Split] = []
    for i, entry in enumerate(data.get("splits") or []):
        try:
            symbol = str(entry["symbol"])
            ex_date = entry["ex_date"]
            ratio = Fraction(str(entry["ratio"]))
        except (KeyError, ValueError, ZeroDivisionError) as e:
            raise ValueError(f"{path}: [[splits]] #{i + 1} is invalid: {e}") from e
        if not isinstance(ex_date, date):  # tomllib parses bare dates; quoted strings need converting
            ex_date = date.fromisoformat(str(ex_date))
        if ratio <= 0:
            raise ValueError(f"{path}: [[splits]] {symbol} {ex_date}: ratio must be positive")
        splits.append(Split(symbol, ex_date, ratio))
    return Adjustments(fills, splits)


def fill_block(order_id: str, action: Action, reason: str) -> str:
    return (
        f"[[fills]]\norder_id = {json.dumps(order_id)}\naction = {json.dumps(action)}\n"
        f"reason = {json.dumps(reason, ensure_ascii=False)}\n"
    )


def append_fill_decision(path: Path, order_id: str, action: Action, reason: str) -> None:
    """Append one [[fills]] entry, creating the file (with its header) if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8") as f:
        if is_new:
            f.write(HEADER)
        f.write("\n" + fill_block(order_id, action, reason))
