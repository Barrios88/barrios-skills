# Accounting empirical research pipeline: skills vs MCP

**Status:** Content framework draft (not yet a public page)  
**Audience:** Accounting / finance empiricists using Cursor, Claude Code, or Codex with the Barrios Skills catalog  
**Inspired by:** John Barrios, *Claude Code for Accounting Research* (Foundations → Empirical Loop → EDGAR text → WRDS MCP → Writing/Safety/Verification → Seminar)  
**Catalog snapshot:** 46 skills in `catalog/skills.json`; MCP guides in `install/` and `docs/*-mcp.html`

---

## A. Framework

### 1. Framing

Skills teach **how** — Compustat filters, CIK discipline, table notes, attrition rows, what a good DiD write-up looks like. MCP servers provide **live access** — authenticated WRDS queries, EDGAR filings, macro series — without pasting credentials into chat. Neither replaces **verification**: agentic tools make pipelines cheap to produce and leave the costly part (checking joins, iron-law filters, construct validity, and every number in the manuscript) on the researcher. Files on disk are the unit of work; chat is disposable context.

### 2. Pipeline overview (archival accounting)

Nine stages map a typical Compustat / EDGAR / WRDS paper from empty folder to seminar-ready draft. Stages 3–5 are the course empirical loop (download → clean/join → measure/figure) plus Module 3–4 scale; stages 6–9 are estimation through verification debt paydown.

| # | Stage | Course anchor |
|---|--------|----------------|
| 1 | Research question & literature | Foundations; lit tools |
| 2 | Empty folder & six-part opening prompt | Module 2 prompt template |
| 3 | Live data pull (structured) | Module 2 FSDS / Module 4 WRDS |
| 4 | Clean, join, attrition panel | Module 2 loop |
| 5 | Disclosure / EDGAR text measures | Module 3 |
| 6 | Construct measures & sanity EDA | Module 2 checks |
| 7 | Estimation & identification | Econometrics skills + Stata-MCP |
| 8 | Tables, figures, paper trail | Module 2 output + Module 5 trail |
| 9 | Manuscript, slides, pre-submission verify | Module 5 + seminar |

Macro overlays (FRED / OpenEcon) and Stata execution sit beside stages 3 and 7 when needed; they are not separate paper stages.

```mermaid
flowchart LR
  Q[1 Question] --> P[2 Prompt]
  P --> D[3 Pull]
  D --> C[4 Clean/join]
  C --> T[5 Text optional]
  C --> M[6 Measures]
  T --> M
  M --> E[7 Estimate]
  E --> O[8 Tables/figs]
  O --> W[9 Write/verify]
```

---

### 3. Stage-by-stage map

Skill ids are from the live catalog only. MCP names match `install/external-mcps.md` and vendored `wrds-mcp`.

---

#### Stage 1 — Research question and literature

**What the researcher is doing.** Sharpen a question that Compustat, CRSP, EDGAR, or a public panel can actually answer; map prior designs and measurement conventions before writing code.

| | |
|--|--|
| **Primary skills** | `research-ideation`, `hypothesis-generation`, `lit-review-assistant`, `econ-lit-search`, `citation-management` |
| **Also useful** | `research-lookup`, `openalex-api`, `literature-review`, `scientific-critical-thinking` |
| **MCP** | none — skill/scripts only (optional: OpenEcon Data later for “is there a macro series for X?”) |
| **Verification gate** | Name the identifying variation and the unit of observation (firm–year, filing, event) in one sentence; if you cannot, do not open a data session yet. |
| **Reach for this when…** | You are scoping a first paper or a new chapter and need search + synthesis, not SQL. |
| **Skip when…** | The design is already fixed (referee revision with a locked sample); jump to stage 2–3. |

---

#### Stage 2 — Empty folder and six-part opening prompt

