---
name: "paperclip-business"
description: Blueprint for a Claude-agent-operated productized service company that generates consistent monthly recurring revenue (MRR) with minimal founder involvement. Use when designing an automated revenue business, choosing a productized service model, modeling SaaS/service unit economics, forecasting MRR growth, wiring Claude agents into sales/delivery/support, or setting up a founder-as-investor operating rhythm. Applies the "paperclip principle": one metric (MRR), one loop, relentlessly optimized.
---

# Paperclip Business

A production-ready blueprint for an **agent-operated productized service** that delivers consistent MRR while the founder operates in an investor/oversight role. Named after the paperclip-maximizer thought experiment: pick one metric (MRR), build one loop, let the agents run it.

> **Output formats:** All scripts support `--format text` (human) and `--format json` (dashboards). Standard library only, no external dependencies.

---

## The Paperclip Principle

A real business does **one** thing for **one** customer profile at **one** price point, and optimizes a **single** metric. This skill deliberately resists "multi-product" temptations — agents are ruthless optimizers, but only when the objective is scalar.

- **Objective:** Net New MRR per week
- **Constraint:** Gross margin ≥ 70%, churn ≤ 5%/mo
- **Actor:** Claude agents (head agent + 4 sub-agents)
- **Founder role:** Capital, legal, strategic veto — not operations

Read [references/08-paperclip-principle.md](references/08-paperclip-principle.md) before anything else.

---

## Recommended Business (Default Pick)

**AI SEO Content Subscription** — productized content service targeting Series A–B B2B SaaS companies.

| Dimension | Value |
|---|---|
| Offer | 20 SEO-optimized articles/month, published to their CMS |
| Price | $2,000 / $4,000 / $8,000 per month (3 tiers) |
| Target CAC | ≤ $1,200 (payback ≤ 1.5 months on middle tier) |
| Gross margin | 80%+ (Claude + Brave Search + WordPress API) |
| Churn target | ≤ 4%/month |
| Break-even | ~15 customers at middle tier |
| Path to $50k MRR | ~17 middle-tier customers |

Why this one: clear buyer, recurring pain, measurable outcome, 90%+ of delivery is text generation + research + publishing — exactly what Claude does well. Full playbook in [references/02-productized-service-playbook.md](references/02-productized-service-playbook.md).

Not convinced? Run the selector on your constraints:

```bash
python scripts/business_model_selector.py --input assets/sample_business_inputs.json --format text
```

Five alternates are scored: SEO content, competitor intelligence reports, code review subscription, lead enrichment service, newsletter-as-a-service. See [references/01-business-model-selection.md](references/01-business-model-selection.md).

---

## Quick Start

```bash
# 1. Pick a business (or confirm the default)
python scripts/business_model_selector.py --input assets/sample_business_inputs.json --format text

# 2. Model unit economics for your target business
python scripts/unit_economics_modeler.py --input assets/sample_unit_economics.json --format text

# 3. Forecast MRR to $10k, $50k, $100k milestones
python scripts/mrr_forecaster.py --input assets/sample_mrr_inputs.json --format text

# 4. Generate the weekly founder/investor dashboard
python scripts/founder_dashboard.py --input assets/sample_weekly_state.json --format text
```

---

## Architecture: Who Does What

The business runs as a 5-agent constellation. The founder never touches Tier 1–3 work.

```
              ┌────────────────────────────────────────────┐
              │  FOUNDER / INVESTOR  (you)                 │
              │  - Capital, legal, strategic veto          │
              │  - Reviews weekly founder_dashboard.py     │
              │  - Approves price changes & new ICPs       │
              └──────────────────┬─────────────────────────┘
                                 │ weekly digest
              ┌──────────────────▼─────────────────────────┐
              │  HEAD AGENT  ("Paperclip")                 │
              │  - Owns MRR number                         │
              │  - Orchestrates sub-agents                 │
              │  - Escalates only when policy triggers     │
              └─┬───────────┬────────────┬──────────┬──────┘
                │           │            │          │
        ┌───────▼──┐  ┌─────▼─────┐ ┌────▼────┐ ┌───▼──────┐
        │ ACQUIRE  │  │  DELIVER  │ │ RETAIN  │ │ FINANCE  │
        │ (growth) │  │ (content) │ │ (CS)    │ │ (ops)    │
        └──────────┘  └───────────┘ └─────────┘ └──────────┘
```

- **Head agent** — system prompt in [assets/agent_system_prompt.md](assets/agent_system_prompt.md)
- **Acquire** — outbound email + SEO + partner referrals (see `references/03-claude-agent-architecture.md`)
- **Deliver** — the productized work itself (SOP in [assets/sop_content_delivery.md](assets/sop_content_delivery.md))
- **Retain** — health scoring, QBRs, churn saves
- **Finance** — invoicing, reconciliation, tax prep hand-off to human CPA

