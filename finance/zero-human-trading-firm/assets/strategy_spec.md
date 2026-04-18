# Strategy Spec: {STR-NNNN} — {name}

> One-page spec. No new strategy enters the backtest queue without one.

## Identity
- **Ledger ID:** STR-NNNN
- **Proposed by:** (agent or human identifier)
- **Date:** YYYY-MM-DD
- **Source:** (url, paper DOI, conversation id)

## Hypothesis
One or two sentences. Why should this strategy make money? What market inefficiency or structural feature is it exploiting?

## Mechanics
- **Universe:** (e.g., "top 20 perp contracts on hyperliquid by 30-day volume")
- **Bar frequency:** (1m, 5m, 1h, 1d)
- **Entry signal:** (precise rule, no hand-waving)
- **Exit signal:** (precise rule — time stop, target, trailing stop, opposite signal)
- **Sizing rule:** (fixed notional / vol-target / Kelly fraction)
- **Rebalance cadence:** (every bar, daily, weekly)

## Data requirements
- Bars: (source, adjusted/unadjusted, what lookback needed)
- Auxiliary: (funding rates, order book depth, news feed, etc.)
- Lookback: (minimum history the live strategy needs on startup)

## Expected edge
- Annualized return: X%
- Annualized Sharpe: X.X
- Max drawdown: X%
- Basis for these numbers: (prior work, published paper, backtest, gut?)

## Known risks
- Regime dependence: (what regimes does this likely fail in?)
- Capacity: (at what notional does market impact kill the edge?)
- Correlation: (expected correlation to BTC/SPX/portfolio)
- Fragility: (what single parameter change breaks it?)

## Kill switch
The deterministic condition under which this strategy auto-retires. Must be code-expressible. Example:
> Rolling 20-day Sharpe < -0.5 OR drawdown > 2× backtested max_dd

## Promotion gate (overrides defaults, if any)
- min_trades: (default 30)
- min_sharpe: (default 1.0)
- max_dd: (default 0.10)

## References
- (links to papers, forum posts, related strategies in the ledger)
