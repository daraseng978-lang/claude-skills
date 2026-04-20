# 01 — The KDP Puzzle-Book Business Model

## What you're actually selling

You are selling **print-on-demand paperback activity books** through Amazon Kindle Direct Publishing (KDP). Amazon prints a physical copy on order, ships it to the buyer, and deposits a royalty into your bank account. No inventory, no shipping, no customer service.

The optional Kindle (ebook) version is a secondary SKU. For puzzle books it matters less — most buyers want the physical paperback so they can write in it.

## The royalty math

KDP paperback royalty:

```
royalty_per_unit = (list_price × 0.60) − print_cost
```

Print cost for a 110-page black-and-white paperback (puzzle standard size):

```
print_cost ≈ $2.15 fixed + $0.012 × pages
```

Example — $8.99 paperback, 110 pages:

```
royalty = (8.99 × 0.60) − (2.15 + 0.012 × 110)
       = 5.39 − 3.47
       = $1.92 per unit
```

At 10 sales/day that's ~$576/month per SKU. That is one mid-winner.

## Why puzzle books specifically

| Property | Why it matters |
|---|---|
| Zero narrative | Claude can generate content deterministically from a spec |
| Evergreen | No trend risk; a sudoku book from 2016 still sells |
| Gift-friendly | Gift buyers don't comparison-shop as hard |
| Reader doesn't finish in one sitting | Low refund rate |
| High search intent | "sudoku book" is a verb-buy keyword |
| Low IP risk | Generic puzzle content carries no copyright conflict |

## Why most people fail at it

1. They pick a saturated niche with 30+ big-publisher listings in the top 10.
2. They don't disclose AI content and get flagged.
3. They publish one SKU and give up when it earns $12/mo.
4. They stuff keywords and get removed for listing manipulation.
5. They use trademarked terms (Pokémon, Disney, NFL) in titles.
6. They upload without running the PDF through a solver — one wrong puzzle = 1-star reviews.

All six are avoidable. This skill is built to avoid them.

## Realistic expectations

- **Month 1**: 3–6 SKUs published, $0–$50 royalty. Most new listings don't get traffic for 30–60 days.
- **Month 3**: 15+ SKUs, $100–$400 royalty as Amazon's recommender kicks in.
- **Month 6**: 25+ SKUs, $300–$1,500 royalty. You know which niches are working.
- **Month 12**: 50+ SKUs, $1,000–$5,000 royalty if you doubled down on winners.

$5k/mo passive royalty off 50 SKUs is a realistic serious-part-time outcome. It is not "overnight income."

## Where the transcript oversells

The YouTube transcript this skill was built from claims "380 sales per day, $26k/month." That is a **top 1% outcome** and usually comes from a branded series with 20+ SKUs, Amazon Ads spending, and a years-old review moat. Plan for the median, not the outlier.

## The operating loop

```
   ┌────────────────────────────────────────────┐
   │  1. Pick niche  →  score >= 55             │
   │  2. Draft brief →  hand to Claude          │
   │  3. Generate    →  puzzles + solutions     │
   │  4. Typeset     →  interior PDF + cover    │
   │  5. QA          →  solvability + format    │
   │  6. Publish     →  listing + 2 categories  │
   │  7. Observe     →  30 days, read signals   │
   │  8. Double down →  on winners; kill duds   │
   └────────────────────────────────────────────┘
```

Step 7 matters. Most publishers re-publish too fast and never learn which niches work.
