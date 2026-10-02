---
name: paper-pdf
description: Parse an academic paper PDF into page text, page images, tables, figures, citations, and cross-references without inventing missing cells. Use before econ-referee, or whenever a working paper PDF needs a source-faithful local reading. Flags scanned pages and unsafe tables instead of guessing values.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Academic paper PDF parser

Local, deterministic parser for journal and working-paper PDFs. It writes text, page images, table grids, and figure crops. It does not OCR, call a model, or fill a cell it could not read.

The artifact list follows the reading needs of a referee pass. The code is original to this collection. It is not the Ingar30/reviewer preprocessor.

## When to use

- The user hands you a paper PDF and wants tables, text, or figures you can check
- Before [`econ-referee`](../econ-referee/)
- A claim depends on a coefficient, sample size, or caption

Do not use it to summarize the paper or to repair a bad scan.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r skills/writing-and-review/paper-pdf/requirements.txt
```

Needs Python 3.11+ and PyMuPDF. pdfplumber is the second table reader. If it is missing, the parser still runs and marks those tables `single_source`.

## Run

```bash
python skills/writing-and-review/paper-pdf/scripts/parse_paper_pdf.py \
  --pdf paper.pdf \
  --out paper-pdf-work
```

Optional: `--paper-id my-paper` and `--dpi 150` (72–300). Output goes to `paper-pdf-work/<paper-id>/parsed/`. Re-running replaces that `parsed/` folder only.

Encrypted PDFs stop with a message. Export an unlocked file. Do not try to bypass a password.

## What you get

| File | Use |
|------|-----|
| `full_text.md` | Body text in reading order, running headers removed |
| `pages/page_NNN.md` | One page, with the printed page label when one was found |
| `page_images/page_NNN.png` | The page to read when text is unsafe |
| `tables/table_inventory.json` | Caption, status, and paths for each extracted grid |
| `tables/*.csv` | Cells. Empty means empty |
| `tables/*.png` | Crop of the table |
| `figures/figure_inventory.json` | Figure captions and crops |
| `numbers_in_text.json` | Number strings with surrounding words |
| `crossrefs.json` | Table, figure, section, appendix, and equation mentions |
| `in_text_citations.json` | Author-year mentions |
| `reference_list.json` | Bibliography lines after a References heading |
| `sections.json` | Heading lines |
| `quality.json` | Pages and tables that must not be trusted as text |
| `manifest.json` | File hash, tool versions, counts |

## How to read the output

- `status: ok` means PyMuPDF and pdfplumber returned the same grid.
- `single_source` means only one extractor returned cells. Check the crop before quoting a coefficient.
- `unsafe` means the grid is sparse or ragged. Leave those cells blank.
- `conflict` means the two extractors disagree. The main CSV is empty on purpose. Each engine's grid is saved beside it. Quote the crop, not either CSV.
- `ocr_recommended` pages have no text layer, or a large image and little text. Read `page_images/`.
- `glyph_warning` pages contain control or private-use characters, usually broken math fonts. Do not guess the missing symbol.
- Two-column pages are read down the left column, then the right. A line that spans the page stays in vertical order.
- A line-end hyphen joined to a lowercase continuation is one word (`identifica-` / `tion`). Other hyphens stay.
- Repeated running headers are removed from the body. They are not deleted from the page image.

## Rules for the referee

1. Quote a number from a CSV only when that table's status is `ok` or you have checked the crop.
2. Never replace a blank cell with zero or with a value from a nearby row.
3. A caption with no grid is not evidence the table was omitted from the paper. Open the page image.
4. Year-like numbers in `numbers_in_text.json` are marked `year_like`. Do not treat a citation year as an estimate.
5. Reference splits are candidates. A wrapped bibliography line can merge or split incorrectly. Check the page before claiming a citation is missing.
