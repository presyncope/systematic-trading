# Personal Systematic Trading System — Build & Learning Roadmap (1 Year)

## Scope & Constraints

| Item            | Decision                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------ |
| Market          | US equities (primary). KRX out of scope for this roadmap                                                           |
| Coverage        | Trade journal, performance tracking, risk management, backtesting. **Orders stay manual**                          |
| Automation      | Deferred to the next roadmap; design for it, don't build it                                                        |
| Budget          | ≤ ₩150k/month for paid services                                                                                    |
| Time            | ~1h weekdays, 4–6h weekends (~9–11h/week)                                                                          |
| Build principle | Buy/adopt if a mature tool exists. Delegate implementation to an agent, but reserve separate time to verify output |
| Brokers         | Toss Securities = the only integration. KIS dropped 2026-10-02 (implementation parked in `trunk/`)                |

---

## TL;DR

Adopt **TradesViz (journal) + Ghostfolio self-host (performance) + Python OSS stack (backtest/risk)**, and spend the budget on **data quality** rather than software. Only one component genuinely requires custom code: the **broker fills → journal/portfolio CSV adapter**.

Backtest stack is fixed as **vectorbt (fast signal exploration) + nautilus_trader (execution realism, and the path to live parity later)**. Validation uses **walk-forward + Deflated Sharpe + PBO** — no CPCV.

---

## 1. Tool Stack

### 1.1 Journal — TradesViz

- Free tier: 3,000 fills/month, 1 account, stocks only — sufficient for current volume.
- Pro $19.99/mo (annual $14.99) if limits are hit.
- 200+ broker CSV imports, open API, 600+ statistics.
- **No Korean broker auto-sync** → CSV adapter required (see §2).

### 1.2 Performance Tracking — Ghostfolio (self-hosted)

- Free, Docker deploy, public API, multi-currency (USD/KRW), TWR + MWR, benchmark comparison.
- No tax reporting → capital gains handled by a separate module (§2.4).
- _Gap cover(optional):_ Ghostfolio has no rebalancing-drift view and only shallow MWR. Portfolio Performance (desktop, free) fills both — use it for periodic deep dives, not daily tracking. Trade-off: manual CSV import, local file, so it duplicates bookkeeping.

### 1.3 Backtesting

| Engine              | Role                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| **vectorbt**        | Fast parameter sweeps, first-pass signal exploration                                              |
| **nautilus_trader** | Execution realism (slippage, fees, partial fills); same framework carries into live trading later |

Rationale for splitting the two: "does the signal exist" and "does it survive execution" are different questions and should not share an engine. nautilus_trader has a steep learning curve — budget real time for it in Q3 rather than treating it as a drop-in.

### 1.4 Risk & Validation Libraries (all free OSS)

| Library             | Use                                                      |
| ------------------- | -------------------------------------------------------- |
| quantstats-reloaded | Performance/risk tearsheets (Sharpe, MDD, win rate)      |
| empyrical-reloaded  | alpha/beta, VaR, Sortino, rolling metrics                |
| PyPortfolioOpt      | Position sizing / allocation (efficient frontier, HRP)   |
| purgedcv            | Purged & embargoed CV, Deflated and Probabilistic Sharpe |

Prefer the `-reloaded` forks; the original `quantstats` and `mlfinlab` are stalled or now closed-source.

### 1.5 Data

**Start here:** Tiingo Power (~$10/mo, EOD + fundamentals) + FMP Starter (~$14/mo) ≈ **$24/mo (~₩35k)**.

**Upgrade trigger:** if backtest results repeatedly diverge from live results, move to **Norgate US Stocks Platinum** ($630/yr ≈ $52.5/mo) for genuinely survivorship-bias-free history (delistings and historical index membership from 1990).

**Alternative:** EODHD All-in-One (€99.99/mo) if single-vendor simplicity outweighs cost — note this sits at or above the ₩150k ceiling depending on FX.

Avoid `yfinance` for anything beyond prototyping.

### 1.6 Broker APIs

- **Toss Securities Open API** — primary integration target. OAuth2 client credentials, base URL `https://openapi.tossinvest.com`, docs at `developers.tossinvest.com`. Account, holdings, and order queries require the `X-Tossinvest-Account` header. No official SDK — generate a client from the OpenAPI spec. Rollout is staged; general-availability date and history depth are unverified, so validate history depth first before building on it.
- **KIS Developers** — **dropped 2026-10-02.** It was implemented directly (overseas and domestic fills with their fees, holdings, cash, KRX dividends) and then retired by decision, not by a technical blocker; the working code is parked in `trunk/kis/` and the API docs stay in `agent-docs/kis/` for reference. Notes if it is ever revived: fills and fees come from different endpoints and must be joined per trade date/symbol/side, the usable TR_IDs are the ones the docs mark as deprecated, and a v3 rewrite is pending.
- Do **not** use unofficial scraping or session reuse — ToS and blocking risk.

---

## 2. What Must Be Built

Everything else is off-the-shelf.

1. **Broker fills → TradesViz/Ghostfolio CSV adapter** (Toss) — the core required piece.
2. **Data ingest & cache pipeline** — vendor APIs → local parquet.
3. **Glue layer** — backtest output → quantstats tearsheet + purgedcv validation wrapper.
4. **FX (USD/KRW) & capital gains estimator** — no off-the-shelf equivalent exists.

### Data flow

