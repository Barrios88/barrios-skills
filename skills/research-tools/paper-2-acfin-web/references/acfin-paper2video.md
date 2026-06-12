# Paper2Video for accounting & finance seminars

## Formats

| Use | Target length | Structure |
|-----|---------------|-----------|
| Journal video abstract | 3–5 min | Question → design → one result → implication |
| Brown bag / workshop | 12–15 min | Motivation, setting, data, design, main results, robustness |
| Conference talk (short) | 18–20 min | Full empirical arc; skip secondary extensions |

## Narration pacing (empirical ac/fin)

**First 90 seconds (critical):**
1. What market or reporting friction motivates the paper?
2. What is the institutional setting and treatment timing?
3. What is the identification strategy in plain language?

**Middle:** Walk through one main figure (event study or coefficient plot) and one table row with **economic interpretation**.

**Close:** Policy or practitioner takeaway; mention replication availability.

## Slides

- Prefer **Beamer-exported PDF** or pipeline-generated slides with minimal animation
- One message per slide; regression tables max 4–5 columns on screen
- Always verbalize **magnitude** when showing coefficients

## Commands

```bash
python pipeline_light.py \
  --model_name_t gpt-4.1 \
  --model_name_v gpt-4.1 \
  --result_dir "path/to/output" \
  --paper_latex_root "path/to/paper"
```

Talking-head mode requires GPU (see `installation.md`). For most seminar use, slides + voiceover is sufficient.

Pair with `beamer-presentation` if you need a custom deck before running Paper2Video.
