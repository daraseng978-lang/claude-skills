#!/usr/bin/env python3
"""
bsr_to_revenue.py — Estimate daily sales and monthly royalty from an Amazon
Best Seller Rank (BSR) for the Books category.

This uses a piecewise power-law fit derived from publicly reported data
(Kindlepreneur / K-lytics style curves). It is an estimate, not a guarantee.
Use it to rank competitors, not to forecast your own revenue.

Standard library only. No network calls. No LLM calls.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict


# Piecewise BSR → sales/day curve for Amazon Books.
# Anchors (BSR, sales/day) — widely cited public estimates; smoothed with
# log-log interpolation between points.
ANCHORS = [
    (1, 4500),
    (10, 2800),
    (100, 900),
    (1_000, 180),
    (5_000, 50),
    (10_000, 25),
    (25_000, 10),
    (50_000, 5),
    (100_000, 2),
    (250_000, 0.7),
    (500_000, 0.25),
    (1_000_000, 0.08),
    (2_500_000, 0.02),
]


def estimate_sales_per_day(bsr: int) -> float:
    """Log-log interpolation between anchor points."""
    if bsr <= ANCHORS[0][0]:
        return float(ANCHORS[0][1])
    if bsr >= ANCHORS[-1][0]:
        # Extrapolate downward with the last segment's slope.
        (x1, y1), (x2, y2) = ANCHORS[-2], ANCHORS[-1]
        slope = (math.log(y2) - math.log(y1)) / (math.log(x2) - math.log(x1))
        return math.exp(math.log(y2) + slope * (math.log(bsr) - math.log(x2)))

    for (x1, y1), (x2, y2) in zip(ANCHORS, ANCHORS[1:]):
        if x1 <= bsr <= x2:
            slope = (math.log(y2) - math.log(y1)) / (math.log(x2) - math.log(x1))
            return math.exp(math.log(y1) + slope * (math.log(bsr) - math.log(x1)))
    return 0.0


def estimate_royalty(price: float, print_cost: float, royalty_rate: float) -> float:
    """KDP paperback: royalty = price * rate - print_cost. Floor at 0."""
    return max(0.0, price * royalty_rate - print_cost)


def confidence_label(bsr: int) -> str:
    if bsr <= 100:
        return "low"  # extreme top, curve is noisy
    if bsr <= 100_000:
        return "medium"
    return "low"  # long-tail is very noisy


def build(bsr: int, price: float, print_cost: float, royalty_rate: float) -> Dict:
    sales_per_day = estimate_sales_per_day(bsr)
    sales_per_month = sales_per_day * 30
    royalty_per_unit = estimate_royalty(price, print_cost, royalty_rate)
    monthly_royalty = sales_per_month * royalty_per_unit
    return {
        "bsr": bsr,
        "price": round(price, 2),
        "print_cost": round(print_cost, 2),
        "royalty_rate": royalty_rate,
        "royalty_per_unit": round(royalty_per_unit, 2),
        "est_sales_per_day": round(sales_per_day, 2),
        "est_sales_per_month": round(sales_per_month, 1),
        "est_monthly_royalty_usd": round(monthly_royalty, 2),
        "est_annual_royalty_usd": round(monthly_royalty * 12, 2),
        "confidence": confidence_label(bsr),
    }


def render_text(result: Dict) -> str:
    lines = []
    lines.append(f"BSR #{result['bsr']:,}  @  ${result['price']:.2f}")
    lines.append("-" * 48)
    lines.append(f"  Royalty per unit       ${result['royalty_per_unit']:>7.2f}")
    lines.append(f"  Est. sales / day       {result['est_sales_per_day']:>8.2f}")
    lines.append(f"  Est. sales / month     {result['est_sales_per_month']:>8.1f}")
    lines.append(f"  Est. monthly royalty   ${result['est_monthly_royalty_usd']:>7.2f}")
    lines.append(f"  Est. annual royalty    ${result['est_annual_royalty_usd']:>7.2f}")
    lines.append(f"  Confidence             {result['confidence']}")
    lines.append("")
    lines.append("Estimates use a log-log fit of public BSR curves.")
    lines.append("Use for relative ranking, not absolute forecasts.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Estimate KDP royalty from Amazon BSR.")
    p.add_argument("--bsr", type=int, required=True, help="Amazon Books BSR (e.g. 12450)")
    p.add_argument("--price", type=float, default=8.99, help="List price in USD")
    p.add_argument("--print-cost", type=float, default=2.65,
                   help="KDP paperback print cost (110 pages b&w default)")
    p.add_argument("--royalty-rate", type=float, default=0.60,
                   help="Royalty rate (0.60 paperback, 0.70 Kindle eligible)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    if args.bsr < 1:
        p.error("--bsr must be >= 1")
    if args.price <= 0:
        p.error("--price must be > 0")

    result = build(args.bsr, args.price, args.print_cost, args.royalty_rate)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
