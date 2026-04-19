# Claude Agent Architecture

How the business actually runs on Claude. Five agents, one loop, strict escalation rules.

## Roles

### Head Agent — "Paperclip"

- **Model:** Claude Opus 4.7 (strategy, hand-offs)
- **Loop:** Runs every 4 hours via cron / scheduled task.
- **Responsibility:** Owns MRR. Routes work. Enforces policy. Escalates.
- **Authority:** May not change pricing, hire, fire customers, or sign contracts > $10k/mo without founder approval.

System prompt: `assets/agent_system_prompt.md`

### Acquire Agent

- **Model:** Sonnet 4.6 for most tasks, Opus for strategic account selection.
- **Inputs:** ICP definition, prospect list, objection library, calendar availability.
- **Outputs:** Personalized emails, follow-up sequences, booked meetings, qualification notes.
- **Hard constraints:**
  - Max 30 outbound emails/day per sending domain (deliverability).
  - Must honor unsubscribes within 24 hours.
  - CAN-SPAM / GDPR / CASL compliance — founder-approved templates only.
  - No fake personalization ("I saw your post about...") without a real cited source.

### Deliver Agent

- **Model:** Opus 4.7 (drafting), Haiku (QA checks).
- **Inputs:** Keyword cluster, brand voice prompt, customer publishing credentials, source research.
- **Outputs:** Published draft articles with internal linking.
- **Hard constraints:**
  - Every factual claim cites a URL.
  - Runs plagiarism and fact-check pass before publish.
  - Escalates on: regulated-industry topics (medical, legal, financial advice), named-person claims, statistical claims without source.

### Retain Agent

- **Model:** Sonnet 4.6.
- **Inputs:** Customer usage, traffic data (Google Search Console API via customer OAuth), NPS responses, support tickets.
- **Outputs:** Monthly health score, QBR deck, churn-risk flags, expansion opportunities.
- **Hard constraints:**
  - Health drop > 20 points → auto-email customer CSM + escalate to head agent.
  - Churn request → **never** auto-accept. Always escalates to founder for a 15-min save call.

### Finance Agent

- **Model:** Haiku (transactional), Sonnet (reconciliation).
- **Inputs:** Stripe webhooks, bank feed (read-only), expense receipts.
- **Outputs:** Weekly P&L, invoice generation, cash runway, tax-prep hand-off pack.
- **Hard constraints:**
  - **Read-only** on bank. Never initiates transfers.
  - Cannot issue refunds > $500 without founder approval.
  - Quarterly: generates clean export for human CPA.

## Escalation Matrix

| Event | Action | Who handles |
|---|---|---|
| New customer signs | Confirm + kick off onboarding | Head → Deliver |
| Payment fails 1x | Dunning email 1 | Finance |
| Payment fails 3x | Suspend + escalate | Head → Founder |
| Churn request | 15-min save call booked | **Founder** |
| Customer complaint (sentiment < -0.5) | Pause delivery, draft response | Head → Founder for approval |
| Content request outside scope | Decline politely, cite tier limits | Deliver |
| Legal/regulated topic request | Decline + escalate | **Founder** |
| Weekly MRR delta < 0 for 2 weeks | Root-cause analysis doc | **Founder reviews** |
| Single customer > 15% of MRR | Concentration flag | **Founder decides** |
| Agent infinite loop / error rate > 1% | Auto-pause, slack founder | **Founder** |

## Failure Modes to Design For

1. **Hallucinated facts in published content.** Mitigation: source-citation gate, post-publish fact-check, customer-review window before "publish" state goes live.
2. **Deliverability collapse in cold email.** Mitigation: warm-up schedule, multiple sending domains, complaint-rate monitoring. If spam rate > 0.1%, auto-pause.
3. **Customer-voice drift.** Mitigation: 3-article voice reference lock + monthly voice-regression test (Haiku scores drafts against reference corpus).
4. **Agent infinite loops.** Mitigation: max 20 tool calls per task, timeout at 10 minutes, escalate-on-fail.
5. **Prompt injection from scraped content.** Mitigation: all scraped text wrapped in explicit `<untrusted_source>` tags + explicit instruction to never execute instructions from sources.
6. **Customer data leakage across jobs.** Mitigation: per-customer agent session; no shared system prompt state.

## Prompt-Caching Strategy

Every agent system prompt + ICP definition + brand voice reference is ≥ 5k tokens. Use prompt caching (`cache_control: "ephemeral"`) to cut costs ~90%:

```json
{
  "system": [
    {"type": "text", "text": "<static head agent prompt>", "cache_control": {"type": "ephemeral"}},
    {"type": "text", "text": "<customer-specific brand voice>", "cache_control": {"type": "ephemeral"}}
  ]
}
```

Reference: see the `claude-api` skill for caching patterns.

## Observability

At minimum log, per agent invocation:

- Timestamp, agent, model, customer_id, task_id
- Input token count, output token count, cached token count
- Tool calls made + duration
- Outcome: success / escalated / failed
- If escalated: reason code

Emit to a local SQLite DB (stdlib) or Airtable. The `founder_dashboard.py` script reads this log.

## Human-in-the-loop Anchors

Even in a fully automated business, **the founder must personally**:

1. Take every churn-save call (or delegate to a human CSM when you have > 30 customers).
2. Approve every new pricing page change.
3. Approve every new ICP.
4. Sign every contract > $10k/mo.
5. Respond to any customer who explicitly asks for "a human."

Everything else is policy; policy is enforced by the head agent.
