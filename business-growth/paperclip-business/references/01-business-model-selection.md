# Business Model Selection

Five candidate businesses, scored for a Claude-operated, founder-as-investor setup. Score weights (0–10): **Automation Fit** (30%), **Clarity of Buyer** (20%), **Margin Headroom** (20%), **Time-to-Revenue** (15%), **Defensibility** (15%).

## Candidates

### 1. AI SEO Content Subscription — **Score: 8.6 / 10** (Default Pick)

- **Offer:** 20 SEO-optimized long-form articles per month, published directly into customer CMS.
- **Buyer:** Head of Marketing / Content at Series A–B B2B SaaS (20–200 employees).
- **Price:** $2k / $4k / $8k per month, 3 tiers by volume and depth.
- **Automation fit (10/10):** Research, writing, internal linking, publishing — all native Claude territory. Human touch only at topic-strategy and QBR milestones.
- **Margin:** 80%+ gross. Variable cost is tokens + Brave Search API + CMS API calls.
- **Time-to-revenue:** 2–4 weeks with cold outbound. SEO pilots convert well because outcome is measurable.
- **Defensibility:** Moderate. Brand + case studies + compounding content on your own site become the moat.
- **Key risks:** Google algorithm shifts, AI-content devaluation trend. Mitigation: ship content so good it passes human editorial review + cite sources.

### 2. Competitor Intelligence Reports — **Score: 8.1 / 10**

- **Offer:** Weekly 8–12 page brief on 3–5 named competitors: pricing, positioning, new features, job posts, ad creative, press.
- **Buyer:** VP Product / VP Marketing at venture-backed companies in crowded markets.
- **Price:** $1.5k–$5k per month.
- **Automation fit (9/10):** Scraping + summarization + diffing. Heavy on research tools.
- **Margin:** 85%+.
- **Time-to-revenue:** 3–6 weeks (longer sales cycle, more consultative).
- **Defensibility:** Low-to-moderate. Easy to copy; the moat is taste and source quality.
- **Pick this if:** You have industry expertise in a specific vertical (fintech, devtools, healthtech).

### 3. Pull Request Review Subscription — **Score: 7.8 / 10**

- **Offer:** AI code review on every PR, plus a weekly "technical debt" report. Claude reviews against a customer-specific style guide.
- **Buyer:** Engineering managers at 20–100 person engineering teams.
- **Price:** $500–$2,000 per month per repo.
- **Automation fit (10/10):** Core Claude skill. Integrates with GitHub App.
- **Margin:** 75% (higher token spend per unit of revenue).
- **Time-to-revenue:** 6–10 weeks. Longer technical-sell and security review.
- **Defensibility:** Low. Dozens of competitors (CodeRabbit, Greptile, etc.). Only win if you niche aggressively (e.g., "Rails monoliths only", "regulated healthcare codebases only").

### 4. Lead Enrichment + Personalized Outreach — **Score: 7.2 / 10**

- **Offer:** Inbound leads enriched with firmographic data + 3 personalized outreach drafts per lead.
- **Buyer:** SDR leader at $5M–$50M ARR SaaS.
- **Price:** $2k / $4k / $6k per month.
- **Automation fit (9/10):** But depends on paid data sources (Apollo, Clearbit) — watch margin.
- **Margin:** 55–65%. Data costs are the squeeze.
- **Time-to-revenue:** 4–6 weeks.
- **Defensibility:** Low. Lots of "AI SDR" vendors. Differentiate on deliverability + copy quality.
- **Caution:** Cold email regulation risk (CAN-SPAM, GDPR, Canada CASL). Requires legal discipline.

### 5. Newsletter-as-a-Service — **Score: 6.8 / 10**

- **Offer:** Fully written weekly newsletter (800–1,500 words) for B2B brands, delivered in their voice and into their ESP.
- **Buyer:** Marketing generalists at $1M–$10M ARR SaaS who "want a newsletter" but can't staff it.
- **Price:** $1,500–$3,500 per month.
- **Automation fit (9/10):** Voice modeling + research + editing, all Claude-native.
- **Margin:** 80%+.
- **Time-to-revenue:** 3–5 weeks.
- **Defensibility:** Low. Commoditized category. Only works at the low end of the market where buyer doesn't compare vendors rigorously.

## How to Choose

Use `scripts/business_model_selector.py` with your own constraints. The scorer re-ranks based on:

- Capital available (< $5k / $5k–$25k / > $25k)
- Founder monthly time budget (≤ 4hr / 4–10hr / 10–20hr)
- Existing domain expertise (none / some / deep)
- Risk tolerance (conservative / moderate / aggressive)
- Geography (US / EU / global)

If you have no strong opinion and no domain expertise, take the default (SEO Content Subscription). If you have deep domain expertise in a vertical, Competitor Intelligence becomes the top pick.

## Businesses This Skill Explicitly Rejects

- **Dropshipping / ecommerce** — inventory, returns, ads — agents can't operate fulfillment reliably.
- **Crypto/trading bots** — regulatory, custodial, and capital-at-risk concerns.
- **Info-product launches** — spiky, not recurring; not MRR.
- **Done-for-you ads management** — ad-platform TOS + trust constraints make this high-support, low-margin.
- **Generic "AI agency"** — too broad; the paperclip principle requires one buyer, one offer.
