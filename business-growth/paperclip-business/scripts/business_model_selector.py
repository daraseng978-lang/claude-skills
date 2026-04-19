#!/usr/bin/env python3
"""Business model selector: scores 5 candidate Claude-operated businesses
against founder constraints and returns a ranked recommendation.

Standard library only. Usage:
    python business_model_selector.py --input sample_business_inputs.json --format text
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(frozen=True)
class Candidate:
    key: str
    name: str
    base_scores: dict[str, int]  # 0..10
    notes: str
    min_capital: int  # USD
    time_to_first_dollar_weeks: int
    risk_profile: str  # "low" | "medium" | "high"
    requires_domain_expertise: bool


CANDIDATES: list[Candidate] = [
    Candidate(
        key="seo_content",
        name="AI SEO Content Subscription",
        base_scores={
            "automation_fit": 10,
            "buyer_clarity": 9,
            "margin_headroom": 9,
            "time_to_revenue": 9,
            "defensibility": 6,
        },
        notes="Clear buyer, high margin, fast to revenue; algorithm-risk is the main downside.",
        min_capital=1500,
        time_to_first_dollar_weeks=3,
        risk_profile="medium",
        requires_domain_expertise=False,
    ),
    Candidate(
        key="competitor_intel",
        name="Competitor Intelligence Reports",
        base_scores={
            "automation_fit": 9,
            "buyer_clarity": 8,
            "margin_headroom": 9,
            "time_to_revenue": 7,
            "defensibility": 7,
        },
        notes="Works best with deep vertical expertise. Low-moderate defensibility.",
        min_capital=2000,
        time_to_first_dollar_weeks=5,
        risk_profile="medium",
        requires_domain_expertise=True,
    ),
    Candidate(
        key="pr_review",
        name="Pull Request Review Subscription",
        base_scores={
            "automation_fit": 10,
            "buyer_clarity": 8,
            "margin_headroom": 7,
            "time_to_revenue": 6,
            "defensibility": 5,
        },
        notes="Crowded category. Only viable with aggressive niching.",
        min_capital=3000,
        time_to_first_dollar_weeks=8,
        risk_profile="medium",
        requires_domain_expertise=True,
    ),
    Candidate(
        key="lead_enrichment",
        name="Lead Enrichment + Personalized Outreach",
        base_scores={
            "automation_fit": 9,
            "buyer_clarity": 7,
            "margin_headroom": 5,
            "time_to_revenue": 7,
            "defensibility": 4,
        },
        notes="Margin squeezed by paid data sources. Regulatory care on outbound.",
        min_capital=5000,
        time_to_first_dollar_weeks=5,
        risk_profile="high",
        requires_domain_expertise=False,
    ),
    Candidate(
        key="newsletter_aas",
        name="Newsletter-as-a-Service",
        base_scores={
            "automation_fit": 9,
            "buyer_clarity": 6,
            "margin_headroom": 8,
            "time_to_revenue": 8,
            "defensibility": 4,
        },
        notes="Commoditized. Only works at the low end of the market.",
        min_capital=1500,
        time_to_first_dollar_weeks=4,
        risk_profile="low",
        requires_domain_expertise=False,
    ),
]


WEIGHTS = {
    "automation_fit": 0.30,
    "buyer_clarity": 0.20,
    "margin_headroom": 0.20,
    "time_to_revenue": 0.15,
    "defensibility": 0.15,
}


@dataclass
class Inputs:
    capital_usd: int
    monthly_time_budget_hours: float
    domain_expertise: str  # "none" | "some" | "deep"
    risk_tolerance: str  # "conservative" | "moderate" | "aggressive"
    geography: str  # "us" | "eu" | "global"
    industry_focus: str | None = None


@dataclass
class ScoredCandidate:
    key: str
    name: str
    raw_score: float
    adjusted_score: float
    eligible: bool
    adjustments: list[str] = field(default_factory=list)
    notes: str = ""


def score(candidate: Candidate, inp: Inputs) -> ScoredCandidate:
    raw = sum(candidate.base_scores[k] * w for k, w in WEIGHTS.items())
    adjusted = raw
    eligible = True
    adjustments: list[str] = []

    # Capital gate
    if inp.capital_usd < candidate.min_capital:
        eligible = False
        adjustments.append(
            f"Requires ~${candidate.min_capital:,} minimum capital "
            f"(you have ${inp.capital_usd:,})."
        )

    # Domain expertise
    if candidate.requires_domain_expertise and inp.domain_expertise == "none":
        adjusted -= 1.5
        adjustments.append("Penalty: requires domain expertise you lack.")
    elif candidate.requires_domain_expertise and inp.domain_expertise == "deep":
        adjusted += 0.8
        adjustments.append("Bonus: your deep domain expertise is a strong fit.")

    # Risk tolerance vs candidate risk
    risk_rank = {"low": 1, "medium": 2, "high": 3}
    tolerance_rank = {"conservative": 1, "moderate": 2, "aggressive": 3}
    if risk_rank[candidate.risk_profile] > tolerance_rank[inp.risk_tolerance]:
        adjusted -= 1.0
        adjustments.append("Penalty: risk profile exceeds your tolerance.")

    # Time budget — low time budgets favor simpler, more-automatable businesses
    if inp.monthly_time_budget_hours < 16 and candidate.base_scores["automation_fit"] < 9:
        adjusted -= 0.6
        adjustments.append("Penalty: low time budget requires higher automation fit.")

    # Geography caution on outbound-heavy candidates
    if candidate.key == "lead_enrichment" and inp.geography == "eu":
        adjusted -= 0.5
        adjustments.append("Penalty: stricter EU cold-outreach regulation.")

    return ScoredCandidate(
        key=candidate.key,
        name=candidate.name,
        raw_score=round(raw, 2),
        adjusted_score=round(max(adjusted, 0.0), 2),
        eligible=eligible,
        adjustments=adjustments,
        notes=candidate.notes,
    )


def rank(inp: Inputs) -> list[ScoredCandidate]:
    results = [score(c, inp) for c in CANDIDATES]
    results.sort(key=lambda r: (r.eligible, r.adjusted_score), reverse=True)
    return results


def render_text(results: list[ScoredCandidate], inp: Inputs) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append("PAPERCLIP BUSINESS — MODEL SELECTOR")
    lines.append("=" * 68)
    lines.append("")
    lines.append(
        f"Inputs: ${inp.capital_usd:,} capital | "
        f"{inp.monthly_time_budget_hours:g} hr/mo | "
        f"expertise={inp.domain_expertise} | "
        f"risk={inp.risk_tolerance} | geo={inp.geography}"
    )
    lines.append("")
    lines.append(f"{'Rank':<5} {'Business':<40} {'Score':>6} {'Eligible':>9}")
    lines.append("-" * 68)
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i:<5} {r.name[:40]:<40} {r.adjusted_score:>6.2f} "
            f"{'yes' if r.eligible else 'no':>9}"
        )
    lines.append("")
    top = next((r for r in results if r.eligible), None)
    if top:
        lines.append(f"RECOMMENDED: {top.name} (score {top.adjusted_score})")
        lines.append(f"Why: {top.notes}")
        if top.adjustments:
            lines.append("Adjustments applied:")
            for a in top.adjustments:
                lines.append(f"  - {a}")
    else:
        lines.append("No eligible candidates. Consider raising capital floor.")
    lines.append("")
    lines.append("Full breakdown:")
    for r in results:
        lines.append(f"  - {r.name}: raw={r.raw_score} adj={r.adjusted_score}")
        for a in r.adjustments:
            lines.append(f"      · {a}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Rank candidate Claude-operated businesses.")
    p.add_argument("--input", required=True, help="Path to JSON inputs file.")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    try:
        with open(args.input, encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.input}: {e}", file=sys.stderr)
        return 2

    try:
        inp = Inputs(
            capital_usd=int(raw["capital_usd"]),
            monthly_time_budget_hours=float(raw["monthly_time_budget_hours"]),
            domain_expertise=raw["domain_expertise"],
            risk_tolerance=raw["risk_tolerance"],
            geography=raw.get("geography", "global"),
            industry_focus=raw.get("industry_focus"),
        )
    except KeyError as e:
        print(f"Error: missing required input field: {e}", file=sys.stderr)
        return 2

    valid_expertise = {"none", "some", "deep"}
    valid_risk = {"conservative", "moderate", "aggressive"}
    if inp.domain_expertise not in valid_expertise:
        print(f"Error: domain_expertise must be one of {valid_expertise}", file=sys.stderr)
        return 2
    if inp.risk_tolerance not in valid_risk:
        print(f"Error: risk_tolerance must be one of {valid_risk}", file=sys.stderr)
        return 2

    results = rank(inp)

    if args.format == "json":
        payload = {
            "inputs": asdict(inp),
            "ranked": [asdict(r) for r in results],
            "recommended": next((r.key for r in results if r.eligible), None),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(results, inp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
