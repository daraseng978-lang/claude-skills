# Risk Management Principles

The Risk Officer role is the firm's most important seat. Agents are creative; they will find ways to take more risk than you intended. Your job is to make that impossible in the tooling, not just discouraged in the prompt.

## The three layers of risk

1. **Policy** — what's allowed (JSON file, code-enforced)
2. **Sizing** — how much to allocate to a given opportunity (per-strategy logic)
3. **Monitoring** — what to do when something goes wrong (circuit breakers, kill switches)

An LLM can help with all three. An LLM should *own* none of them.

## Hard constraints (Layer 1)

These live in `scripts/risk_policy_enforcer.py`. Tune the defaults, but the *list* should rarely change:

| Constraint | Default | Why |
|------------|---------|-----|
| Max position % of equity | 10% | No single bet is existential |
| Max gross exposure | 1.5x equity | Unlevered or light levered books |
| Max net exposure | 1.0x equity | No more long than you have |
| Max leverage | 2.0x | Survives a 50% adverse move |
| Max daily drawdown | 5% | Forces a human to review before doubling down |
| Venue whitelist | explicit | Prevents an agent from routing to an untested venue |

## Sizing (Layer 2)

### Vol targeting

For each strategy, set a target portfolio-level volatility (e.g., 15% annualized). Size each position inversely proportional to its realized volatility:

```
weight_i = target_vol / realized_vol_i  (capped by policy)
```

### Fractional Kelly

For strategies with known edge, size a fraction of Kelly (commonly 0.25x to 0.5x). Full Kelly is theoretically optimal for growth but has a punishing drawdown profile that shakes out agents and humans alike.

### Correlation haircut

If two strategies are 0.8+ correlated, they're 1.1 strategies, not 2. Sum their sizes, then haircut by correlation before summing into the portfolio.

## Monitoring (Layer 3)

### Circuit breakers

- **Daily:** -5% on the portfolio flattens all positions and halts new entries until Risk Officer reviews.
- **Weekly:** -10% triggers a strategy-by-strategy review with potential retirement of laggards.
- **Strategy-level:** rolling 30-day Sharpe < 0 OR drawdown > 2x backtest max → auto-retire.

### Kill switches

Every live strategy has an explicit kill switch condition in its spec. When tripped:
1. Flatten the strategy's positions immediately
2. Mark state `retired` in the ledger with reason
3. Open a postmortem issue

Kill switches are *code*, not prompts. An agent can recommend retirement; the kill switch *is* retirement.

## Drawdown budgets

Allocate annual drawdown budget across strategies. Example for a $100K firm:
- Total drawdown budget: 15% ($15K)
- 3 strategies live, equally sized: 5% each ($5K)
- A strategy that hits its 5% personal max is auto-retired even if the firm is up overall

This prevents the "one good strategy hides three bad ones" failure mode.

## Correlation to BTC / SPX

Your firm's first correlation is to the dominant asset in its venue. If 90% of your alpha is "long BTC in disguise," you have a beta product, not an alpha product. Run the regression monthly.

## Fees, funding, and financing

For leveraged perps: funding rate > carry-adjusted edge? You're paying to be in the trade. This is a legitimate strategy kill condition.

For equities on margin: financing cost > strategy return? Close the book.

## The narrator's warning (from the interview)

> "It would just circumvent them anyway because it would just redeploy if it didn't like what the risk constraint was."

**Do not let an LLM have write access to the risk service.** If it can redeploy the policy, the policy doesn't exist. Host the policy enforcer on a box the agents cannot push to. Give them a read-only config check endpoint. Every deploy of the risk service requires a human PR review.

## Signing off

A paper→live promotion requires TWO sign-offs in the ledger:
- `red_team_signed_off`: adversarial review is complete
- `risk_officer_signed_off`: constraints verified

In a single-human firm, both can be you on different days. In a multi-agent firm, use different agent identities so the signatures are at least loosely independent.
