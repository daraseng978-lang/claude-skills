#!/usr/bin/env python3
"""Step 2 — Junk-filter the raw Outscraper CSV + split by query.

Drops rows matching obvious non-candidates (big-box retailers, permanently closed,
missing website, out-of-scope categories). Also routes walk-in-tub query rows to
a separate output path so they feed WalkInTubPros instead of AccessRemodel.

Stdlib only. Adapted from Frey's Step 2 Claude Code prompt — codified so it's
deterministic and free to rerun.

Usage:
    python 02_clean.py <raw_csv> <primary_out_csv> [--walkintub-out <path>]

Example:
    python 02_clean.py companies/accessremodel/data/01_raw.csv \\
        companies/accessremodel/data/02_cleaned.csv \\
        --walkintub-out companies/walkintubpros/data/02_cleaned.csv
"""
from __future__ import annotations

import argparse
import csv
import re
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

REQUIRED_FIELDS = ("name", "address", "website")

WALKINTUB_QUERY_MARKERS = ("walk in tub", "walk-in tub", "walkintub")


def is_walkintub(row: dict) -> bool:
    q = (row.get("query") or "").strip().lower()
    return any(m in q for m in WALKINTUB_QUERY_MARKERS)


def is_junk(row: dict) -> tuple[bool, str]:
    name = (row.get("name") or "").strip().lower()
    website = (row.get("website") or "").strip()
    status = (row.get("business_status") or "").strip().lower()
    cat_bits = " ".join([
        (row.get("category") or ""),
        (row.get("subtypes") or ""),
        (row.get("type") or ""),
    ]).strip().lower()

    for field in REQUIRED_FIELDS:
        if not (row.get(field) or "").strip():
            return True, f"missing_{field}"

    if status in {"closed_permanently", "permanently_closed"}:
        return True, "permanently_closed"

    for brand in BIG_BOX_BLOCKLIST:
        if brand in name:
            return True, f"bigbox:{brand}"

    for bad in OFF_NICHE_CATEGORIES:
        if bad in cat_bits:
            return True, f"off_niche:{bad}"

    if not re.match(r"^https?://", website):
        return True, "bad_website_url"

    return False, ""


def main(in_path: Path, primary_out: Path, walkintub_out: Path | None) -> None:
    primary_kept = 0
    walkintub_kept = 0
    dropped: dict[str, int] = {}

    primary_out.parent.mkdir(parents=True, exist_ok=True)
    if walkintub_out is not None:
        walkintub_out.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames or []

        fout_primary = primary_out.open("w", newline="", encoding="utf-8")
        fout_walkintub = walkintub_out.open("w", newline="", encoding="utf-8") if walkintub_out else None

        try:
            writer_primary = csv.DictWriter(fout_primary, fieldnames=fieldnames)
            writer_primary.writeheader()
            writer_walkintub = None
            if fout_walkintub is not None:
                writer_walkintub = csv.DictWriter(fout_walkintub, fieldnames=fieldnames)
                writer_walkintub.writeheader()

            for row in reader:
                junk, reason = is_junk(row)
                if junk:
                    dropped[reason] = dropped.get(reason, 0) + 1
                    continue
                if writer_walkintub is not None and is_walkintub(row):
                    writer_walkintub.writerow(row)
                    walkintub_kept += 1
                else:
                    writer_primary.writerow(row)
                    primary_kept += 1
        finally:
            fout_primary.close()
            if fout_walkintub is not None:
                fout_walkintub.close()

    total_dropped = sum(dropped.values())
    print(f"Primary kept:    {primary_kept:>6}  ->  {primary_out}")
    if walkintub_out is not None:
        print(f"WalkInTub kept:  {walkintub_kept:>6}  ->  {walkintub_out}")
    print(f"Dropped:         {total_dropped:>6}")
    for reason, count in sorted(dropped.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {count}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("raw_csv", type=Path)
    p.add_argument("primary_out", type=Path)
    p.add_argument("--walkintub-out", type=Path, default=None,
                   help="Optional: route rows whose query column mentions 'walk in tub' here")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.raw_csv, args.primary_out, args.walkintub_out)
