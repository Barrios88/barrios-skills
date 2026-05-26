# Collection philosophy

**Barrios Skills** is John Barrios's personal catalog of AI agent workflows for empirical economics and accounting research.

## Core focus (40 skills)

1. **Econometrics & empirical data** — Stata, R, Python panels, WRDS
2. **Data & visualization** — Publication-quality figures and Python data stacks
3. **Research & literature** — Paper search, citations, economic APIs, scraping
4. **Writing & review** — Econ prose voice, LaTeX, referee reports

## Optional (`skills/optional/`)

Document tools, career materials, and specialty libraries that are useful but not central to the collection's mission.

## Curating after sync

```bash
python3 scripts/sync-skills.py
python3 scripts/curate-collection.py
bash scripts/sanitize-skills.sh
bash scripts/audit-secrets.sh
bash scripts/generate-site.sh
```
