# 06 — Compliance and AI Disclosure

This is the reference that keeps your account alive. Skim this the first time, re-read it every time you publish.

## Amazon's AI-content policy (as of 2026)

When you submit a book on KDP, Amazon asks you to disclose whether the content was **AI-generated** or **AI-assisted**, separately for:

- Text
- Images
- Translations

Definitions (per KDP's policy page):

- **AI-generated:** content created by an AI tool that you included unchanged or with minimal edits.
- **AI-assisted:** AI was used as a tool (brainstorming, editing, grammar), but you did meaningful human writing.
- **Neither:** no AI involvement.

### How to answer for a puzzle book generated with Claude

If Claude produced the puzzles (grids, word lists, solutions) with a prompt, that is **AI-generated text** regardless of how much you massaged it. Disclose it.

The disclosure is **private** — it does not appear on the product page. But Amazon uses it to tune their content moderation, and undisclosed AI content found later can trigger account-level enforcement.

Don't lie on the form. The consequences of being caught — account termination, royalty forfeiture, loss of the entire catalog — vastly exceed the marginal ranking difference of not disclosing.

## KDP content-quality guidelines

Amazon's broader quality policy applies regardless of AI. The common violations for puzzle books:

1. **Duplicate content.** You can't publish a book that's 95% identical to an existing book (yours or someone else's). Small re-theming is not enough.
2. **Poorly-formatted content.** Misaligned grids, unreadable fonts, cut-off puzzles.
3. **Misleading titles or descriptions.** "1000 Puzzles" on a 100-puzzle book.
4. **Missing or wrong answer keys.** Amazon treats this as defective.
5. **Broken links / external URLs inside the book.** Removed on sight.
6. **Books under 24 pages** (KDP minimum for paperback).

Any of these gets the SKU blocked and may weaken your account standing across the catalog.

## Trademark and copyright

Never use:

- **Franchise names:** Disney, Pixar, Marvel, DC, Pokémon, Harry Potter, Star Wars, Minecraft, Roblox, Nintendo, Lego, Barbie, Hot Wheels, Mattel properties.
- **Sports leagues and teams:** NFL, NBA, MLB, NHL, FIFA, premier-league club names and crests, Olympic rings, FIFA/UEFA nomenclature.
- **Brand/product names:** Nike, Adidas, Coca-Cola, Apple, Google, Microsoft, Tesla, etc.
- **Song lyrics, movie quotes, book excerpts.** These are under copyright.
- **Living celebrity names** in titles. (Publicity rights vary by jurisdiction.)
- **Political-figure likenesses** on covers.

Safe alternatives:
- Generic nouns: "Football," "Soccer," "Racing Cars," "Princesses" (not "Disney Princesses").
- Historical / mythological figures (no publicity rights).
- Public-domain literature (pre-1929 in most jurisdictions).
- Generic themes: "Gardening," "Baking," "Travel," "Pets."

The `kdp_listing_builder.py` script denies a default trademark list. You can extend it with `--denylist my_brands.txt`.

## Content warnings / age appropriateness

If you publish for children (any audience under 12), the book is held to additional standards:

- No violence, horror, or adult themes in puzzles or images.
- No product placements or affiliate links.
- Cover must be age-appropriate.
- Use word lists appropriate to the target age group.

For senior-facing books:
- No predatory health claims ("prevents Alzheimer's" is prohibited — you can say "brain exercise").
- If large-print, actually be large-print. 16pt minimum.

## KDP volume limits

As of 2026 KDP limits new-title submissions to **~3 per day per account** (varies by account standing). This cap is enforced account-wide across pseudonyms. Plan your publishing cadence accordingly — batching 20 SKUs into one weekend will hit the limit.

## Pen names / pseudonyms

You can publish under a pen name. Best practice:

- One pen name per niche or audience. Confusing a "seniors" buyer with a "kids activity book" author dilutes the brand.
- Never use a real person's name (living author, public figure).
- Pen names do not bypass the 3-per-day cap — it's account-level.
- Consistency matters. Amazon links books under the same pen name for "more by this author" carousels. This is free traffic.

## Returns and 1-star reviews

Your biggest compliance risk after launch is **customer complaints**:

- A customer who can't solve a puzzle leaves a 1-star review. Three in a week tanks BSR.
- If Amazon sees a return-rate spike, they temporarily de-list the book and email you.
- **Prevention:** solve a random 10% of puzzles before you publish. Automate if producing volume.

## Tax and business registration

Ignored by most tutorials, matters for your actual business:

- KDP requires a W-9 (US) or W-8BEN (non-US) before paying royalties.
- Puzzle-book income is self-employment income — in most jurisdictions you owe self-employment tax plus income tax.
- Track your expenses (cover design, Book Bolt, Claude API costs, printed proofs). They're deductible.
- At >$20k/yr revenue consider forming an LLC or equivalent for liability separation.

This skill does not provide tax or legal advice. Consult a local accountant before revenue > ~$5k/mo.
