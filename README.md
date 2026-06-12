# Barrios Skills

John Barrios's curated AI agent skills for **economists and accountants** — focused on econometrics, data visualization, research workflows, and academic writing.

## Website

Browse the collection: `https://YOUR_USERNAME.github.io/barrios-skills/`

Enable GitHub Pages: repo **Settings → Pages → Build from GitHub Actions**.

Local preview:
```bash
cd docs && python3 -m http.server 8080
```


## Repository layout

This repo has **two separate parts**:

| Folder | What it is | Install |
|--------|------------|---------|
| [`skills/`](skills/) | **Agent skills** — markdown instructions (Stata, LaTeX, writing, etc.) | Copy folder to `~/.cursor/skills/` |
| [`mcp/`](mcp/) | **MCP servers** — programs that connect agents to external data | `pip install` + register in Cursor/Claude + your credentials |

Skills teach *how* to work. MCP servers give the agent *live tools* (e.g. run SQL on WRDS).

## What this collection covers

| Area | Skills | What you get |
|------|--------|--------------|
| **Econometrics & empirical data** | 5 | Stata regressions, panel data, WRDS, R IV/DiD/RDD |
| **Data & visualization** | 11 | Econ figures, matplotlib/seaborn, polars, statsmodels, PyMC |
| **Research & literature** | 12 | Econ lit search, citations, FRED/APIs, web scraping, ac/fin paper dissemination |
| **Writing & review** | 13 | Econ voice humanizer, LaTeX tables, peer review, Beamer |

**41 core skills** in the main catalog. Additional document, career, and specialty tools live in [`skills/optional/`](skills/optional/) if you need them.

## Quick start

