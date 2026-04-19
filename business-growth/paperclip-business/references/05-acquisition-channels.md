# Acquisition Channels

Ranked by expected CAC, time-to-first-dollar, and automation fit. Use only one or two at a time — the Acquire agent gets distracted by channel sprawl.

## Channel Scorecard

| Channel | Blended CAC | Time-to-1st-$ | Automation | Ceiling | Recommended |
|---|---|---|---|---|---|
| Founder-led outbound email | $200–$600 | 2–4 weeks | Medium | $40k MRR | ✅ First 20 customers |
| Content SEO (own blog) | $300–$900 | 12–24 weeks | High | $300k MRR | ✅ Always-on, compounding |
| LinkedIn founder content | $100–$500 | 4–12 weeks | Medium | $80k MRR | ✅ Always-on |
| Partnership / referral program | $200–$700 | 8–16 weeks | Medium | $150k MRR | ✅ Month 4+ |
| Paid search (Google Ads) | $1,500–$4,000 | 4 weeks | Medium | Uncapped | ⚠️ Only after $25k MRR |
| Paid social (LinkedIn Ads) | $2,000–$6,000 | 6–10 weeks | Medium | Uncapped | ❌ Too expensive pre-PMF |
| Podcast sponsorships | Varies wildly | 4–8 weeks | Low | Unclear | ❌ Noisy signal |
| Webinars / virtual events | $400–$1,200 | 4–8 weeks | Low | $100k MRR | ⚠️ Only with a co-host |
| Cold calling | $600–$1,500 | 2 weeks | Low | $50k MRR | ❌ Not Claude-friendly |

## Playbook: Founder-Led Outbound Email (Channel A)

This is the first channel. **The founder sends the first 50 emails personally**, not the agent. Why: the agent needs a corpus of what works before it takes over.

### Week 0 — List building

- Pull 500 ICP-fit companies. Criteria (for SEO business):
  - B2B SaaS, $2M–$30M ARR (Crunchbase, PitchBook)
  - Blog with < 4 articles/month last 90 days
  - Hired a marketing leader in past 12 months (LinkedIn)
- For each, identify the "content owner" (Head of Marketing, Head of Content, or CMO).

### Week 1–2 — Manual sending

- 30 emails/day, Monday–Thursday. 4 email sequence per prospect.
- Email 1: "First free article" offer, 70 words max.
- Email 2 (day 4): Case study proof, 60 words.
- Email 3 (day 9): Specific keyword audit teaser (you pulled from Ahrefs/SEMrush free tier).
- Email 4 (day 14): Break-up email.

Capture everything: subject lines that got opens, angles that got replies, objections raised. This becomes the Acquire agent's training corpus.

### Week 3+ — Agent takeover

- Founder drafts a final system prompt for Acquire agent with:
  - Email templates (the winning variants)
  - Objection library (with approved responses)
  - Disqualification rules
  - Sending windows
- Acquire agent sends up to 30/day per domain. Founder reviews daily digest for first 2 weeks, then weekly.

### Deliverability guardrails

- 2 sending domains minimum (rotate).
- Warm up each new domain for 14 days before volume.
- Bounce rate < 3%. Complaint rate < 0.08%. Auto-pause if exceeded.
- Honor unsubscribe within 24 hours. Maintain a suppression list.
- Never use images or tracking pixels in cold email (hurts deliverability).

### Compliance

- CAN-SPAM (US): physical address in footer, clear unsubscribe, accurate subject.
- GDPR (EU): cold email to business addresses is legal under "legitimate interest" but document the reasoning. Unsubscribe is absolute.
- CASL (Canada): express consent required. Generally skip Canadian prospects in cold channels until later.

## Playbook: Content SEO (Channel B)

### Strategy

- Target **money-keyword long-tail** queries your ICP actually searches.
  - For SEO content business: "b2b saas content marketing agency", "ai seo content service", "productized content subscription".
- Pillar-cluster model: 1 pillar page + 8 cluster articles per quarter.
- Publish 2 articles/week, indefinitely.

### Execution

- Deliver agent writes the company's own blog content as a "customer of one." This has two benefits:
  - Free case study: "We used our own service to grow our blog from 0 to 40k visits in 6 months."
  - Agent practice in a lower-stakes environment.

### KPI

- Domain rating: +10 points/year (via guest posts + mentions).
- Organic traffic: 2x every 6 months for first 18 months.
- Conversion: 1–2% of organic traffic → demo request (free article).

## Playbook: LinkedIn Founder Content (Channel C)

### Strategy

- Founder personal brand, not company page.
- 4 posts/week: 2 case studies, 1 contrarian opinion, 1 tactical "how we did X" thread.
- **Founder writes or approves every post**. Agent drafts, founder ships. This voice can't be fully delegated.

### KPI

- 100 inbound DMs/month at 2k followers.
- 2% DM-to-meeting rate.
- 30% meeting-to-customer rate.

## Channel Discipline

**One channel at a time** until it's producing consistent leads. Layer a second only when:
- Channel 1 is producing > $10k new MRR/month consistently
- You've identified CAC on Channel 1 within a narrow band
- Founder has > 2hr/week of bandwidth to seed Channel 2

Adding channels prematurely splits the Acquire agent's focus and makes attribution impossible.

## When to Kill a Channel

- CAC > LTV/3 for 8 consecutive weeks.
- Channel-attributable customers have 2x the average churn.
- Channel requires > 4 founder hours/week to operate.

If a channel dies, do the post-mortem — especially: was it bad targeting, bad copy, or a bad offer? Often "bad channel" is really "right channel, wrong message."
