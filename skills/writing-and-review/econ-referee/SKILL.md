---
name: econ-referee
description: Pre-submission referee report for economics, finance, and accounting papers. Runs source-fidelity, numerical, claim-evidence, identification, sample, magnitude, and robustness audits, then ranks confirmed corrections above interpretive critiques. Use when stress-testing a working paper, writing a referee report, or preparing a JAR, TAR, JAE, JF, JFE, RFS, or AEA submission. For general science checklists use peer-review; for scoring rubrics use scholar-evaluation.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Econ / finance / accounting pre-submission referee

John Barrios's referee workflow for this collection. Evidence rules and specialist lenses are adapted from [Ingar30/reviewer](https://github.com/Ingar30/reviewer) (MIT). This skill stays a single referee workflow. It does not run that repository's parser, validators, or multi-agent runtime.

**After** the judgment is settled, use [`econ-write`](../econ-write/) + [`econ-humanizer`](../econ-humanizer/) to implement revisions.

## When to use

- Stress-test a working paper before journal submission
- Produce a referee-style report the author can act on
- Separate **confirmed corrections** (the paper disagrees with itself) from **qualifications** and **optional development**

Skip this skill for a summary, a rewrite, or proofreading alone.

## Evidence contract

Every major comment cites manuscript evidence. Do not invent table numbers, coefficients, sample sizes, signs, or formulas.

- If the PDF, table image, or equation is too garbled to check, mark **Cannot verify** and name the missing exhibit. Do not reconstruct it.
- One independently fixable defect per comment. Distinct denominators, samples, or corrections stay separate even when they share a sentence.
- State the problem in the first line. Example: "Table 3, column 2 reports 0.041; the text on p. 12 calls the same cell 4.1 percent."
- A missing row, undocumented covariate, or absent code file is a disclosure limit. It is not proof the authors omitted the procedure. Ask for the exhibit unless retained evidence shows the error.
- Before calling two quantities inconsistent, confirm they share estimand, aggregation, sample, denominator, and period. A ratio of averages need not equal an average of ratios. Percent and percentage-point changes can both be correct. A log-point coefficient is not automatically an arithmetic-mean effect.
- An explicitly scoped comparison need not show every arm, outcome, or subgroup. Flag an exclusion only when it misleads the stated estimand or departs from a stated plan.
- Separate the observation from the diagnosis. A verified inconsistency may have several causes. Ask the authors to reconcile it. Do not assert an unobserved coding mistake or a replacement number.
- The absence of a method, dataset, experiment, or formal model is not a defect. Skip that lens.
- Literature critiques name the study and the version checked, or they are **Cannot verify**. An older abstract does not prove a later draft lacks a design.
- Do not accuse fraud. Ask for clarification.

Detail for each lens: [`references/audit-lenses.md`](references/audit-lenses.md).

## Read the manuscript safely

When the input is a PDF, parse it with [`paper-pdf`](../paper-pdf/) before the audits:

```bash
python skills/writing-and-review/paper-pdf/scripts/parse_paper_pdf.py \
  --pdf paper.pdf --out paper-pdf-work
```

Read `parsed/full_text.md`, the table and figure crops, and `parsed/quality.json`.

1. If a page or table is marked unsafe, conflicting, or OCR-recommended, use the page image. A blank cell is blank. Do not type a number the parser did not extract.
2. Note exhibits you cannot trust. Those claims stay **Cannot verify**.
3. A heading or table missing from extracted text is not evidence the manuscript omitted it. Search the page images before reporting a broken cross-reference.

## Workflow

Finish each coverage pass before writing findings. Do not stop at the first error. Stop the whole review only when the exhibits behind the main claim cannot be read.

### 1. Classify

Empirical reduced-form, archival accounting, asset pricing, banking, macro, theory, structural, experiment, or mixed. Name the claimed identification and the target venue if the user gave one.

### 2. Contribution sentence

Write the contribution in the author's words, then in skeptical words. If they diverge, that is a comment only when a specific sentence overclaims. Positioning preferences that do not make a sentence false go to exploratory suggestions.

### 3. Always-on audits

Run these on every paper that reports results. Record findings before later passes. A later interpretive pass must not rewrite a number already checked.

1. **Source fidelity.** Ledger of central claims against the cited table, figure, column, sample, sign, and definition. Then one pass over each main display.
2. **Numbers.** Recompute material differences, percents, percentage points, ratios, log points, and adding-up identities (shares, flows, probabilities, budget items) when the paper says the parts exhaust a total.
3. **Claims and summaries.** Abstract, introduction, and conclusion versus the body, including construct labels broader than the measured object.
4. **Displayed specs.** Dependent variable, sample, treatment, reference group, fixed effects, and estimator versus the prose and table note.
5. **Cross-references** that a result depends on (Table 4, Appendix B, equation (3)).

### 4. Conditional audits

Run a lens only when the paper contains that object. See the reference file.

Identification, sample construction, robustness language, economic magnitude, power and multiple testing, randomization, institutional or regulatory facts, pre-analysis or replication claims, literature positioning, formal theory, external validity and policy language.

