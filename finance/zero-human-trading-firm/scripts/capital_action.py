#!/usr/bin/env python3
"""
Capital Action Signer

Every capital movement (tranche funding, profit withdrawal) is reified
as a signed artifact that the founder approves by committing it to a
private 'firm-actions' git repo. capital_allocator.py will refuse to
move capital without a matching approved artifact.

Workflow:
    1. CEO or founder proposes an action:
         python capital_action.py propose --action fund --amount 10000 \
             --reason "month 2 budget" --out actions/pending/

    2. Founder reviews the JSON, moves it to actions/approved/, and
       commits the move. The git commit is the signature.

         mv actions/pending/A-2026-04-15-fund.json actions/approved/
         git add actions/approved/A-2026-04-15-fund.json
         git commit -sS -m "approve A-2026-04-15-fund: fund +10000"

    3. Operator passes the approved file to capital_allocator.py:

         python capital_allocator.py fund --amount 10000 \
             --action-file actions/approved/A-2026-04-15-fund.json

    4. capital_allocator verifies the file schema + approved_ts, then
       commits the tranche to capital_ledger.json with the action_id
       linked for audit.

Why this exists:
    Capital movement at a shell prompt with no audit trail is how firms
    lose real money to fat fingers. This gives you an immutable log
    (the firm-actions git repo) that ties every dollar in and out to a
    signed founder decision.

Usage:
    python capital_action.py propose --action fund --amount 10000 --reason "..."
    python capital_action.py approve --file actions/pending/A-2026-04-15-fund.json
    python capital_action.py verify --file actions/approved/A-2026-04-15-fund.json
    python capital_action.py list --dir actions/
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

VALID_ACTIONS = {"fund", "withdraw", "risk_policy_change", "kill_switch_reset"}


def action_id(action: str, ts: int) -> str:
    stamp = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    return f"A-{stamp}-{action}"


def cmd_propose(args: argparse.Namespace) -> int:
    if args.action not in VALID_ACTIONS:
        print(f"ERROR: action must be one of {sorted(VALID_ACTIONS)}", file=sys.stderr)
        return 2
    if args.action in ("fund", "withdraw") and args.amount is None:
        print(f"ERROR: --amount required for {args.action}", file=sys.stderr)
        return 2

    ts = int(time.time())
    aid = action_id(args.action, ts)
    artifact: Dict[str, Any] = {
        "id": aid,
        "action": args.action,
        "amount": args.amount,
        "currency": "USD",
        "reason": args.reason,
        "proposed_by": args.proposed_by or "ceo",
        "proposed_ts": ts,
        "approved_ts": None,
        "approved_by": None,
        "schema_version": 1,
    }
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{aid}.json")
    with open(path, "w") as f:
        json.dump(artifact, f, indent=2, sort_keys=True)
    print(f"proposed: {path}")
    print(f"  action:   {args.action}")
    if args.amount is not None:
        print(f"  amount:   {args.amount:+.2f} USD")
    print(f"  reason:   {args.reason}")
    print()
    print("Next step (founder):")
    print(f"  1. read {path}")
    print(f"  2. if approved, run: capital_action.py approve --file {path}")
    print( "  3. commit the moved file with a signed commit:")
    print(f"     git add actions/approved/{aid}.json && git commit -sS -m 'approve {aid}'")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    if not os.path.exists(args.file):
        print(f"ERROR: {args.file} not found", file=sys.stderr)
        return 2
    with open(args.file, "r") as f:
        artifact = json.load(f)
    if artifact.get("approved_ts"):
        print(f"already approved at {artifact['approved_ts']}")
        return 0
    artifact["approved_ts"] = int(time.time())
    artifact["approved_by"] = args.approved_by

    pending_dir = os.path.dirname(args.file)
    approved_dir = os.path.join(os.path.dirname(pending_dir), "approved")
    os.makedirs(approved_dir, exist_ok=True)
    basename = os.path.basename(args.file)
    dest = os.path.join(approved_dir, basename)

    with open(dest, "w") as f:
        json.dump(artifact, f, indent=2, sort_keys=True)
    if os.path.abspath(args.file) != os.path.abspath(dest):
        os.unlink(args.file)
    print(f"approved -> {dest}")
    print("Final step: sign the commit so there's an audit trail:")
    print(f"  git add {dest} && git commit -sS -m 'approve {artifact['id']}'")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    if not os.path.exists(args.file):
        print(f"INVALID: file not found", file=sys.stderr)
        return 2
    with open(args.file, "r") as f:
        artifact = json.load(f)
    errors = []
    for field in ("id", "action", "reason", "proposed_ts", "approved_ts", "approved_by"):
        if field not in artifact:
            errors.append(f"missing field: {field}")
    if artifact.get("action") not in VALID_ACTIONS:
        errors.append(f"invalid action: {artifact.get('action')!r}")
    if artifact.get("action") in ("fund", "withdraw") and artifact.get("amount") is None:
        errors.append(f"action {artifact['action']} requires amount")
    if not artifact.get("approved_ts"):
        errors.append("not approved (no approved_ts)")
    if errors:
        for e in errors:
            print(f"INVALID: {e}")
        return 2
    print(f"OK: {artifact['id']} — {artifact['action']} "
          f"{artifact.get('amount'):+.2f} approved by {artifact['approved_by']}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    if not os.path.isdir(args.dir):
        print(f"ERROR: {args.dir} not a directory", file=sys.stderr)
        return 2
    rows = []
    for root, _, files in os.walk(args.dir):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, "r") as f:
                    a = json.load(f)
            except Exception:
                continue
            state = "approved" if a.get("approved_ts") else "pending"
            rows.append((a.get("id", fn), a.get("action", "?"),
                         a.get("amount"), state, path))
    print(f"{'ID':<30} {'ACTION':<22} {'AMOUNT':>12}  {'STATE':<10} PATH")
    print("-" * 90)
    for aid, act, amt, state, path in rows:
        amt_s = f"{amt:+.2f}" if isinstance(amt, (int, float)) else "-"
        print(f"{aid:<30} {act:<22} {amt_s:>12}  {state:<10} {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Signed capital-action artifacts for founder-mode")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("propose", help="create a pending action artifact")
    pr.add_argument("--action", required=True, choices=sorted(VALID_ACTIONS))
    pr.add_argument("--amount", type=float, default=None)
    pr.add_argument("--reason", required=True)
    pr.add_argument("--proposed-by", default="ceo")
    pr.add_argument("--out", default="actions/pending")
    pr.set_defaults(func=cmd_propose)

    ap = sub.add_parser("approve", help="approve a pending action (founder)")
    ap.add_argument("--file", required=True)
    ap.add_argument("--approved-by", default="founder")
    ap.set_defaults(func=cmd_approve)

    vf = sub.add_parser("verify", help="verify an action file is valid + approved")
    vf.add_argument("--file", required=True)
    vf.set_defaults(func=cmd_verify)

    ls = sub.add_parser("list", help="list all actions under a directory")
    ls.add_argument("--dir", default="actions")
    ls.set_defaults(func=cmd_list)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
