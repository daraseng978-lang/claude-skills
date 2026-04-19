#!/usr/bin/env python3
"""
Capital Allocator

Founder-mode capital management. The founder commits tranches; the CEO
and Risk Officer operate within that envelope.

v2 schema (capital_ledger.json):
{
  "version": 2,
  "base_currency": "USD",
  "require_signed_actions": false,
  "tranches": [ {id, amount, opened_ts, closed_ts, note, signed_by_founder,
                 action_id} ],
  "allocations": [ {id, strategy_id, tranche_id, amount, opened_ts,
                    closed_ts, status} ],
  "realized_pnl_events": [ {strategy_id, amount, ts, note} ],
  "mark_events": [ {strategy_id, amount, ts, note} ],  # unrealized MTM snapshots
  "withdrawals": [ {amount, ts, note, action_id} ],
  "pnl_events": [ ... ]  # deprecated; if present, treated as realized
}

Realized vs unrealized is the difference between "I can safely withdraw
this" and "this number could evaporate before settlement". Mark events
are point-in-time snapshots; the *latest* mark per strategy is the
current unrealized P&L for that strategy.

Usage:
    python capital_allocator.py fund --amount 10000 --note "Q2 initial"
    python capital_allocator.py fund --action-file actions/approved/A-001.json
    python capital_allocator.py allocate --strategy STR-0042 --amount 3000
    python capital_allocator.py pnl --strategy STR-0042 --amount 150 --note "trade closed"
    python capital_allocator.py mark --strategy STR-0042 --amount -40 --note "EOD MTM"
    python capital_allocator.py close --allocation AL-0001 --reason "retired"
    python capital_allocator.py withdraw --amount 2000 --action-file actions/approved/A-002.json
    python capital_allocator.py status
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List

DEFAULT_LEDGER = "capital_ledger.json"


def load(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {
            "version": 2,
            "base_currency": "USD",
            "require_signed_actions": False,
            "tranches": [],
            "allocations": [],
            "realized_pnl_events": [],
            "mark_events": [],
            "withdrawals": [],
        }
    with open(path, "r") as f:
        data = json.load(f)
    # v1 → v2 migration: pnl_events treated as realized
    if data.get("version", 1) < 2:
        data["realized_pnl_events"] = data.get("pnl_events", [])
        data.setdefault("mark_events", [])
        data.setdefault("require_signed_actions", False)
        data["version"] = 2
    else:
        data.setdefault("realized_pnl_events", data.get("pnl_events", []))
        data.setdefault("mark_events", [])
        data.setdefault("require_signed_actions", False)
    return data


def save(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def next_id(items: List[Dict[str, Any]], prefix: str) -> str:
    return f"{prefix}-{len(items) + 1:04d}"


def total_committed(ledger: Dict[str, Any]) -> float:
    return sum(float(t["amount"]) for t in ledger["tranches"])


def total_withdrawn(ledger: Dict[str, Any]) -> float:
    return sum(float(w["amount"]) for w in ledger["withdrawals"])


def total_active_allocations(ledger: Dict[str, Any]) -> float:
    return sum(float(a["amount"]) for a in ledger["allocations"] if a.get("status") == "active")


def realized_pnl(ledger: Dict[str, Any]) -> float:
    return sum(float(p["amount"]) for p in ledger.get("realized_pnl_events", []))


def unrealized_pnl(ledger: Dict[str, Any]) -> float:
    """Sum of the latest mark per strategy."""
    latest: Dict[str, float] = {}
    for m in sorted(ledger.get("mark_events", []), key=lambda x: x.get("ts", 0)):
        latest[m["strategy_id"]] = float(m["amount"])
    return sum(latest.values())


def strategy_realized(ledger: Dict[str, Any], sid: str) -> float:
    return sum(float(p["amount"]) for p in ledger.get("realized_pnl_events", []) if p["strategy_id"] == sid)


def strategy_unrealized(ledger: Dict[str, Any], sid: str) -> float:
    marks = [m for m in ledger.get("mark_events", []) if m["strategy_id"] == sid]
    if not marks:
        return 0.0
    latest = max(marks, key=lambda x: x.get("ts", 0))
    return float(latest["amount"])


def available(ledger: Dict[str, Any]) -> float:
    """Cash available for withdrawal or new allocation.

    Deliberately EXCLUDES unrealized marks. A strategy up $500 on paper
    is not $500 of withdrawable cash — the position still has to be
    closed, possibly through slippage, possibly through margin.
    """
    return (
        total_committed(ledger)
        + realized_pnl(ledger)
        - total_withdrawn(ledger)
        - total_active_allocations(ledger)
    )


def _require_action(ledger: Dict[str, Any], action_file: str, expected_action: str,
                    expected_amount: float) -> Dict[str, Any]:
    """Load and validate a signed-action artifact before a capital movement.

    Returns the parsed action dict. Raises RuntimeError on invalid.
    """
    if not action_file:
        if ledger.get("require_signed_actions"):
            raise RuntimeError(
                "this ledger requires --action-file for fund/withdraw. "
                "generate one with capital_action.py propose, then have the founder "
                "approve it (git commit into actions/approved/)."
            )
        return {}
    if not os.path.exists(action_file):
        raise RuntimeError(f"action file not found: {action_file}")
    with open(action_file, "r") as f:
        action = json.load(f)
    if action.get("action") != expected_action:
        raise RuntimeError(f"action file is {action.get('action')!r}, expected {expected_action!r}")
    if abs(float(action.get("amount", 0)) - expected_amount) > 0.005:
        raise RuntimeError(
            f"action file amount {action.get('amount')} does not match --amount {expected_amount}"
        )
    if not action.get("approved_ts"):
        raise RuntimeError("action file is not approved (no approved_ts). founder must approve first.")
    return action


def cmd_fund(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    try:
        action = _require_action(ledger, args.action_file, "fund", args.amount)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    tid = next_id(ledger["tranches"], "TR")
    note = args.note or action.get("reason", "")
    entry = {
        "id": tid,
        "amount": args.amount,
        "opened_ts": int(time.time()),
        "closed_ts": None,
        "note": note,
        "signed_by_founder": True,
    }
    if action:
        entry["action_id"] = action.get("id", "")
    ledger["tranches"].append(entry)
    save(args.ledger, ledger)
    print(f"tranche {tid}: +{args.amount:.2f} ({note}) — signed by founder")
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

    if args.per_strategy_cap is not None:
        existing = sum(
            float(a["amount"]) for a in ledger["allocations"]
            if a["strategy_id"] == args.strategy and a.get("status") == "active"
        )
        if existing + args.amount > args.per_strategy_cap:
            print(
                f"ERROR: {args.strategy} would have {existing + args.amount:.2f} allocated, "
                f"exceeds per-strategy cap {args.per_strategy_cap:.2f}",
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
    """Record a REALIZED p&l event (closed trade, cash-settled)."""
    ledger = load(args.ledger)
    ledger["realized_pnl_events"].append({
        "strategy_id": args.strategy,
        "amount": args.amount,
        "ts": int(time.time()),
        "note": args.note,
    })
    save(args.ledger, ledger)
    sign = "+" if args.amount >= 0 else ""
    print(f"{args.strategy}: REALIZED pnl {sign}{args.amount:.2f} ({args.note})")
    print(f"strategy realized pnl: {strategy_realized(ledger, args.strategy):+.2f}")
    print(f"available now: {available(ledger):.2f}")
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    """Record an UNREALIZED mark-to-market snapshot (open positions)."""
    ledger = load(args.ledger)
    ledger["mark_events"].append({
        "strategy_id": args.strategy,
        "amount": args.amount,
        "ts": int(time.time()),
        "note": args.note,
    })
    save(args.ledger, ledger)
    sign = "+" if args.amount >= 0 else ""
    print(f"{args.strategy}: UNREALIZED mark {sign}{args.amount:.2f} ({args.note})")
    print(f"strategy unrealized: {strategy_unrealized(ledger, args.strategy):+.2f} (latest mark)")
    print(f"total unrealized across firm: {unrealized_pnl(ledger):+.2f}")
    print(f"available (realized only): {available(ledger):.2f}")
    return 0


def cmd_withdraw(args: argparse.Namespace) -> int:
    ledger = load(args.ledger)
    try:
        action = _require_action(ledger, args.action_file, "withdraw", args.amount)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    avail = available(ledger)
    if args.amount > avail:
        unr = unrealized_pnl(ledger)
        msg = f"ERROR: withdrawal {args.amount:.2f} exceeds REALIZED available {avail:.2f}"
        if unr > 0:
            msg += (
                f". Unrealized P&L of {unr:+.2f} is NOT withdrawable — "
                f"close positions first to realize it."
            )
        print(msg, file=sys.stderr)
        return 2
    note = args.note or action.get("reason", "")
    entry = {
        "amount": args.amount,
        "ts": int(time.time()),
        "note": note,
    }
    if action:
        entry["action_id"] = action.get("id", "")
    ledger["withdrawals"].append(entry)
    save(args.ledger, ledger)
    print(f"withdrew {args.amount:.2f} ({note})")
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
        r = strategy_realized(ledger, sid)
        u = strategy_unrealized(ledger, sid)
        by_strategy.append({
            "strategy_id": sid,
            "active_allocation": active,
            "realized_pnl": r,
            "unrealized_pnl": u,
            "total_pnl": r + u,
            "roi_pct": ((r + u) / active * 100.0) if active > 0 else 0.0,
        })
    by_strategy.sort(key=lambda x: x["total_pnl"], reverse=True)
    return {
        "committed": total_committed(ledger),
        "realized_pnl": realized_pnl(ledger),
        "unrealized_pnl": unrealized_pnl(ledger),
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
    print(f"{'unrealized pnl (MTM)':<25}{s['unrealized_pnl']:>+14.2f}  (not withdrawable)")
    print(f"{'withdrawn':<25}{s['withdrawn']:>14.2f}")
    print(f"{'active allocations':<25}{s['active_allocations']:>14.2f}")
    print(f"{'available (realized)':<25}{s['available']:>14.2f}")
    print()
    if s["by_strategy"]:
        print(f"{'STRATEGY':<12}{'ACTIVE':>12}{'REALIZED':>12}{'UNREAL.':>12}{'ROI %':>10}")
        print("-" * 58)
        for row in s["by_strategy"]:
            print(
                f"{row['strategy_id']:<12}"
                f"{row['active_allocation']:>12.2f}"
                f"{row['realized_pnl']:>+12.2f}"
                f"{row['unrealized_pnl']:>+12.2f}"
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
    f.add_argument("--action-file", default="", help="signed action artifact (recommended)")
    f.set_defaults(func=cmd_fund)

    a = sub.add_parser("allocate", help="allocate capital to a strategy")
    a.add_argument("--strategy", required=True)
    a.add_argument("--amount", type=float, required=True)
    a.add_argument("--tranche", default="")
    a.add_argument("--per-strategy-cap", type=float, default=None)
    a.set_defaults(func=cmd_allocate)

    c = sub.add_parser("close", help="close an allocation")
    c.add_argument("--allocation", required=True)
    c.add_argument("--reason", required=True)
    c.set_defaults(func=cmd_close)

    pn = sub.add_parser("pnl", help="record a REALIZED p&l event (closed trade)")
    pn.add_argument("--strategy", required=True)
    pn.add_argument("--amount", type=float, required=True)
    pn.add_argument("--note", default="")
    pn.set_defaults(func=cmd_pnl)

    mk = sub.add_parser("mark", help="record an UNREALIZED mark (open position MTM)")
    mk.add_argument("--strategy", required=True)
    mk.add_argument("--amount", type=float, required=True, help="current unrealized P&L for the strategy")
    mk.add_argument("--note", default="")
    mk.set_defaults(func=cmd_mark)

    w = sub.add_parser("withdraw", help="founder withdraws capital from the firm")
    w.add_argument("--amount", type=float, required=True)
    w.add_argument("--note", default="")
    w.add_argument("--action-file", default="", help="signed action artifact (recommended)")
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
