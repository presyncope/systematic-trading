"""Export KIS fills as a Ghostfolio activities JSON file. The exporter is
brokers/common/ghostfolio_export.py.

One Ghostfolio account per currency: USD fills go to "KIS", KRW fills to "KIS KRW" (create both
in Ghostfolio first, with that currency). KRX symbols are written as Yahoo knows them
(005930.KS / 440110.KQ, from the instruments table).

Usage:
    uv run kis-export-ghostfolio                        # USD fills -> data/kis/ghostfolio_activities.json
    uv run kis-export-ghostfolio --cash                 # ...and push today's USD cash balance to Ghostfolio
    uv run kis-export-ghostfolio --currency KRW --cash  # KRX fills -> ..._krw.json, KRW 예수금 to "KIS KRW"
    uv run kis-export-ghostfolio --offline              # no API calls
"""

from __future__ import annotations

import sys

from brokers.common.ghostfolio_export import (
    ACCOUNT_NAMESPACE,
    DATA_SOURCE,
    TARGET,
    account_id,
    export_json,
    push_cash_balance,
    to_activity,
)
from brokers.common.ghostfolio_export import main as _main
from brokers.kis.broker import KIS

__all__ = [
    "ACCOUNT_NAMESPACE",
    "DATA_SOURCE",
    "TARGET",
    "account_id",
    "export_json",
    "main",
    "push_cash_balance",
    "to_activity",
]


def main(argv: list[str] | None = None) -> int:
    return _main(KIS, argv)


if __name__ == "__main__":
    sys.exit(main())
