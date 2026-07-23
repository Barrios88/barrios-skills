---
name: econ-referee
description: Pre-submission referee report for economics, finance, and accounting papers — verified comments tied to page/table evidence, separate editing notes, and a prioritized revision plan. Barrios-original workflow for JAR/TAR/JAE/JF/JFE/RFS/AEA-style empirics. For general science checklists use peer-review; for scoring rubrics use scholar-evaluation.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Econ / finance / accounting pre-submission referee

John Barrios's compact referee workflow. Inspired by the *idea* of verified, revision-ready AI refereeing in the OpenEcon ecosystem, but written for this collection (MIT) with an accounting and finance lens — **not** a fork of the PolyForm-Noncommercial `econ-paper-review-skill`.

## When to use

- Stress-test a working paper before journal submission
- Produce a referee-style report the author can act on
- Separate **substance** (identification, inference, contribution) from **editing** (clarity, typos)

**After** the judgment is settled, use [`econ-write`](../econ-write/) + [`econ-humanizer`](../econ-humanizer/) to implement revisions.

## Iron law: every major comment cites evidence

Do not invent table numbers, coefficients, or sample sizes. If the PDF/manuscript does not support the claim, mark **Unverified** and ask for the exhibit.

Format substance comments as:

```text
[Severity: Critical|Major|Minor] [Topic: Identification|Inference|Data|Contribution|Clarity]
Location: §X / Table Y / Figure Z (p. N if known)
Issue: ...
Why it matters for this literature: ...
Concrete fix: ...
```

## Workflow

### 1. Classify the paper

- Empirical reduced-form / archival accounting / asset pricing / banking / macro / theory / structural / mixed
- Claimed identification (DiD, IV, RDD, bunching, event study, disclosure mandate, etc.)
- Target venue band if the user names one (e.g. JAR vs JAE vs JF)

### 2. Read for the contribution sentence

Write the paper's one-sentence contribution *in the author's terms*, then in your own skeptical terms. If these diverge, that is Comment #1.

### 3. Audit in this order (stop early only if fatal)

1. **Research integrity** — results match text; no silent sample changes across tables
2. **Design / identification** — parallel trends, exclusion, bandwidth, disclosure timing, etc.
3. **Inference** — clustering, multiple testing, weak IV, staggered DiD estimator choice
4. **Data construction** — Compustat filters, winsorization, look-ahead, delisting, CIK merges
5. **Economic magnitude** — is the effect sized in interpretable units?
6. **Literature / novelty** — relative to the frontier the paper cites
7. **Presentation** — only after substance

### 4. Accounting- and finance-specific flags

| Field | Recurring issues |
|-------|------------------|
| Archival accounting | Measurement of accruals/quality; within-GAAP discretion vs real effects; disclosure vs recognition; auditor/office clustering |
| Corporate finance | Endogenous policy; bad controls (collider); industry×year FE debates; CEO vs firm clustering |
| Asset pricing | Multiple testing; tradability; microstructure; anomaly t-stats vs Sharpe |
| Banking / intermediation | Regulatory timing; call-report breaks; call vs market data mismatch |
| Governance / ESG | Construct validity; boilerplate NLP; selection into disclosure |

### 5. Deliverables (always produce all three)

**A. Referee report** (1–2 pages)

- Summary paragraph (contribution + verdict tone)
- Main comments (numbered, verified)
- Minor comments
- Overall recommendation language suitable for *private* pre-submission use (Accept/R&R/Reject *as a forecast*, clearly labeled as advisory)

**B. Editing notes** (separate)

- Clarity, structure, notation — not mixed into substance comments

**C. Revision plan**

| Priority | Comment # | Action | Depends on |
|----------|-----------|--------|------------|
| P0 | … | … | … |

## Red lines

- Do not accuse fraud without documentary support; ask for clarification instead
- Do not demand citations to papers you cannot name accurately
- Do not rewrite the paper's contribution into a different paper
- Do not rubber-stamp: if identification is weak, say so plainly

## Optional journal-fit paragraph

Only if the user asks. Map claims to venue norms (identification bar, magnitude, mechanism evidence) without pretending to know editorial boards' private thresholds.

## Venue checklists (accounting & finance)

Use when the user names a target outlet. These are *pre-submission stress tests*, not editorial promises.

### JAR / TAR / JAE (archival accounting)

- [ ] Research question is about **accounting** (measurement, disclosure, assurance, real effects of GAAP/IFRS) — not a generic corporate-finance paper with an accounting covariate
- [ ] Construct validity: accruals / AQ / conservatism / disclosure indices defined and defended against alternatives
- [ ] Identification threat named in accounting terms (discretion, concurrent standards changes, auditor change, XBRL mandate timing, etc.)
- [ ] Sample filters: Compustat `indfmt/datafmt/popsrc/consol`; fiscal-year alignment; winsorization / truncation disclosed
- [ ] Clustering: firm at minimum; auditor/office or state when the shock lives there
- [ ] Mechanism / channel evidence expected at top journals (not only reduced-form ATE)
- [ ] Economic magnitude in accounting units (pp of ROA, days of accruals, basis points of spread) — not only t-stats
- [ ] Parallel-trends / pre-trends or placebo around disclosure/effective dates when DiD-like

### JF / JFE / RFS (finance)

- [ ] Contribution vs asset-pricing / corporate-finance / banking frontier is explicit in one sentence
- [ ] Endogeneity: policy, leverage, and governance designs state the exclusion story without hand-waving
- [ ] Fixed effects match the variation (firm + year; industry×year when industry shocks are the threat)
- [ ] Clustering justified (firm vs CEO vs deal); no silent switch across tables
- [ ] For pricing papers: multiple testing, tradability, and microstructure addressed or scoped out
- [ ] Magnitudes in return space (bps, abnormal returns, Sharpe-relevant units) with horizon clear
- [ ] Staggered shocks: not only TWFE when adoption timing varies

### AEA / general interest econ

- [ ] External validity and mechanism get more weight than accounting-construct debates
- [ ] Identification section could stand alone for a non-specialist empirical reader
- [ ] Tables emphasize main claim; appendices hold robustness forests

If the paper straddles accounting and finance, say which literature's bar you are applying and why.