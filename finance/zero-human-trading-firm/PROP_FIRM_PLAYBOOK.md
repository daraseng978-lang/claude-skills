# Prop Firm Playbook

**Purpose:** leverage prop-firm capital to scale the zero-human trading firm without putting more personal capital at risk. Buy evaluations only after IB live has proven the strategies — not before.

This playbook is a sequencing + configuration guide. It does NOT replace the FOUNDER_QUICKSTART or the CEO_BOOTSTRAP. Run the firm on IB first. Come back here in month 6-7.

---

## When you're ready for this

All of the following must be true:

- [ ] Firm has been running paper for 90+ days with no risk-policy breaches.
- [ ] At least one strategy has cleared `execution_gate.py --founder-mode` with Sharpe ≥ 1.0 and both sign-offs from distinct agent identities.
- [ ] You have 30+ **live** trades on IB (not paper) with a positive expectancy.
- [ ] Broker reconciliation via `founder_report.py --broker-statement` has returned clean for 30+ consecutive days.
- [ ] You understand why your strategies work (not just that they do).

If any box is unchecked, close this file. Prop firm evaluations are capital that evaporates when strategies don't have edge.

---

## The unit economics

| Capital source | Personal risk | Deployed capital | Your share of PnL |
|----------------|---------------|------------------|--------------------|
| Personal IB ($25k) | $25,000 | $25,000 | 100% |
| One $100k prop eval | ~$500 | $100,000 | 80-90% |
| Three stacked $100k evals | ~$1,500 | $300,000 | 80-90% |

A strategy producing 10% net annual on $300k of prop capital with an 80% split pays ~$24,000/yr. Your personal capital at risk is the eval fees, capped at a few thousand dollars. **This is the correct way to leverage AI edge.**

---

## Firm selection — algo-friendly tier only

Most retail prop firms prohibit fully autonomous trading or require "human decision present." Those are not viable for this setup. Verify rules on the firm's website in the 7 days before you buy any evaluation — policies change without notice.

| Firm | Asset class | Algo policy (as of 2026) | Max scalable capital | Payout split |
|------|-------------|--------------------------|----------------------|--------------|
| **Apex Trader Funding** | Futures | EAs + auto-trading allowed; multi-account stacking | $300k+ via 20-account stack | 90% initial / 100% after threshold |
| **MyFundedFutures** | Futures | Fully autonomous OK | $150k per account | 90/10 |
| **Topstep** | Futures | EAs allowed, no copy-trading | $150k combined | 90/10 |
| **TickTickTrader** | Futures | Full auto, one-step eval | $150k | 80/20 → 90/10 |
| **SurgeTrader** | Forex / indices | Full autonomy, one-step eval | $250k | 75/25 → 90/10 |
| **E8 Markets** | Forex / indices | EAs allowed, copy-trading OK | $200k | 80/20 |

**Explicitly avoid for autonomous trading:** FTMO, FundedNext, The Funded Trader, most "challenge-style" forex firms — all require manual trader discretion.

**Recommended starting point:** Apex or MyFundedFutures. Both are algo-native, futures-only (cleaner than forex for systematic strategies), and stackable. Futures contract sizes also map cleanly onto the existing `per_asset_caps` logic.

---

## Rule compatibility with your existing risk policy

Before buying an evaluation, confirm your `risk_policy.json` is tighter than the firm's rules on every axis. Hugging the line = random termination.

| Constraint | Your policy default | Typical prop firm | Action |
|------------|---------------------|-------------------|--------|
| Max daily drawdown | 3% | 3-5% | Tighten to **2.5%** — leaves buffer |
| Max total drawdown | 10% monthly | 5-10% of initial balance | Tighten to **7%** for funded accounts |
| Position size | 5% of equity | No hard cap, but consistency rules apply | Add per-firm `max_position_pct` override |
| Overnight holding | allowed | banned at some firms | Add per-venue flag |
| News trading window | allowed | often restricted 2 min around major prints | Add per-venue news-block |
| Consistency rule | none | no single day > 40-50% of profit | Add `max_single_day_profit_pct` enforcement |

**If a strategy only works at looser limits than the firm permits, do not fund it with prop capital.** The tighter constraints are not negotiable — they are terms of service, and a breach zeroes the account.

---

## Config changes to ship before your first evaluation

These land in one PR, roughly two hours of work.

### 1. Extend `risk_policy.json` with per-venue overrides

```json
"venue_overrides": {
  "apex-futures-50k": {
    "max_daily_drawdown": 0.025,
    "max_total_drawdown_from_start": 0.05,
    "overnight_holding": false,
    "news_block_windows": ["FOMC", "NFP", "CPI"],
    "max_single_day_profit_pct": 0.40
  },
  "apex-futures-100k": { ... },
  "myff-futures-50k": { ... }
}
```

The risk enforcer picks the override based on `order.venue`. A strategy running on multiple venues gets checked against each venue's rules independently.

### 2. Per-account separate ledgers

Each prop account gets its own `capital_ledger_<venue>_<account_id>.json` with `require_signed_actions: true` from day one. This isolates blow-ups — one prop account dying does not contaminate the others' accounting.

