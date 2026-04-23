# Portfolio Status — Checkpoint

_Living document. Updated at end of each working session. Read this first when resuming._

**Last updated:** 2026-04-23 (mid-session)
**Branch:** `claude/check-founder-skill-status-LpK6O`
**Active PR:** #13 (draft)

---

## Where we are in the playbook

Working through the 9-step launch sequence. Status per step:

| # | Step | Status |
|---|---|---|
| 1 | Scrape (Outscraper, 8 queries) | ✅ done — `01_raw.xlsx` delivered, 426 rows |
| 2 | Clean + split by query | ✅ done — AccessRemodel 247 / WalkInTubPros 98 / dropped 81 |
| 3 | Verify (Crawl4AI + Haiku) | ✅ done — AR 28 / WTP 15 verified with relaxed thresholds (D-012) |
| 4 | Enrich verified (services, CAPS, insured) | ✅ done — AR 28, WTP 15 enriched |
| 5 | Build site data (merge verified + unverified) | ✅ done — `listings.json` written for both properties |
| 6 | Scaffold Next.js site (AccessRemodel) | ✅ done — 341 static routes, 87.3 KB shared JS, build passes |
| 7 | Commit + push site code | ✅ done — commit `b9b7073` on feature branch |
| 8 | **Vercel project + deploy** | ⏸ **in progress — founder pausing here** |
| 9 | DNS: point `accessremodel.co` at Vercel | ⏳ pending Step 8 |
| 10 | Scaffold + deploy WalkInTubPros | ⏳ pending AccessRemodel live |
| 11 | Scrape remaining 3 niches (DementiaCare, IVFCost, ADUBuilders) | ⏳ Day 5 / 8 / 11 |

---

## Current tier distribution (for site UX)

| Property | Specialist | Offers | Unverified | Total | States |
|---|---|---|---|---|---|
| AccessRemodel | 5 | 23 | 219 | 247 | 11 |
| WalkInTubPros | 1 | 14 | 83 | 98 | 6 |

---

## Budget

- **Authorized:** $850 (Gate #1 revised per D-007)
- **Spent:** ~$24 (AccessRemodel domain $12 + WalkInTubPros domain $12)
- **Remaining:** ~$826
- **Next expense:** $0 — Vercel Hobby tier is free, Cloudflare DNS is free

---

## Domains

| Property | Domain | Status |
|---|---|---|
| AccessRemodel | `accessremodel.co` | ✅ owned, DNS parked at Cloudflare |
| WalkInTubPros | `walkintubpros.co` | ✅ owned (D-011) |
| DementiaCare | `dementiacare.co` | ⏳ buy before Day 5 scrape |
| IVFCost | `ivfcost.co` | ⏳ buy before Day 11 scrape |
| ADUBuilders | `adubuilders.co` | ⏳ buy before Day 8 scrape |

---

## Resume instructions — pick up at Step 8 (Vercel)

### 1. Create Vercel project

- Go to **https://vercel.com/new**
- Import Git Repo → `daraseng978-lang/claude-skills`
- Project name: `accessremodel`
- **Root Directory:** `companies/accessremodel/site` (click Edit, paste exactly)
- Framework: Next.js (auto-detects)
- Build/Install/Output: all defaults
- Env vars: none
- Click **Deploy**

### 2. Change production branch

Vercel defaults to `main` but site code is on `claude/check-founder-skill-status-LpK6O`.

- Vercel → `accessremodel` project → **Settings → Git**
- Production Branch: set to `claude/check-founder-skill-status-LpK6O`
- Save
- **Deployments** tab → latest deploy → **⋯ → Promote to Production**

### 3. Verify the `*.vercel.app` URL loads with:
- Hero: "Find ADA-Accessible Bathroom Contractors Near You"
- 247 listings count
- 11 state grid

---

## Claude Code state on the Windows box

- **Claude Code version:** 2.1.118 (installed)
- **Repo:** `C:\Users\Administrator\claude-skills-repo` on branch `claude/check-founder-skill-status-LpK6O`
- **Data folders (outside repo):**
  - `C:\Users\Administrator\companies\accessremodel\data\` — 01_raw.csv, 02_cleaned.csv, 03_verified.csv, 04_enriched.csv
  - `C:\Users\Administrator\companies\walkintubpros\data\` — 02_cleaned.csv, 03_verified.csv, 04_enriched.csv
- **Python deps installed:** anthropic, crawl4ai, openpyxl, playwright chromium, PowerShell ImportExcel module
- **Env vars:** `ANTHROPIC_API_KEY` set at User scope (starts with `sk-ant-api03-E9...`)

---

## Open questions for founder

- **Holding company name:** unpicked. Candidates: Keystone Directory Holdings · Nichecraft Holdings · Signal Directory Co. · Atlas Listings Group
- **Repo strategy:** revised to "one repo, multiple Vercel projects with different root directories" (was "one repo per property"). Decision pending formal log.

---

## Next session cold-start prompt

> Resume Directory Portfolio Co. Read `companies/status.md` for current checkpoint. Last action: AccessRemodel site scaffolded + committed; paused before Vercel deploy. Resume from Step 8 in the status doc.