Full wiring in [references/03-claude-agent-architecture.md](references/03-claude-agent-architecture.md).

---

## Reference Library

| # | File | Purpose |
|---|---|---|
| 01 | [business-model-selection.md](references/01-business-model-selection.md) | 5 candidate businesses scored against automation-friendliness |
| 02 | [productized-service-playbook.md](references/02-productized-service-playbook.md) | End-to-end playbook for the default pick |
| 03 | [claude-agent-architecture.md](references/03-claude-agent-architecture.md) | Sub-agent design, escalation rules, failure modes |
| 04 | [pricing-and-packaging.md](references/04-pricing-and-packaging.md) | 3-tier design, annual discounts, overage logic |
| 05 | [acquisition-channels.md](references/05-acquisition-channels.md) | SEO, cold email, partnerships, ranked by CAC |
| 06 | [operations-and-delivery.md](references/06-operations-and-delivery.md) | SOPs, QA gates, escalation thresholds |
| 07 | [founder-operating-rhythm.md](references/07-founder-operating-rhythm.md) | Weekly / monthly / quarterly cadence |
| 08 | [paperclip-principle.md](references/08-paperclip-principle.md) | Single-metric optimization philosophy |

---

## Scripts

### 1. `business_model_selector.py`
Scores 5 candidate businesses against your constraints (capital, monthly time budget, technical comfort, geography, risk tolerance). Returns ranked list with rationale.

### 2. `unit_economics_modeler.py`
Models CAC, LTV, gross margin, payback, and break-even customer count for a given offer + pricing + cost stack.

### 3. `mrr_forecaster.py`
Cohort-based MRR projection. Inputs: starting MRR, gross adds/month, logo churn, expansion. Outputs path to $10k / $50k / $100k MRR with confidence bands.

### 4. `founder_dashboard.py`
Generates the weekly founder digest: MRR delta, pipeline, churn events, red flags, decisions requiring human input. This is the **only** report the founder reads.

---

## Asset Templates

- [agent_system_prompt.md](assets/agent_system_prompt.md) — Head agent system prompt (drop into Claude Code / Agent SDK)
- [sop_content_delivery.md](assets/sop_content_delivery.md) — Standard operating procedure for delivery
- [founder_weekly_template.md](assets/founder_weekly_template.md) — Investor-style weekly update format
- [sample_business_inputs.json](assets/sample_business_inputs.json) — Example input for selector
- [sample_unit_economics.json](assets/sample_unit_economics.json) — Example input for economics modeler
- [sample_mrr_inputs.json](assets/sample_mrr_inputs.json) — Example input for forecaster
- [sample_weekly_state.json](assets/sample_weekly_state.json) — Example weekly business state

---

## First 90 Days (Founder Checklist)

1. **Week 0** — LLC/Ltd, business bank, Stripe, domain, transactional email (Postmark), shared Google Drive. ~$500 total.
2. **Week 1** — Deploy head agent with system prompt from `assets/`. Seed CRM (Airtable or HubSpot free). Wire Stripe webhooks.
3. **Week 2–3** — Founder makes **first 10 sales manually** (do not delegate). Capture every objection — this becomes training data for the Acquire agent.
4. **Week 4–6** — Hand Acquire + Deliver to agents. Founder only reviews the weekly dashboard. Target: 5 customers, ~$10k MRR.
5. **Week 7–12** — Optimize loop. Kill channels with CAC > LTV/3. Target exit: $25k–$40k MRR with ≤ 4hr/week founder time.

Detail in [references/07-founder-operating-rhythm.md](references/07-founder-operating-rhythm.md).

---

## What This Skill Is NOT

- **Not** a "passive income" fantasy — the first 60 days require real founder work.
- **Not** a recommendation to skip legal/tax advisors. Use a human CPA and lawyer for incorporation, contracts, and tax.
- **Not** a replacement for customer judgment. Agents deliver; the founder sets policy.
- **Not** a moat by itself. The moat is brand, relationships, and compounding SEO — things agents accelerate but don't invent.

---

## Related Skills

- `business-growth/revenue-operations/` — Pipeline health, MRR forecast accuracy
- `business-growth/customer-success-manager/` — Churn scoring, expansion
- `marketing-skill/` — Content production (used by Deliver agent)
- `finance/` — Financial modeling, DCF, SaaS metrics
- `engineering/agent-designer/` — Deeper agent architecture patterns
- `c-level-advisor/` — Strategic decisions the founder cannot delegate

---

**License:** Apache-2.0. Use freely; commercial use encouraged.