The eval fee itself is a signed `fund` action for that ledger. Keep the audit trail intact from the first dollar.

### 3. Reconciliation per account

`founder_report.py --broker-statement` already accepts a single broker statement. Extend to accept `--broker-statement path1.json --broker-statement path2.json ...` — one per funded account — and run reconciliation independently. Any drift on any account suppresses the decision section.

### 4. Consistency-rule pre-check

Most futures firms enforce a rule like "no single day's profit may exceed 40% of total period profit." Add a pre-order hook:

```
current_day_profit / cumulative_period_profit > 0.35  →  reject order
```

The threshold is firm-specific. Pull it from `venue_overrides.<venue>.max_single_day_profit_pct`.

### 5. Payout tracking

Futures prop firms pay monthly, minus reserves. Add a `prop_payout_events` section to the per-account ledger, and have the Sunday CEO note summarize: "Apex-50k eligible for payout on 2026-05-01, estimated $1,240 after 10% reserve."

---

## The evaluation-stacking schedule

Don't buy 10 evals in one day. You'll lose them all to the same bug.

| Week | Action |
|------|--------|
| Week 1 | Buy **one** Apex $50k eval. Run the firm against it with tightened config. |
| Week 2-4 | Pass the eval. Strategies adapt to the tighter DD. If you fail, you learn where. |
| Week 5 | First funded account live. Wait for first payout cycle. |
| Week 9 | Buy a **second** Apex eval ($50k or $100k). Run in parallel. |
| Week 13 | If both accounts are profitable AND payouts have cleared, buy a MyFundedFutures $50k. Diversifies firm risk. |
| Month 4+ | Stack at a pace matched by funded-account payout velocity. Never let eval fees exceed one month of payouts. |

**Stacking rules:**
- New eval only funded when previous account has cleared one payout cycle.
- Eval fees come from prop profits, not personal capital.
- If total deployed prop capital exceeds $500k, add a second prop firm for diversification even if the first is scaling-plan-eligible.

---

## Failure modes to plan for

**Evaluation fails in week 1.** Expected ~50% of the time on your first eval. The strategies weren't compatible with the consistency or DD rules. Tighten, re-evaluate, don't rage-buy a second eval in the same week.

**Account terminated mid-funded.** Prop firms kill accounts for rule breaches automatically. Write a CEO playbook for "account zero'd" — retire the linked strategies from that venue, run a post-mortem using `assets/postmortem_template.md`, do NOT re-fund the same strategy on the same venue without a config change.

**Firm changes rules.** Happens every 60-90 days in this industry. Subscribe to the firm's changelog or Discord. Run a monthly rule-review task in the CEO's weekly schedule.

**Firm goes under.** Several prop firms have collapsed — MyForexFunds, True Forex Funds, others. Diversify across at least 2 firms once deployed prop capital exceeds $100k. **Do not treat funded balances as capital you own** — they are a contractual claim that can evaporate.

**Payout disputed / delayed.** Reputable firms pay on schedule; sketchy ones stall. If a payout is more than 14 days late, stop funding new evals with that firm and withdraw everything that's withdrawable.

---

## The honest EV comparison

Assume year 1 median firm performance: **+5% net annual** (optimistic for an unproven system).

| Setup | Personal risk | Deployed capital | Year 1 median PnL (after split) | ROI on personal risk |
|-------|---------------|------------------|----------------------------------|----------------------|
| Personal IB only ($25k) | $25,000 | $25,000 | +$1,250 | +5% |
| One prop eval ($100k, 80/20) | $500 | $100,000 | +$4,000 | +800% |
| Three stacked evals ($300k) | $1,500 | $300,000 | +$12,000 | +800% |
| Hybrid: $10k IB + 3 evals | $11,500 | $310,000 | +$12,400 | +108% |

**But** — the probability of passing 3 evals without proven live performance is ~1-2%. The realistic path is the hybrid sequence above, where each eval is bought only after the prior funded account has cleared payouts.

---

## When to retire this playbook

- You've lost 3 consecutive evaluations in 90 days → system does not have an edge compatible with prop firm rules. Shelve the playbook. Continue on IB.
- Deployed prop capital exceeds $500k and firm kill switch is trending tighter every month → you have a scaling problem. Stop buying evals, consolidate to the best-performing account, re-evaluate.
- You're spending more than 2 hours/week managing prop-firm compliance → you've re-humanized the firm. Simplify back to one or two accounts.

---

## Related files

- `FOUNDER_QUICKSTART.md` — IB setup. Prerequisite for this playbook.
- `CEO_BOOTSTRAP.md` — agent handoff. Add prop-firm venue entries once active.
- `assets/risk_policy.json` — where `venue_overrides` lives.
- `scripts/capital_allocator.py` — already supports per-venue ledgers; just instantiate one per prop account.
- `scripts/founder_report.py` — extend `--broker-statement` to accept repeated flags (one per funded account).

---

**Bottom line.** Prop firm leverage is the right way to scale an AI-driven systematic firm once strategies are proven. It is the wrong way to *validate* them. Earn the right to buy evaluations by surviving 6 months of real IB live trading first. Everything in this file assumes that prerequisite.
