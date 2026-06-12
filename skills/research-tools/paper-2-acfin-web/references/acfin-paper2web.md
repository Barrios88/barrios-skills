# Paper2Web for accounting & finance papers

## Homepage structure (recommended)

Build sections in this order — matches how JAR/JAE/TAR and JF/JFE/RFS readers scan empirical work:

1. **Title + one-line question** — Policy shock, market friction, or reporting choice
2. **Identification summary** — 3–4 sentences: setting, treatment, timing, main spec
3. **Key findings** — Bullets with economic magnitude (e.g., "15 bps increase in spreads")
4. **Main figure** — Event study, parallel trends, or primary coefficient plot
5. **Main table** — Interactive or static HTML from LaTeX table export
6. **Institutional background** — Regulation, market rule, or institutional detail (short)
7. **Data** — Sources, sample period, unit of observation, filters (Compustat/CRSP codes)
8. **Robustness** — Collapsible subsections or linked appendix page
9. **Authors + links** — SSRN, journal version, replication repo, contact

## Design notes

- Prefer **conservative academic styling** (serif headings, muted palette) over startup landing-page aesthetics
- Use **tabular figures** for balance tables and summary stats — finance readers expect them early
- Link to **replication package** prominently; note WRDS/SEC restrictions if data cannot be public
- Citation block: BibTeX + DOI when published; SSRN abstract ID when working paper

## LaTeX tips

- `\input{tables/main_results}` — ensure tables compile standalone for clean extraction
- Vector figures (PDF) for coefficient plots and event studies
- Avoid custom macros in table captions without definitions in `main.tex`

## Commands

```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-website
```

Review `index.html` and tighten identification and magnitude language before publishing.