**What the researcher is doing.** Start in a clean directory. Write the Module 2 six-part prompt *before* any code: **DATA**, **JOIN**, **MEASURE**, **AGGREGATION**, **OUTPUT**, **PAPER TRAIL**. Demand named scripts, `DECISIONS.md`, `LOG.md`, and attrition rows — not chat-only results.

| | |
|--|--|
| **Primary skills** | `exploratory-data-analysis` (for “what files do we have?” after the first pull), `wrds` and/or `sec-edgar` (to front-load iron laws / CIK discipline into the prompt) |
| **MCP** | none at prompt-writing time — MCP comes online in stage 3 |
| **Verification gate** | Paste the six headings; every blank that an agent would have to guess (years, tags/filters, join key, filename) is filled by you. |
| **Reach for this when…** | Starting any new empirical project or lab-style loop. |
| **Skip when…** | Extending an existing repo that already has `DECISIONS.md` and stage scripts — refine the prompt for the *delta*, do not reinvent the folder. |

**Six-part checklist (course template, abbreviated):**

1. **DATA** — source, years, tables/files, variables  
2. **JOIN** — key(s), pre/post row counts, unmatched-key report  
3. **MEASURE** — exact definition, filters (e.g. `qtrs`, form type, Compustat iron laws)  
4. **AGGREGATION** — statistic, grouping, time unit  
5. **OUTPUT** — figure/table filenames + underlying CSV/Parquet  
6. **PAPER TRAIL** — named scripts, `DECISIONS.md`, `LOG.md`, attrition printed on every filter  

---

#### Stage 3 — Live data pull (structured fundamentals / returns / bulk XBRL)

**What the researcher is doing.** Authenticated or bulk download of analysis inputs onto disk (`~/wrds_data`, project `data/raw/`, FSDS zips). Credentials never enter the conversation.

| | |
|--|--|
| **Primary skills** | `wrds`, `sec-edgar`, `api-data-fetcher`, `datacommons-client` |
| **MCP** | **wrds-mcp** (vendored) for Compustat/CRSP/etc.; **SEC EDGAR MCP** when resolving CIKs / pulling filings or XBRL facts; **OpenEcon Data** or **FRED MCP** for macro controls |
| **Verification gate (WRDS / Compustat)** | Four inspections *and* iron laws before trusting the extract: (1) row count vs expectation written beforehand, (2) `.head()`/`.sample()`, (3) null check on analysis columns, (4) date-range `min`/`max`. SQL must include `indfmt='INDL'`, `datafmt='STD'`, `popsrc='D'`, `consol='C'`. CRSP share-type/exchange filters are **manual** — never assume a helper applied them. |
| **Reach for this when…** | You need licensed WRDS tables, live EDGAR/XBRL, or pinned macro series at scale. |
| **Skip when…** | Reproducing from a frozen Parquet already on disk — use skills/scripts only; do not re-query WRDS “for convenience.” |

**Skill vs MCP pairing:** `wrds` encodes query patterns and iron laws; **wrds-mcp** executes them. `sec-edgar` encodes CIK discipline and rate limits; **SEC EDGAR MCP** fetches. `api-data-fetcher` is the reproducible-script path; OpenEcon/FRED MCP is the interactive discovery path.

---

#### Stage 4 — Clean, join, attrition panel

**What the researcher is doing.** Turn raw extracts into an analysis-ready firm–year (or firm–quarter) panel. Print attrition at every filter. Join on the correct key (`gvkey`–`fyear`, `adsh`, CCM link table — never hand-typed tickers as primary keys).

| | |
|--|--|
| **Primary skills** | `stata-data-cleaning`, `polars`, `python-panel-data`, `exploratory-data-analysis`, `dask` (large frames) |
| **MCP** | none — skill/scripts only (Stata-MCP optional if cleaning runs in Stata interactively) |
| **Verification gate** | One join audit: n before / n after / reason for every drop; flag unmatched keys; no silent many-to-many blow-ups. |
| **Reach for this when…** | Building or revising the sample that will enter every table. |
| **Skip when…** | The panel is locked and you are only adding an outcome column — document the append in `DECISIONS.md` and re-print attrition for that step only. |

