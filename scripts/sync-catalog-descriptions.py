#!/usr/bin/env python3
"""Refresh catalog descriptions and human summaries from each skill's SKILL.md."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "catalog" / "skills.json"

SUMMARY_OVERRIDES: dict[str, str] = {
    "wrds": "Query WRDS libraries — Compustat, CRSP, TRACE, TAQ, and more — with agent-ready SQL patterns.",
    "web-scrape": "Scrape websites, download journal PDFs, and extract tables using the right tool for each source.",
    "econ-humanizer-plus": "Stronger Cochrane-style rules for removing AI tells in economics and finance prose.",
    "econ-writing-plus": "Identification-strategy writing conventions, modern DiD guidance, and AEA submission standards.",
    "econ-lit-search": "Search ~51k economics papers with full-text search, abstracts, and citation sorting.",
    "citation-management": "Find papers, validate metadata, and generate BibTeX for your bibliography.",
    "exploratory-data-analysis": "Profile scientific data files across 200+ formats before analysis.",
    "literature-review": "Systematic literature reviews across PubMed, arXiv, Semantic Scholar, and more.",
    "venue-templates": "LaTeX templates and submission rules for major journals and conferences.",
    "matplotlib": "Fine-grained static plots for publication — full control over every chart element.",
    "research-lookup": "Look up recent research with Perplexity Sonar via OpenRouter, with citations.",
    "sec-edgar": "SEC filings, XBRL financials, and Form 4 via EDGAR MCP — with CIK discipline for accounting research.",
    "pyfixest": "Fast high-dimensional FE regression in Python (fixest-like) for firm–year accounting and finance panels.",
    "financial-text-nlp": "FinBERT and domain models for 10-K, earnings-call, and central-bank text features.",
    "econ-write": "Cochrane/McCloskey/Shapiro-style paper drafting for economics, finance, and accounting.",
    "econ-slides": "Paper-to-Beamer talks with honest numbers, discussant decks, and speaker scripts.",
    "econ-referee": "Pre-submission referee reports with verified comments and a revision plan for econ/finance/accounting.",
}

AGENT_HEAVY_RE = re.compile(
    r"(this skill should be used|use this skill whenever|use this skill when|triggers on:|also use when)",
    re.I,
)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}

    result: dict[str, str] = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith((" ", "\t")) or ":" not in line:
            i += 1
            continue

        key, rest = line.split(":", 1)
        key = key.strip()
        rest = rest.strip()

        if rest in (">", "|", "|-", "|+"):
            folded = rest == ">"
            chunks: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith((" ", "\t")):
                chunks.append(lines[i].strip())
                i += 1
            result[key] = " ".join(chunks) if folded else "\n".join(chunks)
            continue

        if (rest.startswith('"') and rest.endswith('"')) or (
            rest.startswith("'") and rest.endswith("'")
        ):
            rest = rest[1:-1]
        result[key] = rest
        i += 1

    return result


def read_skill_meta(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    return parse_frontmatter(text)


def first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return parts[0].strip() if parts else text.strip()


def agent_heavy(text: str) -> bool:
    return bool(AGENT_HEAVY_RE.search(text))


def make_summary(description: str, skill_id: str) -> str:
    text = re.sub(r"\s+", " ", description).strip()
    if not text or text == ">":
        return SUMMARY_OVERRIDES.get(
            skill_id, "Research workflow skill for economists and accountants."
        )

    if skill_id in SUMMARY_OVERRIDES:
        return SUMMARY_OVERRIDES[skill_id]

    if len(text) <= 130 and not agent_heavy(text):
        return text

    stripped = text
    for pattern in (
        r"^This skill should be used when (?:the user )?",
        r"^Use this skill whenever ",
        r"^Use this skill when ",
        r"^Use when ",
    ):
        stripped = re.sub(pattern, "", stripped, flags=re.I)

    if stripped.count('"') >= 3:
        return SUMMARY_OVERRIDES.get(skill_id, first_sentence(stripped))

    for sep in (
        ". Use this skill",
        ". Use when",
        ". Triggers on",
        ". Also use when",
        ". Best for",
        ". For interactive",
        ". For static",
        ". For larger-than-RAM",
        ". For guided",
        ". Works for",
        ". Complements",
        ". USE when",
        ". USE alongside",
    ):
        if sep in stripped:
            stripped = stripped.split(sep, 1)[0].strip()
            if not stripped.endswith("."):
                stripped += "."
            break

    summary = first_sentence(stripped)
    if len(summary) > 155:
        summary = summary[:152].rsplit(" ", 1)[0] + "…"
    if summary and not summary.endswith(("…", ".", "!", "?")):
        summary += "."
    return summary


def sync_skill(skill: dict) -> bool:
    skill_md = REPO_ROOT / skill["path"] / "SKILL.md"
    if not skill_md.is_file():
        return False

    meta = read_skill_meta(skill_md)
    desc = meta.get("description", "").strip()
    if not desc:
        return False

    summary = meta.get("summary", "").strip() or make_summary(desc, skill["id"])
    changed = skill.get("description") != desc or skill.get("summary") != summary
    skill["description"] = desc
    skill["summary"] = summary
    return changed


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    updated = 0

    for skill in catalog["skills"]:
        if sync_skill(skill):
            updated += 1

    by_id = {s["id"]: s for s in catalog["skills"]}
    for cat in catalog["categories"]:
        for skill in cat["skills"]:
            if skill["id"] in by_id:
                src = by_id[skill["id"]]
                skill["description"] = src["description"]
                skill["summary"] = src["summary"]

    CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Synced descriptions and summaries from SKILL.md ({updated} updated)")


if __name__ == "__main__":
    main()
