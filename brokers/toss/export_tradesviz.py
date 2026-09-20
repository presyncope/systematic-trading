"""Export Toss fills as a TradesViz Custom CSV. The exporter is brokers/common/tradesviz.py.

Usage:
    uv run toss-export-tradesviz                        # USD fills -> data/toss/tradesviz_executions.csv
    uv run toss-export-tradesviz --interactive          # decide flagged fills on the spot
    uv run toss-export-tradesviz --offline              # stored splits only, no API calls
    uv run toss-export-tradesviz --currency ALL         # include KRW (KRX symbols are 6-digit codes)
    uv run toss-export-tradesviz --tz America/New_York  # exchange time; select US/Eastern when importing
"""

from __future__ import annotations

import sys

from brokers.common.tradesviz import COLUMNS, DEFAULT_TZ, TARGET, export_csv, to_row
from brokers.common.tradesviz import main as _main
from brokers.toss.broker import TOSS

__all__ = ["COLUMNS", "DEFAULT_TZ", "TARGET", "export_csv", "main", "to_row"]


def main(argv: list[str] | None = None) -> int:
    return _main(TOSS, argv)


if __name__ == "__main__":
    sys.exit(main())
