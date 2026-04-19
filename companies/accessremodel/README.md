# AccessRemodel — ADA-Accessible Bathroom Contractors

**Portfolio property #1.** Nationwide directory of contractors specializing in accessibility retrofits (grab bars, roll-in showers, walk-in tubs, ADA-compliant vanities).

## Status

| | |
|---|---|
| Domain | `accessremodel.co` ✅ purchased |
| Vercel | project pending (Day 1 tomorrow) |
| Resend | domain verified ✅ |
| Outscraper | $100 allocated |
| Launch target | Day 1–2 of Phase 0 (first property live) |

## Niche Thesis

- **Decision-driver:** ADA compliance (binary, non-specialists can't fake it)
- **TAM:** ~$2B US accessible bathroom remodel annual spend
- **Tailwind:** ~10K Americans turn 65 daily; aging-in-place is #1 senior preference (AARP 77%)
- **Lead value:** $50–200 (projects $5K–$50K, contractor CAC tolerance ~$200)
- **AI-search resilience:** Specific compliance queries ("ADA bathroom contractor near me with roll-in shower") survive LLM aggregation

## Filter Schema

- Services: grab bars, roll-in shower, walk-in tub, curbless shower, accessible vanity, raised toilet, shower seat, non-slip flooring, stair lift, ramp install, widened doorways
- CAPS certification (NAHB Certified Aging-in-Place Specialist)
- Licensed & insured
- Service radius (miles)
- Free consultation offered

## Files

- `niche-recommendation.md` — original CEO/CPO memo justifying this niche
- `site-config.md` — Next.js metadata, DNS records, schema.org, Resend lead route
- (shared) `../pipeline/` — scrape + clean + verify + enrich scripts
- (shared) `../company-context.md`, `../execution-plan.md`, `../budget-ledger.md`

## Per-Property Budget

| Line | $ |
|---|---|
| Outscraper | $100 |
| Claude API credits | $50 |
| Domain | $12 |
| **Total** | **$162** |

## Launch Milestones

- [ ] Outscraper pull complete (~50K raw rows)
- [ ] Cleaned to ~15K contractors
- [ ] Verified ~800–1.5K ADA specialists
- [ ] Enriched with services + certifications
- [ ] Site deployed to Vercel
- [ ] Google Search Console verified
- [ ] First 3 inbound leads

Kill criteria: <300 monthly visits AND $0 MRR at Day 90 → sunset domain, reallocate.
