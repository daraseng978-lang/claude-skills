#!/usr/bin/env python3
"""
portfolio_planner.py — Plan a quarterly KDP publishing portfolio.

Takes your cost/capacity inputs and a set of niches with expected per-SKU
royalty. Models a realistic hit rate (portfolio power law: a few winners
carry the P&L) and returns an expected monthly royalty, publishing schedule
respecting Amazon's ~3-titles-per-day limit, and investment required.

Standard library only. No LLM calls.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, List


# Hit-rate distribution: out of 100 SKUs, this is the canonical shape.
# Empirically derived from published self-publisher retrospectives.
HIT_DISTRIBUTION = {
    "home_runs": (0.03, 4.0),   # 3% of SKUs earn 4x the median estimate
    "winners": (0.15, 1.5),     # 15% earn 1.5x
    "breakeven": (0.40, 0.6),   # 40% earn 0.6x
    "duds": (0.42, 0.1),        # 42% earn 0.1x
}


def _weighted_expected(base_royalty: float) -> float:
    return sum(share * multiplier * base_royalty
               for share, multiplier in HIT_DISTRIBUTION.values())


def schedule(total_skus: int, days_per_week: int, skus_per_day: int) -> List[Dict]:
    """Produce a weekly publishing schedule honoring Amazon's 3/day cap."""
    skus_per_day = min(skus_per_day, 3)
    skus_per_week = skus_per_day * days_per_week
    weeks = math.ceil(total_skus / skus_per_week) if skus_per_week else 0
    schedule = []
    remaining = total_skus
    for w in range(1, weeks + 1):
        this_week = min(skus_per_week, remaining)
        schedule.append({"week": w, "skus_published": this_week})
        remaining -= this_week
    return schedule


def plan(inputs: Dict) -> Dict:
    niches = inputs["niches"]  # list of {name, skus, base_royalty_per_month}
    cost_per_sku = inputs.get("cost_per_sku_usd", 12.0)  # cover art, proofs, tools
    days_per_week = inputs.get("publish_days_per_week", 5)
    skus_per_day = inputs.get("skus_per_day", 2)

    total_skus = sum(n["skus"] for n in niches)
    total_expected_royalty = 0.0
    by_niche = []

    for n in niches:
        per_sku_expected = _weighted_expected(n["base_royalty_per_month"])
        niche_expected = per_sku_expected * n["skus"]
        total_expected_royalty += niche_expected
        by_niche.append({
            "niche": n["name"],
            "skus": n["skus"],
            "base_royalty_per_sku": round(n["base_royalty_per_month"], 2),
            "expected_per_sku_per_month": round(per_sku_expected, 2),
            "expected_niche_per_month": round(niche_expected, 2),
        })

    expected_home_runs = round(total_skus * HIT_DISTRIBUTION["home_runs"][0], 1)
    expected_winners = round(total_skus * (HIT_DISTRIBUTION["home_runs"][0]
                                          + HIT_DISTRIBUTION["winners"][0]), 1)
    expected_duds = round(total_skus * HIT_DISTRIBUTION["duds"][0], 1)

    investment = round(total_skus * cost_per_sku, 2)
    # Breakeven month: month where cumulative royalty > investment
    months_to_breakeven = None
    cumulative = 0.0
    for m in range(1, 37):
        cumulative += total_expected_royalty
        if cumulative >= investment:
            months_to_breakeven = m
            break

    return {
        "total_skus": total_skus,
        "expected_home_runs": expected_home_runs,
        "expected_winners_or_better": expected_winners,
        "expected_duds": expected_duds,
        "expected_monthly_royalty_usd": round(total_expected_royalty, 2),
        "expected_annual_royalty_usd": round(total_expected_royalty * 12, 2),
        "upfront_investment_usd": investment,
        "months_to_breakeven": months_to_breakeven,
        "by_niche": by_niche,
        "publishing_schedule": schedule(total_skus, days_per_week, skus_per_day),
    }


def render_text(r: Dict) -> str:
    lines = []
    lines.append(f"Portfolio: {r['total_skus']} SKUs")
    lines.append("=" * 64)
    lines.append(f"  Expected home runs     {r['expected_home_runs']}")
    lines.append(f"  Expected winners+      {r['expected_winners_or_better']}")
    lines.append(f"  Expected duds          {r['expected_duds']}")
    lines.append(f"  Expected monthly royalty  ${r['expected_monthly_royalty_usd']:,.2f}")
    lines.append(f"  Expected annual royalty   ${r['expected_annual_royalty_usd']:,.2f}")
    lines.append(f"  Upfront investment        ${r['upfront_investment_usd']:,.2f}")
    bt = r["months_to_breakeven"]
    lines.append(f"  Months to breakeven       {bt if bt else '>36'}")
    lines.append("")
    lines.append("By niche:")
    for n in r["by_niche"]:
        lines.append(f"  {n['niche']:<40} {n['skus']:>3} SKUs  →  ${n['expected_niche_per_month']:>9,.2f}/mo")
    lines.append("")
    lines.append("Publishing schedule:")
    for w in r["publishing_schedule"][:12]:
        lines.append(f"  Week {w['week']:>2}: {w['skus_published']} SKUs")
    if len(r["publishing_schedule"]) > 12:
        lines.append(f"  … {len(r['publishing_schedule']) - 12} more weeks")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Plan a KDP publishing portfolio.")
    p.add_argument("--input", required=True, help="JSON portfolio input (see assets/sample_portfolio_inputs.json)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    with open(args.input) as f:
        data = json.load(f)
    result = plan(data)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
