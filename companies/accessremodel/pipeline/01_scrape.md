# Step 1 — Outscraper Raw Pull

**Owner:** CTO · **Cost:** $100 (approved, Gate #1) · **Runtime:** ~15 min

## Queries (Google Maps via Outscraper)

Run these nationwide (or split by top-50 metros if cost needs throttling):

1. `bathroom remodeling contractor`
2. `accessible bathroom contractor`
3. `ADA bathroom remodel`
4. `aging in place contractor`
5. `walk-in tub installer`
6. `handicap bathroom contractor`

## Outscraper Settings

- Data: **Google Maps Scraper**
- Fields: name, full_address, city, state, postal_code, phone, website, rating, reviews, business_status, categories, latitude, longitude
- Dedup: enabled (by place_id)
- Output: CSV
- Expected rows: ~50K–80K pre-dedup, ~40K–60K post

## Save As

`companies/accessremodel/data/01_raw.csv`

## Founder Action Required

This step requires a paid Outscraper API call. Founder (or Chief of Staff with founder's key) triggers the run. All subsequent steps are local + API-credit-based, no further cash outlays until Gate #2.
