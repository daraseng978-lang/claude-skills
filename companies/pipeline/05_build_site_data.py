#!/usr/bin/env python3
"""Step 5 — Convert enriched CSV to site-ready JSON + URL-safe slugs.

Produces two files:
- listings.json     — full flat list for the directory site
- index_by_state.json — state → list of slugs for programmatic SEO routing

Stdlib only.

Usage:
    python 05_build_site_data.py data/04_enriched.csv site/data/
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


def row_to_listing(row: dict) -> dict:
    services = [t for t in (row.get("services") or "").split("|") if t]
    return {
        "id": slugify(f"{row['name']}-{row.get('city', '')}-{row.get('state', '')}"),
        "name": row["name"],
        "slug": slugify(row["name"]),
        "address": row.get("full_address", ""),
        "city": row.get("city", ""),
        "state": row.get("state", ""),
        "postal_code": row.get("postal_code", ""),
        "phone": row.get("phone", ""),
        "website": row.get("website", ""),
        "rating": float(row["rating"]) if row.get("rating") else None,
        "reviews": int(row["reviews"]) if row.get("reviews", "").isdigit() else 0,
        "lat": float(row["latitude"]) if row.get("latitude") else None,
        "lng": float(row["longitude"]) if row.get("longitude") else None,
        "verdict": row.get("verdict", ""),
        "services": services,
        "caps_certified": str(row.get("caps_certified", "")).lower() == "true",
        "insured": str(row.get("insured", "")).lower() == "true",
        "service_radius_miles": int(row["service_radius_miles"])
            if (row.get("service_radius_miles") or "").isdigit() else None,
        "free_consultation": str(row.get("free_consultation", "")).lower() == "true",
    }


def main(in_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    listings = [row_to_listing(r) for r in csv.DictReader(in_path.open(newline="", encoding="utf-8"))]

    by_state: dict[str, list[str]] = defaultdict(list)
    for l in listings:
        if l["state"]:
            by_state[l["state"]].append(l["id"])

    (out_dir / "listings.json").write_text(json.dumps(listings, indent=2))
    (out_dir / "index_by_state.json").write_text(json.dumps(dict(by_state), indent=2))

    print(f"Wrote {len(listings)} listings across {len(by_state)} states to {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
