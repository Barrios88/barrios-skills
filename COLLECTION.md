# Collection philosophy

**Barrios Skills** is John Barrios's personal catalog of **agent skills** (`skills/`) and **MCP servers** (`mcp/`) — kept in separate folders because they install differently — for empirical economics, finance, and accounting research.

## Core focus (46 skills)

1. **Econometrics & empirical data** — Stata, R, Python panels, pyfixest, WRDS
2. **Data & visualization** — Publication-quality figures and Python data stacks
3. **Research & literature** — Paper search, citations, EDGAR/FRED APIs, NLP, scraping
4. **Writing & review** — Econ voice, paper craft, Beamer talks, pre-submission referee

## Optional (`skills/optional/`)

Document tools, career materials, and specialty libraries that are useful but not central to the collection's mission.

## Barrios touch (how upstream tools get curated)

When adopting an external skill or MCP:

1. **Inspect** quality, license, and overlap with the existing catalog
2. **Do not vendor AGPL** MCP source into this MIT repo — document install + write a companion skill
3. **Adapt MIT skills** with `curated-by` / collection banner, accounting–finance defaults, and stack-fit links (`econ-humanizer`, `wrds`, etc.)
4. **Rewrite** when the license is noncommercial or the upstream is a poor fit — keep the workflow idea, own the text
5. Prefer **iron-law checklists** (filters, CIK, clustering, sample inspection) over generic tool tips

## Curating after sync

```bash
python3 scripts/sync-skills.py
python3 scripts/curate-collection.py
bash scripts/sanitize-skills.sh
bash scripts/audit-secrets.sh
bash scripts/generate-site.sh
```
