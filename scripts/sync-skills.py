#!/usr/bin/env python3
"""Copy curated skills from local installs into Barrios_Skills."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"

SOURCES = [
    Path.home() / ".cursor" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".codex" / "skills",
    Path.home() / "Yale University Dropbox" / "John Barrios" / "Claude" / "Skills",
]

EXCLUDE = {"som-llm-api", "figma", "figma-implement-design", "playwright", "vercel-deploy"}

CATEGORY_MAP = {
    "stata-regression": "econometrics",
    "stata-data-cleaning": "econometrics",
    "r-econometrics": "econometrics",
    "python-panel-data": "econometrics",
    "wrds": "econometrics",
    "econ-humanizer": "writing-and-review",
    "econ-humanizer-plus": "writing-and-review",
    "econ-writing-plus": "writing-and-review",
    "academic-paper-writer": "writing-and-review",
    "peer-review": "writing-and-review",
    "hypothesis-generation": "writing-and-review",
    "market-research-reports": "writing-and-review",
    "scholar-evaluation": "writing-and-review",
    "scientific-critical-thinking": "writing-and-review",
    "scientific-slides": "writing-and-review",
    "scientific-writing": "writing-and-review",
    "venue-templates": "writing-and-review",
    "latex-econ-model": "writing-and-review",
    "latex-posters": "writing-and-review",
    "latex-tables": "writing-and-review",
    "beamer-presentation": "writing-and-review",
    "aeon": "data-and-visualization",
    "dask": "data-and-visualization",
    "econ-visualization": "data-and-visualization",
    "geopandas": "data-and-visualization",
    "matplotlib": "data-and-visualization",
    "networkx": "data-and-visualization",
    "plotly": "data-and-visualization",
    "polars": "data-and-visualization",
    "pymc": "data-and-visualization",
    "scikit-learn": "data-and-visualization",
    "seaborn": "data-and-visualization",
    "shap": "data-and-visualization",
    "simpy": "data-and-visualization",
    "statistical-analysis": "data-and-visualization",
    "statsmodels": "data-and-visualization",
    "sympy": "data-and-visualization",
    "umap-learn": "data-and-visualization",
    "vaex": "data-and-visualization",
    "docx": "documents",
    "pdf": "documents",
    "pptx": "documents",
    "xlsx": "documents",
    "markitdown": "documents",
    "doc": "documents",
    "slides": "documents",
    "spreadsheets": "documents",
    "api-data-fetcher": "research-tools",
    "datacommons-client": "research-tools",
    "exploratory-data-analysis": "research-tools",
    "lit-review-assistant": "research-tools",
    "literature-review": "research-tools",
    "paper-2-web": "research-tools",
    "research-ideation": "research-tools",
    "research-lookup": "research-tools",
    "scientific-brainstorming": "research-tools",
    "scientific-schematics": "research-tools",
    "web-scrape": "research-tools",
    "openalex-api": "research-tools",
    "notion-research-documentation": "research-tools",
    "academic-letter-architect": "career-and-grants",
    "career-document-architect": "career-and-grants",
}


def extract_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"')
    return None


def score_dir(path: Path) -> int:
    score = 10 if (path / "SKILL.md").exists() else 0
    scripts = path / "scripts"
    refs = path / "references"
    if scripts.is_dir():
        score += sum(1 for _ in scripts.rglob("*") if _.is_file())
    if refs.is_dir():
        score += sum(1 for _ in refs.rglob("*") if _.is_file())
    skill_md = path / "SKILL.md"
    if skill_md.exists():
        score += len(skill_md.read_bytes()) // 1000
    return score


def iter_skill_dirs(root: Path):
    if not root.is_dir():
        return
    # Dropbox layout
    if (root / "web-scrape" / "SKILL.md").exists():
        yield root / "web-scrape"
    if (root / "kyle_skills" / "SKILL.md").exists():
        yield root / "kyle_skills"
    for item in sorted(root.iterdir()):
        if not item.is_dir() or item.name == ".system":
            continue
        if (item / "SKILL.md").exists():
            yield item
        for sub in item.iterdir():
            if sub.is_dir() and (sub / "SKILL.md").exists():
                yield sub


def main():
    best: dict[str, tuple[int, Path]] = {}
    for root in SOURCES:
        for path in iter_skill_dirs(root):
            name = extract_name(path / "SKILL.md") or path.name
            if name in EXCLUDE:
                continue
            s = score_dir(path)
            if name not in best or s > best[name][0]:
                best[name] = (s, path)

    if SKILLS_ROOT.exists():
        shutil.rmtree(SKILLS_ROOT)
    SKILLS_ROOT.mkdir(parents=True)

    for name, (_, src) in sorted(best.items()):
        cat = CATEGORY_MAP.get(name, "research-tools")
        dest = SKILLS_ROOT / cat / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest)
        print(f"  copied: {name} -> skills/{cat}/{name}")

    print(f"\nSync complete: {len(best)} skills copied")


if __name__ == "__main__":
    main()
