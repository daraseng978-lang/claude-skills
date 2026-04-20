---
name: "kdp-puzzle-publisher"
description: Blueprint for an agent-operated Amazon KDP puzzle-book publishing company that uses Claude to generate content, researches proven niches, optimizes listings for Amazon + Google search, and scales a portfolio of low-content / activity books (word search, sudoku, mazes, logic puzzles). Use when planning a KDP business, validating a puzzle niche via BSR and competitive analysis, drafting Claude-generated book briefs, writing keyword-rich KDP listings, or forecasting portfolio revenue across many SKUs. Emphasizes quality, Amazon AI-content disclosure compliance, and trademark/copyright safety.
---

# KDP Puzzle Publisher

A production-ready blueprint for running an **Amazon KDP puzzle-book publishing business** with Claude as the content engine. Turns the "make money with Claude" playbook into a repeatable, compliant pipeline: niche research → book brief → Claude-generated content → listing optimization → publish → iterate.

> **Output formats:** All scripts support `--format text` (human) and `--format json` (dashboards). Standard library only. No LLM calls in scripts — Claude is invoked in the authoring workflow, not the tooling.

---

## The Model in One Paragraph

Pick a proven evergreen puzzle niche on Amazon (word search, sudoku, mazes, cryptograms, activity books). Validate it against Best Seller Rank (BSR), review count, and price. Commission Claude to generate a 100-puzzle manuscript + description + cover brief. Typeset in a KDP-ready PDF. Publish on Kindle Direct Publishing with a keyword-rich title, subtitle, 7 backend keywords, and 2 browse categories. Rinse and repeat into a **portfolio of 20–100 SKUs**. Revenue compounds because one winner funds ten tests, and Amazon's recommendation engine cross-lists similar SKUs for free.

| Dimension | Value |
|---|---|
| Product | 100-puzzle softcover / paperback activity book |
| Price point | $6.99 – $12.99 |
| Royalty (60% / print cost) | ~$2.50 – $5.00 per unit |
| Unit economics | ~$0 marginal cost per sale (print-on-demand) |
| Winning SKU | 5–30 sales/day × ~$3 royalty = $450–$2,700/mo |
| Portfolio target | 10% of SKUs are winners; fund tests from winners |
| Path to $5k/mo | 3 mid-winners or 1 big-winner out of ~30 SKUs |
| Content actor | Claude (puzzles + descriptions + cover copy) |
| Founder role | Niche selection, brand, quality QA, publishing |

---

## Scope, Ethics, and Compliance (read this first)

This skill is for **quality-first, disclosed AI-assisted publishing**. It is not a "AI slop farm" playbook. Before using it:

1. **Amazon KDP AI-content disclosure is mandatory.** You must disclose AI-generated content (text, images, translations) on the KDP content page. Non-disclosure risks takedown. See [references/06-compliance-and-disclosure.md](references/06-compliance-and-disclosure.md).
2. **Amazon's volume limit.** KDP caps new title submissions at ~3 / day per account. Plan accordingly.
3. **Trademark/copyright safety.** Do not use Disney, NFL, Pokémon, song lyrics, or any third-party IP in puzzles, titles, or covers.
4. **Quality bar.** Every puzzle must be solvable and correct. Every answer key must match. No duplicate grids inside a book.
5. **Content policy.** No bonus-content spam, no keyword stuffing in descriptions, no misleading titles, no pen-names impersonating real authors.

Skip this skill if you intend to mass-produce low-quality AI content. Amazon removes those listings and bans accounts.

---

## Quick Start

```bash
# 1. Score a niche against public Amazon signals (BSR, reviews, price, competition)
python scripts/niche_scorer.py --input assets/sample_niche_inputs.json --format text

# 2. Convert a competitor's BSR into a daily-sales and monthly-royalty estimate
python scripts/bsr_to_revenue.py --bsr 12450 --price 8.99 --format text

# 3. Generate an SEO-optimized KDP listing (title / subtitle / description / 7 keywords / 2 categories)
python scripts/kdp_listing_builder.py --input assets/sample_listing_inputs.json --format text

# 4. Plan a 30-SKU quarterly portfolio and forecast expected royalty
python scripts/portfolio_planner.py --input assets/sample_portfolio_inputs.json --format text
```

