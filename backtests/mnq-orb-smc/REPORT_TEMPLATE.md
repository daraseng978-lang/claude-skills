# MNQ ORB — before / after report

**Instrument**: MNQ (Micro E-mini Nasdaq 100)
**Timeframe**: 5-minute
**Data range**: `YYYY-MM-DD` → `YYYY-MM-DD`
**Bars**: _____
**Source**: TradingView Strategy Tester  /  `backtest.py`  (circle one)
**Slippage modeled**: 0.5 pt/side
**Commission modeled**: $_____ / contract / side

## Configurations compared

| Setting            | Baseline | Improved |
|--------------------|----------|----------|
| ORB window         | 9:30–9:35 (5 min) | 9:30–9:45 (15 min) |
| TP1 (% ORB)        | 50       | 100      |
| TP2 (% ORB)        | 75       | 150      |
| SL (% ORB)         | 100      | 100      |
| Pyramiding         | 10       | 1        |
| Allow ORB+SMC      | yes      | no       |
| Regime filter      | off      | on (15m EMA20) |
| Daily kill-switch  | off      | on (2 losses or −2× max-loss) |
| ATR stop floor     | off      | on (0.5 × ATR14) |
| Volume filter      | on (same) | on (same) |

## Results

|                        | Baseline | Improved | Δ |
|------------------------|---------:|---------:|---:|
| Trades                 |          |          |    |
| Net P/L $              |          |          |    |
| Win rate %             |          |          |    |
| Profit factor          |          |          |    |
| Expectancy $ / trade   |          |          |    |
| Avg win $              |          |          |    |
| Avg loss $             |          |          |    |
| Max drawdown $         |          |          |    |
| Sharpe (daily)         |          |          |    |
| Largest losing streak  |          |          |    |
| Largest winning streak |          |          |    |

## Equity curves

Paste screenshots or attach `equity_baseline.csv` / `equity_improved.csv`.

## Observations

- Did the R:R fix alone flip expectancy positive?
- Did the kill-switch help or hurt net P/L?  (Less trades ≠ worse if DD drops.)
- Did the regime filter cut false-breakout days?  Check losses on gap days.
- Any day-of-week skew?  (Friday post-NFP is a common culprit.)

## Verdict

- [ ] Ship improved defaults
- [ ] Revert — baseline is better than expected
- [ ] Need more data / split sample before deciding
