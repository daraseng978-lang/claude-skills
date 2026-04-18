#!/usr/bin/env python3
"""
Firm Scaffolder

Scaffolds a new zero-human trading firm workspace: role instruction
stubs, empty ledger, risk policy, issue templates, and a FIRM.md
with your chosen venue and constraints.

Usage:
    python firm_init.py --name "Lewis Ventures" --venue bittensor --out ./my-firm
    python firm_init.py --name "Acme Quant" --venue equities --out ./acme
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


ROLES = [
    ("ceo", "CEO", "Hires and fires. Sets quarterly priorities. Reads daily research and P&L reports. Escalates capital requests to the founder."),
    ("research_engineer", "Research Engineer", "Picks backtest library, data sources, infrastructure. Owns data pipeline. Keeps research reproducible."),
    ("strategy_researcher", "Strategy Researcher", "Reads papers, transcripts, forums, GitHub. Proposes strategies with hypothesis + source + expected edge."),
    ("backtest_engineer", "Backtest Engineer", "Implements proposed strategies. Enforces hygiene: no lookahead, OOS split, walk-forward, realistic fees and slippage."),
    ("red_team", "Red Team", "Breaks every strategy before risk signs off. Hunts for overfit, survivorship, regime dependence, dataset artifacts. Distinct identity from risk_officer."),
    ("risk_officer", "Risk Officer", "Owns hard constraints. Signs off (or not) on paper->live. Triggers circuit breaker on drawdown. Distinct identity from red_team."),
    ("execution_engineer", "Execution Engineer", "Order routing, slippage tracking, fail-safes. Never owns risk limits."),
    ("accountant", "Accountant", "Immutable daily P&L, tax lots, exportable ledger. Weekly reconciliation. Drafts the monthly founder report."),
    ("report_reviewer", "Report Reviewer (self-eval)", "Reviews the monthly founder report for honesty. Catches score inflation before it reaches the founder."),
]


ROLE_INSTRUCTION_TEMPLATE = """# {title}

## Identity
{description}

## What good looks like
- [Fill this in with 5-10 concrete examples of excellent work for this role]
- [Specific rubrics, anti-patterns you've seen, style preferences]
- [If this role outputs reports, include a sample good one]

## Tools this role uses
- [Link to scripts/ or external tools]

## Success metrics
- [2-3 measurable outputs the role is accountable for]

## Escalation
- Blocks on: [who signs off]
- Notifies on: [what triggers a ping to the CEO or Risk Officer]
"""


RISK_POLICY_DEFAULT = {
    "description": "Founder-mode conservative policy. Edit before going live.",
    "mode": "founder_autonomous",
    "max_position_pct": 0.05,
    "max_gross_exposure": 1.0,
    "max_net_exposure": 0.75,
    "max_leverage": 1.0,
    "max_daily_drawdown": 0.03,
    "max_weekly_drawdown": 0.06,
    "max_monthly_drawdown": 0.10,
    "firm_kill_switch_monthly_pct": 0.15,
    "per_asset_caps": {},
    "venue_whitelist": [],
}


FIRM_MD_TEMPLATE = """# {name}

An autonomous trading firm.

- **Created:** {created}
- **Venue:** {venue}
- **Status:** Phase 1 — firm setup

## Roles
{role_list}

## Operating principles
1. Start small, grow by need.
2. LLMs cannot own hard risk limits.
3. Taste is the product.
4. Paper before live, always.

## Daily rhythm
- 00:00 UTC: Research Agent nightly digest
- 06:00 UTC: Backtest Engineer picks up new `proposed` ideas
- 12:00 UTC: Red Team review window
- 18:00 UTC: Accountant daily P&L report

## Key files
- `FIRM.md` — this file
- `strategy_ledger.json` — institutional memory of every idea
- `risk_policy.json` — hard constraints
- `roles/` — per-role instruction files (fill these out!)
- `daily_reports/` — where research digests land
"""


ORG_CHART = {
    "version": 1,
    "description": "Importable org structure for agent orchestration frameworks",
    "org": {
        "board": ["human"],
        "reports_to_board": ["ceo"],
        "reports_to_ceo": ["cto_research_engineer", "risk_officer", "accountant"],
        "reports_to_cto": ["strategy_researcher", "backtest_engineer", "red_team", "execution_engineer"],
    },
    "roles": [
        {"key": key, "title": title, "responsibility": desc}
        for key, title, desc in ROLES
    ],
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def scaffold(name: str, venue: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)

    role_list = "\n".join(f"- **{title}** — {desc}" for _, title, desc in ROLES)
    firm_md = FIRM_MD_TEMPLATE.format(
        name=name,
        created=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        venue=venue,
        role_list=role_list,
    )
    write(out / "FIRM.md", firm_md)

    for key, title, desc in ROLES:
        write(
            out / "roles" / f"{key}.md",
            ROLE_INSTRUCTION_TEMPLATE.format(title=title, description=desc),
        )

    write(
        out / "risk_policy.json",
        json.dumps(RISK_POLICY_DEFAULT, indent=2),
    )
    write(
        out / "strategy_ledger.json",
        json.dumps({"version": 1, "strategies": [], "events": []}, indent=2),
    )
    write(
        out / "capital_ledger.json",
        json.dumps({
            "version": 1,
            "base_currency": "USD",
            "tranches": [],
            "allocations": [],
            "pnl_events": [],
            "withdrawals": [],
        }, indent=2),
    )
    write(
        out / "org_chart.json",
        json.dumps(ORG_CHART, indent=2),
    )
    (out / "daily_reports").mkdir(exist_ok=True)
    (out / "research").mkdir(exist_ok=True)
    (out / "postmortems").mkdir(exist_ok=True)
    (out / "postmortems" / "redteam").mkdir(exist_ok=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold a new zero-human trading firm workspace")
    p.add_argument("--name", required=True, help="firm name")
    p.add_argument("--venue", required=True, help="trading venue (equities, crypto, bittensor, hyperliquid, etc.)")
    p.add_argument("--out", required=True, help="output directory")
    args = p.parse_args()

    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        print(f"ERROR: output directory {out} is not empty", file=sys.stderr)
        return 2

    scaffold(args.name, args.venue, out)
    print(f"firm scaffolded at {out}")
    print("next steps:")
    print(f"  1. cd {out}")
    print(f"  2. edit roles/*.md to fill in taste and rubrics")
    print(f"  3. edit risk_policy.json to set hard constraints")
    print(f"  4. import org_chart.json into your agent framework")
    return 0


if __name__ == "__main__":
    sys.exit(main())
