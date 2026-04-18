# Backtesting Hygiene

A strategy with a great backtest and poor hygiene is a liar. This reference documents the minimum standards your Backtest Engineer agent must enforce before a strategy can be marked `backtested` in the ledger.

## 1. No lookahead bias

**The rule:** every signal at time `t` may only use data known at time `t`.

Common sins:
- Using the close of bar `t` to decide the trade at bar `t` (you don't know the close until the bar ends — trade at `t+1`)
- Using the high or low as part of a signal (you didn't know them in real time)
- Indicators that are normalized by statistics computed over the whole series (z-score, min/max scaling) — must be rolling
- Joining data that was revised later (economic data revisions, adjusted closes, fundamentals)

**Test:** shift your signals by +1 bar. If your backtest improves, you had lookahead.

## 2. Out-of-sample split

Default to 70/30 in-sample / out-of-sample. Never tune parameters on the OOS set — if you do, it's not OOS anymore.

For regime-sensitive strategies, prefer **walk-forward**: fit on rolling 12-month windows, test on the next 3 months, slide, repeat. Report aggregate OOS metrics.

If IS Sharpe = 2.0 and OOS Sharpe = 0.2, your strategy is curve-fit. Reject.

## 3. Fee and slippage realism

Defaults for `backtest_runner.py`:
- `--fee-bps 10` (10 basis points per fill)
- `--slippage-bps 5`

These are conservative. Do your own venue research:
- Hyperliquid perps: ~2.5 bps taker, ~0 bps maker (but fill rate matters)
- US equities retail: near zero explicit, 1-5 bps effective on mid-cap
- DEX spot: 30+ bps including routing

A strategy that needs zero fees to be profitable is not a strategy.

## 4. Survivorship bias

If your dataset only contains tickers/tokens that still trade today, you're missing the ones that went to zero. Backtests on survivors-only data overstate returns by 2-5% annualized on equities, far more on crypto alts.

**Mitigation:** use point-in-time universes. For crypto, include delisted tokens with terminal-value zero. For equities, use a CRSP-style full-history database.

## 5. Look-ahead in universe selection

Related but separate: if you filter your universe at time `t` using criteria that includes data from `t+1..T`, you're cheating. Example: "top 50 coins by market cap" — use the market cap as of `t`, not today.

## 6. Overfit detection

Red flags:
- More than ~5 tunable parameters for a strategy trading on daily bars
- Sharpe drops more than 50% from IS to OOS
- Strategy's performance is wildly sensitive to a single parameter (bump fast MA from 20 to 21, returns halve)
- Trade count is low (< 30 in the OOS window). Small samples say nothing.

**Test:** Monte Carlo the parameters. Randomize ±20% and re-run. If most neighbors fail, you're on a knife edge.

## 7. Regime dependence

A "works in 2021" strategy is a 2021 strategy. Test across at least two qualitatively different regimes: bull/bear, high-vol/low-vol, trending/chop.

For crypto, minimum data: 2018-present (covers the 2018-20 bear, 2021 blow-off, 2022 collapse, 2023 recovery, 2024-25 bull). Without at least one crash in your test set, you have no evidence your strategy survives one.

## 8. Execution feasibility

A strategy that requires 100x the available liquidity at your fill price is a paper strategy. For any trade, check:
- Notional vs average 1-min volume at that bar
- Spread and depth at the time of signal
- Assume 20-50% of top-of-book depth is takeable before you move the market

## 9. Trade count

Statistical meaningfulness requires sample size. Absolute minimums:
- Backtest: 100 trades on in-sample
- Paper: 30 trades before considering promotion
- Live confidence: 100+ live trades before sizing up

## 10. Report what you'd report to an investor

Every backtest should include:
- Period, bar frequency, universe
- Trade count, win rate
- Total return, annualized return, annualized Sharpe
- Max drawdown, drawdown duration
- Turnover, avg holding period
- Fee/slippage assumptions
- Best/worst month
- Correlation to benchmark (BTC, SPX)

If any of these is "not computed," the backtest is incomplete.