```
[Toss fills & balances]     → (CSV adapter) → [TradesViz journal] + [Ghostfolio performance]
                                                    ↓
                                        [quantstats risk dashboard]

[Tiingo/FMP (→Norgate)] → (ingest & parquet cache) → [vectorbt exploration]
     → [nautilus_trader execution check] → [WFO + DSR + PBO validation] → strategy approved
```

### Delegation split

|Agent implements|You verify|
|---|---|
|CSV adapter|Field mapping correctness — fees, FX rate, fill timestamp, buy/sell sign; splits and dividends|
|Data ingest scripts|Survivorship-bias handling, adjusted-price consistency, gaps and duplicates|
|Validation wrapper|Methodology parameters — embargo/purge length, trial count fed into DSR|
|FX & tax module|Current rates and deductions, correct trade-date FX basis|
|Docker deploy & cron|Secrets, backups, access control|

**Rule: the agent writes code; you validate assumptions, mappings, and statistical validity.** Backtest statistics and tax logic are never trusted without manual checking.

---

## 3. Designing for Future Automation

- Keep the signal layer and execution layer separate from day one.
- Emit signals in a standard format (target weights or orders) so only the execution adapter changes later.
- Choosing nautilus_trader now means backtest code and live code share a framework — no rewrite at the automation step.
- Broker auth/account modules built for read-only queries are reusable for order submission.

---

## 4. Learning Roadmap

|Quarter|Focus|Reading|System deliverable|
|---|---|---|---|
|**Q1**|Systematic-trading mindset: risk, diversification, simplicity|Carver, _Systematic Trading_; Van Tharp on position sizing (key chapters)|TradesViz set up; Toss→CSV adapter built; Ghostfolio deployed; 6 months of history backfilled|
|**Q2**|Data pipeline and backtest methodology|López de Prado, _AFML_ Ch.1–8 (data, labeling, CV); Clenow, _Trading Evolved_|Ingest/cache pipeline live; first vectorbt backtest (momentum / MA) with transaction-cost modeling|
|**Q3**|Overfitting and multiple-testing control; walk-forward|Bailey & López de Prado, _Deflated Sharpe Ratio_ (2014); Bailey et al., _Probability of Backtest Overfitting_; Harvey & Liu, _Backtesting_|Walk-forward validation of the first strategy; DSR and PBO reported; nautilus_trader execution check|
|**Q4**|Risk management, factors, execution readiness|Carver, _Advanced Futures Trading Strategies_; Grinold & Kahn, _Active Portfolio Management_; Gray & Vogel, _Quantitative Momentum_|Risk dashboard (MDD limits, correlations, FX exposure); position-sizing rules in code; automation design doc|

**Risk topics running across all quarters:** volatility targeting, fractional Kelly, R-multiples, max-drawdown limits, correlation-based diversification, USD/KRW hedging decision, and the net-of-cost/net-of-tax impact on returns.

### Validation stance

Walk-forward (stitched OOS windows) is treated as sufficient for leakage prevention. Multiple-testing exposure is handled by reporting a **Deflated Sharpe Ratio** with an honest trial count, not by adding CPCV — the added complexity isn't justified for a single-operator system.

Keep the parameter grid small (roughly 5–9 configs per strategy family, a canonical value plus neighbors). Quantizing parameter values prevents implausible inputs but does **not** control trial count — grid size must be capped separately. Adopt or reject at the family level rather than cherry-picking the single best config.

---

## 5. Milestones (Definition of Done)

|Quarter|Milestone|Done when|
|---|---|---|
|Q1|Journal & performance tracking live|Every new trade appears in TradesViz + Ghostfolio within 24h; 6-month backfill complete; TWR and MDD displayed automatically|
|Q2|Data pipeline & backtest environment|US daily data auto-ingested and cached; one vectorbt backtest reproducible with costs and taxes applied|
|Q3|First strategy validated|Walk-forward OOS performance documented; DSR and PBO reported|
|Q4|Risk dashboard & automation-ready|MDD / correlation / FX-exposure dashboard live; sizing rules in code; automation architecture doc and paper-trading plan complete|

### Strategy adoption thresholds

- Deflated Sharpe Ratio > 0 after trial-count correction
- PBO < 50%
- Walk-forward OOS Sharpe ≥ half of in-sample
- Beats SPY **after** transaction costs and taxes

Fails any of these → redesign or discard. Do not be fooled by a raw Sharpe ratio.

### Automation pre-flight checklist (next roadmap)

- [ ] Order API tested on a paper/simulated account
- [ ] Signal → target position → order translation layer standardized
- [ ] Failure, retry, partial-fill, and disconnection handling designed
- [ ] Hard risk limits coded (daily loss, MDD, per-name weight)
- [ ] Logging, alerting (Discord/Slack), audit trail
- [ ] Kill switch and manual override procedure

---

## 6. Tax & Cost Basis (US equities, Korean resident)

- **Capital gains:** 22% (20% + 2% local) on gains above the ₩2.5M annual deduction. Filed the following May. Losses cannot be carried forward, but gains and losses within the same year net out. FX applied at the trade-date reference rate.
- **Dividends:** 15% US withholding.
- Personal circumstances vary — confirm with a tax professional before relying on any figure.

---

## Caveats

- Pricing and feature tiers are as of 2026 and change; re-check vendor pages before committing.
- Toss Open API is still in staged rollout — GA date, history depth, and stability are unverified. Validate history depth before making it the primary integration; there is no second broker integration now that KIS is dropped.
- Backtest statistics and tax calculations produced by an agent must be manually verified before use.
