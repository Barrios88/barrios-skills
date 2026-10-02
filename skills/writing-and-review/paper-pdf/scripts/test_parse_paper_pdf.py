#!/usr/bin/env python3
"""Build a small paper PDF and check that the parser keeps reading order and blank cells."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

import pymupdf as fitz

SCRIPT = Path(__file__).resolve().parent / "parse_paper_pdf.py"
sys.path.insert(0, str(SCRIPT.parent))
import parse_paper_pdf as parser  # noqa: E402


def draw_table(page: fitz.Page, origin: tuple[float, float], rows: list[list[str]]) -> None:
    x, y = origin
    col_w, row_h = 110, 22
    n_rows, n_cols = len(rows), len(rows[0])
    for row_index in range(n_rows + 1):
        yy = y + row_index * row_h
        page.draw_line((x, yy), (x + n_cols * col_w, yy), width=0.8)
    for col_index in range(n_cols + 1):
        xx = x + col_index * col_w
        page.draw_line((xx, y), (xx, y + n_rows * row_h), width=0.8)
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            if not value:
                continue
            page.insert_text(
                (x + col_index * col_w + 4, y + row_index * row_h + 15),
                value,
                fontsize=9,
            )


def build_pdf(path: Path) -> None:
    doc = fitz.open()
    header = "Working Paper Series"

    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 36), header, fontsize=9)
    page.insert_text((300, 770), "1", fontsize=9)
    page.insert_text((72, 80), "Abstract", fontsize=12)
    page.insert_text((72, 110), "Smith (2020) reports a gain of 4.1 percent.", fontsize=11)
    page.insert_text((72, 140), "The identifica-", fontsize=11)
    page.insert_text((72, 156), "tion uses a disclosure threshold.", fontsize=11)
    page.insert_text((72, 190), "Results are in Table 1 and Figure 1.", fontsize=11)

    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 36), header, fontsize=9)
    page.insert_text((300, 770), "2", fontsize=9)
    # Right column inserted first so reading order must come from geometry.
    page.insert_text((340, 90), "RIGHTBETA starts this column.", fontsize=11)
    page.insert_text((340, 110), "It continues with a second sentence.", fontsize=11)
    page.insert_text((72, 90), "LEFTALPHA starts this column.", fontsize=11)
    page.insert_text((72, 110), "It continues with a second sentence.", fontsize=11)
    page.insert_text((72, 200), "Table 1: Main estimates", fontsize=11)
    draw_table(
        page,
        (72, 220),
        [
            ["", "Coef.", "N"],
            ["Treat", "0.041", "1,200"],
            ["Placebo", "", "1,200"],
        ],
    )

    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 36), header, fontsize=9)
    page.insert_text((300, 770), "3", fontsize=9)
    page.draw_rect(fitz.Rect(72, 80, 300, 220), color=(0, 0, 0), width=1)
    page.insert_text((72, 250), "Figure 1: Event-study path", fontsize=11)
    page.insert_text((72, 320), "References", fontsize=12)
    page.insert_text((72, 350), "Smith, A. 2020. Disclosure thresholds.", fontsize=11)

    page = doc.new_page(width=612, height=792)
    pixmap = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 40, 40), 0)
    pixmap.clear_with(200)
    page.insert_image(fitz.Rect(72, 72, 540, 700), pixmap=pixmap)

    doc.save(path)
    doc.close()


def test_conflict_status() -> None:
    merged = parser.merge_table_hits(
        [
            {
                "source": "pymupdf",
                "bbox": [0, 0, 100, 40],
                "rows": [["0.041"], ["1"]],
            },
            {
                "source": "pdfplumber",
                "bbox": [1, 1, 99, 39],
                "rows": [["0.014"], ["1"]],
            },
        ]
    )
    assert merged[0]["status"] == "conflict"
    assert merged[0]["rows"] == []
    assert merged[0]["alternates"][0]["rows"][0][0] in {"0.041", "0.014"}


def main() -> int:
    test_conflict_status()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pdf_path = root / "Sample Paper.pdf"
        build_pdf(pdf_path)
        result = parser.parse_pdf(pdf_path, root / "out", "sample-paper", dpi=100)
        parsed = Path(result["parsed_dir"])
        text = (parsed / "full_text.md").read_text(encoding="utf-8")
        assert "Working Paper Series" not in text
        assert "Smith (2020)" in text
        assert "4.1 percent" in text
        assert "identification uses a disclosure threshold" in text
        page2 = (parsed / "pages" / "page_002.md").read_text(encoding="utf-8")
        assert page2.index("LEFTALPHA") < page2.index("RIGHTBETA")
        tables = json.loads((parsed / "tables" / "table_inventory.json").read_text())
        assert tables and tables[0]["label"] == "1"
        grid = (parsed.parent / tables[0]["csv"]).read_text(encoding="utf-8")
        assert "0.041" in grid
        assert "1,200" in grid
        # The blank placebo coefficient stays blank rather than becoming 0.
        rows = list(csv.reader(grid.splitlines()))
        placebo = next(row for row in rows if row and row[0] == "Placebo")
        assert placebo[1] == ""
        figures = json.loads((parsed / "figures" / "figure_inventory.json").read_text())
        assert any(item["label"] == "1" for item in figures)
        citations = json.loads((parsed / "in_text_citations.json").read_text())
        assert any(item["authors"].startswith("Smith") for item in citations)
        quality = json.loads((parsed / "quality.json").read_text())
        assert 4 in quality["ocr_recommended_pages"]
        assert (parsed / "page_images" / "page_001.png").is_file()
        assert result["page_count"] == 4
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
