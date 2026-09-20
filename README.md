# systematic-trading

Fetches order history from the Toss Securities Open API (and, in progress, the KIS Open API),
stores it in SQLite, and exports fills as TradesViz and Ghostfolio files.

## Setup

```bash
cp .env.example .env   # fill in TOSS_CLIENT_ID / TOSS_CLIENT_SECRET
uv sync
```

Issue a client under Toss Securities WTS Settings > Open API, and register your current IP in the allowed IP list.

- `.env` — credentials only (gitignored)
- `config.toml` — non-secret settings such as the API base URL, token cache, DB and export paths (`[toss]` section)
- `data/toss/adjustments.toml` — manual corrections for the exporter (gitignored, see below)

Package layout: `brokers/common/` is broker-neutral (ledger, split detection, adjustments, the export
pipeline and both exporters); `brokers/toss/` and `brokers/kis/` plug one broker each into it.

## Usage

```bash
uv run toss-auth                 # issue a token (cached in .toss_token.json, valid for 24h)
uv run toss-backfill-orders      # backfill all closed orders → data/toss/orders.sqlite
uv run toss-export-tradesviz     # USD fills → data/toss/tradesviz_executions.csv
uv run toss-export-ghostfolio    # USD fills → data/toss/ghostfolio_activities.json
```

Common options:

```bash
uv run toss-backfill-orders --status ALL                 # include open orders
uv run toss-backfill-orders --from 2025-01-01 --to 2025-12-31
uv run toss-backfill-orders --symbol 005930
uv run toss-backfill-orders --restart                    # ignore the saved cursor and start over
uv run toss-auth --status                                # show token cache status
uv run toss-export-tradesviz --interactive               # decide on flagged fills as you go
uv run toss-export-tradesviz --offline                   # no API calls: stored splits, no holdings check
uv run toss-export-tradesviz --currency ALL              # include KRW fills
uv run toss-export-tradesviz --tz America/New_York       # exchange time instead of KST
```

If a backfill is interrupted, re-running with the same options resumes from the last page.

### KIS (한국투자증권)

Under construction: overseas (US) fills are stored; exporters, domestic fills and rights follow.
Setup: at [KIS Developers](https://apiportal.koreainvestment.com) issue a **live-trading** (실전투자) app
key for the account, put it in `.env` as `KIS_APP_KEY` / `KIS_APP_SECRET` and the account number as
`KIS_ACCOUNT=12345678-01` (종합계좌번호-계좌상품코드). Overseas endpoints also require the account to
have 해외증권 거래신청 done.

```bash
uv run kis-auth                              # issue a token (cached in .kis_token.json, valid for 24h)
uv run kis-auth --status | --revoke          # cache status / revoke the token early
uv run python -m brokers.kis.client --probe  # call the domestic + overseas balance APIs once
uv run kis-backfill                          # overseas fills → data/kis/kis.sqlite (incremental)
uv run kis-backfill --restart                # the whole history again
```

How KIS fills are built (`brokers/kis/fills.py`): the order endpoint (TTTS3035R) has the order id,
KST time, quantity and price but no fees; the daily-transaction endpoint (CTOS4001R) has the fees,
aggregated per trade date, symbol and side. The two are joined on that key and the fees are spread
over the day's orders in proportion to their amount (`dmst_frcr_fee1` → commission, `frcr_fee1` → fees).
Transaction rows without an order (fractional-share trades, which TTTS3035R omits) become one
synthetic fill at the session close; orders without a transaction row yet are stored with zero fees
and flagged `unsettled` until the next run (every run re-fetches the last 45 days). A ticker change
is recognised from the ISIN on the transaction rows and the earlier fills are renamed to the current
ticker. KIS reports the order-acceptance time, not the fill time, so that is what `filled_at` holds.

KIS issues at most one token a day per app key (a repeat request within 6 hours returns the same
token, more frequent requests are refused), so the cache file is shared by every command. The
paper-trading domain is not supported; the [kis] section of config.toml points at the live one.

### What the exporters check

Both exporters share one pipeline (`brokers/common/pipeline.py`; everything in `brokers/common/` is
broker-neutral, `brokers/toss/` plugs Toss into it). The order history alone is not enough for a
correct journal, so each export also:

1. **Detects stock splits** from Toss daily candles (adjusted vs. raw close) and rewrites pre-split
   fills into the current share basis, so buys and sells add up and open positions match the broker.
   Detected splits are stored in the DB (`splits` table).
2. **Flags sells with no opening fill** (e.g. fractional shares received as a gift, which never appear
   as orders). Each one needs a decision recorded in `data/toss/adjustments.toml` before a CSV is
   written; the exporter prints the block to paste, or `--interactive` asks and records it for you:
   ```toml
   [[fills]]
   order_id = "..."
   action = "exclude"     # or "keep"
   reason = "0.000081 TSLA dust from a fractional gift"
   ```
   Splits the candle check could not resolve go in the same file as `[[splits]]` entries
   (`symbol`, `ex_date`, `ratio = "1/40"`); `ratio = "1/1"` cancels a wrongly detected one.
   Large return-of-capital distributions (YieldMax-style) also move Toss's adjusted price; jumps
   that do not match a real split ratio are logged as distributions and ignored.
3. **Reconciles net positions with `GET /api/v1/holdings`.** A mismatch means something the order
   history cannot show (ticker change, merger, shares moved in or out); the CSV is still written
   but the exit code is 4.

Exit codes: 0 ok · 1 nothing to export · 2 auth/config error · 3 undecided findings (no CSV) · 4 holdings mismatch.

### Importing into TradesViz

Import page → platform **Custom** (execution-level CSV), timezone **Asia/Seoul** (or whatever
`--tz` you exported with), currency **USD**. Re-importing the full file is safe: TradesViz
de-duplicates on timestamp + symbol. Format reference: `agent-docs/tradesviz/custom-csv-format.md`.

That de-duplication also means TradesViz ignores rows that *changed*. When a newly detected split
rewrites a symbol's earlier rows, the exporter says so (`Delete <symbol> trades in TradesViz, then
import this file`); delete that symbol's trades in TradesViz first, then import.

## Ghostfolio (performance tracking)

Self-hosted in Docker, published only on the Tailscale IP (see `deploy/ghostfolio/`):

```bash
cd deploy/ghostfolio
cp .env.example .env            # fill in the secrets: openssl rand -hex 32
docker compose up -d
docker compose logs -f ghostfolio
```

UI: `http://quant-server.tail69c58b.ts.net:3333` (or `http://100.104.205.124:3333`) from any device on
the tailnet. First visit → *Get Started* creates the admin user and shows a security token once — save it,
it is the login. Data is in the `ghostfolio_postgres` volume; back up with
`docker exec gf-postgres pg_dump -U user ghostfolio-db > ghostfolio.sql`.

Then create an account named **Toss** (Settings > Accounts, USD) and import
`data/toss/ghostfolio_activities.json` under Settings > Import. It is JSON rather than CSV because
only JSON keeps the fill timestamps: with date-only rows Ghostfolio processes same-day buys and
sells in random order and day trades turn into phantom gains. Quantities are in today's share
basis, which is what Ghostfolio's Yahoo-based valuation needs. Later runs:
`uv run toss-export-ghostfolio --from YYYY-MM-DD` for just the new sessions (a full re-export works
too, Ghostfolio flags the rows it already has as duplicates). Dividends are not in the Toss API;
add them in Ghostfolio by hand.

`--cash` also records today's USD cash balance on the account (Toss buying power, which matches
the app). The import ignores balances of an existing account, so this uses Ghostfolio's API:
put the security token in `.env` as `GHOSTFOLIO_ACCESS_TOKEN` and the instance URL in `config.toml`
(`[ghostfolio] url`).

