---
name: paper-2-acfin-web
description: Convert accounting and finance papers into dissemination assets — interactive project websites, seminar videos, and conference posters. Use when turning a JAR/JAE/TAR, JF/JFE/RFS, or empirical arch manuscript (LaTeX or PDF) into a Paper2Web homepage, Paper2Video talk, or Paper2Poster for AAA, FARS, MFA, WFA, or journal promotion.
curated-by: John Barrios
collection: barrios-skills
---

> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Paper2AcFin: Accounting & Finance Paper Dissemination

Adapted from the Paper2All pipeline (`paper-2-web`), focused on **empirical accounting and finance** manuscripts — identification, institutional settings, archival data, and regression evidence.

## Overview

Transform LaTeX or PDF papers into three outputs:

1. **Paper2Web** — Interactive project homepage (question, design, tables, figures, replication)
2. **Paper2Video** — Seminar-style video with slides and narration
3. **Paper2Poster** — Conference poster (AAA, FARS, MFA, WFA, regional workshops)

Uses the open-source [Paper2All](https://github.com/YuhangChen1/Paper2All) toolchain. This skill adds **accounting/finance content priorities** the generic pipeline does not enforce.

## When to use

- Promote a working paper on SSRN, personal site, or lab page
- Build a companion site for a journal submission or revision
- Prepare **AAA / FARS / MFA / WFA** poster or video materials
- Create a seminar deck + video from a finance or accounting empirical paper
- Batch homepages for a research agenda (e.g., licensing, disclosure, corporate governance series)

**Triggers:** "paper to website", "conference poster from my LaTeX", "video abstract for my finance paper", "project homepage for my JAR submission", "Paper2Web for accounting paper"

## Accounting & finance content priorities

When extracting or editing generated content, foreground what accounting and finance readers expect:

| Section | Emphasize |
|---------|-----------|
| **Research question** | Policy or market friction; why the setting matters (regulation, reporting, intermediation) |
| **Institutional setting** | Rule changes, filing regimes, market structure, sample window with dates |
| **Data** | Compustat, CRSP, TRACE, EDGAR, hand-collected disclosure — source and unit of observation |
| **Design** | DiD/event study, IV, RDD, matching, panel structure; parallel trends or first stage |
| **Results** | Economic magnitude (bps, % of assets, $ effects), not only significance |
| **Robustness** | Alternative samples, windows, definitions, placebo tests |
| **Replication** | Link to code, data availability statement, WRDS/SEC access notes |

**De-emphasize** generic "novel contribution" boilerplate; **keep** coefficient tables, key figures, and a clear identification paragraph on the homepage hero.

## Workflow

```
Need dissemination for an ac/fin paper?
│
├─ Permanent project page / SSRN companion?
│  └─→ Paper2Web (see references/acfin-paper2web.md)
│
├─ Conference poster session?
│  └─→ Paper2Poster — AAA/FARS 4×3 or 4×4 ft (references/acfin-paper2poster.md)
│
├─ Seminar or video abstract?
│  └─→ Paper2Video — 5 min (abstract) or 15–20 min (job talk slice)
│
└─ Full package?
   └─→ All three; generate website first (fastest QA)
```

## Quick start

### 1. Install Paper2All

```bash
git clone https://github.com/YuhangChen1/Paper2All.git
cd Paper2All
conda create -n paper2all python=3.11
conda activate paper2all
pip install -r requirements.txt
```

System deps: LibreOffice, Poppler. See `references/installation.md`.

### 2. Configure API keys

```bash
# .env in Paper2All root — never commit
OPENAI_API_KEY=your_key_here
```

### 3. Organize input (LaTeX preferred)

```
paper_directory/
├── main.tex
├── figures/          # event-study, balance table, main coef plot
├── tables/           # regression tables as standalone if needed
└── bibliography.bib
```

### 4. Run pipeline

**Website only:**
```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-website
```

**Poster (typical 48×36 in):**
```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-poster \
  --poster-width-inches 48 \
  --poster-height-inches 36
```

**Video (seminar):**
```bash
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir "path/to/output" \
  --paper_latex_root "path/to/paper"
```

After generation, **edit** the site copy using ac/fin priorities above — especially identification, sample, and magnitude language. Pair with `econ-humanizer` or `econ-humanizer-plus` for prose cleanup.

## Post-generation checklist (ac/fin)

- [ ] Hero states the policy/market question in one sentence
- [ ] Identification strategy visible without scrolling (or in sticky summary)
- [ ] Main table and event-study (or parallel trends) figure above the fold
- [ ] Data sources named (Compustat, CRSP, EDGAR, etc.)
- [ ] Replication / contact / SSRN link in footer
- [ ] Poster readable at 4–6 feet; magnitudes on poster, not only stars
- [ ] Video opens with setting + design in first 90 seconds

## Output layout

```
output/paper_name/
├── website/     index.html, assets/
├── poster/      poster_final.pdf, .png
└── video/       final_video.mp4, slides/
```

Deploy websites to GitHub Pages, university hosting, or Netlify. Posters: university print shop or poster service. Videos: YouTube (unlisted), seminar sites, SSRN if journal allows.

## Pair with other Barrios skills

| Task | Skill |
|------|-------|
| Prose on generated pages | `econ-humanizer`, `econ-humanizer-plus` |
| Beamer deck before video | `beamer-presentation` |
| Figures for web/poster | `econ-visualization`, `latex-tables` |
| Pull Compustat/CRSP for live tables | `wrds` skill + `wrds-mcp` |

## References

- `references/installation.md` — Paper2All setup
- `references/acfin-paper2web.md` — Homepage structure for ac/fin papers
- `references/acfin-paper2poster.md` — Poster layout and conference sizes
- `references/acfin-paper2video.md` — Seminar and video-abstract pacing
- `references/usage_examples.md` — End-to-end ac/fin workflows

Upstream: [Paper2All](https://github.com/YuhangChen1/Paper2All). Generic baseline: `skills/optional/research-tools/paper-2-web`.
