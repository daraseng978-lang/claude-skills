# Execution Plan — Directory Portfolio Co.

## Phase 0 — 5-Property Parallel Launch (30 days)

**Goal:** All 5 directories indexed, first inbound leads across the portfolio by Day 30.

### Parallel Workstreams

All 5 properties run the **same pipeline in parallel**, staggered by 2–3 days to manage API rate limits and cognitive load.

| # | Owner | Task | Deliverable | Shared vs Per-property |
|---|---|---|---|---|
| 1 | CTO | Outscraper pulls (5 niches, nationwide) | 5 raw CSVs | Per-property ($50–100 each) |
| 2 | CTO | Junk-filter (`pipeline/02_clean.py`) | 5 cleaned CSVs | Shared code, per-property data |
| 3 | CTO | Niche-verification (parameterize `03_verify_*.py` per niche) | 5 verified CSVs | Shared code with niche prompts |
| 4 | CPO | Decision-driver research per niche → filter schemas | 5 `decision-drivers.md` files | Per-property |
| 5 | CTO | Enrichment passes (services, certifications, service radius) | 5 enriched CSVs | Shared code, per-property |
| 6 | CTO | Next.js template → 5 deploys on Vercel free tier | 5 live sites | Shared template, per-property config |
| 7 | CMO | Programmatic SEO: city × service matrix per property | ~10K pages total indexed | Per-property content |
| 8 | CMO | Backlink seed per property (HARO, niche blogs) | ≥2 DR30+ backlinks per property | Per-property |
| 9 | CRO | Lead form + Resend routing per property | Inbound leads → founder inbox | Shared code, per-property domain |
| 10 | CFO | Weekly portfolio dashboard | `dashboards/phase0.md` | Portfolio-aggregate |

### Launch Schedule (2-week rollout)

| Week | Day | Property launched | Rationale |
|---|---|---|---|
| 1 | 1–2 | **AccessRemodel** | Anchor, pipeline already scoped |
| 1 | 3–4 | **WalkInTubPros** | ~50% data reuse from #1 |
| 1 | 5–7 | **DementiaCare** | Different domain, needs YMYL-conscious content |
| 2 | 8–10 | **ADUBuilders** | State-permit data layer requires research |
| 2 | 11–14 | **IVFCost** | Most complex (price aggregation + CDC success rate overlay) |

## Phase 0 Budget — $850 Approved

| Line | $ |
|---|---|
| Claude Code Max (shared, already running) | 100 |
| Outscraper pulls (5 × ~$70 avg) | 350 |
| Claude API credits (verification + enrichment × 5) | 150 |
| Domains (5 × ~$12, `.co` each) | 60 |
| Vercel + Resend (free tiers) | 0 |
| Buffer 10% | 90 |
| Anthropic API credits (founder-funded, not in budget) | 30 |
| Funded-to-date | 200 |
| **Phase 0 approved total** | **$850** |

### Budget Gate #1 — Done
- [x] Initial $280 approved
- [x] Revised to $850 after founder push for portfolio launch
- [x] Niches + names delegated → selected (see `portfolio-strategy.md`)

### Budget Gate #2 — Trigger Conditions
First of:
- Phase 0 cost overrun projected > $100 across portfolio
- Day 30 with ≥3 of 5 properties indexed → proceed to monetization experiments
- Typical ask: paid-tier infra (~$60) + domain renewals

---

## Phase 1 — Monetize Winners, Kill Losers (Days 30–90)

**Goal:** First paying customer on at least 1 property; $1K+ aggregate MRR.

- CRO runs contractor outreach on top-3 performing properties (featured listing upgrades)
- CRO tests lead-sale pricing on properties where form conversion ≥3%
- CMO doubles down on SEO for 2–3 properties showing traffic traction
- **Kill losers at Day 60** if traffic <100/mo (reallocate API budget and sunset the site)
- CFO reports aggregate weekly; budget ask only if experiments need >$100

### Budget Gate #3 — Day 90 Portfolio Review
- **Keepers:** any property with ≥$200 MRR OR ≥1K visits/mo → Phase 1 continues
- **Watchlist:** <$200 MRR AND <1K visits → 30-day ultimatum, then kill
- **Kills:** <300 visits AND $0 MRR → sunset + domain park
- If portfolio MRR ≥$1K: approve Phase 2 (add properties #6+)
- If portfolio MRR <$500 across all 5: post-mortem, rotate all

---

## Phase 2 — Scale Winners, Add Depth (Days 90–365)

- Expand city coverage on winning properties (programmatic long-tail SEO)
- Add micro-SaaS wedges to top 1–2 performers (e.g., quote tool, compliance checker)
- Stream 4 display ads live once any property hits 50K sessions/mo (Mediavine)
- Only add new properties (#6+) if capital-ROI positive

### Budget Gate #4 — Day 365
- Target: ≥$5K aggregate MRR
- Decision: hold-and-compound, raise capital, or strategic sale of top performer

---

## Founder Touchpoints Summary

| Gate | When | Founder Decision |
|---|---|---|
| #1 | Done | Approve $850 Phase 0 ✅ |
| #2 | Day 30 or overrun | Approve infra paid tiers (~$60) |
| #3 | Day 90 | Kill/keep/scale each property |
| #4 | Day 365 | Hold, raise, or strategic sale |
| #5+ | Per new property added | Approve marginal Phase 0 budget (~$150 each) |

Chief of Staff sends one summary per gate. No other founder interaction expected.
