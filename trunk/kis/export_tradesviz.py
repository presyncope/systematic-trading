"""Export KIS fills as a TradesViz Custom CSV. The exporter is brokers/common/tradesviz.py.

Usage:
    uv run kis-export-tradesviz                        # USD fills -> data/kis/tradesviz_executions.csv
    uv run kis-export-tradesviz --currency KRW         # KRX fills -> data/kis/tradesviz_executions_krw.csv
    uv run kis-export-tradesviz --interactive          # decide flagged fills on the spot
    uv run kis-export-tradesviz --offline              # no API calls (no holdings check)
"""

from __future__ import annotations

import sys

from brokers.common.tradesviz import COLUMNS, DEFAULT_TZ, TARGET, export_csv, to_row
from brokers.common.tradesviz import main as _main
from brokers.kis.broker import KIS

__all__ = ["COLUMNS", "DEFAULT_TZ", "TARGET", "export_csv", "main", "to_row"]


def main(argv: list[str] | None = None) -> int:
    return _main(KIS, argv)


if __name__ == "__main__":
    sys.exit(main())
