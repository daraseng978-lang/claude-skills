# IVFCost — Fertility Clinic Price Transparency Directory

**Portfolio property #4.** Nationwide directory of IVF clinics with transparent pricing, success rates, and insurance coverage — the clearest price-transparency play in the portfolio.

## Status

| | |
|---|---|
| Domain | TBD (suggested: `ivfcost.co` or `fertilitypricing.co`) |
| Launch target | Day 11–14 of Phase 0 |

## Niche Thesis

- **Decision-driver:** IVF cycle pricing varies $12K–$30K between clinics with near-zero transparency; success rates vary even more
- **TAM:** US IVF market ~$7B/yr, growing 4–6% CAGR
- **Tailwind:** 1 in 6 couples affected by infertility; employer coverage expanding
- **Lead value:** $100–400 (clinics are highly motivated to acquire cycle-starts)
- **AI-search resilience:** Strong — IVF decisions are high-stakes, families research exhaustively
- **Unique wedge:** **Frey's price-transparency thesis** applied to the highest-variance pricing market in healthcare

## Killer Feature

Cost calculator + success rate overlay:

- Input: age, diagnosis, location, insurance
- Output: expected all-in cost per live birth (not just per cycle), with clinic-specific estimates
- Data sources:
  - **CDC ART (Assisted Reproductive Technology) public database** — success rates by clinic
  - **Clinic-provided pricing** (via outreach) — base IVF, ICSI, PGT-A, meds, freezing
  - **User-submitted** actual costs (long-term data moat)

## YMYL Consideration

Healthcare = YMYL. Mitigations:
- Link every claim to CDC ART data, SART, or clinic source
- No medical advice — pricing and outcome data only
- Doctor-reviewed content (find CMO-sponsored advisor)
- Clear disclosure that this is informational, not medical advice

## Filter Schema

- Clinic accreditation (CAP, CLIA)
- SART membership (yes/no)
- Services: IVF, ICSI, PGT-A, egg freezing, donor egg, gestational carrier
- Insurance accepted (Progyny, Carrot, WINFertility, direct employer)
- Financing partners (Future Family, Prosper Healthcare)
- Multi-cycle package pricing
- Live birth rate per transfer (age bucket)
- LGBTQ+ affirming (yes/no)
- Languages spoken

## Per-Property Budget

| Line | $ |
|---|---|
| Outscraper | $50 (smaller niche, ~500 clinics nationwide) |
| Claude API credits | $30 |
| Domain | $12 |
| **Total** | **$92** |

## Launch Milestones

- [ ] Outscraper for "IVF clinic", "fertility clinic", "reproductive endocrinology"
- [ ] Cross-reference against CDC ART 2023 report (public data)
- [ ] Outreach to top-100 clinics for pricing disclosure
- [ ] Deploy cost calculator as interactive tool
- [ ] YMYL-compliant editorial with medical disclaimers

Kill criteria: <300 monthly visits AND $0 MRR at Day 90.
