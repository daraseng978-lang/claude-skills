#!/usr/bin/env python3
"""
Capital Allocator

Founder-mode capital management. The founder commits tranches (e.g.,
"$10K Q2 budget, max $3K per strategy"). The CEO and Risk Officer
operate within that envelope; any ask for more capital goes back to
the founder.

This is the only surface a founder touches regularly. Everything else
is automated.

Allocation ledger schema (capital_ledger.json):
{
  "version": 1,
  "base_currency": "USD",
  "tranches": [
    {
      "id": "TR-0001",
      "amount": 10000,
      "opened_ts": 1712000000,
      "closed_ts": null,
      "note": "Q2 2026 initial funding",
      "signed_by_founder": true
    }
  ],
  "allocations": [
    {
      "id": "AL-0001",
      "strategy_id": "STR-0042",
      "tranche_id": "TR-0001",
      "amount": 3000,
      "opened_ts": 1712100000,
      "closed_ts": null,
      "status": "active"
    }
  ],
  "pnl_events": [
    {"strategy_id": "STR-0042", "amount": 150.50, "ts": 1712200000, "note": "end-of-day mark"}
  ],
  "withdrawals": [
    {"amount": 2000, "ts": 1712900000, "note": "Q2 profit sweep"}
  ]
}

Usage:
    python capital_allocator.py fund --amount 10000 --note "Q2 2026 initial"
    python capital_allocator.py allocate --strategy STR-0042 --amount 3000
    python capital_allocator.py pnl --strategy STR-0042 --amount 150.50
    python capital_allocator.py close --allocation AL-0001 --reason "strategy retired"
    python capital_allocator.py withdraw --amount 2000 --note "Q2 sweep"
    python capital_allocator.py status
    python capital_allocator.py status --format json
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

DEFAULT_LEDGER = "capital_ledger.json"


def load(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {
            "version": 1,
            "base_currency": "USD",
            "tranches": [],
            "allocations": [],
            "pnl_events": [],
            "withdrawals": [],
        }
    with open(path, "r") as f:
        return json.load(f)


def save(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def next_id(items: List[Dict[str, Any]], prefix: str) -> str:
    n = len(items) + 1
    return f"{prefix}-{n:04d}"


def total_committed(ledger: Dict[str, Any]) -> float:
    return sum(float(t["amount"]) for t in ledger["tranches"])


def total_withdrawn(ledger: Dict[str, Any]) -> float:
    return sum(float(w["amount"]) for w in ledger["withdrawals"])


def total_active_allocations(ledger: Dict[str, Any]) -> float:
    return sum(float(a["amount"]) for a in ledger["allocations"] if a.get("status") == "active")


def realized_pnl(ledger: Dict[str, Any]) -> float:
    return sum(float(p["amount"]) for p in ledger["pnl_events"])


def available(ledger: Dict[str, Any]) -> float:
    return (
        total_committed(ledger)
        + realized_pnl(ledger)
        - total_withdrawn(ledger)
        - total_active_allocations(ledger)
    )


def strategy_pnl(ledger: Dict[str, Any], strategy_id: str) -> float:
    return sum(float(p["amount"]) for p in ledger["pnl_events"] if p["strategy_id"] == strategy_id)


def cmd_fund(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    tid = next_id(ledger["tranches"], "TR")
    ledger["tranches"].append({
        "id": tid,
        "amount": args.amount,
        "opened_ts": int(time.time()),
        "closed_ts": None,
        "note": args.note,
        "signed_by_founder": True,
    })
    save(args.ledger, ledger)
    print(f"tranche {tid}: +{args.amount:.2f} ({args.note}) — signed by founder")
    print(f"available now: {available(ledger):.2f}")
    return 0


def cmd_allocate(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    avail = available(ledger)
    if args.amount > avail:
        print(
            f"ERROR: allocation {args.amount:.2f} exceeds available {avail:.2f} — "
            f"founder must fund another tranche",
            file=sys.stderr,
        )
        return 2

    per_strategy_cap = args.per_strategy_cap
    if per_strategy_cap is not None:
        existing = sum(
            float(a["amount"]) for a in ledger["allocations"]
            if a["strategy_id"] == args.strategy and a.get("status") == "active"
        )
        if existing + args.amount > per_strategy_cap:
            print(
                f"ERROR: {args.strategy} would have {existing + args.amount:.2f} allocated, "
                f"exceeds per-strategy cap {per_strategy_cap:.2f}",
                file=sys.stderr,
            )
            return 2

    aid = next_id(ledger["allocations"], "AL")
    tranche_id = args.tranche or (ledger["tranches"][-1]["id"] if ledger["tranches"] else "")
    ledger["allocations"].append({
        "id": aid,
        "strategy_id": args.strategy,
        "tranche_id": tranche_id,
        "amount": args.amount,
        "opened_ts": int(time.time()),
        "closed_ts": None,
        "status": "active",
    })
    save(args.ledger, ledger)
    print(f"{aid}: allocated {args.amount:.2f} to {args.strategy} from {tranche_id}")
    print(f"available now: {available(ledger):.2f}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    for a in ledger["allocations"]:
        if a["id"] == args.allocation:
            a["status"] = "closed"
            a["closed_ts"] = int(time.time())
            a["close_reason"] = args.reason
            save(args.ledger, ledger)
            print(f"{args.allocation}: closed ({args.reason})")
            print(f"available now: {available(ledger):.2f}")
            return 0
    print(f"ERROR: allocation {args.allocation} not found", file=sys.stderr)
    return 2


def cmd_pnl(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    ledger["pnl_events"].append({
        "strategy_id": args.strategy,
        "amount": args.amount,
        "ts": int(time.time()),
        "note": args.note,
    })
    save(args.ledger, ledger)
    sign = "+" if args.amount >= 0 else ""
    print(f"{args.strategy}: pnl {sign}{args.amount:.2f} ({args.note})")
    print(f"strategy lifetime pnl: {strategy_pnl(ledger, args.strategy):+.2f}")
    print(f"available now: {available(ledger):.2f}")
    return 0


def cmd_withdraw(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    avail = available(ledger)
    if args.amount > avail:
        print(
            f"ERROR: withdrawal {args.amount:.2f} exceeds available {avail:.2f}",
            file=sys.stderr,
        )
        return 2
    ledger["withdrawals"].append({
        "amount": args.amount,
        "ts": int(time.time()),
        "note": args.note,
    })
    save(args.ledger, ledger)
    print(f"withdrew {args.amount:.2f} ({args.note})")
    print(f"available now: {available(ledger):.2f}")
    return 0


def status(ledger: Dict[str, Any]) -> Dict[str, Any]:
    strategy_ids = sorted({a["strategy_id"] for a in ledger["allocations"]})
    by_strategy: List[Dict[str, Any]] = []
    for sid in strategy_ids:
        active = sum(
            float(a["amount"]) for a in ledger["allocations"]
            if a["strategy_id"] == sid and a.get("status") == "active"
        )
        pnl = strategy_pnl(ledger, sid)
        by_strategy.append({
            "strategy_id": sid,
            "active_allocation": active,
            "lifetime_pnl": pnl,
            "roi_pct": (pnl / active * 100.0) if active > 0 else 0.0,
        })
    by_strategy.sort(key=lambda x: x["lifetime_pnl"], reverse=True)
    return {
        "committed": total_committed(ledger),
        "realized_pnl": realized_pnl(ledger),
        "withdrawn": total_withdrawn(ledger),
        "active_allocations": total_active_allocations(ledger),
        "available": available(ledger),
        "by_strategy": by_strategy,
        "tranches": len(ledger["tranches"]),
    }


def cmd_status(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    s = status(ledger)
    if args.format == "json":
        print(json.dumps(s, indent=2))
        return 0
    print(f"{'committed':<25}{s['committed']:>14.2f}")
    print(f"{'realized pnl':<25}{s['realized_pnl']:>+14.2f}")
    print(f"{'withdrawn':<25}{s['withdrawn']:>14.2f}")
    print(f"{'active allocations':<25}{s['active_allocations']:>14.2f}")
    print(f"{'available':<25}{s['available']:>14.2f}")
    print()
    if s["by_strategy"]:
        print(f"{'STRATEGY':<12}{'ACTIVE':>14}{'PNL':>14}{'ROI %':>10}")
        print("-" * 50)
        for row in s["by_strategy"]:
            print(
                f"{row['strategy_id']:<12}"
                f"{row['active_allocation']:>14.2f}"
                f"{row['lifetime_pnl']:>+14.2f}"
                f"{row['roi_pct']:>+9.2f}%"
            )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Founder-mode capital allocator")
    p.add_argument("--ledger", default=DEFAULT_LEDGER)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fund", help="founder commits a capital tranche")
    f.add_argument("--amount", type=float, required=True)
    f.add_argument("--note", default="")
    f.set_defaults(func=cmd_fund)

    a = sub.add_parser("allocate", help="allocate capital to a strategy")
    a.add_argument("--strategy", required=True, help="strategy id (e.g. STR-0042)")
    a.add_argument("--amount", type=float, required=True)
    a.add_argument("--tranche", default="", help="tranche id (default: latest)")
    a.add_argument("--per-strategy-cap", type=float, default=None)
    a.set_defaults(func=cmd_allocate)

    c = sub.add_parser("close", help="close an allocation (e.g. on retirement)")
    c.add_argument("--allocation", required=True)
    c.add_argument("--reason", required=True)
    c.set_defaults(func=cmd_close)

    pn = sub.add_parser("pnl", help="record a p&l event against a strategy")
    pn.add_argument("--strategy", required=True)
    pn.add_argument("--amount", type=float, required=True)
    pn.add_argument("--note", default="")
    pn.set_defaults(func=cmd_pnl)

    w = sub.add_parser("withdraw", help="founder withdraws capital from the firm")
    w.add_argument("--amount", type=float, required=True)
    w.add_argument("--note", default="")
    w.set_defaults(func=cmd_withdraw)

    st = sub.add_parser("status", help="show capital snapshot")
    st.add_argument("--format", default="text", choices=["text", "json"])
    st.set_defaults(func=cmd_status)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
