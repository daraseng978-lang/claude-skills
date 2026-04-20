# 02 — The Seven-Step Pipeline

Every SKU follows this exact sequence. Each step has a decision gate — if you fail the gate, stop and fix the upstream step.

## Step 1 — Niche research

**Input:** a candidate niche (e.g. "large-print word search for seniors").

**Process:**
1. Search Amazon for the niche's primary keyword.
2. Record the top 10 organic results (not sponsored). For each: BSR, price, review count, publish date, publisher.
3. Fill out `assets/sample_niche_inputs.json` with your data.
4. Run `python scripts/niche_scorer.py --input my_niche.json`.

**Gate:** niche score >= 55. Below that, pick a different niche.

**What Claude does:** nothing yet. Humans collect the Amazon data.

## Step 2 — Book concept brief

**Input:** a qualified niche from Step 1.

**Process:** fill out `assets/book_brief_template.md` with:
- Puzzle type and count (default 100)
- Theme (e.g. "gardening", "1950s nostalgia", "ocean life")
- Difficulty mix (e.g. 30 easy / 40 medium / 30 hard)
- Audience (e.g. "seniors 65+")
- Physical specs (size, page count, margin, grid size)

**Gate:** the brief fully specifies the book. If you can't write the brief, you can't write the book.

**What Claude does:** help you brainstorm theme angles and difficulty curves. Not yet generating content.

## Step 3 — Listing draft

**Input:** the brief.

**Process:**
1. Convert the brief into a concept JSON (see `assets/sample_listing_inputs.json`).
2. Run `python scripts/kdp_listing_builder.py --input my_listing.json`.
3. Review the generated title, subtitle, description, 7 keywords, 2 categories.
4. Read the "Issues" section — fix any policy flags.

**Gate:** zero issues from the listing builder. Trademark and KDP-policy flags block publishing.

**What Claude does:** optionally rewrite the description in your brand voice after the builder emits a compliant base.

## Step 4 — Revenue sanity check

**Input:** the niche's top 3 competitors' BSR and price.

**Process:**
```bash
python scripts/bsr_to_revenue.py --bsr 12450 --price 8.99
python scripts/bsr_to_revenue.py --bsr 34780 --price 7.99
python scripts/bsr_to_revenue.py --bsr 98200 --price 9.99
```

**Gate:** average est. monthly royalty of top 3 >= $200. If lower, the niche is not worth publishing into — even if you rank #1.

## Step 5 — Portfolio fit

**Input:** your running portfolio plan.

**Process:** run `python scripts/portfolio_planner.py --input my_portfolio.json` with this SKU added. Confirm the expected breakeven is within 12 months.

**Gate:** does this SKU improve the portfolio's blended expected royalty? If it cannibalizes an existing SKU (same keyword, same audience), skip it or merge.

## Step 6 — Manuscript generation

**Input:** the brief + the listing.

**Process:** hand the brief to Claude using the prompts in `assets/claude_prompts.md`. Ask for:
1. The puzzle set (N × puzzle grids with solutions).
2. A short intro page (how to solve, how to use).
3. Page-level layout spec (one puzzle per page, solutions in the back).

Save the output as a structured file (plain text, CSV of word lists, or generated PDF via separate tooling).

**Gate:** every puzzle must be independently solvable. Run a solver or have a human solve a random sample of 10% before publishing.

**What Claude does:** generates content. This is the only step where LLM output is the product.

## Step 7 — QA and publish

**Input:** the manuscript PDF, cover PDF, and listing.

**Process:** run through `assets/publishing_checklist.md` (40 points covering solvability, formatting, cover specs, metadata, AI disclosure, pricing).

**Gate:** zero unchecked items on the checklist. Then upload to KDP and submit for review.

## After publishing

Don't touch the SKU for 30 days. Amazon's algorithm needs time to classify and rank it. After 30 days:

- **Winner signal:** BSR < 50,000 in your category → double down with a Volume 2.
- **Dud signal:** BSR > 500,000 after 60 days → leave it live (costs nothing) and move on.
- **Middle:** BSR 50k–500k → add a 2nd browse category and run a $5/day Amazon Ads test for 2 weeks.

Log all outcomes. After 20–30 SKUs you'll see which niches to scale into.
