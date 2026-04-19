# Founder Quickstart

**Plain-English setup for non-technical founders.** Follow these steps in order. Nothing here costs more than ~$30/mo or risks real money until you explicitly approve it.

**Honest time commitment:**
- **Setup:** ~90 minutes spread over a day (the steps below). You can pause at any numbered step.
- **First 90 days:** ~30 min/week reading the Sunday CEO note and tightening role instructions.
- **After 90 days:** ~15 min/month reading the founder report and approving/declining the one recommended action.

If anyone (including me) sells you "10 min/month from day one," they're selling a fantasy. A fresh AI trading firm needs babysitting until its taste is trained.

---

## Before you start: shopping list

Buy / sign up for these. You only do this once.

| # | Thing | Where | Cost | Time |
|---|-------|-------|------|------|
| 1 | Main VPS (8 GB RAM, Ubuntu 22.04) | Hetzner, DigitalOcean, Linode — your choice | ~$20/mo | 5 min |
| 2 | Risk host VM (1 GB RAM, Ubuntu 22.04) | **Different account/provider from #1** | ~$5/mo | 5 min |
| 3 | IB paper-trading account | alredy have this via your IB login | free | 2 min to enable API |
| 4 | Claude Code subscription | claude.ai | $20/mo | 2 min |

**Why two different providers?** If one account is compromised, the attacker can't reach both. This is the single most important setup rule.

After you finish the shopping list, you'll have **two IP addresses** (call them `<VPS_IP>` and `<RISK_IP>`) and **one IB paper account number** (looks like `DU1234567`).

---

## Step 1 — Set up the main VPS (~10 min)

Open a terminal on your laptop.

```
ssh root@<VPS_IP>
```

Paste the password your VPS provider emailed you. Then on the VPS:

```
curl -sSL https://raw.githubusercontent.com/daraseng978-lang/claude-skills/main/finance/zero-human-trading-firm/scripts/install_vps.sh | bash -s -- lewis-ventures
```

