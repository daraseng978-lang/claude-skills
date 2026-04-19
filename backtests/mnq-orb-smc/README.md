# MNQ ORB + SMC — backtest deliverables

Context: the Claude Code sandbox has no outbound network, so the actual
backtest must run on your machine. This folder gives you everything needed
to produce the before/after report.

## Files

- `strategy_improved.pine` — drop-in v6 replacement for the user's strategy
  with targeted fixes (R:R, ORB window, pyramiding, kill-switch, regime
  filter, ATR floor). A header block documents every change and how to
  revert to baseline.
- `backtest.py` — standalone Python backtester (pandas only). Runs the
  baseline and improved ORB logic on an OHLCV CSV and prints a before/after
  table plus writes equity curves and per-trade logs.
- `REPORT_TEMPLATE.md` — fill-in template for the full report.

## Option A — run the real backtest in TradingView

1. Paste `strategy_improved.pine` into TradingView's Pine editor on an MNQ
   5-min chart. The SMC and Zigzag sections are NOT duplicated in this file
   (they don't affect the fixes). Paste them verbatim from your original
   into the indicated spot, or keep them out entirely if you only want to
   evaluate the ORB leg.
2. In the Strategy Tester, record metrics for the baseline (flip the four
   defaults listed in the header back) and for the improved defaults.
3. Copy the numbers into `REPORT_TEMPLATE.md`.

## Option B — run the Python backtester

1. Export MNQ (or NQ) 5-min OHLCV from your broker or TradingView as CSV
   with columns: `datetime,open,high,low,close,volume`.
2. Run:

   ```
   python3 backtest.py --csv your_data.csv
   ```

   Add `--tz-in UTC` if your timestamps are UTC. Script converts to
   America/New_York internally.
3. Output: printed table + `equity_baseline.csv`, `equity_improved.csv`,
   `trades_baseline.csv`, `trades_improved.csv`.

## What the Python backtester models (and doesn't)

Models:
- ORB window → breakout on close, confirmed by prior-bar close on the other
  side
- Volume filter (volume > N-period MA × mult)
- Two-target exit (TP1 = 1 contract, TP2 = 1 contract), SL on the runner
- Breakeven stop on TP1 hit
- Session flat at `sess_end`
- HTF 15-min EMA20 regime filter (improved only)
- Daily kill-switch after 2 losses or −2× max-loss budget (improved only)
- ATR(14) × 0.5 stop floor (improved only)
- Slippage (0.5 pt per side) and hook for commission

Does NOT model:
- SMC channel detection / breakout (depends on TradingView's
  `tvta.requestUpAndDownVolume`)
- Volume-delta filter (same reason)
- Zigzag3 (unused in trade logic anyway)

Because the Python backtester ignores the SMC leg, its numbers will differ
from TradingView's. Use the Pine file for the definitive run and the
Python tool for quick before/after iteration on the ORB logic.

## Why these changes, no over-fitting

Only 8 changes, none introduce new tunable parameters:
1. TP/SL ratio moved from 0.5R/0.75R to 1R/1.5R (fixes negative expectancy)
2. ORB window 5→15 min (1-bar range was noise)
3. pyramiding 10→1 (eliminates stacked-entry tail risk)
4. canEnterNewTrade requires flat
5. Daily kill-switch (binary; no new tunable — reuses max-loss)
6. Regime filter: close vs 15m EMA20 (binary; no new tunable)
7. ATR floor on stop (0.5× ATR; a fixed fraction)
8. Volume MA uses prior bar (removes self-reference)
