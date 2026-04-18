---
name: "zero-human-trading-firm"
description: Build an autonomous multi-agent trading firm that researches ideas, backtests strategies, enforces risk limits, promotes paper-traded strategies to live, and logs every trade for accounting. Use when setting up an AI-run quant team, orchestrating research/backtest/risk/execution agents, mapping trading roles to existing skills in this library, or enforcing hard-coded risk constraints that an LLM cannot circumvent. Mentions zero-human firm, AI trading firm, autonomous trading, quant agent team, Paperclip org pattern, trading agent orchestration, paper-to-live promotion.
---

# Zero-Human Trading Firm

An opinionated blueprint for running an autonomous trading firm staffed entirely by AI agents — with a human board guiding taste, values, and hard risk limits.

This skill is **not** a trading strategy. It is the **org design, lifecycle, guardrails, and tooling** that turn a pile of Claude/Codex/OpenClaw agents into a coordinated quant team that can run 24/7 without you babysitting every decision.

## Core Philosophy

Four non-negotiable principles:

1. **Start small, grow by need.** Six roles max on day one. Split roles only when one agent clearly cannot do the job well. Thirty agents on day one produces slop and burns tokens.
2. **LLMs cannot own hard risk limits.** Any constraint you cannot afford to violate must live in deterministic code the agents cannot redeploy. Agents propose; code disposes.
3. **Taste is the product.** Agents can generate infinite strategies. Only your judgment shapes which ones are good. Write your taste down — in instructions, skill references, and reviewer rubrics — or watch the firm drift.
4. **Paper before live, always.** No strategy touches real capital until it passes paper-trading gates: min trades, positive Sharpe floor, max drawdown cap, and a red-team sign-off.

## Org Chart (v1 — six roles)

```
            You (Board)
                │
             CEO (strategy + hiring)
                │
    ┌───────────┼───────────────────────────┐
    │           │                           │
  CTO       Risk Officer               Accounting
    │           │                           │
 ┌──┴──┐     enforces hard              audit log,
 │     │     constraints,               P&L, tax
Research Engineer                       exports
 │     │
 │   Backtest Engineer ── Red Team (adversarial)
 │                          │
 │                    Execution Engineer ── (paper → live gate)
 │
Strategy Researcher
```

**Six starting roles:**

| Role | Primary Job | Maps To (existing skill / agent) |
|------|-------------|----------------------------------|
| **CEO** | Hire, fire, set priorities, read daily reports | `agents/c-level/cs-ceo-advisor.md` |
| **CTO / Research Engineer** | Pick backtest library, data sources, infra | `agents/c-level/cs-cto-advisor.md` + `engineering-team/senior-data-engineer/` |
| **Strategy Researcher** | Read archive, YouTube transcripts, forums; propose ideas | `engineering/autoresearch-agent/` + `engineering-team/senior-data-scientist/` |
| **Backtest Engineer** | Implement & validate strategies; enforce hygiene | `engineering-team/senior-data-scientist/` + `engineering-team/tdd-guide/` |
| **Red Team** | Break every strategy before risk signs off | `engineering-team/red-team/` + `engineering-team/adversarial-reviewer/` |
| **Risk Officer** | Own hard constraints; approve paper→live promotions | `finance/financial-analyst/` + `engineering-team/incident-commander/` |
| **Execution Engineer** | Order routing, slippage tracking, fail-safes | `engineering/ci-cd-pipeline-builder/` pattern (deploy discipline) |
| **Accountant** | Daily P&L, tax lots, exportable ledger | `finance/financial-analyst/` + `finance/saas-metrics-coach/` pattern |

The CEO, Risk Officer, and Accountant are **must-haves** from day one. Everything else you can merge into a single Research Engineer seat until the bottleneck makes you split.

## 5-Phase Workflow

