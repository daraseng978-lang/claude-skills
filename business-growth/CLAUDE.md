# Business & Growth Skills - Claude Code Guidance

This guide covers the production-ready business and growth skills and their Python automation tools.

## Business & Growth Skills Overview

**Available Skills:**
1. **customer-success-manager/** - Customer health scoring, churn risk analysis, expansion opportunities (3 Python tools)
2. **sales-engineer/** - Technical discovery, RFP analysis, competitive positioning, POC planning (3 Python tools)
3. **revenue-operations/** - Pipeline analysis, forecast accuracy, GTM efficiency metrics (3 Python tools)
4. **paperclip-business/** - Agent-operated productized-service blueprint with MRR forecasting, unit-economics modeling, business-model selector, and founder dashboard (4 Python tools, 8 reference guides, 4 asset templates)
5. **kdp-puzzle-publisher/** - Claude-powered Amazon KDP puzzle-book publishing company with niche scoring, BSR-to-revenue estimation, KDP listing builder, and portfolio planner (4 Python tools, 7 reference guides, 6 asset templates)

**Total Tools:** 17 Python automation tools, 24 knowledge bases, 29+ templates

## Python Automation Tools

### Customer Success Manager Tools

#### 1. Health Score Calculator (`customer-success-manager/scripts/health_score_calculator.py`)

**Purpose:** Multi-dimensional customer health scoring with trend analysis

**Features:**
- Weighted scoring across 4 dimensions (usage, engagement, support, relationship)
- Red/Yellow/Green classification with configurable thresholds
- Trend analysis comparing current vs previous period
- Segment-aware benchmarking (Enterprise/Mid-Market/SMB)

**Usage:**
```bash
python customer-success-manager/scripts/health_score_calculator.py customer_data.json
python customer-success-manager/scripts/health_score_calculator.py customer_data.json --format json
```

#### 2. Churn Risk Analyzer (`customer-success-manager/scripts/churn_risk_analyzer.py`)

**Purpose:** Identify at-risk accounts with intervention recommendations

**Features:**
- Risk scoring based on behavioral signals
- Warning signal detection and categorization
- Tier-appropriate intervention playbooks
- Urgency-based prioritization

**Usage:**
```bash
python customer-success-manager/scripts/churn_risk_analyzer.py customer_data.json
python customer-success-manager/scripts/churn_risk_analyzer.py customer_data.json --format json
```

#### 3. Expansion Opportunity Scorer (`customer-success-manager/scripts/expansion_opportunity_scorer.py`)

**Purpose:** Identify upsell and cross-sell opportunities

**Features:**
- Adoption depth analysis across product modules
- Whitespace mapping for unused features
- Revenue opportunity estimation
- Priority ranking by effort and impact

**Usage:**
```bash
python customer-success-manager/scripts/expansion_opportunity_scorer.py customer_data.json
python customer-success-manager/scripts/expansion_opportunity_scorer.py customer_data.json --format json
```

### Sales Engineer Tools

#### 4. RFP Response Analyzer (`sales-engineer/scripts/rfp_response_analyzer.py`)

**Purpose:** Score RFP/RFI coverage and identify gaps

**Features:**
- Requirement coverage scoring (Full/Partial/Planned/Gap)
- Effort estimation per requirement
- Gap identification with mitigation strategies
- Overall bid/no-bid recommendation

**Usage:**
```bash
python sales-engineer/scripts/rfp_response_analyzer.py rfp_data.json
python sales-engineer/scripts/rfp_response_analyzer.py rfp_data.json --format json
```

#### 5. Competitive Matrix Builder (`sales-engineer/scripts/competitive_matrix_builder.py`)

**Purpose:** Generate feature comparison matrices and competitive positioning

**Features:**
- Feature-by-feature comparison matrix
- Competitive scoring with weighted categories
- Differentiator identification
- Battlecard-ready output

**Usage:**
```bash
python sales-engineer/scripts/competitive_matrix_builder.py competitive_data.json
python sales-engineer/scripts/competitive_matrix_builder.py competitive_data.json --format json
```

#### 6. POC Planner (`sales-engineer/scripts/poc_planner.py`)

**Purpose:** Plan proof-of-concept engagements

**Features:**
- Timeline estimation based on scope
- Resource allocation planning
- Success criteria definition
- Evaluation scorecard generation

**Usage:**
```bash
python sales-engineer/scripts/poc_planner.py poc_data.json
python sales-engineer/scripts/poc_planner.py poc_data.json --format json
```

### Revenue Operations Tools

#### 7. Pipeline Analyzer (`revenue-operations/scripts/pipeline_analyzer.py`)

**Purpose:** Analyze sales pipeline health and velocity

**Features:**
- Coverage ratio calculation (pipeline/quota)
- Stage conversion rate analysis
- Sales velocity metrics (4-lever model)
- Deal aging analysis

**Usage:**
```bash
python revenue-operations/scripts/pipeline_analyzer.py pipeline_data.json
python revenue-operations/scripts/pipeline_analyzer.py pipeline_data.json --format json
```

#### 8. Forecast Accuracy Tracker (`revenue-operations/scripts/forecast_accuracy_tracker.py`)

**Purpose:** Measure and improve forecast accuracy

**Features:**
- MAPE (Mean Absolute Percentage Error) calculation
- Forecast bias detection (over/under-forecasting)
- Period-over-period trend analysis
- Category-level accuracy breakdown

**Usage:**
```bash
python revenue-operations/scripts/forecast_accuracy_tracker.py forecast_data.json
python revenue-operations/scripts/forecast_accuracy_tracker.py forecast_data.json --format json
```

#### 9. GTM Efficiency Calculator (`revenue-operations/scripts/gtm_efficiency_calculator.py`)

**Purpose:** Calculate go-to-market efficiency metrics

**Features:**
- Magic number calculation
- LTV:CAC ratio analysis
- CAC payback period
- Burn multiple assessment
- Industry benchmarking

**Usage:**
```bash
python revenue-operations/scripts/gtm_efficiency_calculator.py gtm_data.json
python revenue-operations/scripts/gtm_efficiency_calculator.py gtm_data.json --format json
```

### Paperclip Business Tools

#### 10. Business Model Selector (`paperclip-business/scripts/business_model_selector.py`)

**Purpose:** Rank 5 candidate Claude-operated businesses against founder constraints

**Features:**
- 5 pre-scored candidates (SEO content, competitor intel, PR review, lead enrichment, newsletter)
- Constraint-aware adjustments (capital, time, expertise, risk, geography)
- Weighted scoring: automation fit, buyer clarity, margin, time-to-revenue, defensibility
- Rationale and adjustment trace for each candidate

**Usage:**
```bash
python paperclip-business/scripts/business_model_selector.py --input sample_business_inputs.json
python paperclip-business/scripts/business_model_selector.py --input sample_business_inputs.json --format json
```

#### 11. Unit Economics Modeler (`paperclip-business/scripts/unit_economics_modeler.py`)

**Purpose:** Model gross margin, CAC, payback, LTV, and break-even for a tier

**Features:**
- Contribution margin per customer
- Effective churn with expansion offset
- LTV in months and dollars
- CAC payback period
- Automatic warnings on margin/payback/LTV:CAC/churn thresholds

**Usage:**
```bash
python paperclip-business/scripts/unit_economics_modeler.py --input sample_unit_economics.json
```

#### 12. MRR Forecaster (`paperclip-business/scripts/mrr_forecaster.py`)

**Purpose:** Cohort-based MRR simulation to $10k/$50k/$100k milestones

**Features:**
- Monthly cohort simulation with growth and churn
- Expansion revenue modeling
- Milestone hit-month identification
- 24-month default horizon (configurable)

**Usage:**
```bash
python paperclip-business/scripts/mrr_forecaster.py --input sample_mrr_inputs.json
```

#### 13. Founder Dashboard (`paperclip-business/scripts/founder_dashboard.py`)

**Purpose:** Weekly digest the founder reads (only report they need)

**Features:**
- MRR WoW and MoM deltas
- Pipeline coverage vs quota
- Runway calculation
- Automatic red-flag detection (SLA misses, spam rate, concentration, churn, burn)
- Surfaces only escalations requiring founder decision

**Usage:**
```bash
python paperclip-business/scripts/founder_dashboard.py --input sample_weekly_state.json
```

### KDP Puzzle Publisher Tools

#### 14. Niche Scorer (`kdp-puzzle-publisher/scripts/niche_scorer.py`)

**Purpose:** Score a KDP puzzle-book niche against public Amazon signals (BSR, reviews, price, freshness)

**Features:**
- Log-linear demand, competition, pricing, and freshness sub-scores
- Saturation + seasonality flags
- Niche-specific recommendations
- GO / CONDITIONAL / PASS verdict with 0-100 overall

**Usage:**
```bash
python kdp-puzzle-publisher/scripts/niche_scorer.py --input sample_niche_inputs.json
```

#### 15. BSR to Revenue (`kdp-puzzle-publisher/scripts/bsr_to_revenue.py`)

**Purpose:** Estimate daily sales and monthly royalty from an Amazon BSR

**Features:**
- Piecewise log-log curve fit to public BSR anchors
- Configurable price, print cost, and royalty rate (paperback/Kindle)
- Confidence label based on BSR tier

**Usage:**
```bash
python kdp-puzzle-publisher/scripts/bsr_to_revenue.py --bsr 12450 --price 8.99
```

#### 16. KDP Listing Builder (`kdp-puzzle-publisher/scripts/kdp_listing_builder.py`)

**Purpose:** Generate a KDP-compliant listing (title, subtitle, description, 7 keywords, 2 categories) from a concept brief

**Features:**
- Validates character limits per KDP's 200/200/4000 rules
- Flags banned words (bestseller, #1, free) and trademark hits
- Naive keyword-stuffing detector
- Category defaults per puzzle type + audience

**Usage:**
```bash
python kdp-puzzle-publisher/scripts/kdp_listing_builder.py --input sample_listing_inputs.json
```

#### 17. Portfolio Planner (`kdp-puzzle-publisher/scripts/portfolio_planner.py`)

**Purpose:** Forecast expected monthly royalty and publishing schedule across a multi-SKU portfolio

**Features:**
- Power-law hit-rate model (home runs / winners / breakeven / duds)
- Weekly publishing schedule respects KDP's 3-per-day cap
- Months-to-breakeven against upfront per-SKU investment
- Per-niche expected royalty breakdown

**Usage:**
```bash
python kdp-puzzle-publisher/scripts/portfolio_planner.py --input sample_portfolio_inputs.json
```

## Quality Standards

**All business & growth Python tools must:**
- Use standard library only (no external dependencies)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for invalid input
- Return appropriate exit codes
- Process files locally (no API calls)
- Include argparse CLI with `--help` support

## Related Skills

- **Marketing:** Content creation, demand generation -> `../marketing-skill/`
- **Product Team:** User research, feature prioritization -> `../product-team/`
- **C-Level:** Strategic planning -> `../c-level-advisor/`
- **Engineering:** Technical implementation -> `../engineering-team/`

---

**Last Updated:** April 2026
**Skills Deployed:** 5/5 business & growth skills production-ready
**Total Tools:** 13 Python automation tools
