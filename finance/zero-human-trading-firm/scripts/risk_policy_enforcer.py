#!/usr/bin/env python3
"""
Risk Policy Enforcer

Deterministic hard-constraint check for any proposed order. The agents
propose orders; this tool disposes of ones that violate the policy.

**This tool is useless if agents can redeploy it.** Host it behind an API
boundary the agents can call but cannot push code to. Treat the policy
file and this script as firm-level infrastructure, not per-strategy code.

Checks enforced:
    - Per-position size vs equity cap
    - Per-asset exposure cap (existing + proposed)
    - Portfolio gross exposure ceiling
    - Portfolio net exposure ceiling
    - Daily drawdown circuit breaker
    - Max leverage
    - Venue whitelist

Order JSON schema:
    {
      "asset": "BTC-PERP",
      "side": "buy" | "sell",
      "quantity": 0.5,
      "price": 65000.0,
      "venue": "hyperliquid"
    }

Portfolio state JSON schema:
    {
      "equity": 100000.0,
      "starting_equity_today": 102000.0,
      "positions": {
        "BTC-PERP": {"quantity": 0.1, "avg_price": 64000.0},
        "ETH-PERP": {"quantity": -1.0, "avg_price": 3200.0}
      }
    }

Policy JSON schema: see assets/risk_policy.json.

Usage:
    python risk_policy_enforcer.py check --order order.json \
        --state portfolio.json --policy risk_policy.json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple


def load(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def signed_qty(side: str, qty: float) -> float:
    return qty if side == "buy" else -qty


def position_notional(pos: Dict[str, float], mark: float) -> float:
    return pos["quantity"] * mark


def check(order: Dict[str, Any], state: Dict[str, Any], policy: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    # 0) Venue whitelist
    whitelist = policy.get("venue_whitelist")
    if whitelist and order.get("venue") not in whitelist:
        errors.append(f"venue '{order.get('venue')}' not in whitelist {whitelist}")

    equity = float(state["equity"])
    if equity <= 0:
        errors.append("non-positive equity: halt all trading")
        return False, errors

    # 1) Daily drawdown circuit breaker
    start_eq = float(state.get("starting_equity_today", equity))
    daily_dd_cap = float(policy.get("max_daily_drawdown", 0.05))
    if start_eq > 0:
        dd_today = max(0.0, (start_eq - equity) / start_eq)
        if dd_today >= daily_dd_cap:
            errors.append(
                f"daily drawdown {dd_today:.2%} >= cap {daily_dd_cap:.2%} — circuit breaker tripped"
            )

    # Prospective position after fill
    asset = order["asset"]
    side = order["side"]
    qty = float(order["quantity"])
    price = float(order["price"])
    signed = signed_qty(side, qty)

    positions: Dict[str, Dict[str, float]] = dict(state.get("positions", {}))
    current = positions.get(asset, {"quantity": 0.0, "avg_price": price})
    new_qty = current["quantity"] + signed
    prospective_positions = dict(positions)
    prospective_positions[asset] = {"quantity": new_qty, "avg_price": price}

    # 2) Per-position size cap (notional / equity)
    pos_notional = abs(new_qty * price)
    per_pos_cap = float(policy.get("max_position_pct", 0.10))
    if equity > 0 and (pos_notional / equity) > per_pos_cap:
        errors.append(
            f"position notional {pos_notional:.0f} = "
            f"{pos_notional/equity:.2%} of equity > cap {per_pos_cap:.2%}"
        )

    # 3) Per-asset exposure cap (for paired hedged books)
    per_asset_caps: Dict[str, float] = policy.get("per_asset_caps", {})
    if asset in per_asset_caps:
        cap = per_asset_caps[asset]
        if equity > 0 and (pos_notional / equity) > cap:
            errors.append(
                f"asset {asset} exposure {pos_notional/equity:.2%} > per-asset cap {cap:.2%}"
            )

    # 4) Gross and net exposure
    gross = sum(abs(p["quantity"] * p.get("avg_price", price)) for p in prospective_positions.values())
    net = sum(p["quantity"] * p.get("avg_price", price) for p in prospective_positions.values())
    gross_cap = float(policy.get("max_gross_exposure", 2.0))
    net_cap = float(policy.get("max_net_exposure", 1.0))
    if equity > 0:
        if (gross / equity) > gross_cap:
            errors.append(f"gross exposure {gross/equity:.2f}x > cap {gross_cap:.2f}x")
        if abs(net / equity) > net_cap:
            errors.append(f"net exposure {net/equity:+.2f}x > cap +/-{net_cap:.2f}x")

    # 5) Max leverage (same as gross for linear books, but separated for clarity)
    max_lev = float(policy.get("max_leverage", 3.0))
    if equity > 0 and (gross / equity) > max_lev:
        errors.append(f"implied leverage {gross/equity:.2f}x > max {max_lev:.2f}x")

    return (len(errors) == 0), errors


def cmd_check(args: argparse.Namespace) -> int:
    order = load(args.order)
    state = load(args.state) if args.state else {"equity": 0, "starting_equity_today": 0, "positions": {}}
    policy = load(args.policy)

    ok, errors = check(order, state, policy)
    result = {
        "approved": ok,
        "errors": errors,
        "order": order,
    }
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if ok:
            print("APPROVED")
        else:
            print("REJECTED")
            for e in errors:
                print(f"  - {e}")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Hard-constraint risk policy check")
    sub = p.add_subparsers(dest="cmd", required=True)
    ch = sub.add_parser("check", help="validate an order against policy")
    ch.add_argument("--order", required=True, help="order JSON path")
    ch.add_argument("--state", default="", help="portfolio state JSON path")
    ch.add_argument("--policy", required=True, help="risk policy JSON path")
    ch.add_argument("--format", default="text", choices=["text", "json"])
    ch.set_defaults(func=cmd_check)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
