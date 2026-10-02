"""Daily sync: Toss -> SQLite -> Ghostfolio (via its API) + TradesViz CSV, with a notification.

Steps, each run as a subprocess of this venv so its output is logged and can be quoted:

    1. toss-backfill-orders              new and changed orders into SQLite
    2. toss-export-ghostfolio --cash     activities JSON + today's cash balance on the account
    3. Ghostfolio import                 POST /api/v1/import; the server skips what it already
                                         has (IS_DUPLICATE) and reports every other error
    4. toss-export-tradesviz --offline   CSV (splits were just synced in step 2); copied to
                                         [tradesviz] sync_dir when set, e.g. a Google Drive folder
                                         that TradesViz auto-syncs from
    5. toss-export-portfolio             today's USD holdings + USD cash as a portfolio file that
                                         tradingagents-web reads; runs whatever the steps above did
    6. USD cash check                    compares today's USD cash with the last run's; a change
                                         with no new activity (deposit, exchange) counts as news

A step's exit code decides what follows: backfill failure skips everything (stale data would
only be re-exported); exporter exit 3 (a sell without an opening fill needs a decision in
adjustments.toml) skips the imports and asks for `toss-export-ghostfolio --interactive`; exit 4
(holdings mismatch) still imports but is reported. Anything not clean is sent to the webhook
(jobs/notify.py); --notify-success also sends the summary when everything is fine, --notify-changes
only when it is fine and new activities went into Ghostfolio (the summary then lists them).
--notify-test sends a test message (and, for Telegram, prints the chat ids that have messaged
the bot so TELEGRAM_CHAT_ID can be filled in).

Scheduling: deploy/systemd/daily-sync.timer (09:30 and 18:30 KST). A lock file prevents overlapping runs.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import logging
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import httpx

from brokers.toss import config
from ghostfolio.client import GhostfolioClient, GhostfolioError
from jobs import notify

__all__ = ["Level", "StepResult", "import_to_ghostfolio", "main", "notify_test", "run_module", "summarize"]

log = logging.getLogger("jobs.daily_sync")

STEP_TIMEOUT = 1800  # seconds; the Toss API retries maintenance windows for a few minutes per call
TAIL_LINES = 12

type Level = str  # "ok" | "warn" | "fail" | "skipped"


@dataclass
class StepResult:
    name: str
    level: Level
    note: str = ""
    output: str = ""  # combined stdout/stderr, for the log and the notification
    rc: int | None = None
    changed: bool = False  # the step wrote something new (activities created in Ghostfolio)

    @property
    def ok(self) -> bool:
        return self.level == "ok"


Runner = Callable[[str, list[str]], StepResult]


def run_module(module: str, args: list[str]) -> StepResult:
    """Run `python -m module args` in this venv and capture its output."""
    cmd = [sys.executable, "-m", module, *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=STEP_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"") if isinstance(e.stdout, bytes) else (e.stdout or "")) or ""
        return StepResult(module, "fail", f"timed out after {STEP_TIMEOUT}s", str(out), None)
    output = (proc.stdout or "") + (proc.stderr or "")
    return StepResult(
        module, "ok" if proc.returncode == 0 else "fail", f"exit {proc.returncode}", output, proc.returncode
    )


def _tail(text: str, n: int = TAIL_LINES) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[-n:])


def import_to_ghostfolio(path: Path, *, client: GhostfolioClient | None = None) -> StepResult:
    """Preview the export file with a dry run (the server classifies every activity: new, IS_DUPLICATE
    or rejected), then import for real only when something is new. A real import returns just the
    activities it created."""
    name = "ghostfolio-import"
    token = config.ghostfolio_access_token()
    if client is None and not token:
        return StepResult(name, "fail", "GHOSTFOLIO_ACCESS_TOKEN is not set in .env")
    doc = json.loads(path.read_text())
    try:
        gf = client or GhostfolioClient(config.ghostfolio_url(), token or "", http=httpx.Client(timeout=600.0))
        try:
            preview = gf.import_activities(doc, dry_run=True)
            fresh = [a for a in preview if not a.get("error")]
            duplicates = [a for a in preview if (a.get("error") or {}).get("code") == "IS_DUPLICATE"]
            rejected = [a for a in preview if a.get("error") and a["error"].get("code") != "IS_DUPLICATE"]
            created = gf.import_activities(doc) if fresh else []
        finally:
            if client is None:
                gf.close()
    except (GhostfolioError, httpx.HTTPError) as e:
        return StepResult(name, "fail", f"import failed: {e}")

    note = f"{len(created)} new, {len(duplicates)} already there"
    changed = bool(created)
    if rejected:
        detail = "\n".join(_describe_rejected(a) for a in rejected[:TAIL_LINES])
        return StepResult(name, "fail", f"{note}, {len(rejected)} rejected", detail, changed=changed)
    detail = "\n".join(_describe_activity(a) for a in created)
    if len(created) != len(fresh):
        return StepResult(name, "warn", f"{note}; expected {len(fresh)} new", detail, changed=changed)
    return StepResult(name, "ok", note, detail, changed=changed)


def _describe_activity(a: dict) -> str:
    symbol = (a.get("assetProfile") or {}).get("symbol") or a.get("symbol")
    when = str(a.get("date", ""))[:10]
    return f"  {when} {a.get('type', '')} {symbol} {a.get('quantity', '')} @ {a.get('unitPrice', '')}"


def _describe_rejected(a: dict) -> str:
    err = a.get("error") or {}
    return f"{_describe_activity(a)}: {err.get('code')} {err.get('message', '')}".rstrip()


def _copy_to_sync_dir(csv_path: Path, sync_dir: Path) -> StepResult:
    name = "tradesviz-sync-dir"
    try:
        sync_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(csv_path, sync_dir / csv_path.name)
    except OSError as e:
        return StepResult(name, "fail", f"copy to {sync_dir} failed: {e}")
    return StepResult(name, "ok", f"copied to {sync_dir / csv_path.name}")


def summarize(results: list[StepResult], started: datetime) -> str:
    marks = {"ok": "✅", "warn": "⚠️", "fail": "❌", "skipped": "⏭️"}
    lines = [f"daily-sync {started:%Y-%m-%d %H:%M} UTC"]
    for r in results:
        lines.append(f"{marks[r.level]} {r.name}: {r.note}")
    for r in results:  # what went wrong, or what is new
        if (r.level in ("warn", "fail") or r.changed) and r.output.strip():
            lines.append(f"--- {r.name}\n{_tail(r.output)}")
    return "\n".join(lines)


def _sync(runner: Runner, *, cash: bool, import_client: GhostfolioClient | None = None) -> list[StepResult]:
    results = _sync_orders(runner, cash=cash, import_client=import_client)
    # The holdings snapshot comes straight from the API, so it does not depend on the order steps.
    portfolio = runner("brokers.toss.export_portfolio", [])
    portfolio.name = "portfolio-export"
    results.append(portfolio)
    if portfolio.ok:
        traded = any(r.changed for r in results)
        results.append(check_cash(config.portfolio_json_path(), state_path(), traded=traded))
    return results


def state_path() -> Path:
    """What daily-sync remembers between runs (gitignored data dir, next to the lock)."""
    return config.db_path().parent / "daily-sync-state.json"


def check_cash(portfolio_json: Path, state_file: Path, *, traded: bool) -> StepResult:
    """Compare the USD cash in today's portfolio file with the last run's.

    Cash moves with every trade, so a change counts as news (a notification under
    --notify-changes) only when no new activity was imported: a deposit, a currency
    exchange or a withdrawal, which the Toss API has no transaction record of.
    """
    name = "usd-cash"
    try:
        cash = Decimal(str(json.loads(portfolio_json.read_text())["cash"])).quantize(Decimal("0.01"))
    except (OSError, ValueError, KeyError) as e:
        return StepResult(name, "warn", f"could not read {portfolio_json.name}: {e}")
    try:
        state = json.loads(state_file.read_text())
    except (OSError, ValueError):
        state = {}
    previous = state.get("usd_cash")
    state["usd_cash"] = str(cash)
    state_file.write_text(json.dumps(state, indent=2) + "\n")
    if previous is None:
        return StepResult(name, "ok", f"{cash:,} USD (first record)")
    previous = Decimal(previous)
    if cash == previous:
        return StepResult(name, "ok", f"{cash:,} USD, unchanged")
    delta = cash - previous
    note = f"{previous:,} → {cash:,} USD ({delta:+,})"
    if traded:
        return StepResult(name, "ok", f"{note} with trades")
    return StepResult(name, "ok", f"💵 {note}, no trades: deposit, exchange or withdrawal", changed=True)


def _sync_orders(runner: Runner, *, cash: bool, import_client: GhostfolioClient | None = None) -> list[StepResult]:
    results: list[StepResult] = []

    backfill = runner("brokers.toss.backfill_orders", [])
    backfill.name = "backfill"
    results.append(backfill)
    if not backfill.ok:
        results.append(StepResult("ghostfolio-export", "skipped", "backfill failed"))
        results.append(StepResult("ghostfolio-import", "skipped", "backfill failed"))
        results.append(StepResult("tradesviz-export", "skipped", "backfill failed"))
        return results

    gf_export = runner("brokers.toss.export_ghostfolio", ["--cash"] if cash else [])
    gf_export.name = "ghostfolio-export"
    if gf_export.rc == 3:
        gf_export.level, gf_export.note = "fail", "decision required: run `uv run toss-export-ghostfolio --interactive`"
    elif gf_export.rc == 4:
        gf_export.level, gf_export.note = "warn", "holdings mismatch (file written)"
    results.append(gf_export)

    if gf_export.rc in (0, 4):
        results.append(import_to_ghostfolio(config.ghostfolio_json_path(), client=import_client))
    else:
        results.append(StepResult("ghostfolio-import", "skipped", "no export"))

    if gf_export.rc in (0, 4):
        tv = runner("brokers.toss.export_tradesviz", ["--offline"])
        tv.name = "tradesviz-export"
        results.append(tv)
        sync_dir = config.tradesviz_sync_dir()
        if tv.ok and sync_dir:
            results.append(_copy_to_sync_dir(config.tradesviz_csv_path(), sync_dir))
    else:
        results.append(StepResult("tradesviz-export", "skipped", "no export"))
    return results


def notify_test() -> int:
    """Send a test notification; help with the Telegram chat id first if it is missing."""
    token, chat_id = config.telegram_credentials()
    if token and not chat_id:
        try:
            chats = notify.telegram_chat_ids(token)
        except httpx.HTTPError as e:
            print(f"Telegram getUpdates failed: {e}")
            return 1
        if not chats:
            print("No chats yet: send any message to the bot in Telegram, then run this again.")
            return 1
        print("Chats that messaged the bot; put one in .env as TELEGRAM_CHAT_ID:")
        for cid, who in chats:
            print(f"  TELEGRAM_CHAT_ID={cid}    # {who}")
        return 1
    ok = notify.send(f"daily-sync test {datetime.now(UTC):%Y-%m-%d %H:%M} UTC ✅")
    print("sent" if ok else "not sent (see log)")
    return 0 if ok else 1


def main(argv: list[str] | None = None, *, runner: Runner = run_module) -> int:
    p = argparse.ArgumentParser(description="Daily Toss -> Ghostfolio/TradesViz sync")
    p.add_argument("--notify-success", action="store_true", help="also send the summary when everything is fine")
    p.add_argument(
        "--notify-changes",
        action="store_true",
        help="also send the summary when everything is fine and new activities were imported, "
        "or USD cash changed without a trade",
    )
    p.add_argument("--no-notify", action="store_true", help="never send a notification (print only)")
    p.add_argument("--notify-test", action="store_true", help="send a test notification and exit")
    p.add_argument("--no-cash", action="store_true", help="skip the cash balance update")
    p.add_argument("--lock", type=Path, default=None, help="lock file (default: <db dir>/daily-sync.lock)")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stderr)
    if args.notify_test:
        return notify_test()

    lock_path = args.lock or config.db_path().parent / "daily-sync.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log.warning("Another daily-sync is running (lock %s); exiting", lock_path)
            return 0

        results = _sync(runner, cash=not args.no_cash)

    text = summarize(results, started)
    print(text)
    for r in results:  # full output goes to the log, not the notification
        if r.output.strip():
            log.info("[%s] output:\n%s", r.name, r.output.rstrip())

    clean = all(r.ok for r in results)
    changed = any(r.changed for r in results)
    if not args.no_notify and (not clean or args.notify_success or (args.notify_changes and changed)):
        notify.send(text)
    return 0 if all(r.level != "fail" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
