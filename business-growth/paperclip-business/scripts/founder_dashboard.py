#!/usr/bin/env python3
"""Founder weekly dashboard: single digest the founder reads each Monday.

Takes the current business state and produces a prioritized list of:
  - MRR delta vs last week
  - Pipeline health
  - Churn events
  - Red flags
  - Decisions requiring the founder

Standard library only.

Usage:
    python founder_dashboard.py --input sample_weekly_state.json --format text
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field


@dataclass
class Decision:
    topic: str
    urgency: str  # "critical" | "high" | "standard"
    options: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class WeeklyState:
    week_ending: str
    mrr_current: float
    mrr_last_week: float
    mrr_4_weeks_ago: float
    new_logos_this_week: int
    churned_logos_this_week: int
    pipeline_value: float
    quota_this_month: float
    meetings_booked: int
    meetings_held: int
    close_rate_trailing_4wk: float
    cash_balance: float
    monthly_burn: float
    delivery_sla_miss_count: int
    cold_email_spam_rate: float
    customer_concentration_top1: float  # fraction of MRR from top customer
    escalations: list[dict] = field(default_factory=list)


@dataclass
class RedFlag:
    severity: str  # "critical" | "high" | "medium"
    message: str


def growth_rate(current: float, past: float) -> float:
    if past <= 0:
        return 0.0
    return (current - past) / past


def red_flags(s: WeeklyState) -> list[RedFlag]:
    flags: list[RedFlag] = []

    wow = s.mrr_current - s.mrr_last_week
    mom = growth_rate(s.mrr_current, s.mrr_4_weeks_ago)

    if wow < 0:
        flags.append(RedFlag("high", f"MRR declined ${abs(wow):,.0f} WoW."))
    if mom < 0:
        flags.append(RedFlag("critical", f"MRR declined {mom:.1%} vs 4 weeks ago."))

    if s.delivery_sla_miss_count > 0:
        sev = "critical" if s.delivery_sla_miss_count > 3 else "high"
        flags.append(
            RedFlag(sev, f"{s.delivery_sla_miss_count} delivery SLA misses this week.")
        )

    if s.cold_email_spam_rate > 0.001:
        flags.append(
            RedFlag(
                "critical",
                f"Cold email spam rate {s.cold_email_spam_rate:.3%} exceeds 0.1% ceiling.",
            )
        )

    if s.customer_concentration_top1 > 0.15:
        flags.append(
            RedFlag(
                "high",
                f"Top customer is {s.customer_concentration_top1:.0%} of MRR — concentration risk.",
            )
        )

    if s.monthly_burn > 0 and s.cash_balance > 0:
        runway_months = s.cash_balance / s.monthly_burn
        if runway_months < 6:
            flags.append(
                RedFlag("critical", f"Runway is {runway_months:.1f} months (< 6).")
            )

    if s.close_rate_trailing_4wk > 0.40:
        flags.append(
            RedFlag(
                "medium",
                f"Close rate {s.close_rate_trailing_4wk:.0%} > 40% — likely underpriced.",
            )
        )
    elif s.close_rate_trailing_4wk < 0.10 and s.meetings_held >= 5:
        flags.append(
            RedFlag(
                "medium",
                f"Close rate {s.close_rate_trailing_4wk:.0%} < 10% — messaging or ICP issue.",
            )
        )

    if s.churned_logos_this_week > 0 and s.new_logos_this_week == 0:
        flags.append(
            RedFlag(
                "high",
                f"{s.churned_logos_this_week} logo(s) churned with 0 new logos this week.",
            )
        )

    return flags


def render_text(s: WeeklyState) -> str:
    wow_delta = s.mrr_current - s.mrr_last_week
    mom_pct = growth_rate(s.mrr_current, s.mrr_4_weeks_ago)
    pipeline_coverage = s.pipeline_value / s.quota_this_month if s.quota_this_month else 0
    meeting_show_rate = (
        s.meetings_held / s.meetings_booked if s.meetings_booked else 0
    )
    runway = (
        s.cash_balance / s.monthly_burn if s.monthly_burn > 0 else float("inf")
    )

    lines = [
        "=" * 72,
        f"FOUNDER DASHBOARD — week ending {s.week_ending}",
        "=" * 72,
        "",
        "THE NUMBER",
        "-" * 72,
        f"  MRR:            ${s.mrr_current:>10,.0f}",
        f"  Δ WoW:          ${wow_delta:>+10,.0f}",
        f"  Δ vs 4w ago:    {mom_pct:>+10.1%}",
        "",
        "LOGOS",
        "-" * 72,
        f"  New this week:     {s.new_logos_this_week:>4}",
        f"  Churned this week: {s.churned_logos_this_week:>4}",
        "",
        "PIPELINE",
        "-" * 72,
        f"  Pipeline value:       ${s.pipeline_value:>12,.0f}",
        f"  Coverage vs quota:    {pipeline_coverage:>12.1f}x  (target ≥ 3x)",
        f"  Meetings booked:      {s.meetings_booked:>12}",
        f"  Meetings held:        {s.meetings_held:>12}  "
        f"({meeting_show_rate:.0%} show rate)",
        f"  Close rate (T4W):     {s.close_rate_trailing_4wk:>12.0%}",
        "",
        "FINANCIAL",
        "-" * 72,
        f"  Cash balance:       ${s.cash_balance:>12,.0f}",
        f"  Monthly burn:       ${s.monthly_burn:>12,.0f}",
        f"  Runway:             {runway:>12.1f} months"
        if runway != float("inf")
        else "  Runway:                    profitable",
        "",
    ]

    flags = red_flags(s)
    critical = [f for f in flags if f.severity == "critical"]
    high = [f for f in flags if f.severity == "high"]
    medium = [f for f in flags if f.severity == "medium"]

    lines.append("RED FLAGS")
    lines.append("-" * 72)
    if not flags:
        lines.append("  None this week.")
    else:
        for f in critical:
            lines.append(f"  [CRITICAL] {f.message}")
        for f in high:
            lines.append(f"  [HIGH]     {f.message}")
        for f in medium:
            lines.append(f"  [MEDIUM]   {f.message}")
    lines.append("")

    lines.append("DECISIONS FOR FOUNDER")
    lines.append("-" * 72)
    if not s.escalations:
        lines.append("  No escalations. Stay out of the agents' way.")
    else:
        for e in s.escalations:
            lines.append(
                f"  [{e.get('urgency', 'standard').upper()}] {e.get('topic', '(no topic)')}"
            )
            for opt in e.get("options", []):
                lines.append(f"      · {opt}")
            if e.get("recommendation"):
                lines.append(f"      → Recommendation: {e['recommendation']}")
    lines.append("")

    lines.append("THE 3 QUESTIONS")
    lines.append("-" * 72)
    lines.append("  1. Is trailing-4-week MRR growth accelerating?")
    lines.append("  2. Am I spending > 4 hours this week? Where?")
    lines.append("  3. What's the one decision I've been avoiding?")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate the weekly founder dashboard.")
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
        s = WeeklyState(
            week_ending=raw["week_ending"],
            mrr_current=float(raw["mrr_current"]),
            mrr_last_week=float(raw["mrr_last_week"]),
            mrr_4_weeks_ago=float(raw["mrr_4_weeks_ago"]),
            new_logos_this_week=int(raw["new_logos_this_week"]),
            churned_logos_this_week=int(raw["churned_logos_this_week"]),
            pipeline_value=float(raw["pipeline_value"]),
            quota_this_month=float(raw["quota_this_month"]),
            meetings_booked=int(raw["meetings_booked"]),
            meetings_held=int(raw["meetings_held"]),
            close_rate_trailing_4wk=float(raw["close_rate_trailing_4wk"]),
            cash_balance=float(raw["cash_balance"]),
            monthly_burn=float(raw["monthly_burn"]),
            delivery_sla_miss_count=int(raw.get("delivery_sla_miss_count", 0)),
            cold_email_spam_rate=float(raw.get("cold_email_spam_rate", 0.0)),
            customer_concentration_top1=float(raw.get("customer_concentration_top1", 0.0)),
            escalations=list(raw.get("escalations", [])),
        )
    except (KeyError, ValueError) as e:
        print(f"Error in inputs: {e}", file=sys.stderr)
        return 2

    flags = red_flags(s)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "week_ending": s.week_ending,
                    "mrr": {
                        "current": s.mrr_current,
                        "wow_delta": s.mrr_current - s.mrr_last_week,
                        "mom_pct": growth_rate(s.mrr_current, s.mrr_4_weeks_ago),
                    },
                    "logos": {
                        "new": s.new_logos_this_week,
                        "churned": s.churned_logos_this_week,
                    },
                    "red_flags": [f.__dict__ for f in flags],
                    "escalations": s.escalations,
                },
                indent=2,
            )
        )
    else:
        print(render_text(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