Then hand off to Claude with [assets/book_brief_template.md](assets/book_brief_template.md) to generate the manuscript.

---

## The 7-Step Pipeline

Every SKU follows this pipeline. Steps 1, 3, 4, 5 are scripted. Steps 2, 6 are Claude. Step 7 is manual QA + upload.

```
[1] Niche Research      → niche_scorer.py
[2] Book Concept        → Claude (book_brief_template.md)
[3] Listing Draft       → kdp_listing_builder.py
[4] Revenue Sanity      → bsr_to_revenue.py on top 3 competitors
[5] Portfolio Fit       → portfolio_planner.py
[6] Manuscript          → Claude (brief → 100 puzzles + solutions + intro)
[7] QA & Publish        → publishing_checklist.md, upload to KDP
```

Full walk-through in [references/02-seven-step-pipeline.md](references/02-seven-step-pipeline.md).

---

## Architecture: Who Does What

```
┌─────────────────────────────────────────────────────────────┐
│  FOUNDER (you)                                              │
│  - Niche selection, brand, cover art direction              │
│  - Quality QA before publish                                │
│  - KDP account ownership + tax/legal                        │
└────────────────────────────┬────────────────────────────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
┌─────────────┐        ┌─────────────┐      ┌─────────────┐
│  CLAUDE:    │        │  CLAUDE:    │      │  CLAUDE:    │
│  Research   │        │  Content    │      │  Listing    │
│  agent      │        │  agent      │      │  agent      │
│             │        │             │      │             │
│ Summarizes  │        │ Generates   │      │ Writes      │
│ Amazon      │        │ puzzles,    │      │ titles,     │
│ search      │        │ solutions,  │      │ descriptions│
│ pages into  │        │ intros,     │      │ keywords,   │
│ niche       │        │ fronts/backs│      │ categories  │
│ briefs      │        │             │      │             │
└─────────────┘        └─────────────┘      └─────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│  SCRIPTS (deterministic, standard library only)             │
│  niche_scorer │ bsr_to_revenue │ listing_builder │ portfolio│
└─────────────────────────────────────────────────────────────┘
```

Prompts for each Claude role are in [assets/claude_prompts.md](assets/claude_prompts.md).

---

## Default Niche Set (tested evergreens)

Start here. These categories have proven demand, low seasonality, and low content-policy risk.

| Niche | Why it works | Price range |
|---|---|---|
| Large-print word search for seniors | Aging demographic, gift-giving, high review density | $7.99 – $9.99 |
| Sudoku (easy / medium / hard, per book) | Global demand, clear difficulty segmentation | $6.99 – $8.99 |
| Mazes for kids (ages 4–6, 6–8, 8–12) | Parent-driven purchases, school/summer spikes | $5.99 – $7.99 |
| Cryptograms / logic puzzles | Low saturation, loyal niche audience | $7.99 – $10.99 |
| Travel activity books (road trip, airplane) | Gift-giving, seasonal peaks | $8.99 – $11.99 |
| Themed word search (gardening, sports, cooking) | Cross-sells via Amazon "also viewed" | $7.99 – $9.99 |

Full playbook in [references/03-niche-selection.md](references/03-niche-selection.md).

---

## Output Contracts

All scripts emit structured output. `--format json` for dashboards, `--format text` for humans.

- **niche_scorer.py** → `{ niche, score_0_100, verdict, bsr_median, review_median, price_median, saturation_flag, seasonality_flag, recommendations }`
- **bsr_to_revenue.py** → `{ bsr, est_sales_per_day, est_sales_per_month, est_monthly_royalty, confidence }`
- **kdp_listing_builder.py** → `{ title, subtitle, description_markdown, keywords[7], categories[2], character_counts }`
- **portfolio_planner.py** → `{ total_skus, expected_winners, expected_monthly_royalty, publishing_schedule, investment_required }`