## Daily sync (automation)

`daily-sync` runs the whole chain once a day: backfill → `toss-export-ghostfolio --cash` →
Ghostfolio API import (dry run first; only new activities are created) → `toss-export-tradesviz`
(copied to `[tradesviz] sync_dir` if set, e.g. a Google Drive folder TradesViz auto-syncs from).
Anything that is not clean is sent to Telegram (`TELEGRAM_BOT_TOKEN` from @BotFather and
`TELEGRAM_CHAT_ID` in `.env`) and/or a Discord/Slack incoming webhook (`NOTIFY_WEBHOOK_URL`);
`--notify-success` also sends the daily summary.

```bash
uv run daily-sync --notify-test          # first: message the bot, then this prints the chat id / sends a test
deploy/bin/daily-sync.sh                 # run now; log in data/logs/daily-sync.log
uv run daily-sync --no-notify            # print only
```

Scheduled with a systemd user timer at 12:00 KST (`deploy/systemd/`):

```bash
ln -sf "$PWD"/deploy/systemd/daily-sync.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now daily-sync.timer
sudo loginctl enable-linger "$USER"      # once: keep user timers running without a login session
systemctl --user list-timers daily-sync.timer
```

Exit 3 from an exporter (a sell without an opening fill) stops the imports until you record a
decision with `uv run toss-export-ghostfolio --interactive`; exit 4 (holdings mismatch) still
imports but is reported every day until resolved.

## Notes

- Toss API spec: `agent-docs/toss/openapi.json`
- KIS (한국투자증권) API docs: `agent-docs/kis/README.md` (index) + one markdown file per API, generated from the
  portal xlsx export by `uv run --with openpyxl scripts/convert_kis_docs.py agent-docs/kis/source/<export>.xlsx`
- Order types the Open API does not support (e.g. after-hours closing-price orders) are not returned.
- Execution info is an order-level aggregate only (no per-fill list), so one order = one CSV row.
- Fills are exported regardless of order status (a canceled order can carry a partial fill).
- The API has no corporate-action or dividend data. Splits are inferred from candles; dividends,
  deposits and withdrawals are out of scope for the journal (TradesViz does not import them).