1. Clone this repo
2. Pick a skill from [Browse by task](#browse-by-task)
3. Copy the folder to your agent's skills directory:
   - [Cursor](install/cursor.md) → `~/.cursor/skills/`
   - [Claude Code](install/claude.md) → `~/.claude/skills/`
   - [Codex](install/codex.md) → `~/.codex/skills/`


## MCP servers (separate from skills)

MCP servers are **not** skills. They live in [`mcp/`](mcp/) and require installation, MCP registration, and often **your own account credentials**.

### WRDS MCP (query Compustat, CRSP, and more)

This repo includes **[wrds-mcp](mcp/wrds-mcp/)** — an MCP server by John Barrios for Wharton WRDS.

**You need your own WRDS account.** Setup (install, your username/password, Duo tunnel, Cursor/Claude config):

→ **[WRDS MCP setup (web)](docs/wrds-mcp.html)** · [Markdown version](install/wrds-mcp.md)

Pair with the [`wrds` skill](skills/econometrics/wrds/) for query filters and table conventions.

## Featured skills

| Skill | What it does |
|-------|--------------|
| [stata-regression](skills/econometrics/stata-regression) | Run regression analyses in Stata with publication-ready output tables |
| [wrds](skills/econometrics/wrds) | This skill should be used when the user asks to "query WRDS", "access Compustat", "get CRSP data", "pull Form 4 insider… |
| [python-panel-data](skills/econometrics/python-panel-data) | Panel data analysis with Python using linearmodels and pandas |
| [econ-humanizer-plus](skills/writing-and-review/econ-humanizer-plus) | Supplements the econ-humanizer skill with a more exhaustive and specific rule set for eliminating AI-generated writing … |
| [latex-tables](skills/writing-and-review/latex-tables) | Generate publication-ready regression tables in LaTeX |
| [econ-lit-search](skills/research-tools/econ-lit-search) | Search a curated corpus of ~51k economics papers (NBER working papers, JEL-coded journals) with full-text search, abstr… |
| [peer-review](skills/writing-and-review/peer-review) | Structured manuscript/grant review with checklist-based evaluation |
| [econ-visualization](skills/data-and-visualization/econ-visualization) | Create publication-quality charts and graphs for economics papers |

## Browse by task

### Econometrics & empirical data

*Stata, R, Python panels, WRDS — identification-ready workflows*

| Skill | Description |
|-------|-------------|
| [stata-regression](skills/econometrics/stata-regression) | Run regression analyses in Stata with publication-ready output tables. |
| [stata-data-cleaning](skills/econometrics/stata-data-cleaning) | Clean and transform messy data in Stata with reproducible workflows |
| [r-econometrics](skills/econometrics/r-econometrics) | Run IV, DiD, and RDD analyses in R with proper diagnostics |
| [python-panel-data](skills/econometrics/python-panel-data) | Panel data analysis with Python using linearmodels and pandas. |
| [wrds](skills/econometrics/wrds) | This skill should be used when the user asks to "query WRDS", "access Compustat", "get CRSP data", … |

### Data & visualization

*Publication figures and Python data stacks for applied work*

| Skill | Description |
|-------|-------------|
| [econ-visualization](skills/data-and-visualization/econ-visualization) | Create publication-quality charts and graphs for economics papers. |
| [matplotlib](skills/data-and-visualization/matplotlib) | Low-level plotting library for full customization. Use when you need fine-grained control over ever… |
| [seaborn](skills/data-and-visualization/seaborn) | Statistical visualization with pandas integration. Use for quick exploration of distributions, rela… |
| [plotly](skills/data-and-visualization/plotly) | Interactive visualization library. Use when you need hover info, zoom, pan, or web-embeddable chart… |
| [polars](skills/data-and-visualization/polars) | Fast in-memory DataFrame library for datasets that fit in RAM. Use when pandas is too slow but data… |
| [statsmodels](skills/data-and-visualization/statsmodels) | Statistical models library for Python. Use when you need specific model classes (OLS, GLM, mixed mo… |
| [scikit-learn](skills/data-and-visualization/scikit-learn) | Machine learning in Python with scikit-learn. Use when working with supervised learning (classifica… |
| [statistical-analysis](skills/data-and-visualization/statistical-analysis) | Guided statistical analysis with test selection and reporting. Use when you need help choosing appr… |
| [pymc-bayesian-modeling](skills/data-and-visualization/pymc-bayesian-modeling) | Bayesian modeling with PyMC. Build hierarchical models, MCMC (NUTS), variational inference, LOO/WAI… |
| [dask](skills/data-and-visualization/dask) | Distributed computing for larger-than-RAM pandas/NumPy workflows. Use when you need to scale existi… |
| [geopandas](skills/data-and-visualization/geopandas) | Python library for working with geospatial vector data including shapefiles, GeoJSON, and GeoPackag… |

### Research & literature

*Literature search, citations, APIs, and journal data collection*

| Skill | Description |
|-------|-------------|
| [api-data-fetcher](skills/research-tools/api-data-fetcher) | Fetch economic data from FRED, World Bank, and other APIs |
| [citation-management](skills/research-tools/citation-management) | Comprehensive citation management for academic research. Search Google Scholar and PubMed for paper… |
| [datacommons-client](skills/research-tools/datacommons-client) | Work with Data Commons, a platform providing programmatic access to public statistical data from gl… |
| [econ-lit-search](skills/research-tools/econ-lit-search) | Search a curated corpus of ~51k economics papers (NBER working papers, JEL-coded journals) with ful… |
| [exploratory-data-analysis](skills/research-tools/exploratory-data-analysis) | Perform comprehensive exploratory data analysis on scientific data files across 200+ file formats. … |
| [lit-review-assistant](skills/research-tools/lit-review-assistant) | Search, summarize, and synthesize economics literature |
| [literature-review](skills/research-tools/literature-review) | Conduct comprehensive, systematic literature reviews using multiple academic databases (PubMed, arX… |
| [openalex-api](skills/research-tools/openalex-api) | Access and analyze OpenAlex scholarly metadata through the REST API, including works, authors, inst… |
| [research-ideation](skills/research-tools/research-ideation) | Generate research questions from economic phenomena |
| [research-lookup](skills/research-tools/research-lookup) | Look up current research information using Perplexity Sonar Pro Search or Sonar Reasoning Pro model… |
| [web-scrape](skills/research-tools/web-scrape) |  |
| [paper-2-acfin-web](skills/research-tools/paper-2-acfin-web) | Convert accounting and finance papers into websites, seminar videos, and conference posters (Paper2All) |

### Writing & review

*Econ voice, LaTeX, referee reports, and paper structure*

| Skill | Description |
|-------|-------------|
| [academic-paper-writer](skills/writing-and-review/academic-paper-writer) | Draft economics papers with proper structure and academic style |
| [beamer-presentation](skills/writing-and-review/beamer-presentation) | Create academic presentations in Beamer with professional themes |
| [econ-humanizer](skills/writing-and-review/econ-humanizer) | Remove AI writing patterns from academic economics, finance, and accounting prose. Enforces a clear… |
| [econ-humanizer-plus](skills/writing-and-review/econ-humanizer-plus) | Supplements the econ-humanizer skill with a more exhaustive and specific rule set for eliminating A… |
| [econ-writing-plus](skills/writing-and-review/econ-writing-plus) | Supplements economic-writing, econ-humanizer, academic-paper-writer, research-grants, and referee-r… |
| [hypothesis-generation](skills/writing-and-review/hypothesis-generation) | Structured hypothesis formulation from observations. Use when you have experimental observations or… |
| [latex-econ-model](skills/writing-and-review/latex-econ-model) | Write and typeset economic models in LaTeX with proper notation |
| [latex-posters](skills/writing-and-review/latex-posters) | Create professional research posters in LaTeX using beamerposter, tikzposter, or baposter. Support … |
| [latex-tables](skills/writing-and-review/latex-tables) | Generate publication-ready regression tables in LaTeX. |
| [peer-review](skills/writing-and-review/peer-review) | Structured manuscript/grant review with checklist-based evaluation. Use when writing formal peer re… |
| [scholar-evaluation](skills/writing-and-review/scholar-evaluation) | Systematically evaluate scholarly work using the ScholarEval framework, providing structured assess… |
| [scientific-critical-thinking](skills/writing-and-review/scientific-critical-thinking) | Evaluate scientific claims and evidence quality. Use for assessing experimental design validity, id… |
| [venue-templates](skills/writing-and-review/venue-templates) | Access comprehensive LaTeX templates, formatting requirements, and submission guidelines for major … |

## Optional skills

See [`skills/optional/README.md`](skills/optional/README.md) for document tools (Word, PDF, Excel), career materials, and specialty Python libraries not in the core set.

## Maintenance

```bash
python3 scripts/sync-skills.py      # refresh from local installs
bash scripts/sanitize-skills.sh
bash scripts/audit-secrets.sh
bash scripts/generate-site.sh         # update website catalog
```

See [SECURITY.md](SECURITY.md) for redacted secrets and required env vars.

## License

MIT — see [LICENSE](LICENSE).
