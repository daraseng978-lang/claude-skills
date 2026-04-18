# Postmortem — STR-NNNN

> Filed within 7 days of retirement. Input for the Research Agent's future idea filters.

## Identity
- **Ledger ID:** STR-NNNN
- **Name:** {name}
- **Started paper:** YYYY-MM-DD
- **Went live:** YYYY-MM-DD
- **Retired:** YYYY-MM-DD
- **Retirement trigger:** (auto kill switch / manual / drawdown / correlation)

## Lifetime stats
- Total trades: N
- Total return: X%
- Sharpe: X.X
- Max drawdown: X%
- Realized fees + slippage: $X

## What went wrong
One paragraph. Be specific: which assumption broke, what changed in the market, when did the edge disappear.

## Was this predictable?
- In backtest? (did the backtest hint at this and we ignored it)
- In red team? (did the red team flag this and we signed off anyway)
- In paper? (should we have caught this before going live)

## Patterns for the future
One or two sentences the Research Agent should learn. Example:
> "Funding-rate strategies on this venue are sensitive to ETF flows. When an ETF launches for the underlying, expect funding compression within 90 days."

## Should we retry a variant?
- If yes: what would need to be different? (new venue, new regime, new sizing)
- If no: add to the "do not retry" register with reason

## Capital impact
- Starting allocation: $X
- Ending allocation: $X
- Net contribution to firm P&L: $X