(Replace `lewis-ventures` with your firm's slug. Lowercase, hyphens only.)

Wait ~5 minutes. When it finishes, it prints the next steps.

**Now visit `https://<VPS_IP>/` in your browser.** Finish Paperclip's onboarding wizard:
- Firm name: e.g. "Lewis Ventures"
- Default harness: **Claude Code**
- Leave everything else at defaults

---

## Step 2 — Set up the risk host (~5 min)

SSH into the **second** VM:

```
ssh root@<RISK_IP>
```

Run the install script, passing your main VPS's IP so the firewall only accepts connections from there:

```
curl -sSL https://raw.githubusercontent.com/daraseng978-lang/claude-skills/main/finance/zero-human-trading-firm/scripts/install_risk_host.sh | bash -s -- <VPS_IP>
```

When it finishes, it prints **two things you MUST save:**
- A URL like `http://<RISK_IP>:8443` — save as `<RISK_HOST_URL>`
- A long random bearer token — save as `<RISK_HOST_TOKEN>`

Put them in a password manager now. The token is not displayed again.

---

## Step 3 — Enable IB API access (~5 min)

In IB Client Portal (on your laptop, not the VPS):

1. **Account Management → Settings → API → Settings**
2. Check "Enable ActiveX and Socket Clients"
3. Add a trusted IP: `<VPS_IP>`
4. Set "Read-Only API": **off** (the agents need to place orders)
5. Save

Write down your **paper account ID** (starts with `DU`, e.g. `DU1234567`).

---

## Step 4 — Skip this step

The CEO agent installs IB Gateway + IBC for you in Step 5. If you tried to do it yourself you'd land in a GUI/VNC rabbit hole that isn't worth the hour. Keep moving.

(You'll hand the CEO your IB paper account ID and your IB login password, one-time, through Paperclip's Secret Manager — never in chat, never in a role instruction file. The agent has the `engineering/ci-cd-pipeline-builder` skill attached for exactly this.)

---

## Step 5 — Hand off to the CEO agent (~20 min + wait)

On your laptop, open `finance/zero-human-trading-firm/CEO_BOOTSTRAP.md` (or paste the link into the CEO chat).

**Fill in every `<ALL_CAPS>` placeholder.** Use the values you saved:

| Placeholder | Value |
|-------------|-------|
| `<VPS_HOST>` | `agent@<VPS_IP>` |
| `<RISK_HOST_URL>` | from step 2 |
| `<RISK_HOST_TOKEN>` | from step 2 |
| `<BROKERAGE>` | `ib-paper` |
| `<BROKERAGE_KEY>` | your IB paper account ID (e.g. `DU1234567`) |
| `<BROKERAGE_SECRET>` | `IB Gateway on localhost:4002` |
| `<FIRM_NAME>` | e.g. `Lewis Ventures` |
| `<VENUE>` | `equities-us` (or `crypto-spot` if that's your focus) |
| `<SKILLS_REPO_PATH>` | `/opt/claude-skills` |

In Paperclip, open the CEO seat. Paste the whole filled-in brief as the first message.

The CEO will run through its checklist and stop twice to ask you:
- **"Can I touch the risk host?"** — answer: "no, you can only POST to `/risk/check`". If the CEO says it CAN touch the risk host, something is wrong — tell it to stop and re-run `install_risk_host.sh`.
- **"Ready for paper trading?"** — the CEO will send you a one-page readiness note. Read it. Approve or push back.

---

## Step 6 — First 30 days (~10 min/week)

Paper trading only. Your job each week:
- Read the Sunday weekly note from the CEO
- If role output is sloppy, tell the CEO to tighten that role's instructions

**Do not fund real money yet.** Let the firm produce at least one full monthly founder report on paper.

---

## Step 7 — Month 2: real money decision (~10 min/month)

On the 1st of each month, Paperclip drops a **founder report** in your inbox. One page. It recommends one of three actions:

| Report says | You do |
|-------------|--------|
| "Fund another tranche" | SSH in, run `python3 capital_allocator.py fund --amount X --note "..."` |
| "Sweep profit" | SSH in, run `python3 capital_allocator.py withdraw --amount X --note "..."` |
| "Stay the course" | Nothing. |

To move a strategy from paper to live, the CEO will ask you. You must verify:
1. Three consecutive profitable paper months
2. Red Team and Risk Officer sign-offs from **different** agent identities (the `--founder-mode` flag enforces this)
3. You're comfortable with the worst-case drawdown in the last 90 days of paper

If any of the three fails, say no. No pressure — the firm keeps running on paper.

---

## Escape hatches

In order of escalation. If level 1 doesn't work, go to level 2. If level 2 doesn't work, go to level 3. Don't panic — these exist because the CEO agent WILL hallucinate eventually and you need to know you can always win.

**Level 1 — Tell the CEO in chat.** "Halt all trading." It flattens positions and stops. Works when the CEO agent is responsive.

**Level 2 — Stop Paperclip from the command line.** On your laptop:
```
ssh agent@<VPS_IP> 'sudo systemctl stop paperclip'
```
This kills the agent orchestration. The risk service (on the other VM) is still up, but nobody's sending orders. Works when the CEO is hallucinating, looping, or ignoring you.

**Level 3 — Manual liquidation in IB Client Portal.** If Paperclip is wedged AND you have live positions you want closed, do it yourself:
1. Log in to IB Client Portal on your laptop
2. Orders & Trades → cancel every open order
3. Positions → right-click any position → Close Position → MKT order
4. Verify Account Summary shows flat (zero positions, no open orders)

Keep IB Client Portal bookmarked. You don't want to be searching for it at 2am.

**Level 4 — Shut everything down.** Destroy both VMs from the provider dashboards. You lose ~$25 and nothing else, because you stayed in paper. You can rebuild from a fresh `install_vps.sh` + `install_risk_host.sh` anytime.

---

## What happens if you disappear for 2 weeks

Weddings, vacations, broken wrists — you will eventually be unreachable. Defaults are set so the firm survives your absence without doing anything stupid.

**In paper mode (first 30+ days — your likely state):**
- The firm keeps paper trading. No risk to you.
- Weekly notes and monthly reports queue up in Paperclip. Read them when you get back.
- No paper→live promotions happen without your reply. The CEO will ask, wait 72 hours per the escalation rule, and then mark the request **declined** automatically. You won't come back to find a live strategy.

**In live mode (if/when you get there):**
- Live strategies keep trading within `risk_policy.json` limits.
- The firm kill switch (`firm_kill_switch_monthly_pct`, default 15%) auto-flattens everything if monthly drawdown breaches it. No human required.
- Any proposed risk-policy change auto-declines after 72 hours of silence.
- Any new tranche / withdrawal request auto-declines after 72 hours of silence.

**If your internet dies for a day:** nothing happens to your money. Paperclip is on the VPS, not your laptop. The agents keep running. You catch up when you're back online.

**If your PagerDuty / phone push fails during a kill-switch event:** the kill switch still fires. Trading halts. You'll find out when you check the dashboard. Positions are flat; the worst case is lost opportunity, not lost capital.

**Set up before you go:** put the VPS IP, risk host IP, and IB account ID in your password manager. Tell one trusted person how to run Level 2 and Level 3. That's the only "second pair of eyes" you need.

---

## Common troubles

| Symptom | Cause | Fix |
|---------|-------|-----|
| Paperclip dashboard won't load at `https://<VPS_IP>/` | cert not issued yet | wait 2 minutes, try again |
| CEO says "can't reach risk host" | firewall on risk host doesn't allow your VPS IP | re-run `install_risk_host.sh <VPS_IP>` on the risk host |
| IB Gateway logs out at midnight and nothing reconnects | IBC not running | ask the CEO to set up IBC with 2FA = "IBKR Mobile" |
| Founder report never arrives | routine not wired | ask the CEO to re-read `PAPERCLIP.md` section 6 |
| CEO is proposing edits to `risk_policy.json` | hard rule violation | reject the PR; tell the CEO to read its own hard-rules section |

---

## What you are NOT expected to do

- Write code
- Debug Python
- Know what "OOS" or "Sharpe" means (the CEO explains in plain English if you ask)
- Stay awake for any routine

Everything technical is the CEO agent's job. You are the board; you approve capital, you read one page a month, and you can kill the firm at any time.
