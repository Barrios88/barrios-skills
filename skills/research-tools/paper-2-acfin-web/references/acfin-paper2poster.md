# Paper2Poster for accounting & finance conferences

## Common sizes

| Venue | Typical size |
|-------|----------------|
| AAA / FARS | 48" × 36" (4' × 3') |
| MFA / WFA / regional | 48" × 36" or 60" × 40" |
| Workshop posters | A0 or 36" × 24" |

Confirm requirements on the conference site before final print.

## Recommended layout (landscape 48×36)

```
┌─────────────────────────────────────────────────────────┐
│ TITLE · AUTHORS · AFFILIATIONS                          │
├──────────────┬──────────────────────────────────────────┤
│ Motivation   │  [Main figure: event study / coef plot]  │
│ (3–4 lines)  │                                          │
├──────────────┤  Data & sample (bullet box)              │
│ Identification│  Main results table (simplified)        │
│ diagram or   │                                          │
│ timing text  │  Economic magnitude callout              │
├──────────────┴──────────────────────────────────────────┤
│ Robustness (mini) · QR → project site / SSRN            │
└─────────────────────────────────────────────────────────┘
```

## Content rules

- **Readable at 4–6 feet** — minimum 28–32 pt body, 48+ pt title
- Lead with **question + setting**, not literature survey
- One **main table** only; move alt specs to small font or QR-linked appendix
- State **magnitude** on poster ("Δ = 0.12, 8% of mean") not only significance stars
- Include **data sources** line (Compustat, CRSP, hand-collected 10-K, etc.)

## Commands

```bash
python pipeline_all.py \
  --input-dir "path/to/paper" \
  --output-dir "path/to/output" \
  --model-choice 1 \
  --generate-poster \
  --poster-width-inches 48 \
  --poster-height-inches 36
```

Print test on letter paper before full-size order.
