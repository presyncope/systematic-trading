"""Export Toss fills as a Ghostfolio activities JSON file. The exporter is
brokers/common/ghostfolio_export.py.

Usage:
    uv run toss-export-ghostfolio                       # USD fills -> data/toss/ghostfolio_activities.json
    uv run toss-export-ghostfolio --cash                # ...and push today's cash balance to Ghostfolio
    uv run toss-export-ghostfolio --from 2026-09-18     # only newer sessions
    uv run toss-export-ghostfolio --account "Toss US"   # book into a differently named account
    uv run toss-export-ghostfolio --offline             # stored splits only, no API calls
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
from brokers.toss.broker import TOSS

__all__ = [
    "ACCOUNT_NAMESPACE",
    "DATA_SOURCE",
    "DEFAULT_ACCOUNT",
    "TARGET",
    "account_id",
    "export_json",
    "main",
    "push_cash_balance",
    "to_activity",
]

DEFAULT_ACCOUNT = TOSS.ghostfolio_account


def main(argv: list[str] | None = None) -> int:
    return _main(TOSS, argv)


if __name__ == "__main__":
    sys.exit(main())
