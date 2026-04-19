# Finance Ops Playbook

_Owner: CFO agent. Not legal or tax advice — founder should consult a CPA before final structure._

## Current Structure (Phase 0, Day 1–30)

- **Legal entity:** None. Founder operates as sole proprietor by default (US).
- **Revenue collection:** N/A (pre-revenue).
- **Expenses:** Paid on founder's personal card, tracked in `budget-ledger.md`.
- **Tax treatment:** Any Phase 0 revenue reports on founder's personal Schedule C.

## Why Deferral is Safe Right Now

- Zero revenue for first 30 days (SEO ramp)
- No employees or contractors being paid
- No services rendered to end users (we're an info/referral layer)
- Stripe + personal bank works fine for <$1K/mo sole prop

## Incorporation Triggers (any one activates Phase 1 finance setup)

- First paying contractor subscription ($49/mo+)
- First lead-sale transaction
- Hiring a VA or contractor
- Revenue ≥$500/mo aggregate across portfolio
- Any complaint, demand letter, or liability concern

## Phase 1 Setup (when trigger hits)

Budget: ~$100–$350 total, ~3 hours of founder time (this is part of Budget Gate #2 ask).

| Step | Action | Tool | Cost | Time |
|---|---|---|---|---|
| 1 | File LLC in founder's home state | Northwest Registered Agent / Bizee / state portal | $50–200 | 45 min |
| 2 | Get EIN from IRS | https://irs.gov/businesses/employer-identification-number | $0 | 10 min |
| 3 | Draft operating agreement (single-member LLC) | Free template from state bar or LawDepot | $0 | 30 min |
| 4 | Open business bank account | **Mercury** (recommended) — free, no minimums, online | $0 | 20 min |
| 5 | Create Stripe account under LLC | https://stripe.com | $0 | 30 min |
| 6 | Wire Stripe payouts to Mercury | Stripe dashboard | $0 | 5 min |

**Alternative (richer setup):** Stripe Atlas = $500 one-shot (Delaware C-Corp + bank + legal docs). Use if planning to raise VC/institutional capital. Overkill otherwise.

## Phase 2 Setup (Day 90+ if portfolio MRR ≥$1K)

- Add bookkeeping: **QuickBooks Simple Start** ($30/mo) or **Wave** (free)
- Engage a CPA for quarterly reviews (~$500–1,500/yr)
- Consider **S-corp election** if net income >$50K/yr (payroll tax savings)
- Business credit card (Brex, Ramp, or AmEx Blue Business)

## Revenue Flow Diagram

```
Phase 0 (sole prop):
  Customer → Stripe Checkout → Founder's personal bank → founder's Schedule C

Phase 1 (LLC):
  Customer → Stripe (under LLC) → Mercury (LLC bank) → LLC K-1 / 1065

Phase 2 (S-corp, if elected):
  Customer → Stripe (under S-corp) → Mercury → founder salary + distribution
```

## Stripe Account Setup (when ready)

- **Business type:** Individual (Phase 0) → LLC (Phase 1+)
- **Products to create:**
  - Featured Listing Basic ($49/mo recurring)
  - Featured Listing Pro ($99/mo recurring)
  - Featured Listing Agency ($249/mo recurring)
  - Lead Sale Shared ($40 one-time)
  - Lead Sale Exclusive ($125 one-time)
- **Stripe fees:** 2.9% + $0.30 per transaction
- **Net on $75/mo blended subscription:** ~$72/mo after fees

## Banking Recommendation: Mercury

| Feature | Mercury | Traditional bank |
|---|---|---|
| Setup time | 20 min online | 1–3 days in branch |
| Monthly fees | $0 | $10–25 |
| Min balance | $0 | $500–5,000 |
| API access | Yes | Rare |
| FDIC insured | Yes (up to $5M via sweep network) | Yes ($250K) |
| Cash in/out | ACH, wire, check | All + cash deposits |

Mercury is the default for modern online businesses. Faster than any brick-and-mortar.

## Sales Tax / Nexus Considerations

- Directory subscriptions ("digital services") are **taxable in ~15 states** (NY, PA, WA, TX, OH, etc.)
- For Phase 0: ignore. Sales tax nexus thresholds are typically $100K/yr or 200 transactions per state
- At Phase 1, use **Stripe Tax** ($0.40/transaction) to auto-calculate — saves CPA fees later

## Tax Calendar (Phase 1+)

| When | What |
|---|---|
| Quarterly (Apr/Jun/Sep/Jan) | Federal estimated tax (Form 1040-ES) |
| Jan 31 | 1099-NECs to any contractors paid >$600 (VAs, freelancers) |
| Mar 15 | S-corp / partnership returns (Form 1120-S / 1065) |
| Apr 15 | Personal return + LLC K-1 integration |

## What the Founder Does NOT Need to Do

- No need for a separate physical office
- No need for business phone / PO box (your home address is fine on LLC filing, or use a registered agent)
- No need for business insurance in Phase 0 (add at Phase 2 once revenue >$5K/mo — about $500/yr for E&O + general liability)
- No need for a CPA until Phase 1 revenue >$1K/mo

## Red Flags That Require Immediate Legal Review

- Contractor threatens legal action over listing accuracy
- Customer claims they were misled by a listing
- Any subpoena or regulatory inquiry
- Acquisition offer >$50K

For any of these, pause operations and consult a business attorney (~$300–500/hr, 1 hour usually resolves scope).