---

#### Stage 5 — Disclosure / EDGAR text measures (optional branch)

**What the researcher is doing.** CIK resolution → filing retrieval (cached HTML) → section extraction with fallback patterns → quality report → text feature or NLP score. Construct validity is the accounting contribution; automation is not the finding.

| | |
|--|--|
| **Primary skills** | `sec-edgar`, `financial-text-nlp`, `web-scrape` |
| **MCP** | **SEC EDGAR MCP** for filings / Form 4 / XBRL discovery; extraction and NLP usually stay in project scripts guided by skills |
| **Verification gate** | Read the quality report (failures + suspiciously short sections), not the headline success rate; before a main-table text measure, specify a stratified human-audit protocol (e.g. ~50 filings across high/mid/low measure, size, industry) against a written rubric. |
| **Reach for this when…** | The paper’s contribution is disclosure, sentiment, or filing-based measurement. |
| **Skip when…** | Pure Compustat/CRSP design with no text — do not pull EDGAR “because the MCP is installed.” |

**Iron habit:** CIK discipline — resolve and pin CIKs; never treat ticker strings as stable firm ids across EDGAR joins.

---

#### Stage 6 — Construct measures and sanity EDA

**What the researcher is doing.** Build ratios, treatments, instruments, and controls; winzorize/trim with documented rules; plot distributions and known-event windows *before* regression.

| | |
|--|--|
| **Primary skills** | `exploratory-data-analysis`, `seaborn`, `matplotlib`, `econ-visualization`, `statistical-analysis`, `statsmodels` |
| **MCP** | none — skill/scripts only |
| **Verification gate** | Two Module 2 checks named **before** looking at the pretty figure: (1) benchmark industries or firms with a strong prior, (2) plausibility around a known shock. Write both into the README. |
| **Reach for this when…** | Any new constructed variable enters the analysis file. |
| **Skip when…** | Replicating a locked measure from a prior commit — re-run the measure script and diff outputs instead of re-exploring. |

---

#### Stage 7 — Estimation and identification

**What the researcher is doing.** Run the main specs and pre-committed robustness: FE OLS, Poisson, IV, DiD (including modern estimators), clustering. Prefer high-dimensional FE tools that match accounting panel practice.

| | |
|--|--|
| **Primary skills** | `pyfixest`, `stata-regression`, `python-panel-data`, `r-econometrics`, `statsmodels`, `econ-writing-plus` (for identification prose conventions — use in stage 9 for writing, peek here for design checklist) |
| **MCP** | **Stata-MCP** when estimating in Stata from the agent; else none — skill/scripts only |
| **Verification gate** | One coefficient or N from the log file checked against an independent re-run or a hand calculation on a tiny subsample; confirm FE and cluster choices match `DECISIONS.md`. |
| **Reach for this when…** | The analysis file and measures are frozen enough to estimate. |
| **Skip when…** | Still discovering the sample — more stage 4–6 work; regressions on a moving panel create verification debt. |

---

#### Stage 8 — Tables, figures, and artifact paper trail

**What the researcher is doing.** Export publication tables and figures from scripts; every manuscript number comes from a generated file (`\input{}` / read CSV), never hand-typed from a terminal. Finish README so a stranger can rerun empty-folder → figure.

| | |
|--|--|
| **Primary skills** | `latex-tables`, `econ-visualization`, `matplotlib`, `beamer-presentation` (early talk), `venue-templates` |
| **MCP** | none — skill/scripts only |
| **Verification gate** | Pick one table cell; trace it to the script output file and confirm the manuscript inputs that file — no copied digits. |
| **Reach for this when…** | Specs are stable enough for a working-paper draft or slides. |
| **Skip when…** | Exploratory notebooks only — do not polish LaTeX until the gate in stage 7 passes. |

---

