# Usage examples — accounting & finance

## Example 1: SSRN companion site (disclosure paper)

**Input:** LaTeX WP with EDGAR-based treatment, DiD design, event-study figure.

```bash
python pipeline_all.py \
  --input-dir ~/papers/disclosure_did \
  --output-dir ~/output/disclosure_did \
  --model-choice 1 \
  --generate-website
```

**Post-edit:** Add replication GitHub link; move identification box to hero; run `econ-humanizer` on generated prose.

Deploy `output/disclosure_did/website/` to GitHub Pages; link from SSRN abstract.

---

## Example 2: AAA poster (corporate governance)

**Input:** Published JAE-style paper; poster session 48×36.

```bash
python pipeline_all.py \
  --input-dir ~/papers/governance_iv \
  --output-dir ~/output/governance_poster \
  --model-choice 1 \
  --generate-poster \
  --poster-width-inches 48 \
  --poster-height-inches 36
```

**Post-edit:** Verify first-stage / IV language fits poster space; add QR to project site.

---

## Example 3: Finance seminar video (market microstructure)

**Input:** TRACE-based liquidity paper; 15-minute department seminar.

```bash
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir ~/output/trace_seminar \
  --paper_latex_root ~/papers/trace_liquidity
```

**Post-edit:** Trim lit review slides; extend data and identification segments to ~4 minutes total.

---

## Example 4: Research agenda batch (lab site)

Multiple related papers (e.g., licensing series):

```bash
for p in licensing_150hr licensing_mobility licensing_quality; do
  python pipeline_all.py \
    --input-dir ~/papers/$p \
    --output-dir ~/output/$p \
    --model-choice 1 \
    --generate-website &
done
wait
```

Use consistent footer (lab name, replication policy) across sites.
