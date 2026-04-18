#!/usr/bin/env python3
"""
reel_ideator — generate funny reel idea seeds.

Stdlib-only. No network, no ML. Deterministic with --seed.

Usage:
    python3 reel_ideator.py --topic "solo founder life" --count 10 --platform tiktok
    python3 reel_ideator.py --topic "agency life" --pillar relatable --format json
    python3 reel_ideator.py                 # demo mode, prints samples
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import asdict, dataclass
from typing import List

FRAMEWORKS = [
    "rule-of-3",
    "misdirection",
    "escalation",
    "callback",
    "contrast",
    "relatable-specific",
    "character-commitment",
    "observational-absurdism",
]

FORMATS = [
    "POV skit",
    "talking head",
    "text-on-screen + b-roll",
    "green-screen react",
    "split-screen contrast",
    "duet / stitch",
    "trend remix",
]

PILLARS = {
    "relatable": "universal pain point, viewer nods",
    "educational-comedy": "teach something while being funny",
    "trend": "remix a current audio/format",
    "behind-the-scenes": "show the mess behind the polish",
    "hot-take": "controversial opinion, invites debate",
    "character": "recurring persona, franchise-builder",
}

HOOK_PATTERNS = [
    "POV: {topic} gone wrong",
    "3 things only {topic} people will get",
    "The dumbest thing about {topic}",
    "Why {topic} is actually broken",
    "Nobody talks about this part of {topic}",
    "I tried {topic} for 30 days. Here's what nobody warns you about",
    "Stop doing {topic} like this",
    "{topic} in 2020 vs 2026",
    "Things I wish I knew before {topic}",
    "The {topic} starter pack",
    "If {topic} was a person",
    "Rating {topic} takes as a former insider",
]

PLATFORM_LENGTH = {
    "tiktok": "15-30s",
    "instagram": "15-30s",
    "facebook": "30-60s",
    "all": "20-30s master, export per platform",
}


@dataclass
class ReelIdea:
    hook: str
    framework: str
    format: str
    pillar: str
    length: str
    platform: str
    beat_sketch: str


def beat_sketch(framework: str, topic: str) -> str:
    sketches = {
        "rule-of-3": f"Two normal {topic} takes, third is absurd.",
        "misdirection": f"Setup sounds like a serious {topic} tip, payoff undercuts it.",
        "escalation": f"Same {topic} joke, 3x bigger each beat.",
        "callback": f"Reference an earlier {topic} reel in the background.",
        "contrast": f"{topic} on LinkedIn vs {topic} at 2 AM.",
        "relatable-specific": f"Weirdly specific {topic} moment viewers recognize instantly.",
        "character-commitment": f"Heightened {topic} persona — stay in character the full reel.",
        "observational-absurdism": f"Point out mundane {topic} thing, treat it like it's insane.",
    }
    return sketches.get(framework, f"{framework} applied to {topic}.")


def generate(topic: str, count: int, platform: str, pillar: str | None, rng: random.Random) -> List[ReelIdea]:
    ideas: List[ReelIdea] = []
    length = PLATFORM_LENGTH.get(platform, PLATFORM_LENGTH["all"])
    for _ in range(count):
        framework = rng.choice(FRAMEWORKS)
        fmt = rng.choice(FORMATS)
        chosen_pillar = pillar if pillar else rng.choice(list(PILLARS.keys()))
        hook = rng.choice(HOOK_PATTERNS).format(topic=topic)
        ideas.append(
            ReelIdea(
                hook=hook,
                framework=framework,
                format=fmt,
                pillar=chosen_pillar,
                length=length,
                platform=platform,
                beat_sketch=beat_sketch(framework, topic),
            )
        )
    return ideas


def print_human(ideas: List[ReelIdea]) -> None:
    for i, idea in enumerate(ideas, 1):
        print(f"\n[{i}] {idea.hook}")
        print(f"    pillar:    {idea.pillar}")
        print(f"    framework: {idea.framework}")
        print(f"    format:    {idea.format}")
        print(f"    length:    {idea.length}  ({idea.platform})")
        print(f"    sketch:    {idea.beat_sketch}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate funny reel idea seeds for FB / IG / TikTok.",
    )
    parser.add_argument("--topic", default="solo founder life", help="Topic / theme for the reels.")
    parser.add_argument("--count", type=int, default=5, help="Number of ideas to generate.")
    parser.add_argument(
        "--platform",
        choices=["tiktok", "instagram", "facebook", "all"],
        default="all",
        help="Target platform (drives length sweet spot).",
    )
    parser.add_argument(
        "--pillar",
        choices=list(PILLARS.keys()),
        help="Pin all ideas to one pillar. If omitted, pillars rotate randomly.",
    )
    parser.add_argument("--seed", type=int, help="Seed RNG for deterministic output.")
    parser.add_argument("--format", choices=["human", "json"], default="human")
    args = parser.parse_args(argv)

    if args.count < 1 or args.count > 100:
        parser.error("--count must be between 1 and 100")

    rng = random.Random(args.seed)
    ideas = generate(args.topic, args.count, args.platform, args.pillar, rng)

    if args.format == "json":
        print(json.dumps([asdict(i) for i in ideas], indent=2))
    else:
        print(f"\nRahrah Media — funny-reels ideator")
        print(f"topic: {args.topic} | platform: {args.platform} | count: {args.count}")
        if args.pillar:
            print(f"pillar: {args.pillar} — {PILLARS[args.pillar]}")
        print_human(ideas)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
