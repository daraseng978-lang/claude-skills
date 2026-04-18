# Red Team Playbook

The Red Team's job is to make sure no strategy passes to paper trading without surviving deliberate attempts to break it. This playbook is the adversarial checklist. A strategy can only be marked `red_teamed` in the ledger when every item has been addressed (passed OR documented as a known limitation).

## 14 ways to break a "profitable" backtest

### 1. Lookahead in the signal
Shift the signal by +1 bar. Does the return collapse? If yes, there's leaked future information.

### 2. Lookahead in the universe
Did the universe filter use data unknown at rebalance time? (Market cap, liquidity, fundamentals.) Recompute the universe point-in-time.

### 3. Survivorship bias
Is the test universe "things that still trade today"? Re-run on a point-in-time universe that includes delisted/defunct names at terminal value.

### 4. Regime dependence
Split the test period into regimes (bull/bear, high-vol/low-vol). Does the strategy survive each? A strategy that only makes money in one regime is a regime bet, not alpha.

### 5. Parameter sensitivity
Bump each parameter ±20%. If Sharpe halves for any single parameter, the strategy is on a knife edge. Real alpha is robust to neighbors.

### 6. Trade count
IS trades < 100? OOS trades < 30? Any metric reported on small samples is suspect. Run with a longer history or accept the uncertainty in your reporting.

### 7. Fee/slippage sensitivity
Halve and double the fee/slippage assumptions. The strategy should still work at 2x the assumed cost. If it doesn't, you're depending on an optimistic cost model.

### 8. Execution feasibility
Is the required notional more than 10% of top-of-book depth at each entry? You can't actually fill that trade. Rerun with realistic position sizing.

### 9. Correlation to the dominant asset
Regress strategy returns against BTC (crypto) or SPX (equities). If R² > 0.6, the strategy is mostly beta. Subtract the beta component and recheck the residual Sharpe.

### 10. In-sample overfit via parameter search
How many parameter combinations were tried? If the author searched a 100-cell grid and picked the best, true out-of-sample performance is much worse than reported. Ask for the full grid results, not the winner.

### 11. Data-mining bias across strategies
Firm-level: if you tested 50 strategies and 1 looks great, the expected alpha of that one is the alpha × (1/50). Correct for multiple testing.

### 12. Outlier dependence
Remove the best 5% and worst 5% of trades. Is there still alpha? A strategy whose edge lives in 3 trades out of 200 is a lottery ticket.

### 13. Period dependence
Break the backtest into quartiles by time. Does each quartile have positive return? Or is 90% of the PnL in one quarter?

### 14. Cross-venue arbitrage that doesn't exist
Many "stat arb" strategies assume perfect venue-to-venue execution. Check: would this actually work with your real latency, your real borrow rates, your real withdrawal times?

## Red team report format

Every `red_teamed` transition requires a report at `postmortems/redteam/STR-NNNN.md`:

```markdown
# Red Team Review: STR-NNNN

## Checklist
- [ ] Lookahead: passed / failed / mitigated
- [ ] Universe: point-in-time verified
- [ ] Survivorship: dataset includes delisted
- [ ] Regime: tested across [list regimes]
- [ ] Parameter sensitivity: ±20% robustness
- [ ] Trade count: IS=N, OOS=N
- [ ] Fee/slippage: 2x stress test
- [ ] Execution: depth-aware sizing
- [ ] Beta: R² vs BTC/SPX = X.XX
- [ ] Parameter grid: K combinations tried
- [ ] Multi-test: correction applied
- [ ] Outlier dependence: trimmed 5% each tail, sharpe = X.XX
- [ ] Period stability: Q1-Q4 returns = X, Y, Z, W
- [ ] Cross-venue: latency/borrow/withdrawal verified

## Known limitations
[anything that did not pass but is acceptable]

## Verdict
PASS / FAIL / CONDITIONAL

## Conditions (if conditional)
[e.g., "approve for paper only; cap notional at $1K until regime Y is tested"]
```

## Cultural note

The Red Team is not the enemy of the Research team. Both want the firm to make money. The Red Team's job is to stop the firm from being confidently wrong. A rejected strategy today saves the firm 20 × its backtest drawdown tomorrow.

Your Red Team agent's instructions should include: "Your job is to find reasons to reject. Be mean. The Research team can defend its work; you should not hedge."
