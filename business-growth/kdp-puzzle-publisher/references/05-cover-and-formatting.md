# 05 — Cover and Interior Formatting

This skill does not generate images. It tells you what the KDP specs are, what sells, and what to hand off to your cover designer or image tool.

## Interior PDF specs

- **Trim size:** 8.5" × 11" is the standard for puzzle books (roomy grid).
  - Alternative: 6" × 9" for travel-size or cryptogram books.
- **Bleed:** 0.125" on all outside edges if you have full-bleed backgrounds. Otherwise none.
- **Margins:** 0.75" outside, 0.75" top/bottom, 1.0" inside (gutter).
- **Page count:** multiples of 2 (KDP requirement). Minimum 24 pages.
- **Font:** serif for body (Garamond, Merriweather), sans-serif for titles (Montserrat, Lato). For large-print editions use ≥16pt body.
- **Grid font:** monospace (e.g. Inconsolata) at ≥14pt so letters align in a grid.
- **Format:** PDF/X-1a or PDF/X-3, CMYK color, 300 DPI for any raster elements.

## Cover PDF specs

- **Full wrap cover** in a single PDF: back cover + spine + front cover.
- **Spine width** = page_count × 0.0025" for white paper (KDP provides a calculator).
- **Bleed:** 0.125" on all outside edges (mandatory).
- **Barcode zone:** leave 2" × 1.2" clear at bottom-right of the back cover.
- **Color:** CMYK, 300 DPI.
- **Fonts:** embed all fonts or outline them.

The KDP Cover Calculator (`kdp.amazon.com/cover-calculator`) gives you exact dimensions for your specific trim + page count. Use it; don't guess.

## What sells in puzzle-book covers

1. **High-contrast title** that's readable at thumbnail size (as small as 120×180 px).
2. **Puzzle grid preview** visible — buyers want to see what they're getting.
3. **Audience signal** in imagery — seniors see a cozy reading scene; kids see bright cartoon mascots.
4. **Volume / count callout** in a starburst or badge. "100 Puzzles."
5. **No stock photo clichés** of happy seniors with magnifying glasses — it's a saturated aesthetic.

## Generating covers without an artist

Free and near-free options:
- **Canva.** KDP book cover templates exist. Free tier is sufficient.
- **Book Bolt** (paid). Has 1-click cover templates tuned for KDP.
- **GIMP + free stock (Pexels, Unsplash).** Steepest learning curve, most flexible.
- **Claude-paired image tools.** If you have image-generation access, prompt for "flat illustration, editorial style, no people, no text" and add the title yourself in Canva to keep typography crisp.

## Typesetting the interior

This is where most new publishers stall. Three approaches:

**A. LaTeX (best quality, steepest curve).** Templates for puzzle books with grid macros exist. Output is print-ready PDF. Free.

**B. Book Bolt's interior designer.** Drag-and-drop, KDP-ready output, paid. Shortest time to first SKU.

**C. Word / Google Docs → PDF.** Works for simple layouts. Not recommended for grids — alignment drifts.

Whichever you pick, **never ship a PDF you haven't opened in Adobe Acrobat Reader at 100% zoom.** The KDP online preview is accurate but slow. Reader catches font-embedding issues before you upload.

## The answer key

Every puzzle book needs one. Conventions:
- Place at the back, starting on a right-hand page.
- Header: "Answer Key" in the same typeface as chapter headings.
- One solution per page, same orientation as the puzzle.
- Reduce grid size to ~50% of puzzle-page grid so solutions take less room.
- Number solutions to match puzzle numbers. "Puzzle 1 Solution," etc.

## Final QA on the interior

1. Open every page in a PDF viewer at 100% zoom.
2. Verify no puzzle is truncated at the gutter.
3. Verify answer-key ordering matches puzzle ordering.
4. Solve a random 10% of puzzles by hand or with a solver. Missing a solution = 1-star reviews.
5. Verify page count is even.
6. Verify the trim/bleed matches what you'll declare on the KDP upload form.

A single unsolvable puzzle ruins a book. Automate the solve-check if you're producing volume — this is non-negotiable.
