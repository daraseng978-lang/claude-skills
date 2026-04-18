# Finance Skills - Claude Code Guidance

This guide covers the finance skills and their Python automation tools.

## Finance Skills Overview

**Available Skills:**
1. **financial-analyst/** - Financial statement analysis, ratio analysis, DCF valuation, budgeting, forecasting (4 Python tools)
2. **saas-metrics-coach/** - SaaS financial health: ARR, MRR, churn, CAC, LTV, NRR, Quick Ratio, 12-month projections (3 Python tools)
3. **zero-human-trading-firm/** - Autonomous multi-agent quant trading firm: org chart, strategy lifecycle ledger, hygienic backtester, hard-coded risk policy enforcer, paper-to-live promotion gate (6 Python tools)

**Total Tools:** 13 Python automation tools, 10 knowledge bases, 11 templates

**Commands:** 2 (`/financial-health`, `/saas-health`)

## Python Automation Tools

### 1. Ratio Calculator (`financial-analyst/scripts/ratio_calculator.py`)

**Purpose:** Calculate and interpret financial ratios from statement data

**Features:**
- Profitability ratios (ROE, ROA, Gross/Operating/Net Margin)
- Liquidity ratios (Current, Quick, Cash)
- Leverage ratios (Debt-to-Equity, Interest Coverage, DSCR)
- Efficiency ratios (Asset/Inventory/Receivables Turnover, DSO)
- Valuation ratios (P/E, P/B, P/S, EV/EBITDA, PEG)
- Built-in interpretation and benchmarking

**Usage:**
```bash
python financial-analyst/scripts/ratio_calculator.py financial_data.json
python financial-analyst/scripts/ratio_calculator.py financial_data.json --format json
```

### 2. DCF Valuation (`financial-analyst/scripts/dcf_valuation.py`)

**Purpose:** Discounted Cash Flow enterprise and equity valuation

**Features:**
- Revenue and cash flow projections
- WACC calculation (CAPM-based)
- Terminal value (perpetuity growth and exit multiple methods)
- Enterprise and equity value derivation
- Two-way sensitivity analysis
- No external dependencies (uses math/statistics)

**Usage:**
```bash
python financial-analyst/scripts/dcf_valuation.py valuation_data.json
python financial-analyst/scripts/dcf_valuation.py valuation_data.json --format json
```

### 3. Budget Variance Analyzer (`financial-analyst/scripts/budget_variance_analyzer.py`)

**Purpose:** Analyze actual vs budget vs prior year performance

**Features:**
- Variance calculation (actual vs budget, actual vs prior year)
- Materiality threshold filtering
- Favorable/unfavorable classification
- Department and category breakdown

**Usage:**
```bash
python financial-analyst/scripts/budget_variance_analyzer.py budget_data.json
python financial-analyst/scripts/budget_variance_analyzer.py budget_data.json --format json
```

### 4. Forecast Builder (`financial-analyst/scripts/forecast_builder.py`)

**Purpose:** Driver-based revenue forecasting and cash flow projection

**Features:**
- Driver-based revenue forecast model
- 13-week cash flow projection
- Scenario modeling (base/bull/bear)
- Trend analysis from historical data

**Usage:**
```bash
python financial-analyst/scripts/forecast_builder.py forecast_data.json
python financial-analyst/scripts/forecast_builder.py forecast_data.json --format json
```

## Zero-Human Trading Firm Tools

### Strategy Ledger (`zero-human-trading-firm/scripts/strategy_ledger.py`)
Append-only ledger tracking every strategy through `proposed -> backtested -> red_teamed -> ready_for_paper -> paper -> live -> retired`. Includes sign-off flags for red team and risk officer.

### Backtest Runner (`zero-human-trading-firm/scripts/backtest_runner.py`)
Causal backtester with SMA/EMA cross and mean-revert templates. Enforces in-sample / out-of-sample split, realistic fees and slippage. Standard library only.

### Risk Policy Enforcer (`zero-human-trading-firm/scripts/risk_policy_enforcer.py`)
Deterministic order-level policy check. Agents cannot own this service — host behind an API they can call but cannot deploy to.

### Research Synthesizer (`zero-human-trading-firm/scripts/research_synthesizer.py`)
Deterministic keyword + density ranking over a directory of research files (transcripts, notes, papers).

### Execution Gate (`zero-human-trading-firm/scripts/execution_gate.py`)
Paper-to-live promotion checker. Defaults: min 30 trades, Sharpe >= 1.0, max drawdown <= 10%, both sign-offs present.

### Firm Scaffolder (`zero-human-trading-firm/scripts/firm_init.py`)
Creates a new firm workspace with role instruction stubs, empty ledger, starter risk policy, and importable org chart JSON.

```bash
python zero-human-trading-firm/scripts/firm_init.py --name "Lewis Ventures" --venue bittensor --out ./my-firm
```

## Quality Standards

**All finance Python tools must:**
- Use standard library only (math, statistics, json, argparse)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for invalid input
- Return appropriate exit codes
- Process files locally (no API calls)
- Include argparse CLI with `--help` support

## Related Skills

- **C-Level:** Strategic financial decision-making -> `../c-level-advisor/`
- **Business & Growth:** Revenue operations, sales metrics -> `../business-growth/`
- **Product Team:** Budget allocation, RICE scoring -> `../product-team/`

---

**Last Updated:** April 2026
**Skills Deployed:** 3/3 finance skills production-ready
**Total Tools:** 13 Python automation tools
**Commands:** /financial-health, /saas-health
