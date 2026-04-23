#!/usr/bin/env python3
"""Merge enriched (verified) rows with unverified leftovers, then run Step 5.

Rows in 02_cleaned that are NOT in 04_enriched get:
  - verdict = "unverified", confidence = 0, evidence = ""
  - services, caps_certified, insured, service_radius_miles, free_consultation = empty

Then writes a combined CSV and calls 05_build_site_data.py logic directly.

Usage:
    python 05_merge_and_build.py \\
        <02_cleaned.csv> <04_enriched.csv> <combined.csv> <out_dir/>
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return re.sub(r"-+", "-", s)


TIER_MAP = {"specialist": "specialist", "offers": "offers"}

ENRICH_FIELDS = ["services", "caps_certified", "insured", "service_radius_miles", "free_consultation"]
VERIFY_FIELDS = ["verdict", "confidence", "evidence"]


def row_to_listing(row: dict) -> dict:
    services = [t for t in (row.get("services") or "").split("|") if t]
    verdict = (row.get("verdict") or "").strip().lower()
    tier = TIER_MAP.get(verdict, "unverified")
    return {
        "id": slugify(f"{row['name']}-{row.get('city', '')}-{row.get('state', '')}"),
        "name": row["name"],
        "slug": slugify(row["name"]),
        "address": row.get("address") or row.get("full_address", ""),
        "city": row.get("city", ""),
        "state": row.get("state", ""),
        "postal_code": row.get("postal_code", ""),
        "phone": row.get("phone", ""),
        "website": row.get("website", ""),
        "rating": float(row["rating"]) if row.get("rating") else None,
        "reviews": int(row["reviews"]) if row.get("reviews", "").isdigit() else 0,
        "lat": float(row["latitude"]) if row.get("latitude") else None,
        "lng": float(row["longitude"]) if row.get("longitude") else None,
        "tier": tier,
        "verdict": verdict,
        "confidence": int(row["confidence"]) if (row.get("confidence") or "").isdigit() else 0,
        "services": services,
        "caps_certified": str(row.get("caps_certified", "")).lower() == "true",
        "insured": str(row.get("insured", "")).lower() == "true",
        "service_radius_miles": int(row["service_radius_miles"])
            if (row.get("service_radius_miles") or "").isdigit() else None,
        "free_consultation": str(row.get("free_consultation", "")).lower() == "true",
    }


def main(cleaned_path: Path, enriched_path: Path, combined_path: Path, out_dir: Path) -> None:
    # Load enriched rows, keyed by google_id (fall back to name+city)
    enriched_rows = list(csv.DictReader(enriched_path.open(newline="", encoding="utf-8-sig")))
    enriched_keys = set()
    for r in enriched_rows:
        key = r.get("google_id") or r.get("place_id") or f"{r['name']}|{r.get('city','')}"
        enriched_keys.add(key)

    # Load cleaned rows and find leftovers
    cleaned_rows = list(csv.DictReader(cleaned_path.open(newline="", encoding="utf-8-sig")))
    leftover_rows = []
    for r in cleaned_rows:
        key = r.get("google_id") or r.get("place_id") or f"{r['name']}|{r.get('city','')}"
        if key not in enriched_keys:
            for f in VERIFY_FIELDS:
                r.setdefault(f, "")
            r["verdict"] = "unverified"
            r["confidence"] = "0"
            r["evidence"] = ""
            for f in ENRICH_FIELDS:
                r.setdefault(f, "")
            leftover_rows.append(r)

    print(f"Enriched rows:  {len(enriched_rows)}")
    print(f"Leftover rows:  {len(leftover_rows)}")
    print(f"Total combined: {len(enriched_rows) + len(leftover_rows)}")

    # Build combined fieldnames (enriched has the superset)
    fieldnames = list(enriched_rows[0].keys()) if enriched_rows else list(cleaned_rows[0].keys())
    for f in VERIFY_FIELDS + ENRICH_FIELDS:
        if f not in fieldnames:
            fieldnames.append(f)

    # Pad any missing fields in leftover rows
    for r in leftover_rows:
        for f in fieldnames:
            r.setdefault(f, "")

    combined_path.parent.mkdir(parents=True, exist_ok=True)
    with combined_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(enriched_rows)
        writer.writerows(leftover_rows)

    print(f"Wrote combined CSV → {combined_path}")

    # Step 5: build site data
    out_dir.mkdir(parents=True, exist_ok=True)
    listings = [row_to_listing(r) for r in csv.DictReader(combined_path.open(newline="", encoding="utf-8-sig"))]
    by_state: dict[str, list[str]] = defaultdict(list)
    for lst in listings:
        if lst["state"]:
            by_state[lst["state"]].append(lst["id"])

    (out_dir / "listings.json").write_text(json.dumps(listings, indent=2))
    (out_dir / "index_by_state.json").write_text(json.dumps(dict(by_state), indent=2))
    print(f"Wrote {len(listings)} listings across {len(by_state)} states → {out_dir}")

    # Tier breakdown
    tiers: dict[str, int] = defaultdict(int)
    for lst in listings:
        tiers[lst["tier"]] += 1
    for t, n in sorted(tiers.items()):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
