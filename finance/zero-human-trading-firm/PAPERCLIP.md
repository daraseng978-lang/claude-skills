# Deploying this firm on Paperclip

End-to-end guide for running your zero-human trading firm on a local VPS using [Paperclip](https://paperclip.ng) as the orchestration layer. This skill supplies the opinionated content (org chart, lifecycle, risk policy, CLI tools); Paperclip supplies the dashboard, agent orchestration, approvals, routines, and memory.

## Why Paperclip for founder mode

Founder mode means you only touch the firm for **budget decisions**. Paperclip provides the properties that make that workable:
- A dashboard where you can see every running strategy and approve a capital tranche with one click
- Per-role memory and instructions (so agents don't forget your taste)
- Configurable reviewers/approvers on critical issues
- Skills manager (so the scripts in this folder become callable skills)
- Routines on a cron (for nightly research + daily P&L reports)

## Prerequisites

- A VPS with Docker (2+ vCPU, 4 GB RAM minimum; 8 GB comfortable)
- Claude Code OR Codex subscription (for the CEO/CTO agent harness)
- Ports 443 + 80 (or a reverse proxy) for the dashboard
- A separate host or container that runs `risk_policy_enforcer.py` behind an HTTP API — **this must not be something the agents can deploy to**

## 1. Install Paperclip on the VPS

```bash
curl -sSL https://paperclip.ng/install | bash
paperclip start --host 0.0.0.0 --port 443
```

Visit `https://<your-vps>/` and complete the onboarding. Name your firm (e.g., "Lewis Ventures") and pick Claude Code as the default harness.

## 2. Scaffold the firm content

Run `firm_init.py` once to produce the on-disk artifacts Paperclip will read:

```bash
mkdir -p ~/firms/lewis-ventures
python3 /path/to/claude-skills/finance/zero-human-trading-firm/scripts/firm_init.py \
  --name "Lewis Ventures" \
  --venue bittensor \
  --out ~/firms/lewis-ventures
```

This produces `FIRM.md`, `roles/*.md` (one per role), `risk_policy.json`, `strategy_ledger.json`, `capital_ledger.json`, and `org_chart.json`.

## 3. Import the org chart into Paperclip

In the Paperclip dashboard:
1. Go to **Org chart** → **Import**
2. Select `~/firms/lewis-ventures/org_chart.json`
3. Paperclip creates 8 agent seats: CEO, CTO, Strategy Researcher, Backtest Engineer, Red Team, Risk Officer, Execution Engineer, Accountant

For each role, the imported JSON includes **recommended_skills** — paths into this repository. In Paperclip, go to each role and attach the listed skills via the Skills Manager:

| Role | Skills to attach |
|------|------------------|
| CEO | `agents/c-level/cs-ceo-advisor.md`, `finance/zero-human-trading-firm/SKILL.md` |
| CTO | `agents/c-level/cs-cto-advisor.md`, `engineering-team/senior-data-engineer/SKILL.md` |
| Strategy Researcher | `engineering/autoresearch-agent/SKILL.md`, `engineering-team/senior-data-scientist/SKILL.md` |
| Backtest Engineer | `engineering-team/senior-data-scientist/SKILL.md`, `engineering-team/tdd-guide/SKILL.md` |
| Red Team | `engineering-team/red-team/SKILL.md`, `engineering-team/adversarial-reviewer/SKILL.md` |
| Risk Officer | `engineering-team/incident-commander/SKILL.md`, `finance/financial-analyst/SKILL.md` |
| Execution Engineer | `engineering/ci-cd-pipeline-builder/SKILL.md`, `engineering-team/senior-backend/SKILL.md` |
| Accountant | `finance/financial-analyst/SKILL.md`, `finance/saas-metrics-coach/SKILL.md` |
| **QA on reports** | `engineering/self-eval/SKILL.md` (attach as reviewer on CEO reports to catch score inflation) |

## 4. Configure the "Founder" seat (you)

Paperclip doesn't need an agent for the founder — that's you. Configure:

1. **Skills on your profile:** `agents/personas/finance-lead.md`, `finance/business-investment-advisor/SKILL.md` — so when you open the chat, you get capital-allocation-first thinking.
2. **Notifications:** subscribe only to:
   - `monthly_founder_report` routine output
   - `firm_kill_switch` events
   - CEO requests for a new capital tranche

Everything else is noise; mute it.

## 5. Wire the risk policy service (critical)

**Do not host `risk_policy_enforcer.py` inside the Paperclip container.** Host it on a separate machine/container that the agents can reach via HTTP but cannot deploy to.

Minimal setup on a second box:

```bash
# on a host the trading agents can CALL but not DEPLOY to
pip install fastapi uvicorn
cat > risk_service.py <<'EOF'
from fastapi import FastAPI, HTTPException
import json, subprocess, tempfile, os
app = FastAPI()
POLICY = "/etc/risk_policy.json"  # root-owned, immutable to the agent user

@app.post("/risk/check")
def check(payload: dict):
    order = payload["order"]; state = payload.get("state", {})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as of, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as sf:
        json.dump(order, of); of.flush(); json.dump(state, sf); sf.flush()
        rc = subprocess.run(
            ["python3", "/opt/risk/risk_policy_enforcer.py", "check",
             "--order", of.name, "--state", sf.name, "--policy", POLICY, "--format", "json"],
            capture_output=True, text=True
        )
    os.unlink(of.name); os.unlink(sf.name)
    return json.loads(rc.stdout)
EOF
uvicorn risk_service:app --host 0.0.0.0 --port 8443
```

Permissions that matter:
- The agent user on the Paperclip host has no SSH, no kubectl, no git push access to this host.
- The risk policy file is root-owned on the risk host. The agent can never edit it.
- Deploys of this service require your signature. Use a signed webhook or a deliberate PR review.

Then in each agent's instructions (especially Execution Engineer):
> Every order you propose MUST first pass `POST https://<risk-host>:8443/risk/check`. If the service returns `approved: false`, DO NOT proceed. Report the rejection and stop.

## 6. Wire the routines

In Paperclip, create these routines (Cron-triggered tasks):

| Routine | Schedule | Owner | Output |
|---------|----------|-------|--------|
| Nightly research digest | 00:00 UTC | Strategy Researcher | `daily_reports/YYYY-MM-DD.md` |
| Backtest queue | 06:00 UTC | Backtest Engineer | advance strategies `proposed → backtested` |
| Red team window | 12:00 UTC | Red Team | `postmortems/redteam/STR-*.md` |
| Daily P&L | 18:00 UTC | Accountant | `daily_reports/pnl-YYYY-MM-DD.md` |
| Weekly review | Sun 20:00 UTC | CEO | weekly note |
| **Monthly founder report** | 1st of month 09:00 UTC | CEO + self-eval reviewer | `daily_reports/founder-YYYY-MM.md` |

The monthly founder report is the one that lands in your inbox. Attach `engineering/self-eval/SKILL.md` as a reviewer on this routine so a second agent scores the CEO's report for honesty before it reaches you — this catches score inflation.

## 7. Configure reviewers + approvers

In Paperclip, for each issue type:

| Issue | Reviewers | Approvers |
|-------|-----------|-----------|
| New strategy proposal | Research Engineer | CEO |
| Backtest result | Red Team | Risk Officer |
| Paper→live promotion | Red Team + Risk Officer (distinct agents!) | CEO (or auto in founder mode) |
| New capital tranche | CEO | **FOUNDER** (you) |
| Withdrawal | Accountant | **FOUNDER** (you) |
| Risk policy change | CEO + Risk Officer | **FOUNDER** (you) |
| Firm kill switch | any agent | self-enforcing + founder notification |

**Founder mode** means only the last four rows reach you. Everything else is handled agent-to-agent.

## 8. Founder workflow (monthly)

Your entire involvement looks like this:

1. **1st of the month:** read the founder report that lands in Paperclip (from routine 6). It's one page. Take 10 minutes.
2. Decide one of three things based on the report's "The decision" section:
   - Fund another tranche: `python3 capital_allocator.py fund --amount X --note "month Y budget"`
   - Sweep profit: `python3 capital_allocator.py withdraw --amount X --note "profit sweep"`
   - Stay the course: do nothing.
3. **If a firm kill switch fires** (page or email): open Paperclip, verify trading is halted, decide whether to reset the switch or wind down.

That's it. The rest — research, backtests, red-teaming, execution, daily P&L — happens without you.

## 9. What you'll still want to touch occasionally

Even in founder mode, some events deserve your attention:
- **First 30 days:** review the CEO's weekly notes, tighten any role instruction that produces sloppy output. Your taste is the product.
- **Monthly strategy graveyard:** skim the retirement postmortems. Patterns that emerge should flow back into the Strategy Researcher's instructions.
- **Quarterly risk review:** has any default drifted? Should `max_position_pct` move? This is a PR you review and sign.

## 10. Circuit breakers

Make sure these are real, not aspirational:
- `risk_policy_enforcer.py` rejects trades beyond the policy — hosted where agents can't touch it
- `firm_kill_switch_monthly_pct` in `risk_policy.json` auto-flattens all positions when hit
- Founder's PagerDuty / phone push for kill switch + large CEO requests
- A kill-switch-from-phone: Paperclip has a mobile client; set a hotkey for "HALT"

## Minimum monthly cost estimate

(approximate, 2026 prices — verify)

- VPS (8 GB RAM): $20-40/mo
- Risk host (1 GB VM): $5-10/mo
- Claude Code Pro: $100/mo per heavy user (you can route multiple agent seats through one subscription via harnesses)
- Codex subscription (for dual-harness sign-off): $20/mo
- Data feed: varies wildly. Crypto venues often free; equities L1 data $50-200/mo
- Paperclip: free (open source)

**All-in:** ~$150-400/mo plus whatever data your strategies need.

## Failure modes to watch for

1. **Agents silently drifting.** Schedule a quarterly "role audit" where the CEO writes one paragraph per role describing what it's been doing. Compare to the role's instructions. Drift shows up.
2. **Self-eval not attached.** If the monthly founder report isn't being scored by `self-eval`, the CEO's self-reports will inflate. Always keep self-eval in the reviewer chain.
3. **Risk service drift.** Your agents will try to make the risk service "more helpful." Any PR to that service gets extra scrutiny. If you catch a suggestion that softens a limit, reject it and note the agent/session.
4. **One-harness monoculture.** If both Red Team and Risk Officer run on the same harness and model, their "independent" sign-offs aren't independent. Route them through distinct harnesses (one Claude, one Codex).