#### Stage 9 — Manuscript, slides, pre-submission verification

**What the researcher is doing.** Draft and revise prose (banal vs meaningful line); strip AI tells; build seminar/discussant decks; run a hostile pre-submission pass; pay down verification debt (docs vs git, credentials, no hand-typed numbers).

| | |
|--|--|
| **Primary skills** | `econ-write`, `academic-paper-writer`, `econ-humanizer`, `econ-humanizer-plus`, `econ-writing-plus`, `econ-slides`, `econ-referee`, `scholar-evaluation`, `latex-econ-model`, `paper-2-acfin-web` |
| **MCP** | none — skill/scripts only |
| **Verification gate** | Cross-check one `DECISIONS.md` claim against the git commit it cites; run credential audit (`git log` / grep for secrets should be empty); editor-not-rewriter on identification (comments only, no ghostwritten argument). |
| **Reach for this when…** | Working paper, conference talk, or submission package. |
| **Skip when…** | You only needed a data extract — stop at stage 3–4 with a README; do not open writing skills as a substitute for unfinished empirics. |

---

### 4. Decision table: Skill vs MCP vs both

| Research task | Skill | MCP | Use |
|---------------|-------|-----|-----|
| Compustat / CRSP / CCM pull | `wrds` | **wrds-mcp** | **Both** — skill for filters & patterns; MCP for auth + live SQL |
| EDGAR filings, Form 4, XBRL facts | `sec-edgar` | **SEC EDGAR MCP** | **Both** — CIK/rate-limit conventions + live fetch |
| FinBERT / call / 10-K text features | `financial-text-nlp` | none (scripts); EDGAR MCP only to obtain text | **Skill (+ MCP upstream)** |
| FRED / World Bank / IMF series | `api-data-fetcher` | **OpenEcon Data** or **FRED MCP** | **Either/both** — MCP to discover; skill for pinned reproducible scripts |
| Stata clean / `reghdfe` / `esttab` | `stata-data-cleaning`, `stata-regression` | **Stata-MCP** | **Both** if agent drives Stata; **skill only** if you run `.do` yourself |
| Panel FE in Python | `pyfixest`, `python-panel-data` | none | **Skill only** |
| Lit search / BibTeX | `econ-lit-search`, `citation-management`, … | none | **Skill only** |
| Figures / LaTeX tables | `econ-visualization`, `latex-tables` | none | **Skill only** |
| Paper / slides / referee prep | `econ-write`, `econ-slides`, `econ-referee`, … | none | **Skill only** |
| “What tool rung am I on?” | — | — | Chat for thinking; editor for edits; agent for pipelines; **agent + MCP** only when live licensed/public APIs are required |

**Rule of thumb:** If the bottleneck is *knowing the convention*, reach for a skill. If the bottleneck is *talking to a remote system with secrets or rate limits*, reach for MCP. If both, install both and keep credentials in env files the MCP reads — never in prompts.

---

### 5. Minimum viable stack (first archival paper)

Small set for a Compustat firm–year paper with optional EDGAR and a Stata or Python estimator.

**Skills (install these first)**

| Role | Skill ids |
|------|-----------|
| Data access conventions | `wrds`, `sec-edgar` (if any filing work) |
| Panel & estimate | `stata-data-cleaning` + `stata-regression` **or** `pyfixest` + `python-panel-data` |
| Output | `latex-tables`, `econ-visualization` |
| Write & check | `econ-write`, `econ-humanizer`, `econ-referee` |

**MCP**

| Priority | Server |
|----------|--------|
| Required for WRDS papers | **wrds-mcp** ([`docs/wrds-mcp.html`](../wrds-mcp.html), [`install/wrds-mcp.md`](../../install/wrds-mcp.md)) |
| Optional | **SEC EDGAR MCP**, **OpenEcon Data** / FRED, **Stata-MCP** |

**Non-negotiable habits (not packages)**

