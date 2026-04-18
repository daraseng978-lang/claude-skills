#!/usr/bin/env python3
"""
Strategy Ledger

Append-only JSON ledger tracking every trading strategy through its lifecycle.
The ledger is the institutional memory of the firm: every idea proposed,
backtested, red-teamed, paper-traded, promoted, or retired is recorded.

States:
    proposed        -> idea exists, not yet implemented
    backtested      -> code written, backtest results recorded
    red_teamed      -> adversarial review complete
    ready_for_paper -> passed red team, awaiting paper-trade slot
    paper           -> running in paper mode
    live            -> running on real capital
    retired         -> no longer trading (alpha decay, regime shift, blown up)
    rejected        -> failed backtest or red team, not salvageable

Usage:
    python strategy_ledger.py propose --name "SMA 20/50 on BTC-PERP" \
        --hypothesis "Momentum in trending regimes" --source "youtube-link"

    python strategy_ledger.py advance --id STR-0001 --state backtested \
        --metrics '{"sharpe": 1.4, "max_dd": 0.08, "trades": 142}'

    python strategy_ledger.py list --state ready_for_paper
    python strategy_ledger.py show --id STR-0001
    python strategy_ledger.py retire --id STR-0001 --reason "alpha decay"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_LEDGER = "strategy_ledger.json"

VALID_STATES = [
    "proposed",
    "backtested",
    "red_teamed",
    "ready_for_paper",
    "paper",
    "live",
    "retired",
    "rejected",
]


def load_ledger(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"version": 1, "strategies": [], "events": []}
    with open(path, "r") as f:
        return json.load(f)


def save_ledger(path: str, ledger: Dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(ledger, f, indent=2, sort_keys=True)


def next_id(ledger: Dict[str, Any]) -> str:
    n = len(ledger["strategies"]) + 1
    return f"STR-{n:04d}"


def append_event(ledger: Dict[str, Any], strategy_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    ledger["events"].append({
        "ts": int(time.time()),
        "id": strategy_id,
        "type": event_type,
        "payload": payload,
    })


def find(ledger: Dict[str, Any], strategy_id: str) -> Optional[Dict[str, Any]]:
    for s in ledger["strategies"]:
        if s["id"] == strategy_id:
            return s
    return None


def cmd_propose(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    sid = next_id(ledger)
    strategy = {
        "id": sid,
        "name": args.name,
        "hypothesis": args.hypothesis,
        "source": args.source,
        "state": "proposed",
        "created_ts": int(time.time()),
        "metrics": {},
        "flags": {"red_team_signed_off": False, "risk_officer_signed_off": False},
        "history": [{"state": "proposed", "ts": int(time.time())}],
    }
    ledger["strategies"].append(strategy)
    append_event(ledger, sid, "propose", {"name": args.name})
    save_ledger(args.ledger, ledger)
    print(f"proposed {sid}: {args.name}")
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    strategy = find(ledger, args.id)
    if strategy is None:
        print(f"ERROR: strategy {args.id} not found", file=sys.stderr)
        return 2
    if args.state not in VALID_STATES:
        print(f"ERROR: invalid state '{args.state}'. Valid: {VALID_STATES}", file=sys.stderr)
        return 2
    previous = strategy["state"]
    strategy["state"] = args.state
    strategy["history"].append({"state": args.state, "ts": int(time.time())})
    if args.metrics:
        try:
            metrics = json.loads(args.metrics)
        except json.JSONDecodeError as e:
            print(f"ERROR: --metrics must be valid JSON: {e}", file=sys.stderr)
            return 2
        strategy["metrics"].update(metrics)
    append_event(ledger, args.id, "advance", {"from": previous, "to": args.state})
    save_ledger(args.ledger, ledger)
    print(f"{args.id}: {previous} -> {args.state}")
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    strategy = find(ledger, args.id)
    if strategy is None:
        print(f"ERROR: strategy {args.id} not found", file=sys.stderr)
        return 2
    if args.flag not in ("red_team_signed_off", "risk_officer_signed_off"):
        print(f"ERROR: flag must be red_team_signed_off or risk_officer_signed_off", file=sys.stderr)
        return 2
    strategy["flags"][args.flag] = True
    append_event(ledger, args.id, "sign", {"flag": args.flag, "by": args.by or "unknown"})
    save_ledger(args.ledger, ledger)
    print(f"{args.id}: {args.flag} = True (by {args.by or 'unknown'})")
    return 0


def cmd_retire(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    strategy = find(ledger, args.id)
    if strategy is None:
        print(f"ERROR: strategy {args.id} not found", file=sys.stderr)
        return 2
    strategy["state"] = "retired"
    strategy["history"].append({"state": "retired", "ts": int(time.time()), "reason": args.reason})
    append_event(ledger, args.id, "retire", {"reason": args.reason})
    save_ledger(args.ledger, ledger)
    print(f"{args.id}: retired ({args.reason})")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    rows = ledger["strategies"]
    if args.state:
        rows = [s for s in rows if s["state"] == args.state]
    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("(no strategies match)")
        return 0
    print(f"{'ID':<10} {'STATE':<18} {'NAME':<50}")
    print("-" * 80)
    for s in rows:
        print(f"{s['id']:<10} {s['state']:<18} {s['name'][:50]}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    strategy = find(ledger, args.id)
    if strategy is None:
        print(f"ERROR: strategy {args.id} not found", file=sys.stderr)
        return 2
    print(json.dumps(strategy, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Strategy lifecycle ledger")
    p.add_argument("--ledger", default=DEFAULT_LEDGER, help=f"path to ledger file (default: {DEFAULT_LEDGER})")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("propose", help="propose a new strategy")
    pr.add_argument("--name", required=True)
    pr.add_argument("--hypothesis", required=True)
    pr.add_argument("--source", default="")
    pr.set_defaults(func=cmd_propose)

    ad = sub.add_parser("advance", help="move strategy to new state")
    ad.add_argument("--id", required=True)
    ad.add_argument("--state", required=True, choices=VALID_STATES)
    ad.add_argument("--metrics", default="", help="JSON dict of metrics to merge in")
    ad.set_defaults(func=cmd_advance)

    sg = sub.add_parser("sign", help="record a sign-off flag")
    sg.add_argument("--id", required=True)
    sg.add_argument("--flag", required=True)
    sg.add_argument("--by", default="", help="signer identifier")
    sg.set_defaults(func=cmd_sign)

    rt = sub.add_parser("retire", help="retire a live or paper strategy")
    rt.add_argument("--id", required=True)
    rt.add_argument("--reason", required=True)
    rt.set_defaults(func=cmd_retire)

    ls = sub.add_parser("list", help="list strategies")
    ls.add_argument("--state", default="", choices=[""] + VALID_STATES)
    ls.add_argument("--format", default="table", choices=["table", "json"])
    ls.set_defaults(func=cmd_list)

    sh = sub.add_parser("show", help="show a single strategy")
    sh.add_argument("--id", required=True)
    sh.set_defaults(func=cmd_show)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
