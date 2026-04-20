#!/usr/bin/env python3
"""
kdp_listing_builder.py — Build a KDP listing (title, subtitle, description,
7 backend keywords, 2 browse categories) from a concept brief.

Deterministic: assembles the listing by slotting keywords into KDP-safe
templates, validates character limits, and flags policy risks (banned words,
excessive stuffing, trademark terms you supplied).

Standard library only. No LLM calls.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Dict, List


# KDP field limits (as of 2026). See:
# kdp.amazon.com/en_US/help/topic/G201834380
LIMITS = {
    "title": 200,
    "subtitle": 200,
    "title_plus_subtitle": 200,  # Amazon display truncates ~200 chars combined
    "description": 4000,
    "keyword_each": 50,
    "keywords_count": 7,
    "author_name": 50,
}

# Words that KDP policy flags as misleading or stuffing.
BANNED_WORDS = {
    "bestseller", "#1", "best seller", "free", "amazon", "kindle unlimited",
    "new release", "sale", "discount", "award-winning", "nyt", "new york times",
}

# Reserved brand / franchise names you must never use.
DEFAULT_TRADEMARK_DENYLIST = {
    "disney", "pixar", "marvel", "pokemon", "pokémon", "harry potter",
    "star wars", "nfl", "nba", "mlb", "fifa", "minecraft", "roblox", "lego",
    "barbie", "nintendo", "playstation", "xbox",
}


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _contains_any(text: str, words) -> List[str]:
    t = text.lower()
    return [w for w in words if w in t]


def build_title(concept: Dict) -> str:
    """Format: {Size/Style} {Puzzle Type} {For Audience}"""
    parts = [concept.get("size_modifier", "").strip(),
             concept["puzzle_type"].strip(),
             f"for {concept['audience']}".strip()]
    title = " ".join(p for p in parts if p)
    # Capitalize
    return " ".join(w.capitalize() if w.islower() else w for w in title.split())


def build_subtitle(concept: Dict) -> str:
    """Format: {Volume/Count} {Themed Variants}, {Difficulty}, {Benefit}"""
    count = concept.get("puzzle_count", 100)
    theme = concept.get("theme", "").strip()
    difficulty = concept.get("difficulty", "Easy to Hard").strip()
    benefit = concept.get("benefit", "").strip()
    pieces = [f"{count} {concept['puzzle_type']} Puzzles"]
    if theme:
        pieces.append(f"with {theme} Themes")
    pieces.append(difficulty)
    if benefit:
        pieces.append(benefit)
    return ", ".join(pieces)


def build_description(concept: Dict) -> str:
    audience = concept["audience"]
    ptype = concept["puzzle_type"]
    count = concept.get("puzzle_count", 100)
    theme = concept.get("theme", "engaging")
    difficulty = concept.get("difficulty", "easy to hard")
    size = concept.get("size_modifier", "large-print").lower()
    benefits = concept.get("benefits", [
        "Sharpens memory and focus",
        "Relaxes the mind after a long day",
        "Perfect quiet-time activity",
    ])
    pages = concept.get("pages", count + 20)

    lines = []
    lines.append(f"**{count} hand-crafted {ptype.lower()} puzzles for {audience.lower()}.**")
    lines.append("")
    lines.append(f"Inside this {size} {ptype.lower()} book you'll find:")
    lines.append("")
    lines.append(f"- {count} unique {ptype.lower()} puzzles, {difficulty.lower()}")
    lines.append(f"- {theme.capitalize()} themes across every puzzle")
    lines.append(f"- {size.capitalize()} grid and answer key at the back")
    lines.append(f"- {pages} pages, sturdy matte cover, perfect bound")
    lines.append("")
    lines.append("Why you'll love it:")
    lines.append("")
    for b in benefits:
        lines.append(f"- {b}")
    lines.append("")
    lines.append(f"A thoughtful gift for {audience.lower()}, grandparents, or anyone who loves a good puzzle. Click **Add to Cart** to get your copy today.")
    return "\n".join(lines)


def build_keywords(concept: Dict) -> List[str]:
    """Return up to 7 keyword phrases. Each must be distinct and <=50 chars."""
    ptype = concept["puzzle_type"].lower()
    audience = concept["audience"].lower()
    theme = concept.get("theme", "").lower().strip()
    extras = concept.get("extra_keywords", [])

    base = [
        f"{ptype} puzzle book",
        f"{ptype} book for {audience}",
        f"{ptype} puzzles {audience}",
        "large print puzzle book",
        "activity book gift",
    ]
    if theme:
        base.insert(2, f"{theme} {ptype} puzzles")
    seen = set()
    out = []
    for kw in base + list(extras):
        k = kw.strip().lower()
        if not k or k in seen:
            continue
        if len(k) > LIMITS["keyword_each"]:
            continue
        seen.add(k)
        out.append(k)
        if len(out) == LIMITS["keywords_count"]:
            break
    return out


def build_categories(concept: Dict) -> List[str]:
    """KDP allows 2 browse categories. Defaults per puzzle type."""
    overrides = concept.get("categories")
    if overrides:
        return overrides[:2]

    ptype = concept["puzzle_type"].lower()
    audience = concept["audience"].lower()
    defaults = {
        "word search": [
            "Humor & Entertainment > Puzzles & Games > Word Search",
            "Crafts, Hobbies & Home > Games & Activities > Word Games",
        ],
        "sudoku": [
            "Humor & Entertainment > Puzzles & Games > Sudoku",
            "Crafts, Hobbies & Home > Games & Activities > Logic & Brain Teasers",
        ],
        "mazes": [
            "Children's Books > Activities, Crafts & Games > Games",
            "Humor & Entertainment > Puzzles & Games > Mazes",
        ],
        "cryptogram": [
            "Humor & Entertainment > Puzzles & Games > Cryptograms",
            "Crafts, Hobbies & Home > Games & Activities > Logic & Brain Teasers",
        ],
    }
    for key, cats in defaults.items():
        if key in ptype:
            if "kid" in audience or "child" in audience:
                cats = [c for c in cats if "Children" in c] + [c for c in cats if "Children" not in c]
            return cats[:2]
    return [
        "Humor & Entertainment > Puzzles & Games",
        "Crafts, Hobbies & Home > Games & Activities",
    ]


def validate(listing: Dict, denylist) -> List[str]:
    issues = []
    if len(listing["title"]) > LIMITS["title"]:
        issues.append(f"Title too long ({len(listing['title'])}/{LIMITS['title']}).")
    if len(listing["subtitle"]) > LIMITS["subtitle"]:
        issues.append(f"Subtitle too long ({len(listing['subtitle'])}/{LIMITS['subtitle']}).")
    combined = len(listing["title"]) + len(listing["subtitle"])
    if combined > LIMITS["title_plus_subtitle"] + LIMITS["subtitle"]:
        issues.append("Title+subtitle combined exceeds KDP display limits.")
    if len(listing["description"]) > LIMITS["description"]:
        issues.append(f"Description too long ({len(listing['description'])}/{LIMITS['description']}).")
    if len(listing["keywords"]) > LIMITS["keywords_count"]:
        issues.append(f"Too many keywords ({len(listing['keywords'])}/{LIMITS['keywords_count']}).")
    for k in listing["keywords"]:
        if len(k) > LIMITS["keyword_each"]:
            issues.append(f"Keyword exceeds 50 chars: {k!r}")

    full = " ".join([listing["title"], listing["subtitle"], listing["description"]] + listing["keywords"]).lower()
    hit_banned = _contains_any(full, BANNED_WORDS)
    if hit_banned:
        issues.append(f"Contains KDP-banned words: {hit_banned}")
    hit_tm = _contains_any(full, denylist)
    if hit_tm:
        issues.append(f"Contains trademark/franchise terms: {hit_tm}")

    # Naive stuffing check: no token should appear >6 times in description.
    desc = listing["description"].lower()
    tokens = re.findall(r"\b[a-z]{4,}\b", desc)
    from collections import Counter
    top = Counter(tokens).most_common(3)
    for word, n in top:
        if n > 6 and word not in {"puzzle", "puzzles"}:
            issues.append(f"Possible keyword stuffing: '{word}' appears {n}× in description.")
            break

    return issues


def build(concept: Dict, denylist) -> Dict:
    listing = {
        "title": build_title(concept),
        "subtitle": build_subtitle(concept),
        "description": build_description(concept),
        "keywords": build_keywords(concept),
        "categories": build_categories(concept),
    }
    listing["character_counts"] = {
        "title": len(listing["title"]),
        "subtitle": len(listing["subtitle"]),
        "description": len(listing["description"]),
    }
    listing["issues"] = validate(listing, denylist)
    return listing


def render_text(r: Dict) -> str:
    lines = []
    lines.append("=" * 64)
    lines.append(f"TITLE    ({r['character_counts']['title']}/200)")
    lines.append(r["title"])
    lines.append("")
    lines.append(f"SUBTITLE ({r['character_counts']['subtitle']}/200)")
    lines.append(r["subtitle"])
    lines.append("")
    lines.append(f"DESCRIPTION ({r['character_counts']['description']}/4000)")
    lines.append("-" * 64)
    lines.append(r["description"])
    lines.append("-" * 64)
    lines.append("")
    lines.append("KEYWORDS (7 backend slots):")
    for i, k in enumerate(r["keywords"], 1):
        lines.append(f"  {i}. {k}")
    lines.append("")
    lines.append("CATEGORIES (2 browse paths):")
    for c in r["categories"]:
        lines.append(f"  • {c}")
    lines.append("")
    if r["issues"]:
        lines.append("⚠ ISSUES:")
        for issue in r["issues"]:
            lines.append(f"  - {issue}")
    else:
        lines.append("✓ No issues. Listing is KDP-ready pending human QA.")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build a KDP puzzle-book listing.")
    p.add_argument("--input", required=True, help="JSON concept brief (see assets/sample_listing_inputs.json)")
    p.add_argument("--denylist", help="Extra trademark/brand file (one term per line)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    with open(args.input) as f:
        concept = json.load(f)

    denylist = set(DEFAULT_TRADEMARK_DENYLIST)
    if args.denylist:
        with open(args.denylist) as f:
            for line in f:
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    denylist.add(line)

    result = build(concept, denylist)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))
    return 0 if not result["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
