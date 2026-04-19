# Execution Plan — AccessRemodel

## Phase 0 — Validate (30 days)

**Goal:** Live directory, indexed, first inbound leads.

### Workstreams

| # | Owner | Task | Deliverable | Cost |
|---|---|---|---|---|
| 1 | CTO | Outscraper pull: "bathroom remodeling", "ADA contractors", "accessible home modifications" — nationwide | Raw CSV, ~50K rows | $100 |
| 2 | CTO | Junk-filter pass (`pipeline/02_clean.py`) | ~15K rows cleaned | $0 (Claude Code Max) |
| 3 | CTO | ADA-verification pass via Crawl4AI + classifier (`pipeline/03_verify_ada.py`) | ~800–1.5K verified ADA contractors | $50 API credits |
| 4 | CPO | Decision-driver research (Reddit r/aginginplace, AARP, CAPS certification) | `decision-drivers.md` with filter schema | $0 |
| 5 | CTO | Enrichment passes: certifications (CAPS), services (grab bars, roll-in, walk-in tub, vanity), service radius | Enriched CSV | $0 |
| 6 | CTO | Next.js + Tailwind directory template from `engineering-team/landing-page-generator` skill | Deployed site on Vercel free tier | $0 |
| 7 | CMO | Programmatic SEO: city × service matrix pages, meta + schema.org LocalBusiness | ~2K pages indexed | $0 |
| 8 | CMO | Initial backlink seed: HARO, 3–5 aging-in-place blog outreach | ≥3 DR30+ backlinks | $0 |
| 9 | CRO | Lead form + email routing (Resend free tier) | Inbound leads email to founder inbox | $0 |
| 10 | CFO | Weekly dashboard: traffic, leads, spend | `dashboards/phase0.md` | $0 |

**Phase 0 approved budget:** $280 ($100 scraper + $50 API + $100 Claude Code Max + $30 domain/hosting)

### Budget Gate #1 — Completed (this message)
- [x] $280 authorized
- [x] Niche + company name delegated → chosen

### Budget Gate #2 — Trigger Conditions
First of:
- Phase 0 cost overrun projected > $50
- Day 30 with ≥500 verified listings live (proceed to monetization experiments)
- Ask: domain purchase ($12–30), Supabase paid tier if free hits cap ($25/mo), Resend paid tier ($20/mo)

---

## Phase 1 — Monetize (days 30–90)

**Goal:** First paying contractor, first $1K month.

- CRO runs outbound to top-100 listed contractors: "claim your listing" flow → paid upgrades ($49–99/mo featured slot)
- CRO sets up lead-purchase experiment: $30–50/lead, delivered by email
- CMO layers in city backlink campaigns
- CFO reports weekly to founder; budget ask only if experiment needs >$100

### Budget Gate #3 — Scale decision (day 90)
- If MRR ≥$500: approve Phase 2 (portfolio expansion, pick niche #2)
- If MRR <$500 but traffic >2K/mo: continue Phase 1, reallocate
- If both below: kill criteria met → post-mortem, rotate niche

---

## Phase 2 — Portfolio (days 90–365)

- Add niches in ranked order from `niche-recommendation.md`: dementia senior living, then luxury restroom trailers (if Frey's moat is breakable), then CAPS aging-in-place auditors
- Target: 5 properties live, $5–10K/mo aggregate MRR by day 365
- Evaluate micro-SaaS wedge (e.g., ADA-compliance checker tool for contractors)

---

## Founder Touchpoints Summary

| Gate | When | Founder Decision |
|---|---|---|
| #1 | Done | Approve $280 ✅ |
| #2 | Day 30 or overrun | Approve domain + infra paid tiers (~$60) |
| #3 | Day 90 | Scale, continue, or kill |
| #4+ | Per new niche | Approve next Phase 0 budget (~$280 each) |

Chief of Staff sends a single summary email per gate. No other interaction expected from founder.