### 5. Rank, then write

Classify each finding into exactly one tier:

| Tier | What belongs here |
|------|-------------------|
| Confirmed correction | Arithmetic inconsistency, internal contradiction, mislabeled sample or outcome, inaccurate description of the paper's own evidence, undisclosed departure from a stated plan, or a missing definition required to read a central result |
| Material qualification | Design, measurement, inference, or external-validity limit that narrows a claim and depends partly on judgment |
| Exploratory suggestion | Alternative framing, extra literature, optional analysis, or presentation preference |

Rank by tier, then by consequence for the central result, then by how readily the author can act. A subtle identification worry does not outrank a wrong number in the main table. If reasonable readers could disagree about the preferred framing, it is not a confirmed correction.

Prefer the smallest fix. Precise language beats a demand for new data or a new design when language resolves the issue.

## Comment format

```text
[Tier: Correction|Qualification|Exploratory] [Topic: Source|Numbers|Identification|Inference|Data|Magnitude|Contribution|Clarity]
Location: §X / Table Y / Figure Z (p. N)
Claim checked: ...
Evidence: what the manuscript shows, with the compared cells
Why it matters: consequence for the central result
Minimum fix: smallest adequate correction or qualification
Optional stronger check: only if it adds material value; label it optional
```

If unverified: `Status: Cannot verify` plus what is established, what is unavailable, and the smallest disclosure that would settle it.

## Deliverables

Always produce all three.

### A. Referee report

Write for the authors. Precise, calm, constructive. No process notes about agents or tools.

1. **Summary.** One paragraph: contribution, then up to five confirmed corrections, then one sentence on qualifications.
2. **Confirmed corrections.** Three to six when the evidence supports that many; fewer when it does not. Each uses **Evidence**, **Why it matters**, **Minimum fix**. Add **Optional stronger check** only when useful.
3. **Material qualifications.**
4. **Exploratory development.** Label these as opportunities, not required corrections.
5. **Cannot verify.**

| Item | Established | Unavailable | Next step |
|------|-------------|-------------|-----------|

6. **Advisory forecast**, labeled private pre-submission advice (Accept / R&R / Reject as a forecast). It must follow the tiers. Exploratory comments alone do not support a reject forecast. Confirmed errors that change the main result do.

### B. Editing notes

Separate from substance. Copyediting, notation nits, and bibliography maintenance (year suffixes, incomplete fields) live here. A citation problem stays in the referee report only when it changes the identity of a result the paper relies on.

### C. Revision plan

Order: fixes possible from existing evidence, then qualifications and documentation, then optional analyses.

| Priority | Comment | Action | Depends on |
|----------|---------|--------|------------|
| P0 | … | … | … |

## Field flags

| Field | Recurring issues |
|-------|------------------|
| Archival accounting | Accruals and disclosure constructs broader than the measure; Compustat filters and fiscal-year alignment; auditor or office clustering; human-coded versus model-coded text; adding-up of earnings components |
| Corporate finance | Endogenous policy; bad controls; industry×year fixed effects; silent clustering switches; leverage and governance exclusion stories |
| Asset pricing | Multiple testing; tradability; microstructure; anomaly *t*-stats versus economic magnitude in return space |
| Banking | Regulatory timing; call-report breaks; call versus market data; coverage dates in the data dictionary |
| Governance / ESG | Construct validity; boilerplate text measures; selection into disclosure |

## Venue checklists

Use when the user names a target outlet. These are pre-submission stress tests.

### JAR / TAR / JAE

- [ ] The question is about accounting measurement, disclosure, assurance, or real effects of reporting rules
- [ ] Constructs are defined against the obvious alternative measures
- [ ] The identification threat is named in accounting terms (discretion, concurrent standards, auditor change, mandate timing)
- [ ] Compustat `indfmt` / `datafmt` / `popsrc` / `consol`, fiscal-year alignment, and winsorization are disclosed where the sample depends on them
- [ ] Clustering matches where the shock lives (firm, auditor or office, state)
- [ ] Magnitude is in accounting units, not only a *t*-stat
- [ ] Mechanism evidence is present or the claim is narrowed

### JF / JFE / RFS

- [ ] One sentence states the contribution against the relevant frontier
- [ ] The exclusion story is explicit
- [ ] Fixed effects and clustering match the variation and do not switch silently across tables
- [ ] Pricing papers address multiple testing, tradability, and microstructure, or scope them out
- [ ] Magnitudes are in return space with the horizon stated
- [ ] Staggered adoption is not only two-way fixed effects when timing varies

### AEA / general interest

- [ ] External validity and mechanism get weight alongside the estimate
- [ ] The identification section can stand alone for a non-specialist empirical reader
- [ ] Main tables carry the claim; robustness forests sit in the appendix

If the paper straddles fields, say which bar you are applying and why.

## Red lines

- Do not rubber-stamp a weak design
- Do not rewrite the paper into a different paper
- Do not demand citations you cannot name accurately
- Do not put parser or extraction failures on the author
- Do not let agreement with your own earlier impression replace a check against the cited cell
