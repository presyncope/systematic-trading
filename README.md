# systematic-trading

Fetches order history from the Toss Securities Open API and stores it in SQLite.

## Setup

```bash
cp .env.example .env   # fill in TOSS_CLIENT_ID / TOSS_CLIENT_SECRET
uv sync
```

Issue a client under Toss Securities WTS Settings > Open API, and register your current IP in the allowed IP list.

- `.env` — credentials only (gitignored)
- `config.toml` — non-secret settings such as the API base URL, token cache and DB paths (`[toss]` section)

## Usage

```bash
uv run toss-auth                 # issue a token (cached in .toss_token.json, valid for 24h)
uv run toss-backfill-orders      # backfill all closed orders → data/toss/orders.sqlite
```

Common options:

```bash
uv run toss-backfill-orders --status ALL                 # include open orders
uv run toss-backfill-orders --from 2025-01-01 --to 2025-12-31
uv run toss-backfill-orders --symbol 005930
uv run toss-backfill-orders --restart                    # ignore the saved cursor and start over
uv run toss-auth --status                                # show token cache status
```

If a run is interrupted, re-running with the same options resumes from the last page.

## Notes

- API spec: `agent-docs/toss/openapi.json`
- Order types the Open API does not support (e.g. after-hours closing-price orders) are not returned.
- Execution info is an order-level aggregate only (no per-fill list).
