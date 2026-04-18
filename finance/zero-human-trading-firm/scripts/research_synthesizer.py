#!/usr/bin/env python3
"""
Research Synthesizer

Aggregate plaintext/markdown research sources (YouTube transcripts,
paper abstracts, forum dumps, notes) into a ranked idea list. No LLM
calls — deterministic keyword + co-occurrence scoring.

The agents can still reason on top of these ranked candidates; this tool
just makes sure the Strategy Researcher starts each morning with a
structured digest, not a pile of raw text.

Usage:
    python research_synthesizer.py --input-dir research/ \
        --keywords "momentum,mean reversion,carry,funding rate" --top 20

    python research_synthesizer.py --input-dir research/ --format json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple


DEFAULT_KEYWORDS = [
    "momentum", "mean reversion", "carry", "funding rate",
    "volatility", "basis", "arbitrage", "pairs trading",
    "regime", "breakout", "liquidation", "order flow",
    "sentiment", "seasonality", "options skew",
]

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "for",
    "on", "with", "by", "at", "as", "is", "was", "are", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its",
    "from", "if", "then", "so", "we", "you", "they", "he", "she",
    "i", "my", "our", "your", "their", "also", "not", "can", "will",
    "would", "could", "should", "may", "might", "do", "does", "did",
    "have", "has", "had", "about", "into", "over", "under", "than",
    "too", "very", "just", "like", "such", "more", "most", "some", "any",
}


def iter_text_files(root: str) -> List[str]:
    paths: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith((".txt", ".md", ".markdown")):
                paths.append(os.path.join(dirpath, fn))
    return sorted(paths)


def tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z\-']{2,}", text.lower())


def score_file(text: str, keywords: List[str]) -> Dict[str, Any]:
    toks = tokens(text)
    tok_set = set(toks)
    counts = Counter(toks)

    keyword_hits: Dict[str, int] = {}
    for kw in keywords:
        kw_lower = kw.lower()
        if " " in kw_lower:
            # multi-word keyword
            hits = text.lower().count(kw_lower)
        else:
            hits = counts.get(kw_lower, 0)
        if hits:
            keyword_hits[kw] = hits

    novelty_terms = [
        (w, c) for w, c in counts.most_common(100)
        if w not in STOPWORDS and c >= 2 and len(w) > 3
    ][:15]

    total_keyword_hits = sum(keyword_hits.values())
    coverage = len(keyword_hits) / len(keywords) if keywords else 0.0
    density = total_keyword_hits / max(1, len(toks))

    score = (total_keyword_hits * 2) + (coverage * 20) + (density * 100)
    return {
        "tokens": len(toks),
        "unique_tokens": len(tok_set),
        "keyword_hits": keyword_hits,
        "coverage": coverage,
        "density": density,
        "score": round(score, 3),
        "top_terms": novelty_terms,
    }


def synthesize(input_dir: str, keywords: List[str], top: int) -> Dict[str, Any]:
    paths = iter_text_files(input_dir)
    results: List[Dict[str, Any]] = []
    for p in paths:
        try:
            with open(p, "r", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        if not text.strip():
            continue
        scored = score_file(text, keywords)
        scored["path"] = p
        results.append(scored)

    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:top]

    # Cross-file keyword totals
    totals: Counter = Counter()
    for r in results:
        for kw, n in r["keyword_hits"].items():
            totals[kw] += n

    return {
        "input_dir": input_dir,
        "files_scanned": len(results),
        "keywords": keywords,
        "keyword_totals": dict(totals.most_common()),
        "top_files": top_results,
    }


def format_report(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"Research digest: {report['input_dir']}")
    lines.append(f"Files scanned: {report['files_scanned']}")
    lines.append("")
    lines.append("Keyword totals:")
    for kw, n in report["keyword_totals"].items():
        lines.append(f"  {kw:<25} {n}")
    lines.append("")
    lines.append("Top files by score:")
    lines.append("-" * 72)
    for r in report["top_files"]:
        lines.append(f"[{r['score']:>7.2f}] {r['path']}")
        if r["keyword_hits"]:
            hits = ", ".join(f"{k}={v}" for k, v in r["keyword_hits"].items())
            lines.append(f"          keywords: {hits}")
        if r["top_terms"]:
            terms = ", ".join(f"{w}({c})" for w, c in r["top_terms"][:8])
            lines.append(f"          novel terms: {terms}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Rank research sources by keyword relevance")
    p.add_argument("--input-dir", required=True, help="directory of .txt/.md research files")
    p.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS),
                   help="comma-separated keywords (default: trading keywords)")
    p.add_argument("--top", type=int, default=20, help="how many top files to surface")
    p.add_argument("--format", default="text", choices=["text", "json"])
    args = p.parse_args()

    kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    report = synthesize(args.input_dir, kws, args.top)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
