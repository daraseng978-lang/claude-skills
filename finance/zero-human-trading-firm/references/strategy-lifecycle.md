# Strategy Lifecycle

Every strategy has a single canonical state at any time. The ledger tracks transitions with timestamps and reasons.

## States

```
  proposed ──> backtested ──> red_teamed ──┬──> ready_for_paper ──> paper ──> live ──> retired
     │              │               │       └──> rejected
     └──────────────┴───────────────┘                                 ▲
                    │                                                 │
                    └─── kill switch tripped ─────────────────────────┘
```

| State | Entry condition | Exit options |
|-------|-----------------|--------------|
| `proposed` | Strategy Researcher writes a spec with hypothesis + source | `backtested` (once implemented and run) |
| `backtested` | Code exists, backtest complete with metrics in ledger | `red_teamed` OR `rejected` |
| `red_teamed` | Red Team has completed adversarial review | `ready_for_paper` OR `rejected` |
| `ready_for_paper` | Both sign-offs recorded in ledger | `paper` (capacity allowing) |
| `paper` | Strategy running in paper mode, recording fills | `live` (via execution_gate) OR `retired` (kill switch) |
| `live` | Running on real capital | `retired` (kill switch, decay, or deliberate retirement) |
| `retired` | No longer trading | terminal |
| `rejected` | Failed backtest or red team, not salvageable | terminal |

## Transition rules

- `proposed → backtested` requires a filled-in metrics block (sharpe, max_dd, trades).
- `backtested → red_teamed` requires a red-team report filed (see [red-team-playbook.md](red-team-playbook.md)).
- `red_teamed → ready_for_paper` requires BOTH:
  - `red_team_signed_off = True` in ledger flags
  - `risk_officer_signed_off = True` in ledger flags
- `paper → live` is **never automatic.** `execution_gate.py` returns ELIGIBLE, but the state change is a deliberate human action.
- Any live strategy can transition to `retired` at any time via kill switch — no sign-off required to kill something.

## Promotion gate defaults

```
min_trades:  30     (statistical floor)
min_sharpe:  1.0    (paper, per-trade)
max_dd:      0.10   (paper, absolute)
```

These are defaults for `execution_gate.py`. Tune per strategy type — high-frequency strategies need higher trade counts and lower Sharpe floors; low-frequency macro needs the opposite.

## Retirement triggers

Automatic (code-enforced via kill switch):
- Rolling 30-day live Sharpe < 0
- Drawdown > 2x backtest max
- Strategy spec's explicit kill condition met

Manual (Risk Officer or CEO decision):
- Regime shift documented in weekly review
- Correlation to another strategy exceeds 0.8 and that strategy is younger
- Fees/funding consuming >50% of gross edge

Every retirement gets a postmortem. See [`assets/postmortem_template.md`](../assets/postmortem_template.md).

## Never delete a strategy

Retired strategies stay in the ledger forever. They inform what *not* to try next quarter. The question "have we already tried this and why did it fail?" should always have a searchable answer.

## Example: a strategy's full life

```
2026-01-05  proposed        STR-0042 "Funding rate arb on hyperliquid"
            source: youtube.com/watch?v=xxx + archive.org/paper/2023.12345
            hypothesis: persistent positive funding on BTC perp
            during low-vol regimes creates a short-bias carry trade

2026-01-08  backtested      sharpe=1.8, max_dd=4.1%, trades=156 IS
                            sharpe=1.1, max_dd=6.2%, trades=62 OOS

2026-01-09  red_teamed      survived regime test (2022 bear, 2024 rally)
                            flagged: funding rate survey from retail taker-only
                            venue; wider spread on hyperliquid reduces edge 30%

2026-01-10  sign flags      red_team_signed_off=True (by red-team-agent)
                            risk_officer_signed_off=True (by risk-officer)

2026-01-10  paper           live paper trading begins, capped $1K notional

2026-02-15  execution_gate  ELIGIBLE (38 trades, sharpe=1.2, dd=5.8%)

2026-02-16  live            flipped to live, $5K notional, 30-day review

2026-05-20  retired         rolling 30-day sharpe=-0.2, dd=9.1%
                            reason: "funding rate compression post-ETF flow"
                            postmortem: postmortems/STR-0042.md
```