- Empty folder + six-part prompt  
- Iron-law Compustat filters + four WRDS inspections  
- Attrition rows on every sample change  
- No hand-typed manuscript numbers  
- Two named sanity checks before signing off on a figure  

Everything else in the 46-skill catalog is additive (lit, Bayesian, geospatial, posters, etc.).

---

### 6. Gaps / future skills worth noting

These are **not** in the catalog today; do not invent downloadable ids. Candidates for a later release if demand shows up:

| Gap | Why it matters for accounting empirics |
|-----|----------------------------------------|
| Explicit **CCM / linking** skill (CRSP–Compustat, IBES, BoardEx link tables) | Join mistakes dominate silent bad papers; course teaches CCM via WRDS but a dedicated SOP would help |
| **FSDS bulk** skill (Module 2 path without WRDS) | Public XBRL training loop; currently covered by course materials more than catalog |
| **Sample attrition / flowchart** generator (LaTeX/TikZ from LOG.md) | Reviewer-facing artifact every archival paper needs |
| **Iron-laws linter** (static check of SQL/do-files for Compustat filters) | Makes Module 4 filters machine-enforceable beyond prose in `wrds` |
| **Event-study / disclosure-event** calendar skill | 8-K / earnings / restatement windows as a first-class workflow |
| Deeper **Form 4 / insider** SOP layered on EDGAR MCP | Skill exists partly via `wrds` + EDGAR; a focused insider skill would reduce footguns |
| **Replication packet** skill (Code Ocean / journal checklist) | Module 5 paper trail → submission-ready zip |

Recent catalog strengths to lean on in website copy: `pyfixest`, `sec-edgar`, `financial-text-nlp`, `econ-write`, `econ-slides`, `econ-referee`.

---

### 7. Verification debt (catalog-adapted)

| | Cheap to verify | Costly to verify |
|--|-----------------|------------------|
| **Expensive to make** | Rare with agents; old-world manual coding | Traditional RA-heavy builds (safer correlation of effort and checking) |
| **Cheap to make** | Row counts, iron-law filter presence, date ranges | Keyword/NLP disclosure scores, full regression batteries, AI-drafted tables/prose |

**Danger zone for this catalog:** text measures (`financial-text-nlp` + EDGAR), dense `pyfixest`/`stata-regression` output, and fluent `econ-write` drafts — all cheap to produce, expensive to validate. Pay with stage gates above, not with more autonomy.

---

## B. Website handoff plan (for a NEW chat)

Execute this brief in a follow-up session to turn §A into a user-facing guide with figures. Do not treat this draft markdown as the final page copy — compress voice for the web, keep skill ids and gates.

### 1. Proposed page(s) and nav

| Deliverable | Path | Notes |
|-------------|------|--------|
| Primary guide | `docs/pipeline.html` | New page: “Accounting research pipeline” (or “When to use skills vs MCP”) |
| Optional deep link anchors | `#stage-1` … `#stage-9`, `#mvp`, `#decide` | Shareable stage URLs |
| Optional companion | Keep framework in `docs/drafts/` as editor source; or retire draft once HTML ships | |

**Nav placement (match existing header pattern in `docs/index.html`, `docs/skills.html`, MCP pages):**

- Add **Pipeline** (or **Guide**) link in `site-nav` on all docs pages — suggest order: Popular · All skills · **Pipeline** · MCP · Install · GitHub  
- On homepage: short band under “Skills vs MCP” linking to `pipeline.html` (“See the full empirical pipeline”)  
- Footer: Pipeline alongside WRDS / EDGAR / OpenEcon setup links  
- Cross-links from each stage to skill zips (`docs/downloads/skills/{id}.zip`) and MCP pages (`wrds-mcp.html`, `sec-edgar-mcp.html`, `openecon-data-mcp.html`)

**Data:** Prefer reading stage→skill map from a small JSON (e.g. `docs/data/pipeline.json`) so filters stay maintainable — or hardcode from this draft for v1.

### 2. Figure list (4–6 exhibits)

