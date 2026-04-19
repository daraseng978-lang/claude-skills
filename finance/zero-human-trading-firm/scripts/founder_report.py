#!/usr/bin/env python3
"""
Founder Report

Monthly digest for the founder/investor. This is the ONE artifact the
founder needs to read each month to make the only decision reserved
for them: the next tranche of capital.

Pulls from:
    - capital_ledger.json (committed, allocated, withdrawn, pnl)
    - strategy_ledger.json (active strategies, retired this month)

Outputs a markdown report with:
    - Top-of-page: P&L, runway, available capital
    - By-strategy ROI table (reality check on where alpha is)
    - Strategies retired this month (what we learned)
    - Proposed next-month budget (with explicit assumptions)
    - The ONE decision the founder should make

Usage:
    python founder_report.py \
        --capital capital_ledger.json \
        --strategies strategy_ledger.json \
        --month 2026-04 \
        --out daily_reports/founder-2026-04.md

    python founder_report.py --capital c.json --strategies s.json --format json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Tuple


def load(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def month_range(month: str) -> Tuple[int, int]:
    """Return (start_ts, end_ts) for a YYYY-MM month in UTC."""
    dt = datetime.strptime(month, "%Y-%m").replace(tzinfo=timezone.utc)
    if dt.month == 12:
        nxt = dt.replace(year=dt.year + 1, month=1)
    else:
        nxt = dt.replace(month=dt.month + 1)
    return int(dt.timestamp()), int(nxt.timestamp())


def in_range(ts: int, start: int, end: int) -> bool:
    return start <= ts < end


def compute_reconciliation(
    capital: Dict[str, Any],
    broker: Dict[str, Any],
    drift_threshold: float = 1.0,
) -> Dict[str, Any]:
    """Reconcile internal ledger vs broker statement.

    Broker statement schema (JSON, kept simple so a CEO agent can
    produce it from IB Flex XML/CSV):
    {
      "as_of": 1712200000,
      "cash": 7150.50,
      "positions": [{"symbol": "AAPL", "qty": 10, "mark": 1850.30}],
      "source": "ib-paper-flex"
    }
    """
    ledger_realized = sum(float(p["amount"]) for p in capital.get("realized_pnl_events",
                         capital.get("pnl_events", [])))
    ledger_committed = sum(float(t["amount"]) for t in capital.get("tranches", []))
    ledger_withdrawn = sum(float(w["amount"]) for w in capital.get("withdrawals", []))
    ledger_active_alloc = sum(
        float(a["amount"]) for a in capital.get("allocations", [])
        if a.get("status") == "active"
    )
    # Expected cash at broker = committed + realized_pnl − withdrawn − active_in_positions
    ledger_expected_cash = ledger_committed + ledger_realized - ledger_withdrawn - ledger_active_alloc

    broker_cash = float(broker.get("cash", 0))
    cash_drift = broker_cash - ledger_expected_cash
    cash_flag = abs(cash_drift) > drift_threshold

    broker_position_value = sum(
        float(p.get("mark", 0)) for p in broker.get("positions", [])
    )
    positions_flag = False  # we don't model per-symbol positions in the ledger yet

    return {
        "as_of": broker.get("as_of"),
        "source": broker.get("source", "unknown"),
        "ledger_expected_cash": round(ledger_expected_cash, 2),
        "broker_cash": round(broker_cash, 2),
        "cash_drift": round(cash_drift, 2),
        "cash_flag": cash_flag,
        "broker_position_value": round(broker_position_value, 2),
        "position_count": len(broker.get("positions", [])),
        "positions_flag": positions_flag,
        "drift_threshold": drift_threshold,
        "ok": not (cash_flag or positions_flag),
    }


def compute_metrics(
    capital: Dict[str, Any],
    strategies: Dict[str, Any],
    month: str,
) -> Dict[str, Any]:
    start, end = month_range(month)

    month_pnl = sum(
        float(p["amount"]) for p in capital.get("pnl_events", [])
        if in_range(p["ts"], start, end)
    )
    lifetime_pnl = sum(float(p["amount"]) for p in capital.get("pnl_events", []))
    committed = sum(float(t["amount"]) for t in capital.get("tranches", []))
    withdrawn = sum(float(w["amount"]) for w in capital.get("withdrawals", []))
    active_alloc = sum(
        float(a["amount"]) for a in capital.get("allocations", [])
        if a.get("status") == "active"
    )
    available = committed + lifetime_pnl - withdrawn - active_alloc

    # By-strategy
    strategy_ids = sorted({a["strategy_id"] for a in capital.get("allocations", [])})
    by_strategy: List[Dict[str, Any]] = []
    for sid in strategy_ids:
        active = sum(
            float(a["amount"]) for a in capital.get("allocations", [])
            if a["strategy_id"] == sid and a.get("status") == "active"
        )
        s_month_pnl = sum(
            float(p["amount"]) for p in capital.get("pnl_events", [])
            if p["strategy_id"] == sid and in_range(p["ts"], start, end)
        )
        s_lifetime_pnl = sum(
            float(p["amount"]) for p in capital.get("pnl_events", [])
            if p["strategy_id"] == sid
        )
        strategy_name = sid
        state = "unknown"
        for s in strategies.get("strategies", []):
            if s["id"] == sid:
                strategy_name = s.get("name", sid)
                state = s.get("state", "unknown")
                break
        by_strategy.append({
            "id": sid,
            "name": strategy_name,
            "state": state,
            "active_allocation": active,
            "month_pnl": s_month_pnl,
            "lifetime_pnl": s_lifetime_pnl,
            "roi_pct": (s_lifetime_pnl / active * 100.0) if active > 0 else 0.0,
        })
    by_strategy.sort(key=lambda x: x["month_pnl"], reverse=True)

    # Retired this month
    retired: List[Dict[str, Any]] = []
    for s in strategies.get("strategies", []):
        if s.get("state") != "retired":
            continue
        hist = s.get("history", [])
        for h in hist:
            if h.get("state") == "retired" and in_range(h.get("ts", 0), start, end):
                retired.append({
                    "id": s["id"],
                    "name": s.get("name", ""),
                    "reason": h.get("reason", ""),
                })
                break

    # Promoted to live this month
    promoted: List[Dict[str, Any]] = []
    for s in strategies.get("strategies", []):
        for h in s.get("history", []):
            if h.get("state") == "live" and in_range(h.get("ts", 0), start, end):
                promoted.append({"id": s["id"], "name": s.get("name", "")})
                break

    # Active live strategies
    live = [s for s in strategies.get("strategies", []) if s.get("state") in ("live", "paper")]

    monthly_return_pct = (month_pnl / (active_alloc + 1e-9)) * 100.0 if active_alloc > 0 else 0.0

    return {
        "month": month,
        "headline": {
            "month_pnl": round(month_pnl, 2),
            "monthly_return_pct": round(monthly_return_pct, 2),
            "lifetime_pnl": round(lifetime_pnl, 2),
            "committed": round(committed, 2),
            "withdrawn": round(withdrawn, 2),
            "active_allocation": round(active_alloc, 2),
            "available": round(available, 2),
        },
        "by_strategy": by_strategy,
        "retired_this_month": retired,
        "promoted_this_month": promoted,
        "active_strategies": len(live),
    }


def render_markdown(m: Dict[str, Any], firm_name: str, recon: Dict[str, Any] = None) -> str:
    h = m["headline"]
    lines: List[str] = []
    lines.append(f"# Founder Report — {firm_name} — {m['month']}")
    lines.append("")
    lines.append("> The only thing you need to read this month.")
    lines.append("")

    # Reconciliation block first — if it fails, the decision section is suppressed
    lines.append("## Reconciliation")
    lines.append("")
    if recon is None:
        lines.append("> **RECONCILIATION MISSING — decision section suppressed.**")
        lines.append(">")
        lines.append("> No `--broker-statement` was provided to this report. Internal P&L ")
        lines.append("> has not been verified against the broker. Do NOT fund a new tranche ")
        lines.append("> or approve a withdrawal on this report. Ask the Accountant agent to ")
        lines.append("> export an IB Flex statement, convert to the broker JSON schema, and ")
        lines.append("> rerun with `--broker-statement <path>`.")
        lines.append("")
    else:
        status_icon = "OK" if recon["ok"] else "FLAGGED"
        lines.append(f"- **Status:** {status_icon}")
        lines.append(f"- **Source:** {recon['source']}")
        lines.append(f"- **Ledger expected cash:** {recon['ledger_expected_cash']:.2f}")
        lines.append(f"- **Broker cash:** {recon['broker_cash']:.2f}")
        lines.append(f"- **Cash drift:** {recon['cash_drift']:+.2f}  "
                     f"(threshold: {recon['drift_threshold']:.2f})")
        lines.append(f"- **Broker open positions:** {recon['position_count']} "
                     f"(mark value {recon['broker_position_value']:.2f})")
        if recon["cash_flag"]:
            lines.append("")
            lines.append("> **DRIFT EXCEEDS THRESHOLD.** Do not fund or withdraw on this report ")
            lines.append("> until the Accountant agent investigates the discrepancy.")
        lines.append("")

    lines.append("## Headline")
    lines.append("")
    lines.append(f"- **Month P&L:** {h['month_pnl']:+.2f} ({h['monthly_return_pct']:+.2f}% on active allocation)")
    lines.append(f"- **Lifetime P&L:** {h['lifetime_pnl']:+.2f}")
    lines.append(f"- **Committed capital:** {h['committed']:.2f}")
    lines.append(f"- **Active allocation:** {h['active_allocation']:.2f}")
    lines.append(f"- **Available (idle):** {h['available']:.2f}")
    lines.append(f"- **Withdrawn lifetime:** {h['withdrawn']:.2f}")
    lines.append(f"- **Active strategies:** {m['active_strategies']}")
    lines.append("")

    lines.append("## By-strategy performance (this month)")
    lines.append("")
    if m["by_strategy"]:
        lines.append("| ID | Name | State | Active $ | Month P&L | Lifetime P&L | ROI % |")
        lines.append("|----|------|-------|---------:|----------:|-------------:|------:|")
        for s in m["by_strategy"]:
            lines.append(
                f"| {s['id']} | {s['name'][:40]} | {s['state']} | "
                f"{s['active_allocation']:.2f} | {s['month_pnl']:+.2f} | "
                f"{s['lifetime_pnl']:+.2f} | {s['roi_pct']:+.2f}% |"
            )
    else:
        lines.append("_(no allocations yet)_")
    lines.append("")

    lines.append("## Retired this month")
    lines.append("")
    if m["retired_this_month"]:
        for r in m["retired_this_month"]:
            lines.append(f"- **{r['id']}** — {r['name']}: {r['reason']}")
    else:
        lines.append("_(none retired this month)_")
    lines.append("")

    lines.append("## Promoted to live this month")
    lines.append("")
    if m["promoted_this_month"]:
        for p in m["promoted_this_month"]:
            lines.append(f"- **{p['id']}** — {p['name']}")
    else:
        lines.append("_(no promotions this month)_")
    lines.append("")

    lines.append("## The decision")
    lines.append("")
    if recon is None or not recon.get("ok", False):
        lines.append("- **Ask:** NONE. Reconciliation is missing or flagged; no capital movement "
                     "should be recommended until broker statement ties to ledger.")
        lines.append("")
        lines.append("## Assumptions in this report")
        lines.append("")
        lines.append("- P&L is as marked by the Accountant role; verify against venue statements monthly.")
        lines.append("- ROI % uses current active allocation as denominator (not peak allocation).")
        lines.append("- Reconciliation is a hard gate: no fund/withdraw recommendation without a clean broker tie-out.")
        return "\n".join(lines)
    if h["available"] < h["active_allocation"] * 0.2:
        lines.append(
            "- **Ask:** fund another tranche. Available capital is less than 20% of active allocation."
        )
        suggested = round(h["active_allocation"] * 0.5, -2)
        lines.append(f"- **Suggested tranche:** ~{suggested:.0f} (scale with winners)")
    elif h["month_pnl"] < 0 and h["monthly_return_pct"] < -5:
        lines.append("- **Ask:** review retirement candidates. Monthly return is below -5%.")
        lines.append("- **Suggested action:** no new tranche. Let the Risk Officer trim.")
    elif h["lifetime_pnl"] > h["committed"] * 0.1:
        lines.append(
            "- **Ask:** consider a profit sweep. Lifetime P&L exceeds 10% of committed."
        )
        sweep = round(h["lifetime_pnl"] * 0.3, -2)
        lines.append(f"- **Suggested withdraw:** ~{sweep:.0f} (bank 30% of gains)")
    else:
        lines.append("- **Ask:** no action required. Stay the course.")
    lines.append("")

    lines.append("## Assumptions in this report")
    lines.append("")
    lines.append("- P&L is as marked by the Accountant role; verify against venue statements monthly.")
    lines.append("- ROI % uses current active allocation as denominator (not peak allocation).")
    lines.append("- If any row surprises you, the Accountant's logs are authoritative.")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Monthly founder report")
    p.add_argument("--capital", required=True, help="capital_ledger.json path")
    p.add_argument("--strategies", required=True, help="strategy_ledger.json path")
    p.add_argument(
        "--month",
        default=datetime.now(timezone.utc).strftime("%Y-%m"),
        help="month in YYYY-MM (default: current month UTC)",
    )
    p.add_argument("--firm-name", default="Your Firm")
    p.add_argument("--out", default="", help="write markdown to this file (default: stdout)")
    p.add_argument("--format", default="markdown", choices=["markdown", "json"])
    p.add_argument("--broker-statement", default="",
                   help="path to broker statement JSON for reconciliation (if omitted, "
                        "the decision section is suppressed)")
    p.add_argument("--drift-threshold", type=float, default=1.0,
                   help="cash drift threshold in base currency; exceeding it flags the report")
    args = p.parse_args()

    capital = load(args.capital)
    strategies = load(args.strategies)
    m = compute_metrics(capital, strategies, args.month)
    recon = None
    if args.broker_statement:
        broker = load(args.broker_statement)
        recon = compute_reconciliation(capital, broker, args.drift_threshold)

    if args.format == "json":
        payload = dict(m)
        payload["reconciliation"] = recon
        out = json.dumps(payload, indent=2)
    else:
        out = render_markdown(m, args.firm_name, recon)

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as f:
            f.write(out + ("\n" if not out.endswith("\n") else ""))
        print(f"wrote {args.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
