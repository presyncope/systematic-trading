# TradesViz "Custom" (execution-level CSV) import format

Source: TradesViz import page, platform = "Custom" (captured 2026-09-19).

Use this format when each row of your file is a single execution/order (one fill per row).
If instead each row is a full round-trip trade (open + close), use the Custom Alt format.
Custom format and TradesViz format are not the same.

Currently supported asset classes: Stocks, Options, Futures, Forex, Cryptocurrency.

## Columns

- Required: `date`, `symbol`, `asset_type`, `price`, `currency`, `quantity`
- Optional: `time`, `commission`, `fees`, `side`, `tags`, `notes`, `stop_loss`, `profit_target`, `spread_id`

## Notes

- `asset_type` must be one of: `stock`, `stock_option`, `future`, `future_option`, `index_option`,
  `forex`, `cryptocurrency` (etf is treated as stock).
- `quantity` sign sets the direction: a positive quantity is a buy and a negative quantity is a sell.
  Alternatively, add a `side` column (buy/sell) to set the direction explicitly.
- `date` uses `YYYYMMDD` and `time` uses `HH:MM:SS` (the time can be omitted, or embedded directly
  in the date column).
- `symbol` formats: stocks/crypto/forex use the plain symbol (e.g. AAPL, BTCUSD, USDJPY); options use
  `UNDERLYING DDMMMYY STRIKE C/P` (e.g. `NFLX 28DEC18 230.0 P`); futures use `PRODUCT DDMMMYY`
  (e.g. `MES 20SEP19`); futures options use `PRODUCT DDMMMYY STRIKE C/P` (e.g. `ES 20SEP19 3000.0 C`).
- Options also accept CE/PE, ISO or named-month expiries, and the option type before the strike:
  `NIFTY 2026-09-15 24050 CE`, `NIFTY 15 SEP 2026 CE 24050`. Extra spaces or tabs are accepted.
  Full OCC symbols such as `AAPL260915C00240000` are supported; keep all eight strike digits.
- `commission`/`fees` are the per-execution values for that single row.
- `tags` is a comma-separated list of tags; `notes` is free text. Both are optional.
- `stop_loss`/`profit_target` are optional and let you record your planned exit levels for the trade.
- `spread_id` (optional): give the same value to multiple rows to force them to be grouped into a
  single trade - useful for multi-leg option spreads.

## Import-page settings that matter

- Timezone: the timezone in which the times in the file are reported (see importing-trades.md).
- Currency: the currency in which prices are reported in the file.
- De-duplication is by execution timestamp + symbol, so re-importing the same file is safe.
