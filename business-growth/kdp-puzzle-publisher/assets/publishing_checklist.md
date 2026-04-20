# Publishing Checklist — 40 points

Do not submit a SKU to KDP with any box unchecked.

## Manuscript (interior)

- [ ] Page count is even
- [ ] Minimum 24 pages
- [ ] Trim size matches KDP form (default 8.5" × 11")
- [ ] Bleed set correctly (0.125" if full-bleed elements, else none)
- [ ] Inside margin (gutter) ≥ 1.0"
- [ ] Outside/top/bottom margins ≥ 0.75"
- [ ] Body font ≥ 11pt (≥ 16pt if "large print" in title)
- [ ] All fonts embedded or outlined
- [ ] PDF is CMYK, 300 DPI for any raster elements
- [ ] Answer key starts on a right-hand page
- [ ] Answer-key order matches puzzle-number order

## Puzzles

- [ ] 100% of puzzles manually or algorithmically solvable
- [ ] Random 10% sample solved by a human
- [ ] No duplicate grids or duplicate word lists
- [ ] No trademarked words anywhere in puzzles
- [ ] No words inappropriate for the stated audience age

## Cover

- [ ] Full-wrap cover PDF (back + spine + front in one file)
- [ ] Spine width matches page count × 0.0025"
- [ ] Bleed 0.125" on all outside edges
- [ ] Barcode zone (2"×1.2", bottom-right of back) left clear
- [ ] CMYK, 300 DPI
- [ ] Title readable at thumbnail size (zoom to 150×230 px and re-check)
- [ ] No trademark, franchise, or celebrity imagery

## Listing (from kdp_listing_builder)

- [ ] Title ≤ 200 chars, no banned words
- [ ] Subtitle ≤ 200 chars, adds keywords without repeating title tokens
- [ ] Description ≤ 4000 chars, uses KDP-allowed HTML only
- [ ] Description has: hook, what's inside, benefits, gift, CTA
- [ ] 7 backend keywords, each ≤ 50 chars, all distinct
- [ ] 2 browse categories selected
- [ ] No "bestseller," "free," "#1," or similar banned terms anywhere
- [ ] Zero issues from `kdp_listing_builder.py` validator

## Pricing & royalty

- [ ] Price in the $6.99–$11.99 band (unless intentional outlier)
- [ ] Royalty per unit ≥ $1.00 (run `bsr_to_revenue.py`)
- [ ] Expanded distribution considered (adds 40% royalty penalty but reach)

## Compliance

- [ ] KDP AI-content disclosure filled out correctly (Text: AI-generated)
- [ ] KDP AI-image disclosure filled out correctly (Images: per reality)
- [ ] I own the rights to every word, image, and font used
- [ ] No content violates KDP quality guidelines
- [ ] Pen name is consistent with my existing series (if applicable)

## Final

- [ ] Previewed the full book in KDP's online previewer
- [ ] Downloaded Amazon's rendered PDF and opened it in Acrobat at 100%
- [ ] Screenshot of thumbnail looks professional next to competitors
- [ ] I'd buy this book myself

## Post-submit

- [ ] Added to portfolio tracker (spreadsheet / portfolio_planner input)
- [ ] Calendar reminder at 30 days to pull first BSR snapshot
- [ ] Calendar reminder at 60 days to consider category additions
