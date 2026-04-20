# 04 — Listing Optimization

Your listing is three surfaces: **title**, **subtitle**, **description**. Plus **7 keywords** and **2 categories** behind the scenes. Get these right and Amazon does the rest of the marketing for you. Get them wrong and no amount of paid ads will save the SKU.

## Title

Limit: 200 characters. Usable range in Amazon search results: first ~60 characters.

**Formula:**
```
{Size/Style Modifier} {Puzzle Type} {For Audience}
```

**Good:**
- `Large Print Word Search for Seniors`
- `Jumbo Sudoku for Beginners`
- `Travel Mazes for Kids Ages 6-8`

**Bad:**
- `Word Search Puzzle Book by Amazing Best Seller Publishing — #1 Puzzle Brand Sudoku Crossword Activity Book for Adults Seniors Kids Travel` (keyword stuffing; will get flagged)
- `Fun Puzzles` (no search intent)
- `Disney Princess Word Search` (trademark violation)

Every word in the title is a ranking keyword. Choose words a buyer would search, not words you'd use in marketing copy.

## Subtitle

Limit: 200 characters. Use it to load secondary keywords without polluting the title.

**Formula:**
```
{Puzzle count} {Puzzle Type} Puzzles, {Theme or Modifier}, {Difficulty}, {Benefit}
```

**Good:**
- `100 Large Print Word Search Puzzles, Nature and Animal Themes, Easy to Hard, Relaxing Brain Exercise for Adults`

**Bad:**
- Same tokens as the title repeated
- Random unrelated keywords (penalized)
- Emoji / symbols (KDP rejects these)

## Description

Limit: 4,000 characters. KDP supports simple HTML (bold, italic, bullet lists, line breaks). Use it.

**Structure (6 sections):**

1. **Hook** (1 bold sentence, ≤120 chars). What is this book, who is it for?
2. **What's inside** (5–7 bullet points). Concrete specs: puzzle count, difficulty, page count, size.
3. **Why you'll love it** (3–5 benefit bullets). Outcomes, not features.
4. **Social proof placeholder.** Leave space, but don't fake reviews.
5. **Gift angle** (1 sentence). Most puzzle books are gift purchases — name the occasion.
6. **Call to action** (1 sentence). "Click Add to Cart to get yours today."

**Forbidden:**
- Fake testimonials
- Mention of other products ("buyers also liked our Sudoku Volume 2…")
- External links / email addresses
- Claims of Amazon bestseller status unless true and disclosed
- Claims of awards you didn't win

## Keywords (7 backend slots)

Each slot: up to 50 characters. Use **phrases**, not individual words. Amazon matches tokens across slots, so don't repeat words you already used in the title or subtitle — that wastes a slot.

**Fill order:**
1. Primary search term (e.g. "word search puzzle book")
2. Audience variant (e.g. "puzzle book for seniors")
3. Size/style variant (e.g. "large print puzzle book")
4. Gift variant (e.g. "puzzle gift for grandma")
5. Cross-category catch (e.g. "activity book for adults")
6. Long-tail (e.g. "travel puzzle book for road trips")
7. Buyer-intent (e.g. "dementia activity book" — only if accurate)

Do **not** use:
- Amazon's own terms (`kindle`, `bestseller`, `amazon`)
- Your author name (already indexed separately)
- Words already in the title / subtitle

## Categories (2 slots)

Pick **one primary** (where you realistically can rank top 20) and **one adjacent** (broader, more traffic).

For a word-search book:
- Primary: `Humor & Entertainment > Puzzles & Games > Word Search`
- Adjacent: `Crafts, Hobbies & Home > Games & Activities > Word Games`

Use KDP's category selector. You can request up to 10 additional categories via `kdp-support@amazon.com` after launch — this is the single highest-ROI action most self-publishers skip.

## Pricing

$8.99 is the default for 100-puzzle paperbacks. Above $11.99 unit royalty jumps (good) but conversion drops (bad). Below $6.99 you lose money after print cost.

| Page count | Default price | Royalty |
|---|---|---|
| 80 | $6.99 | $0.99 |
| 110 | $8.99 | $1.92 |
| 150 | $9.99 | $2.09 |
| 200 | $11.99 | $3.11 |

## Post-launch

- **Day 0–30**: don't touch the listing. Amazon's classifier needs signal.
- **Day 30**: run `bsr_to_revenue.py` on your SKU. If monthly royalty < $30, add the 2 adjacent categories via KDP support.
- **Day 60**: still under $30/mo? Rewrite the subtitle with a sharper audience angle. One change per 30 days — you're testing.
- **Day 90**: still dead? Leave it. Don't delete — the listing is free residual income if it moves one copy a month.

Your winners will reveal themselves by month 2–3. Pour all new SKU effort into those niches.