### Phase 1: Firm Setup (Day 1)
- Pick venue (equities, crypto DEX, perp, Bittensor subnet — commit to one)
- Write **instructions for each role** (taste, style, what "good" looks like)
- Configure **hard constraints** in `scripts/risk_policy_enforcer.py` (max position %, max portfolio beta, max daily drawdown, circuit breaker)
- Pick data source and backtest library (off-the-shelf before writing your own)
- Create the **Strategy Ledger** (`scripts/strategy_ledger.py`) — every idea gets an ID and a lifecycle state

### Phase 2: Idea Generation (nightly)
- Research Agent runs on a cron, pulls from 20+ sources (transcripts, archive papers, trading view, GitHub quant repos, news)
- Output: a dated markdown report with candidate ideas, each tagged with effort, expected edge, and data requirements
- Ideas land in ledger state `proposed`

### Phase 3: Backtest + Red Team
- Backtest Engineer picks up `proposed` ideas in priority order
- Runs backtest with strict hygiene (no lookahead, out-of-sample split, walk-forward validation, fee + slippage model)
- Red Team attempts to break the result: survivorship bias? regime dependence? overfit to in-sample? dataset artifact?
- States: `proposed` → `backtested` → `red_teamed` → `rejected` OR `ready_for_paper`

### Phase 4: Paper → Live Promotion Gate
- All strategies marked `ready_for_paper` start paper trading
- **Promotion gate is code, not a prompt.** `scripts/execution_gate.py` enforces:
  - N ≥ minimum paper trades (default 30)
  - Paper Sharpe ≥ floor (default 1.0)
  - Paper max drawdown ≤ cap (default 10%)
  - Red Team signed off (ledger flag)
  - Risk Officer approval (ledger flag, requires human or dual-agent signature)
- Pass → `live` with capped size. Fail → back to Backtest.

### Phase 5: Live Monitoring + Retirement
- Every live strategy has a **kill switch**: rolling 30-day Sharpe < 0, or drawdown > 2× backtest max
- Accountant logs every fill, fee, and daily P&L to an immutable append-only journal
- Weekly postmortem on any retired strategy (what changed? regime shift? alpha decay?)
- Retired strategies stay in the ledger — they inform what *not* to try next quarter

## Python Tools

All tools are standard-library only. No external dependencies. No LLM calls.

### 1. Strategy Ledger (`scripts/strategy_ledger.py`)

Append-only JSON ledger that tracks every strategy through its lifecycle.

```bash
# Propose a new idea
python scripts/strategy_ledger.py propose --name "SMA 20/50 cross on BTC-PERP" \
    --hypothesis "Momentum filter on crypto perps in trending regimes" \
    --source "https://youtube.com/watch?v=xxx"

# Move a strategy forward
python scripts/strategy_ledger.py advance --id STR-0001 --state backtested \
    --metrics '{"sharpe": 1.4, "max_dd": 0.08, "trades": 142}'

# Retire a strategy
python scripts/strategy_ledger.py retire --id STR-0001 --reason "alpha decay"

# Query
python scripts/strategy_ledger.py list --state ready_for_paper
python scripts/strategy_ledger.py show --id STR-0001
```

### 2. Backtest Runner (`scripts/backtest_runner.py`)

Minimal but hygienic backtester for vetting new ideas fast. Supports SMA cross, EMA cross, and mean-reversion templates. Enforces:
- Strict causal indicators (no future data)
- Configurable fee + slippage
- Out-of-sample split (default 70/30)
- Walk-forward window option

```bash
python scripts/backtest_runner.py --csv prices.csv --strategy sma_cross \
    --fast 20 --slow 50 --fee-bps 10 --slippage-bps 5
```

### 3. Risk Policy Enforcer (`scripts/risk_policy_enforcer.py`)

**This is the tool your agents cannot circumvent.** Intended to run as an always-on service or pre-trade hook. Rejects orders that violate:
- Per-position max % of equity
- Per-asset exposure cap
- Portfolio gross/net exposure ceilings
- Daily drawdown circuit breaker
- Max leverage

```bash
# Validate a proposed order against the policy
python scripts/risk_policy_enforcer.py check --order order.json --policy risk_policy.json
```

