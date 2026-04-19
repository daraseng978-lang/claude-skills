# Decision Log — Directory Portfolio Co.

Append-only. Each entry is a ratified decision per the `decision-logger` pattern.

---

## D-001 — Company formed
- **Date:** 2026-04-19
- **Decider:** Founder
- **Decision:** Proceed with AI-operated directory portfolio company.
- **Rationale:** Transcript thesis + directory moat via AI data pipelines.

## D-002 — Budget Gate #1 approved
- **Date:** 2026-04-19
- **Decider:** Founder
- **Decision:** Approve $280 for Phase 0.
- **Allocation:** Claude Code Max $100, Outscraper $100, Claude API $50, domain/hosting $30.

## D-003 — Niche selection delegated → ADA Bathroom Contractors
- **Date:** 2026-04-19
- **Decider:** CEO + CPO (delegated by founder)
- **Decision:** Phase 0 property is ADA-Accessible Bathroom Contractors.
- **Rationale:** See `niche-recommendation.md`. Top score on competition, TAM tailwind, AI-search resilience.

## D-004 — Company name delegated → AccessRemodel
- **Date:** 2026-04-19
- **Decider:** CEO (delegated by founder)
- **Decision:** Brand name is **AccessRemodel**. Domain target `accessremodel.com`.
- **Rationale:** Descriptive for SEO, expandable beyond bathrooms (stair lifts, whole-home retrofit).
- **Fallback:** `accessremodel.co` or `accessremodel.pro` if `.com` unavailable.

## D-005 — Founder interaction rule
- **Date:** 2026-04-19
- **Decider:** Founder
- **Decision:** Founder touches project at budget gates only. Chief of Staff is the only agent that messages founder.

## D-006 — Domain purchased (AccessRemodel)
- **Date:** 2026-04-19
- **Decider:** Founder
- **Decision:** Registered **accessremodel.co** (.com unavailable or too expensive).
- **Implication:** All canonical URLs, meta tags, email sender domains use `.co`. SEO brand terms reference "AccessRemodel" (no TLD) to stay resilient.

## D-007 — Strategy revised: 1-property → 5-property portfolio
- **Date:** 2026-04-19
- **Decider:** Founder (challenge) + CEO (concession)
- **Decision:** Phase 0 expanded from single-property launch to parallel 5-property portfolio.
- **Rationale:** Founder correctly argued that portfolio thesis requires a portfolio. SEO ramp (~6 months) is the serial bottleneck regardless of property count, so parallelizing compresses calendar time. Marginal cost per additional property (~$130) is small vs. fixed costs already paid. 5 shots on goal beats 1 at matched cost of attention.
- **Budget impact:** $280 → $850 (+$570). Approved.
- **Hit-rate expectation:** 2–3 keepers out of 5 at Day 90.

## D-008 — Portfolio composition (5 properties)
- **Date:** 2026-04-19
- **Decider:** CEO + CPO (delegated, founder approved)
- **Decision:** Phase 0 launches AccessRemodel, DementiaCare, WalkInTubPros, IVFCost, ADUBuilders.
- **Rationale:** See `portfolio-strategy.md`. Top 5 of 10 niches scored, diversified across 3 industries (aging-in-place, healthcare, housing). No single sector >40% of portfolio. Runners-up (CAPS contractors, stair lifts, bariatric, luxury restroom trailers, tap water) deferred to Phase 2 or rejected.

## D-009 — Repo restructure for portfolio layout
- **Date:** 2026-04-19
- **Decider:** CTO
- **Decision:** Portfolio-wide docs promoted to `companies/` root; niche-specific content moved to `companies/<property>/` subfolders. Shared pipeline at `companies/pipeline/`.
- **Rationale:** Clear parent/child structure as portfolio grows. Aligns with Chief of Staff + agent orchestration patterns from `c-level-advisor/`.