Course-inspired, catalog-specific. Suggested filenames under `docs/assets/figures/pipeline/` (create folder when designing):

| File | Shows | Course style reference (do not copy verbatim; redesign for this catalog) |
|------|--------|--------------------------------------------------------------------------|
| `FIG-P01_empirical_loop_stages.svg` | Nine-stage pipeline as a horizontal flow (empty folder → … → verify), each node labeled with “skill / MCP / both”; Module 2 five-artifact loop as a callout inset | `…/website/assets/figures/day2/FIG-D2-01_empirical_loop.png`; also `day1/FIG-D1-03_research_map.png` |
| `FIG-P02_skill_vs_mcp_swimlanes.svg` | Two swimlanes (Skills = conventions; MCP = live access) → shared “files on disk” + third rail “Verification gates” | `day1/FIG-D1-01_tool_ladder.png`; `day4/FIG-D4-01_wrds_mcp_architecture.png` |
| `FIG-P03_verification_debt_2x2.svg` | Module 5-style 2×2 with catalog danger-zone examples (NLP scores, regression batteries, AI prose) | `day5/FIG-D5-01_verification_debt_2x2.png` |
| `FIG-P04_stage_tool_map.svg` | Stages 1–9 × primary skill chips × MCP icons | `day6/FIG-D6-01_production_function_map.png` (layout cue); `day3/FIG-D3-01_edgar_pipeline.png` |
| `FIG-P05_six_part_prompt.svg` (optional) | Six-part opening prompt checklist (DATA…PAPER TRAIL) | Module 2 prompt block in `modules/02-empirical-loop.qmd` |
| `FIG-P06_mvp_stack.svg` (optional) | Minimum viable stack diagram | — |

Course assets live under:  
`/Users/jmb432/Yale University Dropbox/John Barrios/Claude/Claude for Academics/website/assets/figures/`  
(and `…/exhibits/`). **Inspiration only** — redesign for the public Barrios Skills site; do not ship course PNGs into `docs/` without checking licensing/attribution.

Style: match Barrios Skills site (Yale blue `#00356b`, Source Serif / Inter) — exhibit clarity over decoration; avoid purple-glow AI clichés. Mirror the decision-table pattern in the course `tools.qmd` (“I want to… → use…”) for any interactive filter UI.

### 3. UX notes

- **Progressive disclosure:** Above-the-fold = one framing paragraph + FIG-P01 + CTA to MVP stack; stages in accordion or filterable sections  
- **Stage filters:** Chips — All · Question · Data · Text · Estimate · Write — filtering the stage cards  
- **Skill chips:** Each chip links to zip download and/or `skills.html?q={id}`  
- **MCP badges:** Link to setup pages; show “credentials in `.env`, never in chat” once near stage 3  
- **Verification gate:** Visually distinct callout per stage (course “Verify this” tone)  
- **Reach / Skip:** Two-column microcopy under each stage — scannable  
- **Mobile:** Stack swimlanes; keep tables as cards  
- **No dashboard hero:** One composition — brand + “Skills teach how; MCP runs live tools; you verify” + primary figure  

### 4. Acceptance criteria (follow-up chat)

- [ ] `docs/pipeline.html` exists, matches site CSS/nav/footer patterns  
- [ ] Nav link present on home, skills, and MCP guide pages  
- [ ] All skill ids on the page exist in `catalog/skills.json` (no invented skills)  
- [ ] Each of 9 stages lists skills, MCP, verification gate, reach/skip  
- [ ] Decision table + MVP stack sections shipped  
- [ ] At least 4 figures from §B.2 rendered (SVG/PNG) and referenced with alt text  
- [ ] Outbound links to skill zips and `wrds-mcp.html` / `sec-edgar-mcp.html` / `openecon-data-mcp.html` work  
- [ ] Homepage teaser band or button to Pipeline  
- [ ] Lighthouse/basic mobile check: readable stage cards without horizontal-only tables  
- [ ] Voice stays verification-first (no “AI will do your paper” framing)

