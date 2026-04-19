# Pipeline — AccessRemodel Phase 0

Codified version of Frey's 7-step directory pipeline, adapted for ADA Bathroom Contractors.

## Dependencies

```bash
pip install crawl4ai anthropic
# Outscraper: use web UI (https://outscraper.com) — no SDK install needed
```

## Run Order

| Step | Script | Input | Output | Runtime |
|---|---|---|---|---|
| 1 | See `01_scrape.md` | Outscraper queries | `data/01_raw.csv` | ~15 min (async) |
| 2 | `02_clean.py` | `data/01_raw.csv` | `data/02_cleaned.csv` | ~1 min |
| 3 | `03_verify_ada.py` | `data/02_cleaned.csv` | `data/03_verified.csv` | 2–4 hr (Crawl4AI + Claude API) |
| 4 | `04_enrich.py` | `data/03_verified.csv` | `data/04_enriched.csv` | 1–2 hr |
| 5 | `05_build_site_data.py` | `data/04_enriched.csv` | `site/data/listings.json` | ~1 min |

## Budget Pointers

- Step 1: Outscraper = $100 (approved, Gate #1)
- Step 3: Claude API ≈ $30–50 on Haiku 4.5 for 15K websites @ ~2K tokens ea
- Steps 2, 4, 5: free (local Python / stdlib)

## Env Vars

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

See `execution-plan.md` for gating rules and who (which C-suite agent) owns each step.