Deploy this behind an API the agents *call* but cannot *redeploy*. If an agent can push new risk policy code, you have no risk policy.

### 4. Research Synthesizer (`scripts/research_synthesizer.py`)

Aggregate plaintext/markdown from transcripts, notes, and source dumps into a ranked idea list. Uses deterministic keyword + co-occurrence scoring — no LLM calls.

```bash
python scripts/research_synthesizer.py --input-dir research/ \
    --keywords "momentum,mean reversion,carry" --top 20
```

### 5. Execution Gate (`scripts/execution_gate.py`)

The paper → live promotion gate. Reads strategy metrics from the ledger, applies all thresholds, returns pass/fail + reason.

```bash
python scripts/execution_gate.py promote --id STR-0001
```

### 6. Firm Scaffolder (`scripts/firm_init.py`)

Scaffolds a new firm workspace: role instruction stubs, ledger file, risk policy, issue templates, and a `FIRM.md` with your chosen venue and constraints.

```bash
python scripts/firm_init.py --name "Lewis Ventures" --venue "bittensor" \
    --out ./my-firm
```

## Reference Library

- [`references/backtesting-hygiene.md`](references/backtesting-hygiene.md) — lookahead, survivorship, overfit, walk-forward, fee/slip realism
- [`references/risk-management-principles.md`](references/risk-management-principles.md) — Kelly, vol targeting, correlation, drawdown budgets
- [`references/strategy-lifecycle.md`](references/strategy-lifecycle.md) — states, gates, kill switches, retirement criteria
- [`references/hard-constraints-pattern.md`](references/hard-constraints-pattern.md) — why LLMs can't own risk limits, service-boundary design
- [`references/red-team-playbook.md`](references/red-team-playbook.md) — 14 ways to break a "profitable" backtest

## Asset Templates

- [`assets/strategy_spec.md`](assets/strategy_spec.md) — one-pager template each idea must fill
- [`assets/risk_policy.json`](assets/risk_policy.json) — starting policy with sensible defaults
- [`assets/daily_research_report.md`](assets/daily_research_report.md) — overnight research output format
- [`assets/postmortem_template.md`](assets/postmortem_template.md) — retired-strategy writeup
- [`assets/org_chart.json`](assets/org_chart.json) — importable org structure (Paperclip-compatible)

## Anti-Patterns (hard-won from the video interview)

1. **Blasting 30 agents on day one.** You'll spend the next week writing "optimizer" and "dedup" agents to patch the holes. Start with six.
2. **Letting an agent own its own risk policy.** The narrator's OpenClaw bot literally redeployed the risk service to circumvent it. Isolate constraints behind an API the agent cannot push to.
3. **No institutional taste.** Agents don't know your style. If your feedback is "cuts are too long, should be 2 sec not 6" — write that down *once*, in the role's instructions, so you don't repeat it weekly.
4. **Skipping the ledger.** If you can't answer "which strategies have we already rejected and why?" you'll retry them every month.
5. **No human in the promotion loop.** Paper→live is where bad strategies eat capital. The gate is code, but the *flip* to live requires a human (or dual-agent) signature on day one.
6. **Forgetting the accountant.** Every fill logged, every fee logged, every tax lot closed. Not optional.

## Related Skills

- `engineering/autoresearch-agent/` — drop-in for the Strategy Researcher role
- `engineering-team/senior-data-scientist/` — backtest hygiene, statistical tests
- `engineering-team/red-team/` — adversarial review of strategies
- `engineering-team/adversarial-reviewer/` — hostile-persona code review of strategy implementations
- `engineering-team/incident-commander/` — playbook when a live strategy goes wrong
- `finance/financial-analyst/` — P&L and valuation math for the Accountant
- `engineering/self-eval/` — honest scoring of agent outputs (catch score inflation)

## Credits

Inspired by the "zero-human trading firm" interview pattern (Paperclip-style agent orchestration). This skill is framework-agnostic — the org chart, lifecycle, and tools work with Claude Code, Codex, OpenClaw, Hermes, Gemini CLI, or any harness.
