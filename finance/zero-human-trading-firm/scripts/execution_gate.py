#!/usr/bin/env python3
"""
Execution Gate

Deterministic paper->live promotion check. Reads a strategy from the
strategy ledger and decides whether it's eligible to be flipped to live.

All thresholds are configurable, but defaults are conservative:
    - Minimum paper trades:  30
    - Paper Sharpe floor:     1.0
    - Paper max drawdown:     10%
    - Red Team sign-off:      required
    - Risk Officer sign-off:  required

The promotion is NOT automatic even if all checks pass. This tool
returns a verdict; the actual state change to 'live' should be a
deliberate human (or dual-agent signature) action.

Usage:
    python execution_gate.py promote --id STR-0001 --ledger strategy_ledger.json
    python execution_gate.py promote --id STR-0001 \
        --min-trades 50 --min-sharpe 1.2 --max-dd 0.08
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple


def load_ledger(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def find(ledger: Dict[str, Any], sid: str) -> Dict[str, Any]:
    for s in ledger["strategies"]:
        if s["id"] == sid:
            return s
    raise SystemExit(f"ERROR: strategy {sid} not found")


def _last_signer(strategy: Dict[str, Any], flag: str) -> str:
    """Find the last event that set `flag` and return the signer id."""
    for event in reversed(strategy.get("_events", []) or []):
        if event.get("type") == "sign" and event.get("payload", {}).get("flag") == flag:
            return event["payload"].get("by", "")
    return ""


def _signer_from_ledger(ledger: Dict[str, Any], sid: str, flag: str) -> str:
    """Find who signed a given flag for strategy sid by scanning ledger events."""
    for event in reversed(ledger.get("events", [])):
        if event.get("id") != sid or event.get("type") != "sign":
            continue
        if event.get("payload", {}).get("flag") == flag:
            return event["payload"].get("by", "")
    return ""


def evaluate(
    strategy: Dict[str, Any],
    min_trades: int,
    min_sharpe: float,
    max_dd: float,
    require_distinct_signers: bool = False,
    ledger: Dict[str, Any] = None,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if strategy["state"] != "paper":
        errors.append(f"state is '{strategy['state']}', must be 'paper' to promote")

    metrics = strategy.get("metrics", {})
    paper_metrics = metrics.get("paper", metrics)  # allow either nested or flat

    trades = int(paper_metrics.get("trades", 0))
    if trades < min_trades:
        errors.append(f"paper trades {trades} < required {min_trades}")

    sharpe = float(paper_metrics.get("sharpe", 0.0))
    if sharpe < min_sharpe:
        errors.append(f"paper sharpe {sharpe:.3f} < floor {min_sharpe:.3f}")

    dd = float(paper_metrics.get("max_dd", 1.0))
    if dd > max_dd:
        errors.append(f"paper max drawdown {dd:.2%} > cap {max_dd:.2%}")

    flags = strategy.get("flags", {})
    if not flags.get("red_team_signed_off"):
        errors.append("red_team_signed_off = False")
    if not flags.get("risk_officer_signed_off"):
        errors.append("risk_officer_signed_off = False")

    if require_distinct_signers and ledger is not None and not errors:
        rt_signer = _signer_from_ledger(ledger, strategy["id"], "red_team_signed_off")
        ro_signer = _signer_from_ledger(ledger, strategy["id"], "risk_officer_signed_off")
        if not rt_signer or rt_signer == "unknown":
            errors.append("red_team signer identity missing (use --by when signing)")
        if not ro_signer or ro_signer == "unknown":
            errors.append("risk_officer signer identity missing (use --by when signing)")
        if rt_signer and ro_signer and rt_signer == ro_signer:
            errors.append(
                f"red_team and risk_officer signed by same identity '{rt_signer}' "
                f"— founder mode requires distinct signers"
            )

    return (len(errors) == 0), errors


def cmd_promote(args: argparse.Namespace) -> int:
    ledger = load_ledger(args.ledger)
    strategy = find(ledger, args.id)
    ok, errors = evaluate(
        strategy,
        args.min_trades,
        args.min_sharpe,
        args.max_dd,
        require_distinct_signers=args.founder_mode,
        ledger=ledger,
    )
    result = {
        "id": args.id,
        "name": strategy["name"],
        "current_state": strategy["state"],
        "promotion_eligible": ok,
        "errors": errors,
        "thresholds": {
            "min_trades": args.min_trades,
            "min_sharpe": args.min_sharpe,
            "max_dd": args.max_dd,
            "founder_mode": args.founder_mode,
        },
        "metrics": strategy.get("metrics", {}),
    }
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if ok:
            print(f"{args.id}: ELIGIBLE FOR PROMOTION to live")
            print("  Proceed with deliberate sign-off action (not automatic).")
        else:
            print(f"{args.id}: NOT ELIGIBLE")
            for e in errors:
                print(f"  - {e}")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Paper->live promotion gate")
    sub = p.add_subparsers(dest="cmd", required=True)
    pm = sub.add_parser("promote", help="check promotion eligibility")
    pm.add_argument("--id", required=True)
    pm.add_argument("--ledger", default="strategy_ledger.json")
    pm.add_argument("--min-trades", type=int, default=30)
    pm.add_argument("--min-sharpe", type=float, default=1.0)
    pm.add_argument("--max-dd", type=float, default=0.10)
    pm.add_argument(
        "--founder-mode",
        action="store_true",
        help="require distinct signer identities for red_team and risk_officer sign-offs",
    )
    pm.add_argument("--format", default="text", choices=["text", "json"])
    pm.set_defaults(func=cmd_promote)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
