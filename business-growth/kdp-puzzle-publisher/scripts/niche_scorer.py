#!/usr/bin/env python3
"""
niche_scorer.py — Score a KDP puzzle-book niche against public Amazon signals.

Input: a JSON file with the top ~10 competitor listings for your candidate
niche. Each competitor supplies BSR, price, review count, review rating,
publish date, and whether it's a large-publisher title. The script computes
demand, competition, pricing, and freshness signals, and returns an overall
0–100 score plus a verdict.

Standard library only. No network calls.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date
from typing import Dict, List


def _median(values: List[float]) -> float:
    return statistics.median(values) if values else 0.0


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def score_demand(bsr_median: float) -> float:
    """Lower BSR = more demand. Map median-top-10 BSR to 0–100."""
    if bsr_median <= 0:
        return 0.0
    if bsr_median <= 20_000:
        return 100.0
    if bsr_median >= 500_000:
        return 0.0
    # log-linear falloff between 20k and 500k
    import math
    lo, hi = math.log(20_000), math.log(500_000)
    x = math.log(bsr_median)
    return round(_clip(100 * (hi - x) / (hi - lo), 0.0, 100.0), 1)


def score_competition(review_median: float, big_pub_share: float) -> float:
    """High reviews + many big publishers = harder. Return 0–100 where 100 is
    easy (low competition)."""
    # Reviews: 0 reviews = 100, 3000+ reviews = 0, log falloff.
    import math
    if review_median <= 10:
        review_ease = 100.0
    elif review_median >= 3000:
        review_ease = 0.0
    else:
        lo, hi = math.log(10), math.log(3000)
        review_ease = _clip(100 * (hi - math.log(review_median)) / (hi - lo), 0.0, 100.0)
    # Big-publisher share penalty (0.0 = none, 1.0 = all). 30%+ hurts.
    pub_ease = _clip(100 * (1 - big_pub_share / 0.3), 0.0, 100.0)
    return round(0.7 * review_ease + 0.3 * pub_ease, 1)


def score_pricing(price_median: float) -> float:
    """Sweet spot is $7.99–$10.99 for paperback puzzle books."""
    if 7.99 <= price_median <= 10.99:
        return 100.0
    if price_median < 5.99 or price_median > 14.99:
        return 20.0
    if price_median < 7.99:
        # below sweet spot, mild penalty
        return round(60 + (price_median - 5.99) / (7.99 - 5.99) * 40, 1)
    # price_median > 10.99
    return round(100 - (price_median - 10.99) / (14.99 - 10.99) * 80, 1)


def score_freshness(days_since_publish_median: float) -> float:
    """If every top listing is >3 years old, you have an opening. If they
    all just launched this month, expect aggressive new entrants."""
    if days_since_publish_median <= 0:
        return 50.0
    if days_since_publish_median >= 1095:  # 3+ years
        return 100.0
    if days_since_publish_median <= 60:
        return 20.0
    return round(20 + (days_since_publish_median - 60) / (1095 - 60) * 80, 1)


def days_between(iso_date: str, today: date) -> int:
    y, m, d = [int(p) for p in iso_date.split("-")]
    return (today - date(y, m, d)).days


def analyze(inputs: Dict) -> Dict:
    niche = inputs["niche"]
    comps = inputs.get("competitors", [])
    if not comps:
        raise ValueError("At least one competitor required under 'competitors'")

    today = date.fromisoformat(inputs.get("as_of", date.today().isoformat()))
    bsrs = [c["bsr"] for c in comps]
    reviews = [c.get("reviews", 0) for c in comps]
    prices = [c.get("price", 0) for c in comps]
    ages = [days_between(c["published"], today) for c in comps if c.get("published")]
    big_pub_share = sum(1 for c in comps if c.get("big_publisher")) / len(comps)

    bsr_median = _median(bsrs)
    review_median = _median(reviews)
    price_median = _median(prices)
    age_median = _median(ages) if ages else 365.0

    s_demand = score_demand(bsr_median)
    s_comp = score_competition(review_median, big_pub_share)
    s_price = score_pricing(price_median)
    s_fresh = score_freshness(age_median)

    overall = round(0.40 * s_demand + 0.30 * s_comp + 0.15 * s_price + 0.15 * s_fresh, 1)

    if overall >= 75:
        verdict = "GO — strong niche, build 3 SKU test batch"
    elif overall >= 55:
        verdict = "CONDITIONAL — test with 1 SKU before scaling"
    else:
        verdict = "PASS — keep searching"

    recs = []
    if s_demand < 50:
        recs.append("Demand is weak. Consider a broader niche or different age segment.")
    if s_comp < 50:
        recs.append("High review counts in top 10 — differentiate on format, size, or theme.")
    if s_price < 60:
        recs.append(f"Price median ${price_median:.2f} is outside the $7.99–$10.99 sweet spot.")
    if s_fresh < 50:
        recs.append("Top listings are very recent — expect competitive pressure.")
    if big_pub_share > 0.3:
        recs.append(f"{int(big_pub_share*100)}% of top 10 are big publishers — hard to rank.")
    if not recs:
        recs.append("No red flags. Proceed with listing draft and brief.")

    return {
        "niche": niche,
        "score_0_100": overall,
        "verdict": verdict,
        "signals": {
            "bsr_median": round(bsr_median, 0),
            "review_median": round(review_median, 0),
            "price_median": round(price_median, 2),
            "age_median_days": round(age_median, 0),
            "big_publisher_share": round(big_pub_share, 2),
        },
        "sub_scores": {
            "demand": s_demand,
            "competition": s_comp,
            "pricing": s_price,
            "freshness": s_fresh,
        },
        "saturation_flag": s_comp < 40,
        "seasonality_flag": inputs.get("seasonal", False),
        "recommendations": recs,
    }


def render_text(r: Dict) -> str:
    lines = []
    lines.append(f"Niche: {r['niche']}")
    lines.append(f"Score: {r['score_0_100']}/100  →  {r['verdict']}")
    lines.append("-" * 56)
    s = r["signals"]
    lines.append(f"  BSR median           {int(s['bsr_median']):>10,}")
    lines.append(f"  Review median        {int(s['review_median']):>10,}")
    lines.append(f"  Price median         ${s['price_median']:>9.2f}")
    lines.append(f"  Listing age (days)   {int(s['age_median_days']):>10,}")
    lines.append(f"  Big publisher share  {s['big_publisher_share']*100:>9.0f}%")
    lines.append("")
    lines.append("Sub-scores (0–100):")
    ss = r["sub_scores"]
    lines.append(f"  Demand        {ss['demand']:>6}")
    lines.append(f"  Competition   {ss['competition']:>6}")
    lines.append(f"  Pricing       {ss['pricing']:>6}")
    lines.append(f"  Freshness     {ss['freshness']:>6}")
    lines.append("")
    lines.append("Recommendations:")
    for rec in r["recommendations"]:
        lines.append(f"  • {rec}")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Score a KDP puzzle-book niche.")
    p.add_argument("--input", required=True, help="Path to JSON input (see assets/sample_niche_inputs.json)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    with open(args.input) as f:
        data = json.load(f)

    result = analyze(data)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
