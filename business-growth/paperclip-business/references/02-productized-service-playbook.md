# Productized Service Playbook — AI SEO Content Subscription

End-to-end playbook for the default business. Replace the specifics if you chose a different model from `01-business-model-selection.md`; the structure is the same.

## 1. Ideal Customer Profile (ICP)

- **Company stage:** Series A or Series B B2B SaaS, $2M–$30M ARR.
- **Team:** 1 marketing generalist, no dedicated content team.
- **Evidence of pain:** Publishes < 4 articles/month, ranks for < 500 keywords, has a blog but it's neglected.
- **Trigger event:** Recent funding round OR new marketing leader in past 90 days.

Do **not** target agencies (they have their own writers) or consumer brands (content dynamics differ).

## 2. Offer Architecture

Three tiers. No custom contracts under the $8k ceiling.

| Tier | Price/mo | Articles | Research Depth | Revisions | SLA |
|---|---|---|---|---|---|
| **Starter** | $2,000 | 10 | Basic (Brave Search + 3 sources) | 1 round | 7 days |
| **Growth** | $4,000 | 20 | Deep (15+ sources, SME interview transcript mining) | 2 rounds | 5 days |
| **Scale** | $8,000 | 40 | Deep + original data angles + pillar pages | 3 rounds | 5 days |

**Annual pre-pay discount:** 15% off (pulls forward 1.8 months of cash; reduces churn optically).

**Overage:** $180/article beyond tier limit (capped at +25% of tier).

## 3. Delivery Flow (The Factory)

```
Customer onboarding (Week 0)
  │
  ├─► Topic strategy session (60 min call, founder + Deliver agent notes)
  ├─► Keyword universe (1,000+ keywords clustered)
  ├─► Brand voice capture (3 reference articles → voice prompt)
  └─► Publishing access (WP / Webflow / Ghost API token)

Per-article loop (repeated 10/20/40x per month)
  │
  ├─► [Acquire agent] — Not involved
  ├─► [Deliver agent] — Keyword selection from approved cluster
  │     │
  │     ├─► Research (Brave Search + scraping + source ranking)
  │     ├─► Outline (H2/H3 + evidence-per-section map)
  │     ├─► Draft (brand-voice prompt + outline + sources)
  │     ├─► Internal QA (fact-check + readability + SEO checklist)
  │     ├─► Image selection (Unsplash API + alt text)
  │     └─► Publish via CMS API (draft state)
  │
  ├─► [Retain agent] — Weekly report: published count, early traffic, keyword wins
  └─► [Finance agent] — Invoice on monthly anniversary
```

## 4. Tech Stack (~$400/month fixed, ~$15/customer/month variable)

- **Agent runtime:** Claude Agent SDK (Opus 4.7 for drafting, Haiku for classification/routing)
- **Research:** Brave Search API ($5/1k queries), web scraping (stdlib only)
- **CRM:** Airtable ($20/mo) or HubSpot free
- **Payments:** Stripe (2.9% + 30¢)
- **Publishing:** WordPress REST API, Ghost Admin API, Webflow CMS API — all native
- **Email (transactional + cold):** Postmark ($15/mo) + Instantly for outbound
- **Ops dashboard:** A single Airtable base + weekly generated Markdown digest
- **Accounting:** Wave (free) or Xero ($13/mo) + quarterly CPA review

Do **not** buy: project management tools, Zapier Pro, content-at-scale SEO tools, heavy CRMs. The agents replace these.

## 5. Go-to-Market (First 20 Customers)

Only two channels matter at this stage. Kill everything else.

### Channel A: Founder-led outbound (Weeks 0–6)

- Build list of 500 ICP-fit companies. Use LinkedIn Sales Navigator free trial → export.
- Send 30 personalized emails per day. **Founder** writes the first 50 manually. This sets the voice for the Acquire agent to learn.
- Offer: "First article free, full audit of your existing content performance, no credit card."
- Target: 2% meeting rate, 30% meeting → customer. Yields ~3 customers per 1,000 emails.

### Channel B: Build-in-public content (Weeks 2+)

- Founder publishes 1 case study per week on LinkedIn + company blog.
- Case study format: "$CUSTOMER was ranking for 120 keywords. After 90 days with us: 840 keywords. Here's the exact process."
- This compounds. By month 6, inbound should be 30% of pipeline.

Do **not** try paid ads before $25k MRR. CAC math doesn't work until you have strong LTV signal.

## 6. Unit Economics (Target)

Middle tier ($4,000/mo) baseline:

| Metric | Target |
|---|---|
| Gross margin | 82% |
| CAC (blended) | ≤ $1,200 |
| Payback | ≤ 1.5 months |
| Logo churn | ≤ 4% monthly |
| Net revenue retention | ≥ 105% |
| LTV (24 months avg life) | ~$78,000 |
| LTV:CAC | ≥ 50:1 (agency-like) |

Run `scripts/unit_economics_modeler.py` to model your own stack.

## 7. Pricing Moves

- **Never discount except annual pre-pay.** Agent pricing authority is locked.
- **Raise prices 10% every 12 months for new customers.** Grandfather existing.
- **Add a custom tier only at $15k+/mo** and only with 12-month commit.

## 8. When to Change the Formula

- **Churn > 6% for 2 consecutive months:** Delivery quality issue. Stop Acquire; fix Deliver. Escalate to founder.
- **CAC > LTV/3:** Either raise prices or cut the channel.
- **< 3 new customers for 4 weeks:** Founder runs a 2-week outbound sprint personally. Diagnose whether the market, offer, or messaging is broken.
- **One customer > 15% of MRR:** Concentration risk. Cap acquisitions in that vertical.

## 9. 12-Month Targets

- Month 3: $10k MRR, 3 customers, founder time ~10 hr/week
- Month 6: $30k MRR, 9 customers, founder time ~6 hr/week
- Month 9: $60k MRR, 17 customers, founder time ~4 hr/week
- Month 12: $100k MRR, 27 customers, founder time ~3 hr/week

After Month 12, consider: raise prices 15%, add Scale tier polish, hire 1 human editor (first employee).
