# The Paperclip Principle

Nick Bostrom's thought experiment imagined an AI that relentlessly converts matter into paperclips because that's the single metric it was given. The warning there is about misaligned objectives at civilizational scale.

Borrowed for a business: **agents are ruthless optimizers, and that's useful only when the metric is right, scalar, and bounded.**

## The Metric

**Weekly Net New MRR.**

- **Weekly**, not monthly. Monthly hides sub-trends.
- **Net new**, so churn shows up in the number.
- **MRR**, because it's the one number that matters for a subscription business.

Everything else — pipeline, close rate, CAC, NPS — is a diagnostic for why the number moved, not the number itself.

## The Loop

One closed loop. Ugly, repetitive, compounding:

```
Acquire → Deliver → Retain → (Expand) → Acquire
```

Each iteration improves:
- Acquire learns which messages close
- Deliver learns which articles retain
- Retain learns which customers expand
- The founder shifts capital toward whichever arm is the current bottleneck

## Why Not Multi-Product?

The moment there are two offerings:
- The agent has to balance priorities (it can, but it optimizes worse).
- The founder must approve two pricing pages, two ICPs, two prompt sets.
- Attribution gets noisy. You can't tell if the Acquire agent improved or got lucky.

Rule: **Only add a second product when the first product's MRR growth rate has plateaued for 90 days despite effort.** If you're still growing, you're not done with the first loop.

## Why Not Optimize Multiple Metrics?

"I want MRR, NPS, gross margin, and team happiness all up."

Sure, but when they conflict — and they always conflict — you need a single tiebreaker. Without it, the agent defaults to whichever is easiest to move, not whichever matters most.

- **MRR** is the primary metric.
- **Gross margin ≥ 70%** and **churn ≤ 5%/mo** are constraints, not objectives.

The head agent is instructed: *maximize MRR subject to those constraints, escalate anything that would violate them.*

## Why Not Vanity Metrics?

Followers, press mentions, website visits — all downstream. If MRR grows, these follow. If MRR stalls, these don't matter.

The dashboard the founder reads every Monday shows MRR first. Everything else is sized proportionally to how much it explains MRR.

## The Risk of Paperclips

The real paperclip-maximizer risk in a business: **optimizing MRR short-term in ways that destroy the business long-term.**

- Discounting to hit a weekly number → unwinds the pricing anchor.
- Over-promising in sales → blows up delivery, spikes churn 60 days later.
- Farming low-intent customers → tanks gross margin.

That's why the constraints exist. The head agent is explicitly prohibited from:

- Discounting below floor price
- Over-committing delivery beyond tier
- Accepting customers outside ICP
- Taking customer work in forbidden categories (regulated medical, legal, etc.)

## Bounded Autonomy

Give the agent real authority **within the box**:

- It can send cold email, close deals, negotiate within pricing rules, refund small amounts, pause bad channels, restart good ones, publish drafts, respond to support, run weekly reports.

Lock it out of **everything that changes the box**:

- Pricing floors/ceilings
- New ICPs
- Legal agreements
- Major expenses
- Public brand communications
- Cap table changes

The founder is the box. The agent is the optimizer inside it.

## The Single Question

At any point in the week, the founder should be able to answer:

> "Is MRR growing? If not, what's the one thing I need to change about the box?"

If the answer to both is "yes" and "nothing," stay out of the agent's way.

If the answer is "no" and "I'm not sure," the job this week is diagnosis — not execution. Go read the dashboard and trace the number to a root cause. Then adjust the box.

## When to Abandon the Principle

Paperclip-maximizer discipline is a tool, not religion. Break it when:

1. The market structurally shifts (e.g., Google launches direct-to-publisher AI, crushing the SEO business). Single-metric optimization in a dying market is just a faster way to die.
2. A larger opportunity emerges that the current loop can't absorb. Then you need a deliberate second loop, staffed intentionally.
3. The agents themselves degrade faster than expected (quality collapse, safety concerns). Pause and re-evaluate.

Otherwise, run the loop. Compound. Let the agents do the work.
