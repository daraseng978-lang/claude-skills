#!/usr/bin/env python3
"""MRR forecaster: cohort-based projection to $10k / $50k / $100k milestones.

Simulates monthly cohorts with gross adds, logo churn, and net expansion.
Standard library only.

Usage:
    python mrr_forecaster.py --input sample_mrr_inputs.json --format text
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field


@dataclass
class Inputs:
    starting_mrr: float
    starting_customers: int
    average_price: float
    monthly_gross_adds: int  # new customers/month
    gross_adds_growth_rate: float  # e.g. 0.08 = 8% MoM growth in adds
    monthly_logo_churn: float  # 0..1
    monthly_net_expansion: float  # 0..1
    months_to_simulate: int = 24
    milestones: list[int] = field(default_factory=lambda: [10_000, 50_000, 100_000])


@dataclass
class MonthState:
    month: int
    gross_adds: int
    cumulative_customers: int
    churned_this_month: float
    mrr: float
    net_new_mrr: float


def simulate(inp: Inputs) -> list[MonthState]:
    customers = float(inp.starting_customers)
    mrr = inp.starting_mrr
    adds = float(inp.monthly_gross_adds)
    history: list[MonthState] = []
    prev_mrr = mrr

    for m in range(1, inp.months_to_simulate + 1):
        churned = customers * inp.monthly_logo_churn
        customers -= churned
        customers += adds
        # MRR evolves: existing base churns and expands, new cohort comes in at avg price
        mrr = mrr * (1 - inp.monthly_logo_churn) * (1 + inp.monthly_net_expansion)
        mrr += adds * inp.average_price
        net_new = mrr - prev_mrr
        history.append(
            MonthState(
                month=m,
                gross_adds=int(round(adds)),
                cumulative_customers=int(round(customers)),
                churned_this_month=round(churned, 2),
                mrr=round(mrr, 2),
                net_new_mrr=round(net_new, 2),
            )
        )
        prev_mrr = mrr
        adds *= 1 + inp.gross_adds_growth_rate

    return history


def find_milestones(history: list[MonthState], milestones: list[int]) -> dict[int, int | None]:
    out: dict[int, int | None] = {}
    for target in milestones:
        hit = next((h.month for h in history if h.mrr >= target), None)
        out[target] = hit
    return out


def render_text(inp: Inputs, history: list[MonthState], hits: dict[int, int | None]) -> str:
    lines = [
        "=" * 76,
        "MRR FORECAST",
        "=" * 76,
        f"Starting MRR: ${inp.starting_mrr:,.0f}  |  Customers: {inp.starting_customers}  "
        f"|  Avg price: ${inp.average_price:,.0f}",
        f"Adds/mo: {inp.monthly_gross_adds} @ {inp.gross_adds_growth_rate:+.1%} MoM  "
        f"|  Churn: {inp.monthly_logo_churn:.1%}  "
        f"|  Net expansion: {inp.monthly_net_expansion:+.1%}",
        "",
        f"{'Mo':>3} {'Adds':>6} {'Cust':>6} {'MRR':>12} {'Net New':>12}",
        "-" * 76,
    ]
    # Print every month for first 12, then every 3 months
    for h in history:
        if h.month <= 12 or h.month % 3 == 0:
            lines.append(
                f"{h.month:>3} {h.gross_adds:>6} {h.cumulative_customers:>6} "
                f"${h.mrr:>10,.0f} ${h.net_new_mrr:>10,.0f}"
            )

    lines.append("")
    lines.append("Milestone hits:")
    for target, month in hits.items():
        if month:
            lines.append(f"  ${target:>7,} MRR  ──►  Month {month}")
        else:
            lines.append(
                f"  ${target:>7,} MRR  ──►  not reached in {inp.months_to_simulate} months"
            )

    # Flag concerns
    lines.append("")
    final = history[-1]
    trailing_3 = sum(h.net_new_mrr for h in history[-3:]) / 3
    lines.append(
        f"End state (M{final.month}): ${final.mrr:,.0f} MRR, "
        f"{final.cumulative_customers} customers, "
        f"trailing-3mo avg net-new: ${trailing_3:,.0f}/mo"
    )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Forecast MRR growth via cohort simulation.")
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
            starting_mrr=float(raw.get("starting_mrr", 0)),
            starting_customers=int(raw.get("starting_customers", 0)),
            average_price=float(raw["average_price"]),
            monthly_gross_adds=int(raw["monthly_gross_adds"]),
            gross_adds_growth_rate=float(raw.get("gross_adds_growth_rate", 0.0)),
            monthly_logo_churn=float(raw["monthly_logo_churn"]),
            monthly_net_expansion=float(raw.get("monthly_net_expansion", 0.0)),
            months_to_simulate=int(raw.get("months_to_simulate", 24)),
            milestones=list(raw.get("milestones", [10_000, 50_000, 100_000])),
        )
    except (KeyError, ValueError) as e:
        print(f"Error in inputs: {e}", file=sys.stderr)
        return 2

    if inp.months_to_simulate < 1 or inp.months_to_simulate > 120:
        print("Error: months_to_simulate must be between 1 and 120", file=sys.stderr)
        return 2

    history = simulate(inp)
    hits = find_milestones(history, inp.milestones)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "inputs": inp.__dict__,
                    "history": [h.__dict__ for h in history],
                    "milestones": hits,
                },
                indent=2,
            )
        )
    else:
        print(render_text(inp, history, hits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
