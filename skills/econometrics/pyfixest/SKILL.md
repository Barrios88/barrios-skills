---
name: pyfixest
description: Fast high-dimensional fixed-effects regression in Python with pyfixest (fixest-like syntax). Use for OLS/IV/Poisson with many FEs, cluster-robust SEs, modern DiD (did2s, Sun-Abraham), and publication tables — the Python counterpart to Stata reghdfe/fixest for accounting and finance panels.
curated-by: John Barrios
collection: barrios-skills
upstream: https://github.com/py-econometrics/pyfixest
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# PyFixest for empirical accounting & finance

## When to use

- Firm–year / firm–quarter panels with firm and year (or industry×year) fixed effects
- High-dimensional FE that are slow in `linearmodels` or plain `statsmodels`
- IV with FE, Poisson/PPML with FE, or modern DiD helpers in Python
- You already know Stata `reghdfe` / R `fixest` and want the same grammar in Python

**Prefer** [`python-panel-data`](../python-panel-data/) when the design is a simple two-way FE / RE with `linearmodels` and you want textbook panel diagnostics. **Prefer** [`r-econometrics`](../r-econometrics/) / Stata skills when the paper's replication package is R/Stata-first.

## Install

```bash
python -m pip install pyfixest
# optional: python -m pip install "pyfixest[plots]"
```

Docs: [pyfixest.org](https://pyfixest.org/pyfixest.html)

## Iron law: specify clustering and FE before estimating

1. State the **unit of treatment / residual correlation** (usually firm, sometimes industry or CEO)
2. State **fixed effects** that absorb the design (firm + year; firm + industry×year; etc.)
3. Estimate with matching `vcov` / cluster
4. Inspect N, absorbed FE counts, and a coefficient sample before writing results into a paper

## Quick patterns

### OLS with multi-way FE + firm clustering

```python
import pyfixest as pf

fit = pf.feols(
    "roa ~ treat + size + mb | gvkey + fyear",
    data=df,
    vcov={"CRV1": "gvkey"},
)
fit.summary()
```

### Multiple specs (fixest-style)

```python
fit = pf.feols(
    "roa ~ treat + size | gvkey + fyear",
    data=df,
    vcov={"CRV1": "gvkey"},
)
# Compare specs with pf.etable([...]) for paper tables
```

### IV with FE

```python
fit = pf.feols(
    "y ~ 1 | gvkey + fyear | endog ~ instrument",
    data=df,
    vcov={"CRV1": "gvkey"},
)
```

### Staggered DiD / event study

Prefer package DiD helpers (`did2s`, Sun-Abraham / local projections as documented upstream) over naive TWFE when adoption is staggered. Report an event-study plot from a robust estimator, not only TWFE — see [`econ-writing-plus`](../../writing-and-review/econ-writing-plus/) for narrative conventions.

## Accounting / finance defaults

| Design | Typical FE | Cluster |
|--------|------------|---------|
| Firm–year treatment | `gvkey + fyear` | firm (`gvkey`) |
| Industry shock | `gvkey + fyear` or `gvkey + industry^fyear` | firm; sometimes industry |
| CEO / executive panel | exec + year or firm + year | firm or exec (justify) |
| State policy | firm + year | firm; often state×year FE debate in text |

## Journal-ready output

- Export LaTeX via pyfixest / maketables helpers; pair with [`latex-tables`](../../writing-and-review/latex-tables/) for house style
- Report within R² / FE set / cluster level in table notes
- Never paste coefficients without SE and N

## Checklist before claiming results

- [ ] Sample filters documented (Compustat `indfmt/datafmt/popsrc/consol` if from WRDS)
- [ ] FE and cluster match the identification story
- [ ] Staggered timing → not only TWFE
- [ ] One exhibit inspected (sign, magnitude, N) against a raw crosstab
