#!/usr/bin/env python3
"""Step 4 — Enrich verified contractors with service + certification tags.

For each row: re-crawl the site, extract specific accessibility services
(grab bars, roll-in showers, walk-in tubs, vanities, stair lifts) and CAPS
certification (NAHB Certified Aging-in-Place Specialist).

Usage:
    python 04_enrich.py data/03_verified.csv data/04_enriched.csv
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

SERVICE_TAGS = [
    "grab_bars", "roll_in_shower", "walk_in_tub", "curbless_shower",
    "accessible_vanity", "raised_toilet", "shower_seat", "non_slip_flooring",
    "stair_lift", "ramp_install", "widened_doorways",
]

ENRICH_PROMPT = """You extract structured metadata for an aging-in-place bathroom contractor.

From the website text below, return JSON with:
- services: subset of %s (include only ones explicitly offered)
- caps_certified: true if NAHB CAPS certification is mentioned, else false
- insured: true if licensed & insured is mentioned
- service_radius_miles: integer or null if not stated
- free_consultation: true if offered, else false

Respond with JSON only.

Website text:
---
%s
---"""


async def crawl(crawler: AsyncWebCrawler, url: str) -> str:
    try:
        cfg = CrawlerRunConfig(word_count_threshold=20, cache_mode="BYPASS")
        r = await crawler.arun(url=url, config=cfg)
        return (r.markdown or "")[:10000] if r.success else ""
    except Exception:
        return ""


def enrich(client: Anthropic, text: str) -> dict:
    if not text.strip():
        return {"services": [], "caps_certified": False, "insured": False,
                "service_radius_miles": None, "free_consultation": False}
    resp = client.messages.create(
        model=MODEL, max_tokens=400,
        messages=[{"role": "user", "content": ENRICH_PROMPT % (SERVICE_TAGS, text)}],
    )
    raw = resp.content[0].text.strip()
    try:
        start = raw.find("{")
        return json.loads(raw[start:raw.rfind("}") + 1])
    except Exception:
        return {"services": [], "caps_certified": False, "insured": False,
                "service_radius_miles": None, "free_consultation": False}


async def process(rows: list[dict], client: Anthropic) -> list[dict]:
    out: list[dict] = []
    sem = asyncio.Semaphore(CONCURRENCY)
    async with AsyncWebCrawler() as crawler:
        async def one(row: dict) -> None:
            async with sem:
                text = await crawl(crawler, row["website"])
                meta = enrich(client, text)
                row["services"] = "|".join(meta.get("services", []))
                row["caps_certified"] = meta.get("caps_certified", False)
                row["insured"] = meta.get("insured", False)
                row["service_radius_miles"] = meta.get("service_radius_miles") or ""
                row["free_consultation"] = meta.get("free_consultation", False)
                out.append(row)
                print(f"[{len(out)}/{len(rows)}] {row['name'][:40]:40} | {len(meta.get('services', []))} services")
        await asyncio.gather(*(one(r) for r in rows))
    return out


def main(in_path: Path, out_path: Path) -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rows = list(csv.DictReader(in_path.open(newline="", encoding="utf-8")))
    enriched = asyncio.run(process(rows, client))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=list(enriched[0].keys()))
        writer.writeheader()
        writer.writerows(enriched)
    print(f"\nEnriched {len(enriched)} listings")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
