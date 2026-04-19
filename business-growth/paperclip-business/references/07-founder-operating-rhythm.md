# Founder Operating Rhythm

The whole point of this business is that the founder operates in investor mode. That still requires discipline — just less of it.

## The 4-Hour Week Target

By Month 6, steady-state founder time should fit in ~4 hours/week:

| Activity | Time | Cadence |
|---|---|---|
| Review weekly dashboard | 30 min | Weekly |
| Founder-led sales calls | 1.5 hr | Weekly |
| Churn-save calls | 30 min | Weekly (as needed) |
| LinkedIn content | 45 min | Weekly |
| Quarterly strategy | 4 hr | Quarterly (~1 hr/week avg) |
| Price / ICP decisions | 15 min | Weekly |
| Admin (legal, tax, banking) | 30 min | Weekly |

Total: ~4 hours. If you're spending more, something is leaking. Diagnose before normalizing.

## Weekly Cadence

### Monday — Dashboard review

Run the generated dashboard:

```bash
python scripts/founder_dashboard.py --input state/week_NN.json --format text
```

The digest tells you:
- MRR delta vs last week (target: +$1k/wk until $40k MRR)
- New logos / churned logos
- Pipeline health (meetings booked, meetings held, close rate)
- Cash position and runway
- Escalations requiring your decision
- Red flags (CAC spike, delivery SLA miss, deliverability drop)

**Action:** make every decision on the escalation list. Write a 3-sentence rationale for each. The agents need the rationale to improve.

### Tuesday — Sales calls

Founder takes sales calls personally until $40k MRR or 20 customers, whichever comes first. Why: you learn the market, keep close rate high, and build case studies agents can't.

At $40k MRR: hire one human AE (first employee after a human editor).

### Thursday — Content + strategy

- Ship 1 LinkedIn thread or case study.
- Spend 30 minutes on strategy: Am I on-track for next MRR milestone? What needs to change?

### Friday — Close the loop

- Review escalations you approved earlier in the week. Did the agents execute correctly?
- Commit any prompt or policy updates.

## Monthly Cadence

- **P&L review** (Finance agent generates; you review): cash, revenue, costs, gross margin.
- **Channel scorecard**: CAC per channel, MER, what's scaling, what's bleeding.
- **Pricing review**: too many Starter sign-ups? Too many customers churning at renewal? Price signals.
- **Agent quality review**: sample 20 agent outputs (articles, emails, support replies) for quality drift.
- **1 customer call**: pick a top-3 customer; spend 30 min understanding their world. No agenda beyond listening.

## Quarterly Cadence

- **Board-level self-review**: Write a 1-page letter to yourself as if you're reporting to your own investor.
  - What shipped?
  - What's the real MRR growth rate trailing-90?
  - What went wrong?
  - What decision do I need to make in the next 90 days?
- **Price check**: bump new-customer pricing if close rate > 35% and churn < 4%.
- **ICP re-evaluation**: has the ideal customer shifted? Are the best customers coming from the original ICP or a drift-in adjacent one?
- **Agent prompt upgrade**: spend 2 focused hours rewriting the 3 most-used prompts. Run A/B against holdout evals.

## Annual Cadence

- **Tax prep pack to CPA** (Finance agent hands off clean exports).
- **Legal review**: MSA template, DPAs, cold-email compliance.
- **Succession/continuity plan**: if you were hit by a bus, could someone else take over in 30 days? Document the minimum.
- **Price increase** for new customers (10%).
- **Vendor audit**: cut subscriptions that aren't earning their keep.

## Decisions You Cannot Delegate

The head agent is explicitly prompted to escalate these:

1. Price changes
2. New ICPs or offering changes
3. Firing a customer
4. Hiring decisions (first human hire is usually an editor around $60k MRR)
5. Lawsuits / legal threats / complaints to regulators
6. Any contract > $10k/mo or > 6-month term
7. Media requests
8. Changes to the brand / name / domain
9. Material pricing or packaging overhaul
10. Taking on debt or raising capital

## Escalation Response Time

You need a SLA with your own business. Target:

- **Critical** (payment processor suspended, legal threat, security incident): 1 hour
- **High** (customer threatening churn > $4k MRR): 4 hours
- **Standard** (pricing decision, prompt update): 48 hours

If you can't meet Critical SLA, you need a backup: another cofounder or a trusted advisor with decision authority.

## Red Flags That Require Immediate Attention

- Two weeks of negative MRR delta.
- Delivery SLA misses on > 10% of articles in a week.
- Cold email spam complaint rate > 0.1%.
- Any customer with a written legal complaint.
- Any public social-media complaint you haven't responded to within 4 hours.
- Cash runway < 6 months.
- Agent error rate > 2% on any gate.

Each of these maps to a specific playbook. If the dashboard flags it, do not "wait and see." Act.

## The 3 Questions You Ask Every Week

1. **What's my trailing-4-week MRR growth rate, and is it accelerating or decelerating?**
2. **Am I spending more than 4 hours this week — and if so, what am I doing that the agents should be doing?**
3. **What's the one decision I've been avoiding?**

If you ask these every Monday for 52 weeks, you'll compound. If you don't, the agents will run the business fine — but it won't grow past its current loop.