### 5. Suggested prompt to start that chat

```
Implement the Barrios Skills pipeline guide from the framework draft.

Read first:
- docs/drafts/accounting-research-pipeline-framework.md (§A content + §B handoff)
- docs/index.html, docs/skills.html, docs/css/site.css, docs/js/site.js (nav + patterns)
- docs/wrds-mcp.html (guide page template)

Build:
1. docs/pipeline.html from §A (user-friendly, not a dump of the draft)
2. Wire nav/footer on existing docs pages + homepage teaser
3. Create docs/assets/figures/pipeline/ with the figures listed in §B.2
   (at least FIG-P01–P04). Match Yale/Barrios site look; exhibit-style clarity.
4. Link skill ids to downloads/skills/{id}.zip and MCP setup pages.
5. Meet acceptance criteria in §B.4.

Constraints: Do not invent skills; keep verification-first voice; prefer
structured stage sections over long prose.
```

---

## C. Style notes for editors

- Voice: concrete, verification-first, accounting-empirical — John Barrios course register, not vendor hype  
- Skill ids always as `code` spans  
- Prefer tables the web chat can turn into figures; mermaid above is optional scaffolding only  
- Iron laws to repeat in UI copy: Compustat four filters; CIK not ticker; no hand-typed numbers; credentials never in chat  
- Course mapping is inspirational alignment, not a claim that the public site replaces the PhD course  

---

---

## D. Exploration appendix (merged from parallel mapping)

Use this when building the page so UX resolves overlaps explicitly and gaps stay honest.

### Overlaps — pick defaults in the UI (do not list every skill as equal)

| Stage | Prefer as default | Present as alternatives / deeper |
|-------|-------------------|----------------------------------|
| Literature | `econ-lit-search` (econ corpus) | `openalex-api` (breadth), `lit-review-assistant` / `literature-review` (synthesis), `research-lookup` (current web) |
| Writing | Sequence: `econ-write` → `econ-writing-plus` (ID) → `econ-humanizer` (+plus) | `academic-paper-writer` as general scaffold |
| Slides | `econ-slides` for paper→talk | `beamer-presentation` for ad-hoc decks |
| Firm–year FE | Stata: `stata-regression`; Python: `pyfixest` | `python-panel-data` / `statsmodels` for simpler panels; `r-econometrics` if R-first |
| Macro | OpenEcon MCP for discovery | FRED MCP if FRED-only; `api-data-fetcher` for pinned scripts |
| Filings vs panels | EDGAR MCP + `sec-edgar` for text/XBRL | WRDS MCP + `wrds` for Compustat/CRSP/Form 4 *panels* |

### Catalog gaps called out by inventory (beyond §A.6)

- No first-class **Audit Analytics**, **I/B/E/S**, **OptionMetrics**, **BoardEx**, **ownership** skills (WRDS/`web-scrape` only)
- Thin **event-study / CAR** as a named skill
- `research-ideation` / `hypothesis-generation` lean econ-phenomena; weak on institution-specific accounting RQ framing — website copy can add a one-liner for “disclosure mandate / auditor / restatement” hooks without inventing a skill id
- Optional folder tools (Word/Excel) stay off the core pipeline map

### Course pages worth reopening in the figure/build chat

| File | Why |
|------|-----|
| `tools.qmd` | “I want to… → use…” decision table |
| `modules/01-foundations.qmd` | Research map + agent vs human |
| `modules/02-empirical-loop.qmd` | Five-stage loop + six-part prompt |
| `modules/05-writing-verify.qmd` / `verification.qmd` | Verification debt; when *not* to trust a skill |
| `modules/06-ai-knowledge-market.qmd` | Automatability × value (optional “judgment stays human” callout) |

---

*Draft for internal use. Source of truth for skill ids: `catalog/skills.json`. MCP install truth: `install/*.md`.*
