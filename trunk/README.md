# trunk — parked work

Code that was built and then taken out of the active tree. Nothing here is imported, built,
linted or type-checked: `trunk` is excluded from ruff (`pyproject.toml`) and outside the
directories pyright is run on, and the wheel only packages `brokers`, `ghostfolio`, `jobs`.

## kis/ — KIS (한국투자증권) Open API integration

Dropped on 2026-10-02 by decision, not because anything was broken. It worked against the live
account: overseas and domestic fills with their fees joined from the separate fee endpoints,
holdings and cash reconciliation (USD + KRW), KRX dividends, TradesViz CSV and Ghostfolio JSON
exports. What was never built: overseas split detection (step 7 of the plan), the daily-sync
integration (step 8), and historical cash balances (step 9). Deposits, withdrawals, FX conversions
and overseas dividends are not in the KIS Open API at all.

`kis/` is `brokers/kis/` moved verbatim, so its imports still read `brokers.kis.*` and
`brokers.common.*`. `tests/` holds the three mock-transport test scripts that went with it (they
were never moved into the repo's test layout; run them with `uv run python trunk/tests/<file>`
after a restore). `data/kis/` (gitignored) keeps the SQLite DB and the last exports from the live
backfill. The API reference stays in `agent-docs/kis/` — its README has the table of TR_IDs this
code used, with the history limits that were verified live.

### Restoring it

```bash
git mv trunk/kis brokers/kis
mkdir -p data && git mv trunk/data/kis data/kis   # if the old DB is still wanted
```

Then put back the wiring that was removed with it.

`config.toml`:

```toml
[kis]
base_url = "https://openapi.koreainvestment.com:9443"   # live trading domain (the paper-trading one is not supported)
token_cache = ".kis_token.json"
db = "data/kis/kis.sqlite"
tradesviz_csv = "data/kis/tradesviz_executions.csv"
ghostfolio_json = "data/kis/ghostfolio_activities.json"
adjustments = "data/kis/adjustments.toml"
```

`pyproject.toml`, under `[project.scripts]`:

```toml
kis-auth = "brokers.kis.auth:main"
kis-backfill = "brokers.kis.backfill:main"
kis-export-tradesviz = "brokers.kis.export_tradesviz:main"
kis-export-ghostfolio = "brokers.kis.export_ghostfolio:main"
```

`.env.example` (and the real values in `.env`):

```
# Korea Investment & Securities (KIS Developers) live-trading app key/secret and the account
# number as "8 digits-2 digits" (종합계좌번호-계좌상품코드)
KIS_APP_KEY=
KIS_APP_SECRET=
KIS_ACCOUNT=12345678-01
```

`.gitignore` needs `.kis_token.json` back (the cache file is written 0600 in the repo root).

The shared layer still has everything the integration needed — `Broker.dividends`, `Fill.trading_date`,
`Broker.normalize_account`, `ghostfolio_symbol`, per-currency export paths and accounts — so no change
is needed in `brokers/common/`. The README section that documented the commands is in the history:
`git show 42ec914:README.md`.
