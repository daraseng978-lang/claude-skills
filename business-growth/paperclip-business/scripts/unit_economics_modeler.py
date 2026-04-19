#!/usr/bin/env python3
"""Unit economics modeler for a productized service business.

Computes gross margin, CAC, payback period, LTV, LTV:CAC, and break-even
customer count. Standard library only.

Usage:
    python unit_economics_modeler.py --input sample_unit_economics.json --format text
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass


@dataclass
class Inputs:
    tier_name: str
    monthly_price: float
    variable_cost_per_customer: float  # tokens, APIs, CMS, etc
    fixed_monthly_overhead: float  # tooling, subs
    blended_cac: float
    monthly_logo_churn: float  # 0..1
    monthly_net_expansion: float  # e.g. 0.015 = +1.5%/mo (negative if net contraction)


@dataclass
class Results:
    gross_margin: float
    contribution_per_customer_monthly: float
    ltv_months: float
    ltv_dollars: float
    payback_months: float
    ltv_to_cac: float
    breakeven_customers: int
    warnings: list[str]


def model(inp: Inputs) -> Results:
    warnings: list[str] = []

    if inp.monthly_price <= 0:
        raise ValueError("monthly_price must be > 0")
    if not (0 <= inp.monthly_logo_churn < 1):
        raise ValueError("monthly_logo_churn must be in [0, 1)")

    gross_margin = (inp.monthly_price - inp.variable_cost_per_customer) / inp.monthly_price
    contribution = inp.monthly_price - inp.variable_cost_per_customer

    # Effective churn includes net expansion dampening
    effective_churn = max(inp.monthly_logo_churn - max(inp.monthly_net_expansion, 0.0), 0.005)
    ltv_months = 1 / effective_churn if effective_churn > 0 else math.inf
    ltv_dollars = contribution * ltv_months

    payback_months = inp.blended_cac / contribution if contribution > 0 else math.inf
    ltv_to_cac = ltv_dollars / inp.blended_cac if inp.blended_cac > 0 else math.inf

    breakeven_customers = (
        math.ceil(inp.fixed_monthly_overhead / contribution) if contribution > 0 else -1
    )

    if gross_margin < 0.6:
        warnings.append(
            f"Gross margin {gross_margin:.0%} is below the 60% floor for a healthy productized service."
        )
    if payback_months > 3:
        warnings.append(
            f"Payback of {payback_months:.1f} months is too slow; target ≤ 3."
        )
    if ltv_to_cac < 3:
        warnings.append(
            f"LTV:CAC of {ltv_to_cac:.1f} is below the 3x minimum."
        )
    if inp.monthly_logo_churn > 0.06:
        warnings.append(
            f"Monthly churn of {inp.monthly_logo_churn:.1%} exceeds 6% — delivery or ICP issue."
        )

    return Results(
        gross_margin=gross_margin,
        contribution_per_customer_monthly=contribution,
        ltv_months=ltv_months,
        ltv_dollars=ltv_dollars,
        payback_months=payback_months,
        ltv_to_cac=ltv_to_cac,
        breakeven_customers=breakeven_customers,
        warnings=warnings,
    )


def render_text(inp: Inputs, r: Results) -> str:
    lines = [
        "=" * 64,
        "UNIT ECONOMICS MODEL",
        "=" * 64,
        f"Tier: {inp.tier_name}  |  Price: ${inp.monthly_price:,.0f}/mo",
        "",
        f"  Variable cost/customer:    ${inp.variable_cost_per_customer:,.2f}/mo",
        f"  Contribution margin:       ${r.contribution_per_customer_monthly:,.2f}/mo "
        f"({r.gross_margin:.1%} gross margin)",
        f"  Fixed overhead:            ${inp.fixed_monthly_overhead:,.2f}/mo",
        f"  Blended CAC:               ${inp.blended_cac:,.2f}",
        "",
        "  Customer lifetime (months): {:.1f}".format(r.ltv_months),
        f"  LTV (dollars):             ${r.ltv_dollars:,.0f}",
        f"  CAC payback:               {r.payback_months:.2f} months",
        f"  LTV : CAC ratio:           {r.ltv_to_cac:.1f} : 1",
        f"  Break-even customers:      {r.breakeven_customers}",
        "",
    ]
    if r.warnings:
        lines.append("WARNINGS:")
        for w in r.warnings:
            lines.append(f"  ! {w}")
    else:
        lines.append("No warnings. Economics look healthy.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Model unit economics for a productized service tier.")
    p.add_argument("--input", required=True)
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    try:
        with open(args.input, encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input: {e}", file=sys.stderr)
        return 2

    try:
        inp = Inputs(
            tier_name=raw["tier_name"],
            monthly_price=float(raw["monthly_price"]),
            variable_cost_per_customer=float(raw["variable_cost_per_customer"]),
            fixed_monthly_overhead=float(raw["fixed_monthly_overhead"]),
            blended_cac=float(raw["blended_cac"]),
            monthly_logo_churn=float(raw["monthly_logo_churn"]),
            monthly_net_expansion=float(raw.get("monthly_net_expansion", 0.0)),
        )
    except (KeyError, ValueError) as e:
        print(f"Error in inputs: {e}", file=sys.stderr)
        return 2

    try:
        r = model(inp)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(
            json.dumps(
                {
                    "inputs": inp.__dict__,
                    "results": {
                        "gross_margin": r.gross_margin,
                        "contribution_per_customer_monthly": r.contribution_per_customer_monthly,
                        "ltv_months": r.ltv_months,
                        "ltv_dollars": r.ltv_dollars,
                        "payback_months": r.payback_months,
                        "ltv_to_cac": r.ltv_to_cac,
                        "breakeven_customers": r.breakeven_customers,
                        "warnings": r.warnings,
                    },
                },
                indent=2,
            )
        )
    else:
        print(render_text(inp, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
