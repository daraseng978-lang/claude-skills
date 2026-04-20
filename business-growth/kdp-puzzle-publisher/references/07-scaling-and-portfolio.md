# 07 — Scaling: 1 → 30 → 100 SKUs

## The power law that runs this business

Out of 100 SKUs, empirically:

| Tier | Share | Per-SKU royalty multiplier |
|---|---|---|
| Home runs | 3% | 4.0× median estimate |
| Winners | 15% | 1.5× |
| Breakeven | 40% | 0.6× |
| Duds | 42% | 0.1× |

The `portfolio_planner.py` script uses these weights. The math means **you need at least 20 SKUs to see reliable performance**, because under 20 you are dominated by variance.

## The three portfolio phases

### Phase 1 — First quarter (SKU 1 → 10)

**Goal:** prove the pipeline works. Do not optimize for revenue yet.

- 3 niches × 3 SKUs = 9 SKUs.
- Publish ~1 SKU/week.
- Do not respond to early sales or reviews. 30-day patience.
- Budget: 20–40 hours of work. ~$100–$200 in design/tool costs.

**Exit criterion:** all 9 SKUs published. At least 1 in review ≥ 4 stars. You understand the full pipeline end-to-end.

### Phase 2 — Second quarter (SKU 10 → 30)

**Goal:** find the winners. Now you have 90 days of data on Phase 1.

- Identify the top 2–3 performers by 60-day royalty.
- Double down on those niches: build 5-SKU series (volumes 1–5), different themes.
- Add 1 new experimental niche to test broader territory.
- Publish 2–3 SKUs/week.

**Exit criterion:** 30 SKUs live. At least one home-run (BSR < 30k, steady). Monthly royalty ≥ $500.

### Phase 3 — Third quarter onward (SKU 30 → 100)

**Goal:** compound. Reinvest winnings into (a) more SKUs in proven niches and (b) operational leverage.

- Automate the interior layout step (LaTeX templates, or paid tooling).
- Hire a freelance cover designer at volume rates (~$20/cover).
- Run $5–10/day Amazon Ads on top 5 SKUs only.
- Cap publishing at ~10 SKUs/week to respect KDP's 3/day cap.
- Start a branded series with a consistent cover look — this compounds the recommendation algorithm.

**Exit criterion:** 100 SKUs live. Monthly royalty ≥ $3k. Decide whether to keep scaling or maintain.

## Compounding mechanisms

Four things that compound if you stay consistent:

1. **Amazon's "Customers also bought" carousel.** Your second SKU in a niche gets traffic from your first, for free.
2. **Series indexing.** "Volume 1, Volume 2" in a branded series gets aggregated on the author page.
3. **Reviews.** Every 30 days, a small fraction of buyers leave reviews. 50 reviews on one SKU is a moat.
4. **Author follow.** Buyers who click "Follow" get emails on new releases. At 500 followers, launch-day velocity pops you to BSR top 1,000 for a day, seeding long-term rankings.

## What kills compounding

- Renaming a pen name. You lose the author page's accumulated authority.
- Deleting old SKUs. Even duds add an author-page SKU count that flatters the follower conversion rate.
- Publishing across 10 unrelated niches on one pen name. Amazon's recommendations don't fire.
- Inconsistent cover style. Buyers of Volume 1 won't recognize Volume 2 on a thumbnail.

## When to kill vs. when to iterate

After 90 days live:

| BSR | 60-day royalty | Action |
|---|---|---|
| < 30,000 | $500+ | Volume 2 immediately |
| 30k–100k | $150–$500 | Add categories, minor subtitle tweak |
| 100k–500k | $20–$150 | Leave alone; passive tail |
| > 500,000 | < $20 | Leave live (free), move on |

Never un-publish. The cost of a dormant SKU is zero, and an occasional $1 royalty is pure profit.

## Operating leverage — what to outsource

In order of ROI:

1. **Cover design.** Freelancer at $15–$30/cover. Your time > $30/hr; covers take 1–2 hrs each.
2. **Interior layout.** Either pay for Book Bolt's designer (one-time cost, infinite books) or invest 8 hours in a LaTeX template.
3. **Solving QA.** Automate with a puzzle solver that outputs a pass/fail report. Don't pay humans to solve puzzles.
4. **Uploading.** Stays manual forever. Amazon requires a human in the loop for KDP uploads.

Do not outsource niche selection or listing copy until you have >50 SKUs of data — these are the highest-leverage decisions and a generic freelancer can't replicate your judgment yet.

## The endgame

At 100+ SKUs a month of passive monitoring is enough. You're running a small content IP portfolio. Realistic mature-state numbers from public case studies:

- 50 SKUs: $1k–$3k/mo
- 100 SKUs: $3k–$8k/mo
- 250 SKUs: $8k–$20k/mo (requires branding, ads, and category dominance)

The top-1% YouTube-transcript number ($26k/mo) corresponds to a 500+ SKU brand with active ads spend. It is not "passive." Treat it as a ceiling, not a target.
