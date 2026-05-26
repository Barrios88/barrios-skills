# Barrios Skills

Curated AI agent skills for **economists and accountants**. Each skill is a folder of instructions that teaches Cursor, Claude, or Codex how to handle a specific research workflow — regressions, LaTeX tables, literature search, document editing, and more.

## Quick start

1. **Clone this repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/barrios-skills.git
   cd barrios-skills
   ```

2. **Pick a skill** from the [catalog below](#browse-by-task) — for example `stata-regression` or `econ-humanizer-plus`.

3. **Install it** for your AI tool:
   - [Cursor](install/cursor.md) — copy to `~/.cursor/skills/`
   - [Claude Code](install/claude.md) — copy to `~/.claude/skills/`
   - [Codex](install/codex.md) — copy to `~/.codex/skills/`

That's it. The agent reads each skill's `SKILL.md` and applies it when your request matches the skill's description.

## Featured skills

| Skill | What it does |
|-------|--------------|
| [stata-regression](skills/econometrics/stata-regression) | Run regression analyses in Stata with publication-ready output tables |
| [econ-humanizer-plus](skills/writing-and-review/econ-humanizer-plus) | Supplements the econ-humanizer skill with a more exhaustive and specific rule set for eliminating AI-generated writing p |
| [wrds](skills/econometrics/wrds) | This skill should be used when the user asks to "query WRDS", "access Compustat", "get CRSP data", "pull Form 4 insider  |
| [latex-tables](skills/writing-and-review/latex-tables) | Generate publication-ready regression tables in LaTeX |
| [web-scrape](skills/research-tools/web-scrape) | > |
| [peer-review](skills/writing-and-review/peer-review) | Structured manuscript/grant review with checklist-based evaluation |
| [econ-lit-search](skills/research-tools/econ-lit-search) | Search a curated corpus of ~51k economics papers (NBER working papers, JEL-coded journals) with full-text search, abstra |
| [academic-paper-writer](skills/writing-and-review/academic-paper-writer) | Draft economics papers with proper structure and academic style |

## Browse by task

### Career & grants

*Letters of recommendation, CVs, research statements*

| Skill | Description |
|-------|-------------|
| [academic-letter-architect](skills/career-and-grants/academic-letter-architect) | Use when writing recommendation letters, reference letters, or award nominations for students, postd... |
| [career-document-architect](skills/career-and-grants/career-document-architect) | Use when writing or reviewing career documents including research statements, teaching statements, d... |

### Data & visualization

*Explore, model, and chart data in Python*

| Skill | Description |
|-------|-------------|
| [aeon](skills/data-and-visualization/aeon) | This skill should be used for time series machine learning tasks including classification, regressio... |
| [dask](skills/data-and-visualization/dask) | Distributed computing for larger-than-RAM pandas/NumPy workflows. Use when you need to scale existin... |
| [econ-visualization](skills/data-and-visualization/econ-visualization) | Create publication-quality charts and graphs for economics papers. |
| [geopandas](skills/data-and-visualization/geopandas) | Python library for working with geospatial vector data including shapefiles, GeoJSON, and GeoPackage... |
| [matplotlib](skills/data-and-visualization/matplotlib) | Low-level plotting library for full customization. Use when you need fine-grained control over every... |
| [networkx](skills/data-and-visualization/networkx) | Comprehensive toolkit for creating, analyzing, and visualizing complex networks and graphs in Python... |
| [plotly](skills/data-and-visualization/plotly) | Interactive visualization library. Use when you need hover info, zoom, pan, or web-embeddable charts... |
| [polars](skills/data-and-visualization/polars) | Fast in-memory DataFrame library for datasets that fit in RAM. Use when pandas is too slow but data ... |
| [pymc-bayesian-modeling](skills/data-and-visualization/pymc-bayesian-modeling) | Bayesian modeling with PyMC. Build hierarchical models, MCMC (NUTS), variational inference, LOO/WAIC... |
| [scikit-learn](skills/data-and-visualization/scikit-learn) | Machine learning in Python with scikit-learn. Use when working with supervised learning (classificat... |
| [seaborn](skills/data-and-visualization/seaborn) | Statistical visualization with pandas integration. Use for quick exploration of distributions, relat... |
| [shap](skills/data-and-visualization/shap) | Model interpretability and explainability using SHAP (SHapley Additive exPlanations). Use this skill... |
| [simpy](skills/data-and-visualization/simpy) | Process-based discrete-event simulation framework in Python. Use this skill when building simulation... |
| [statistical-analysis](skills/data-and-visualization/statistical-analysis) | Guided statistical analysis with test selection and reporting. Use when you need help choosing appro... |
| [statsmodels](skills/data-and-visualization/statsmodels) | Statistical models library for Python. Use when you need specific model classes (OLS, GLM, mixed mod... |
| [sympy](skills/data-and-visualization/sympy) | Use this skill when working with symbolic mathematics in Python. This skill should be used for symbo... |
| [umap-learn](skills/data-and-visualization/umap-learn) | UMAP dimensionality reduction. Fast nonlinear manifold learning for 2D/3D visualization, clustering ... |
| [vaex](skills/data-and-visualization/vaex) | Use this skill for processing and analyzing large tabular datasets (billions of rows) that exceed av... |

### Documents

*Work with Word, Excel, PDF, and PowerPoint files*

| Skill | Description |
|-------|-------------|
| [doc](skills/documents/doc) | Use when the task involves reading, creating, or editing `.docx` documents, especially when formatti... |
| [docx](skills/documents/docx) | Document toolkit (.docx). Create/edit documents, tracked changes, comments, formatting preservation,... |
| [markitdown](skills/documents/markitdown) | Convert files and office documents to Markdown. Supports PDF, DOCX, PPTX, XLSX, images (with OCR), a... |
| [pdf](skills/documents/pdf) | PDF manipulation toolkit. Extract text/tables, create PDFs, merge/split, fill forms, for programmati... |
| [pptx](skills/documents/pptx) | Presentation toolkit (.pptx). Create/edit slides, layouts, content, speaker notes, comments, for pro... |
| [PowerPoint](skills/documents/slides) | Create, edit, render, verify, and export PowerPoint slide decks. Use when Codex needs to build or mo... |
| [Excel](skills/documents/spreadsheets) | Use this skill when a user requests to create, modify, analyze, visualize, or work with spreadsheet ... |
| [xlsx](skills/documents/xlsx) | Spreadsheet toolkit (.xlsx/.csv). Create/edit with formulas/formatting, analyze data, visualization,... |

### Econometrics & data

*Run regressions, pull Compustat, clean panel data*

| Skill | Description |
|-------|-------------|
| [python-panel-data](skills/econometrics/python-panel-data) | Panel data analysis with Python using linearmodels and pandas. |
| [r-econometrics](skills/econometrics/r-econometrics) | Run IV, DiD, and RDD analyses in R with proper diagnostics |
| [stata-data-cleaning](skills/econometrics/stata-data-cleaning) | Clean and transform messy data in Stata with reproducible workflows |
| [stata-regression](skills/econometrics/stata-regression) | Run regression analyses in Stata with publication-ready output tables. |
| [wrds](skills/econometrics/wrds) | This skill should be used when the user asks to "query WRDS", "access Compustat", "get CRSP data", "... |

### Research tools

*Find papers, scrape journals, build project websites*

| Skill | Description |
|-------|-------------|
| [api-data-fetcher](skills/research-tools/api-data-fetcher) | Fetch economic data from FRED, World Bank, and other APIs |
| [citation-management](skills/research-tools/citation-management) | Comprehensive citation management for academic research. Search Google Scholar and PubMed for papers... |
| [datacommons-client](skills/research-tools/datacommons-client) | Work with Data Commons, a platform providing programmatic access to public statistical data from glo... |
| [econ-lit-search](skills/research-tools/econ-lit-search) | Search a curated corpus of ~51k economics papers (NBER working papers, JEL-coded journals) with full... |
| [exploratory-data-analysis](skills/research-tools/exploratory-data-analysis) | Perform comprehensive exploratory data analysis on scientific data files across 200+ file formats. T... |
| [lit-review-assistant](skills/research-tools/lit-review-assistant) | Search, summarize, and synthesize economics literature |
| [literature-review](skills/research-tools/literature-review) | Conduct comprehensive, systematic literature reviews using multiple academic databases (PubMed, arXi... |
| [notion-research-documentation](skills/research-tools/notion-research-documentation) | Research across Notion and synthesize into structured documentation; use when gathering info from mu... |
| [openalex-api](skills/research-tools/openalex-api) | Access and analyze OpenAlex scholarly metadata through the REST API, including works, authors, insti... |
| [paper-2-web](skills/research-tools/paper-2-web) | This skill should be used when converting academic papers into promotional and presentation formats ... |
| [research-ideation](skills/research-tools/research-ideation) | Generate research questions from economic phenomena |
| [research-lookup](skills/research-tools/research-lookup) | Look up current research information using Perplexity Sonar Pro Search or Sonar Reasoning Pro models... |
| [scientific-brainstorming](skills/research-tools/scientific-brainstorming) | Creative research ideation and exploration. Use for open-ended brainstorming sessions, exploring int... |
| [scientific-schematics](skills/research-tools/scientific-schematics) | Create publication-quality scientific diagrams using Nano Banana Pro AI with smart iterative refinem... |
| [web-scrape](skills/research-tools/web-scrape) | > |

### Writing & review

*Polish prose, write papers, referee reports, LaTeX tables*

| Skill | Description |
|-------|-------------|
| [academic-paper-writer](skills/writing-and-review/academic-paper-writer) | Draft economics papers with proper structure and academic style |
| [beamer-presentation](skills/writing-and-review/beamer-presentation) | Create academic presentations in Beamer with professional themes |
| [econ-humanizer](skills/writing-and-review/econ-humanizer) | Remove AI writing patterns from academic economics, finance, and accounting prose. Enforces a clear,... |
| [econ-humanizer-plus](skills/writing-and-review/econ-humanizer-plus) | Supplements the econ-humanizer skill with a more exhaustive and specific rule set for eliminating AI... |
| [econ-writing-plus](skills/writing-and-review/econ-writing-plus) | Supplements economic-writing, econ-humanizer, academic-paper-writer, research-grants, and referee-re... |
| [hypothesis-generation](skills/writing-and-review/hypothesis-generation) | Structured hypothesis formulation from observations. Use when you have experimental observations or ... |
| [latex-econ-model](skills/writing-and-review/latex-econ-model) | Write and typeset economic models in LaTeX with proper notation |
| [latex-posters](skills/writing-and-review/latex-posters) | Create professional research posters in LaTeX using beamerposter, tikzposter, or baposter. Support f... |
| [latex-tables](skills/writing-and-review/latex-tables) | Generate publication-ready regression tables in LaTeX. |
| [market-research-reports](skills/writing-and-review/market-research-reports) | Generate comprehensive market research reports (50+ pages) in the style of top consulting firms (McK... |
| [peer-review](skills/writing-and-review/peer-review) | Structured manuscript/grant review with checklist-based evaluation. Use when writing formal peer rev... |
| [scholar-evaluation](skills/writing-and-review/scholar-evaluation) | Systematically evaluate scholarly work using the ScholarEval framework, providing structured assessm... |
| [scientific-critical-thinking](skills/writing-and-review/scientific-critical-thinking) | Evaluate scientific claims and evidence quality. Use for assessing experimental design validity, ide... |
| [scientific-slides](skills/writing-and-review/scientific-slides) | Build slide decks and presentations for research talks. Use this for making PowerPoint slides, confe... |
| [scientific-writing](skills/writing-and-review/scientific-writing) | Core skill for the deep research and writing tool. Write scientific manuscripts in full paragraphs (... |
| [venue-templates](skills/writing-and-review/venue-templates) | Access comprehensive LaTeX templates, formatting requirements, and submission guidelines for major s... |

## What's included

- **64 skills** across econometrics, writing, data analysis, documents, research tools, and career documents
- Works with **Cursor**, **Claude Code**, and **Codex**
- Sanitized for public sharing — see [SECURITY.md](SECURITY.md) for env vars you may need to set

## Refreshing from a local install

```bash
python3 scripts/sync-skills.py
bash scripts/sanitize-skills.sh
bash scripts/audit-secrets.sh
```

## License

MIT — see [LICENSE](LICENSE).
