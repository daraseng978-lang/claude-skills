#!/usr/bin/env python3
"""Step 3 — Verify each contractor is genuinely ADA/accessibility-specialized.

For each row: crawl the homepage + up to 3 internal pages, extract text, ask Claude
Haiku whether this contractor offers ADA / aging-in-place / accessibility services.

Requires: pip install crawl4ai anthropic
Env:      ANTHROPIC_API_KEY

Usage:
    python 03_verify_ada.py data/02_cleaned.csv data/03_verified.csv
"""
from __future__ import annotations

import asyncio
import csv
import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

CONCURRENCY = 8
MODEL = "claude-haiku-4-5-20251001"

ADA_KEYWORDS = (
    "ada", "accessible", "accessibility", "aging in place", "grab bar",
    "walk-in tub", "walk in tub", "roll-in shower", "roll in shower",
    "barrier-free", "barrier free", "handicap", "mobility", "wheelchair",
    "caps", "certified aging", "universal design", "curbless shower",
)

CLASSIFIER_PROMPT = """You evaluate whether a home-remodeling contractor genuinely offers ADA-accessible or aging-in-place bathroom services.

Classify as one of:
- "specialist": core business is accessibility / ADA / aging-in-place remodeling
- "offers": general contractor that explicitly lists accessibility services
- "no": no evidence of accessibility specialization

Respond with JSON only: {"verdict": "...", "confidence": 0-100, "evidence": "short quote or keyword summary"}.

Website text:
---
%s
---"""


async def crawl_site(crawler: AsyncWebCrawler, url: str) -> str:
    try:
        cfg = CrawlerRunConfig(word_count_threshold=20, cache_mode="BYPASS")
        result = await crawler.arun(url=url, config=cfg)
        return (result.markdown or "")[:8000] if result.success else ""
    except Exception:
        return ""


def classify(client: Anthropic, text: str) -> dict:
    if not text.strip():
        return {"verdict": "no", "confidence": 0, "evidence": "empty_crawl"}
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": CLASSIFIER_PROMPT % text}],
    )
    raw = resp.content[0].text.strip()
    try:
        start = raw.find("{")
        return json.loads(raw[start:raw.rfind("}") + 1])
    except Exception:
        return {"verdict": "no", "confidence": 0, "evidence": f"parse_fail:{raw[:80]}"}


async def process(rows: list[dict], client: Anthropic) -> list[dict]:
    out: list[dict] = []
    sem = asyncio.Semaphore(CONCURRENCY)
    async with AsyncWebCrawler() as crawler:
        async def one(row: dict) -> None:
            async with sem:
                text = await crawl_site(crawler, row["website"])
                fast_hit = any(kw in text.lower() for kw in ADA_KEYWORDS)
                if not fast_hit:
                    row.update(verdict="no", confidence=0, evidence="no_keyword_match")
                else:
                    result = classify(client, text)
                    row.update(verdict=result["verdict"],
                               confidence=result["confidence"],
                               evidence=result["evidence"])
                out.append(row)
                print(f"[{len(out)}/{len(rows)}] {row['name'][:40]:40} → {row['verdict']} ({row['confidence']})")
        await asyncio.gather(*(one(r) for r in rows))
    return out


def main(in_path: Path, out_path: Path) -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rows = list(csv.DictReader(in_path.open(newline="", encoding="utf-8")))
    print(f"Verifying {len(rows)} contractors with concurrency={CONCURRENCY}")

    results = asyncio.run(process(rows, client))

    kept = [r for r in results if r["verdict"] in ("specialist", "offers") and int(r["confidence"]) >= 60]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=list(kept[0].keys()) if kept else list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(kept)

    print(f"\nVerified ADA contractors: {len(kept)} / {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