Sample inputs are in `assets/`.

---

## What This Skill Does Not Do

- **No image generation.** Covers are produced outside this skill (Canva, Book Bolt, GIMP + stock art, Claude-paired image tools). See [references/05-cover-and-formatting.md](references/05-cover-and-formatting.md) for specs.
- **No scraping.** Scripts take public BSR / price / review inputs you supply. Do not scrape Amazon — it violates their ToS.
- **No automated uploads.** KDP requires manual review and submission. The skill prepares everything; you click publish.
- **No paid service requirements.** Book Bolt / Publisher Rocket are optional. Every step can be done with free tools + Claude.

---

## References

- [references/01-kdp-business-model.md](references/01-kdp-business-model.md) — royalty math, print-on-demand mechanics, category landscape
- [references/02-seven-step-pipeline.md](references/02-seven-step-pipeline.md) — the full pipeline with decision gates
- [references/03-niche-selection.md](references/03-niche-selection.md) — how to pick an evergreen niche
- [references/04-listing-optimization.md](references/04-listing-optimization.md) — title/subtitle/description/keyword/category tactics
- [references/05-cover-and-formatting.md](references/05-cover-and-formatting.md) — KDP interior/cover specs and formatting
- [references/06-compliance-and-disclosure.md](references/06-compliance-and-disclosure.md) — AI disclosure, trademarks, content policy
- [references/07-scaling-and-portfolio.md](references/07-scaling-and-portfolio.md) — 1 → 30 → 100 SKU portfolio playbook

---

## Assets

- `assets/sample_niche_inputs.json` — niche_scorer input
- `assets/sample_listing_inputs.json` — kdp_listing_builder input
- `assets/sample_portfolio_inputs.json` — portfolio_planner input
- `assets/book_brief_template.md` — hand off to Claude to generate a manuscript
- `assets/claude_prompts.md` — reusable prompts for research/content/listing agents
- `assets/publishing_checklist.md` — 40-point pre-publish QA list

---

## Related Skills

This skill covers the **operational pipeline** for building a KDP puzzle-book catalog. For the **founder/operator side** — time allocation, burnout prevention, delegation, and the weekly operating rhythm — pair it with:

- [`c-level-advisor/solo-founder/`](../../c-level-advisor/solo-founder/SKILL.md) — Chief Everything Officer advisor for one-person businesses. Use it to scope the MVP catalog (first 9 SKUs), fight scope creep when you're tempted to publish into 7 niches at once, price against your realistic time budget, and make the quit-your-job call once royalty is consistent. Best match while you're pre-revenue through your first ~$1k/month.
- [`c-level-advisor/founder-coach/`](../../c-level-advisor/founder-coach/SKILL.md) — Founder development and leadership growth. Use it once the catalog passes ~30 SKUs and you're deciding what to outsource (cover design, interior layout, QA solving), how to structure your week as an operator vs. a creator, and how to avoid becoming the bottleneck on a portfolio you no longer need to touch daily.

Typical handoff pattern:

```
┌──────────────────────────────────────────────────────────────┐
│ solo-founder     →  "Should I start this? What's the MVP?"   │
│ kdp-puzzle-publ. →  The pipeline for each SKU you publish.   │
│ founder-coach    →  "Now that it works, how do I scale me?"  │
└──────────────────────────────────────────────────────────────┘
```

Adjacent domain skills:

- [`business-growth/paperclip-business/`](../paperclip-business/SKILL.md) — if you want to convert KDP royalty into a productized SaaS/service business with recurring revenue.
- [`marketing-skill/`](../../marketing-skill/) — for Amazon Ads copy, keyword research beyond KDP's 7 slots, and email/social promotion of a branded series.
