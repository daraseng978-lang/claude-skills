# Directory Portfolio — Operating Company

AI-operated portfolio of niche directories. Founder/investor interacts only at budget gates.

## Portfolio (Phase 0)

| # | Property | Niche | Folder | Status |
|---|---|---|---|---|
| 1 | AccessRemodel | ADA bathroom contractors | `accessremodel/` | Anchor — scoped |
| 2 | DementiaCare | Memory care facilities | `dementiacare/` | Queued |
| 3 | WalkInTubPros | Walk-in tub installers | `walkintubpros/` | Queued |
| 4 | IVFCost | Fertility clinic price transparency | `ivfcost/` | Queued |
| 5 | ADUBuilders | Accessory dwelling unit contractors | `adubuilders/` | Queued |

## Structure

| Path | Purpose |
|---|---|
| `company-context.md` | Portfolio-level context consumed by all agents |
| `portfolio-strategy.md` | 10-niche research; why these 5, why not the others |
| `execution-plan.md` | Parallel Phase 0 rollout across all 5 properties |
| `budget-ledger.md` | $850 Phase 0 authorization, actuals tracking |
| `revenue-model.md` | Per-property projection + aggregate portfolio |
| `decisions.md` | Append-only decision log |
| `pipeline/` | Shared scraping + enrichment code (reused across all properties) |
| `<property>/` | Per-property site config, niche-specific pipeline tweaks, brand assets |

## C-Suite Assignments (from `c-level-advisor/`)

| Agent | Role |
|---|---|
| CEO | Portfolio strategy, capital allocation across properties |
| CPO | Niche research, decision-driver + filter schema per property |
| CTO | Shared pipeline + Next.js template + per-property deploys |
| CMO | Programmatic SEO, backlink campaigns, per-property content |
| CRO | Lead-gen monetization, contractor outreach playbook |
| CFO | Unit econ per property, aggregate reporting, budget gates |
| Chief of Staff | Orchestration + single founder touchpoint |

## Founder Interaction Rule

Founder touches the project **only at budget gates**. Chief of Staff sends one summary per gate. No other interaction expected.
