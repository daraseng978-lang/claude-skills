#!/usr/bin/env python3
"""Step 2 — Junk-filter the raw Outscraper CSV.

Drops rows matching obvious non-candidates (big-box retailers, permanently closed,
missing website, out-of-scope categories).

Stdlib only. Adapted from Frey's Step 2 Claude Code prompt — codified so it's
deterministic and free to rerun.

Usage:
    python 02_clean.py data/01_raw.csv data/02_cleaned.csv
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

BIG_BOX_BLOCKLIST = {
    "home depot", "lowe's", "lowes", "menards", "ace hardware",
    "walmart", "target", "ikea", "floor & decor", "ferguson",
    "sherwin-williams", "benjamin moore",
}

OFF_NICHE_CATEGORIES = {
    "real estate agency", "pest control service", "dentist",
    "restaurant", "cafe", "gas station", "car wash", "auto repair shop",
    "grocery store", "bank", "pharmacy", "hair salon", "barber shop",
    "hotel", "motel", "school", "church",
}

REQUIRED_FIELDS = ("name", "full_address", "website")


def is_junk(row: dict) -> tuple[bool, str]:
    name = (row.get("name") or "").strip().lower()
    website = (row.get("website") or "").strip()
    status = (row.get("business_status") or "").strip().lower()
    categories = (row.get("categories") or "").strip().lower()

    for field in REQUIRED_FIELDS:
        if not (row.get(field) or "").strip():
            return True, f"missing_{field}"

    if status in {"closed_permanently", "permanently_closed"}:
        return True, "permanently_closed"

    for brand in BIG_BOX_BLOCKLIST:
        if brand in name:
            return True, f"bigbox:{brand}"

    for bad in OFF_NICHE_CATEGORIES:
        if bad in categories:
            return True, f"off_niche:{bad}"

    if not re.match(r"^https?://", website):
        return True, "bad_website_url"

    return False, ""


def main(in_path: Path, out_path: Path) -> None:
    kept = 0
    dropped: dict[str, int] = {}
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open(newline="", encoding="utf-8") as fin, \
         out_path.open("w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames or [])
        writer.writeheader()
        for row in reader:
            junk, reason = is_junk(row)
            if junk:
                dropped[reason] = dropped.get(reason, 0) + 1
                continue
            writer.writerow(row)
            kept += 1

    total_dropped = sum(dropped.values())
    print(f"Kept:    {kept:>6}")
    print(f"Dropped: {total_dropped:>6}")
    for reason, count in sorted(dropped.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {count}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
