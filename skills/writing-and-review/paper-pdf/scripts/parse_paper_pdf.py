#!/usr/bin/env python3
"""Parse an academic-paper PDF into source-faithful local artifacts.

The parser is deterministic. It does not OCR, call a model, or fill in missing
table cells. Unsafe pages and tables are flagged so a later reader can use the
page image instead of a guessed value.

Artifact layout (under --out/<paper-id>/parsed/):
  manifest.json, quality.json, full_text.md, page_index.json
  pages/, page_images/, tables/, figures/
  sections.json, in_text_citations.json, reference_list.json
  numbers_in_text.json, crossrefs.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pymupdf as fitz

try:
    import pdfplumber
except ImportError:  # optional second table reader
    pdfplumber = None


TABLE_CAPTION_RE = re.compile(
    r"^(Table)\s+([A-Z]?\d+(?:\.\d+)?[A-Za-z]?)\b[:.\s]*(.*)$",
    re.IGNORECASE,
)
FIGURE_CAPTION_RE = re.compile(
    r"^(?:Figure|Fig\.)\s+([A-Z]?\d+(?:\.\d+)?[A-Za-z]?)\b[:.\s]*(.*)$",
    re.IGNORECASE,
)
HEADING_RE = re.compile(
    r"^(?:abstract|introduction|data|results|conclusion|discussion|"
    r"references|bibliography|appendix(?:\s+[A-Z0-9.]+)?|"
    r"(?:[0-9]+|[IVXLC]+)\.?\s+[A-Z].{0,100})$",
    re.IGNORECASE,
)
CITATION_RE = re.compile(
    r"\b([A-Z][A-Za-z'’\-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'’\-]+)?"
    r"(?:\s+et al\.?)?)\s*\(((?:19|20)\d{2}[a-z]?"
    r"(?:\s*,\s*(?:19|20)\d{2}[a-z]?)*)\)"
)
PAREN_CITATION_RE = re.compile(
    r"\(([A-Z][A-Za-z'’\-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z'’\-]+)?"
    r"(?:\s+et al\.?)?),\s*((?:19|20)\d{2}[a-z]?"
    r"(?:\s*;\s*[^)]+)?)\)"
)
CROSSREF_RE = re.compile(
    r"\b(Tables?|Figures?|Figs?\.|Sections?|Appendices|Appendix|"
    r"Equations?|Eqs?\.)\s+(\(?[A-Z]?\d+(?:\.\d+)*[A-Za-z]?\)?)",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(
    r"(?<![\w.])(?:[$€£]\s*)?[-−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"(?:\s?(?:%|percent|percentage\ points|pp|bps|bp))?(?![\w.])",
    re.IGNORECASE,
)
PAGE_LABEL_RE = re.compile(
    r"^(?:\d{1,4}|i{1,3}|iv|vi{0,3}|ix|xi{0,3}|xii|xiii|xiv|xv)$",
    re.IGNORECASE,
)
REFERENCES_RE = re.compile(r"^(?:references|bibliography)$", re.IGNORECASE)


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "paper"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u00ad", "")).strip()


def norm_cell(value: Any) -> str:
    if value is None:
        return ""
    return norm_space(str(value))


def control_and_private_counts(text: str) -> dict[str, int]:
    control = 0
    private = 0
    for char in text:
        code = ord(char)
        if code < 32 and char not in "\n\t":
            control += 1
        elif 0xE000 <= code <= 0xF8FF:
            private += 1
    return {"control": control, "private_use": private}


def group_lines(words: list[tuple], y_tol: float = 2.5) -> list[dict[str, Any]]:
    if not words:
        return []
    ordered = sorted(words, key=lambda word: (round(word[1], 1), word[0]))
    lines: list[dict[str, Any]] = []
    for word in ordered:
        x0, y0, x1, y1, text = word[:5]
        text = str(text).replace("\u00ad", "")
        if not text.strip():
            continue
        placed = False
        if lines:
            current = lines[-1]
            overlap = min(current["y1"], y1) - max(current["y0"], y0)
            height = min(current["y1"] - current["y0"], y1 - y0)
            if overlap >= 0.45 * max(height, 1) or abs(y0 - current["y0"]) <= y_tol:
                current["words"].append((x0, text))
                current["x0"] = min(current["x0"], x0)
                current["x1"] = max(current["x1"], x1)
                current["y0"] = min(current["y0"], y0)
                current["y1"] = max(current["y1"], y1)
                placed = True
        if not placed:
            lines.append(
                {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "words": [(x0, text)]}
            )
    for line in lines:
        line["words"].sort(key=lambda item: item[0])
        line["text"] = norm_space(" ".join(text for _, text in line["words"]))
    return [line for line in lines if line["text"]]


def column_split(lines: list[dict[str, Any]], page_width: float) -> float | None:
    narrow = [line for line in lines if (line["x1"] - line["x0"]) < page_width * 0.62]
    if len(narrow) < 6:
        return None
    centers = sorted((line["x0"] + line["x1"]) / 2 for line in narrow)
    best: float | None = None
    best_gap = 28.0
    lo, hi = page_width * 0.32, page_width * 0.68
    for left, right in zip(centers, centers[1:]):
        gap = right - left
        mid = (left + right) / 2
        if gap > best_gap and lo <= mid <= hi:
            best_gap = gap
            best = mid
    if best is None:
        return None
    n_left = sum(center < best for center in centers)
    n_right = sum(center > best for center in centers)
    if n_left < 3 or n_right < 3:
        return None
    return best


def order_lines(
    lines: list[dict[str, Any]], page_width: float, page_height: float
) -> tuple[list[dict[str, Any]], float | None]:
    split = column_split(lines, page_width)
    if split is None:
        return sorted(lines, key=lambda line: (line["y0"], line["x0"])), None
    full: list[dict[str, Any]] = []
    side: list[dict[str, Any]] = []
    for line in lines:
        crosses = line["x0"] < split - 12 and line["x1"] > split + 12
        wide = (line["x1"] - line["x0"]) > page_width * 0.55
        if crosses or wide:
            full.append(line)
        else:
            side.append(line)
    full.sort(key=lambda line: line["y0"])
    anchors = [-1.0, *[line["y0"] for line in full], page_height + 10]
    ordered: list[dict[str, Any]] = []
    for index in range(len(anchors) - 1):
        band = [
            line
            for line in side
            if anchors[index] < line["y0"] <= anchors[index + 1]
        ]
        left = [line for line in band if (line["x0"] + line["x1"]) / 2 < split]
        right = [line for line in band if (line["x0"] + line["x1"]) / 2 >= split]
        ordered.extend(sorted(left, key=lambda line: (line["y0"], line["x0"])))
        ordered.extend(sorted(right, key=lambda line: (line["y0"], line["x0"])))
        if index < len(full):
            ordered.append(full[index])
    return ordered, split


def furniture_keys(pages: list[dict[str, Any]]) -> set[str]:
    counts: Counter[str] = Counter()
    for page in pages:
        height = page["height"]
        seen: set[str] = set()
        for line in page["lines"]:
            marginal = line["y0"] < height * 0.09 or line["y1"] > height * 0.92
            key = norm_space(line["text"]).lower()
            if marginal and key and key not in seen and not PAGE_LABEL_RE.match(key):
                seen.add(key)
                counts[key] += 1
    count = len(pages)
    if count <= 1:
        return set()
    threshold = count if count < 4 else max(3, (count + 1) // 2)
    return {key for key, seen in counts.items() if seen >= threshold and len(key) > 2}


def page_label(lines: list[dict[str, Any]], height: float) -> str | None:
    candidates: list[tuple[float, str]] = []
    for line in lines:
        text = line["text"].strip()
        marginal = line["y0"] < height * 0.1 or line["y1"] > height * 0.9
        if marginal and PAGE_LABEL_RE.match(text):
            candidates.append((line["y1"], text))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


def drop_furniture(
    lines: list[dict[str, Any]], keys: set[str], height: float
) -> list[dict[str, Any]]:
    kept = []
    for line in lines:
        key = norm_space(line["text"]).lower()
        marginal = line["y0"] < height * 0.09 or line["y1"] > height * 0.92
        if marginal and (key in keys or PAGE_LABEL_RE.match(key)):
            continue
        kept.append(line)
    return kept


def lines_to_text(lines: list[dict[str, Any]]) -> str:
    paragraphs: list[str] = []
    buffer: list[str] = []
    previous: dict[str, Any] | None = None
    for line in lines:
        if previous is not None:
            gap = line["y0"] - previous["y1"]
            typical = max(previous["y1"] - previous["y0"], 8)
            if gap > typical * 0.85:
                paragraphs.append(_join_line_buffer(buffer))
                buffer = []
        buffer.append(line["text"])
        previous = line
    if buffer:
        paragraphs.append(_join_line_buffer(buffer))
    return "\n\n".join(part for part in paragraphs if part)


def _join_line_buffer(parts: list[str]) -> str:
    text = ""
    for part in parts:
        piece = part.strip()
        if not piece:
            continue
        if not text:
            text = piece
            continue
        if text.endswith("-") and piece[:1].islower():
            text = text[:-1] + piece
        elif text.endswith("\u00ad"):
            text = text[:-1] + piece
        else:
            text = f"{text} {piece}"
    return norm_space(text)


def image_coverage(page: fitz.Page) -> float:
    area = float(page.rect.width * page.rect.height) or 1.0
    covered = 0.0
    for info in page.get_image_info():
        bbox = info.get("bbox")
        if not bbox:
            continue
        covered += max(0.0, bbox[2] - bbox[0]) * max(0.0, bbox[3] - bbox[1])
    return min(1.0, covered / area)


def bbox_overlap_ratio(left: list[float], right: list[float]) -> float:
    ix0, iy0 = max(left[0], right[0]), max(left[1], right[1])
    ix1, iy1 = min(left[2], right[2]), min(left[3], right[3])
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    if inter <= 0:
        return 0.0
    area_left = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    area_right = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    denom = min(area_left, area_right) or 1.0
    return inter / denom


def table_density(rows: list[list[Any]]) -> float:
    cells = [cell for row in rows for cell in row]
    if not cells:
        return 0.0
    filled = sum(1 for cell in cells if norm_cell(cell))
    return filled / len(cells)


def rows_agree(left: list[list[Any]], right: list[list[Any]]) -> bool:
    if len(left) != len(right):
        return False
    for left_row, right_row in zip(left, right):
        if len(left_row) != len(right_row):
            return False
        for left_cell, right_cell in zip(left_row, right_row):
            if norm_cell(left_cell) != norm_cell(right_cell):
                return False
    return True


def table_status(rows: list[list[Any]], sources: list[str], conflict: bool) -> str:
    if conflict:
        return "conflict"
    if not rows or table_density(rows) < 0.45:
        return "unsafe"
    widths = {len(row) for row in rows}
    if max(widths) - min(widths) > 1:
        return "unsafe"
    if len(sources) == 1:
        return "single_source"
    return "ok"


def extract_engine_tables(page: fitz.Page, plumber_page: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    try:
        finder = page.find_tables()
        for table in getattr(finder, "tables", []) or []:
            rows = table.extract() or []
            bbox = [float(value) for value in table.bbox]
            found.append({"source": "pymupdf", "bbox": bbox, "rows": rows})
    except Exception as exc:  # extraction failure is a quality flag, not a guess
        found.append({"source": "pymupdf", "bbox": None, "rows": [], "error": str(exc)})
    if plumber_page is not None:
        try:
            for table in plumber_page.find_tables():
                rows = table.extract() or []
                box = table.bbox
                bbox = [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
                found.append({"source": "pdfplumber", "bbox": bbox, "rows": rows})
        except Exception as exc:
            found.append(
                {"source": "pdfplumber", "bbox": None, "rows": [], "error": str(exc)}
            )
    return found


def merge_table_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usable = [hit for hit in hits if hit.get("bbox")]
    groups: list[dict[str, Any]] = []
    for hit in usable:
        placed = False
        for group in groups:
            if bbox_overlap_ratio(group["bbox"], hit["bbox"]) >= 0.5:
                group["hits"].append(hit)
                placed = True
                break
        if not placed:
            groups.append({"bbox": hit["bbox"], "hits": [hit]})
    merged = []
    for group in groups:
        hits = group["hits"]
        primary = max(hits, key=lambda hit: table_density(hit["rows"]))
        conflict = False
        if len(hits) > 1:
            conflict = not all(rows_agree(primary["rows"], hit["rows"]) for hit in hits)
        sources = sorted({hit["source"] for hit in hits})
        rows = [] if conflict else primary["rows"]
        merged.append(
            {
                "bbox": group["bbox"],
                "rows": [[norm_cell(cell) for cell in row] for row in rows],
                "sources": sources,
                "status": table_status(primary["rows"], sources, conflict),
                "alternates": [
                    {
                        "source": hit["source"],
                        "rows": [[norm_cell(cell) for cell in row] for row in hit["rows"]],
                    }
                    for hit in hits
                ]
                if conflict
                else [],
            }
        )
    return merged


def caption_for_bbox(
    lines: list[dict[str, Any]], bbox: list[float], pattern: re.Pattern[str]
) -> dict[str, Any] | None:
    best: tuple[float, dict[str, Any]] | None = None
    for line in lines:
        match = pattern.match(line["text"])
        if not match:
            continue
        horizontal = min(line["x1"], bbox[2]) - max(line["x0"], bbox[0])
        if horizontal < 0 and min(abs(line["x0"] - bbox[0]), abs(line["x1"] - bbox[2])) > 80:
            continue
        if line["y1"] <= bbox[1] + 4:
            distance = bbox[1] - line["y1"]
        elif line["y0"] >= bbox[3] - 4:
            distance = line["y0"] - bbox[3]
        else:
            distance = 0.0
        if distance > 90:
            continue
        if best is None or distance < best[0]:
            best = (distance, {"text": line["text"], "bbox": [line["x0"], line["y0"], line["x1"], line["y1"]], "match": match})
    return None if best is None else best[1]


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return "_No cells extracted. Use the page image._\n"
    width = max(len(row) for row in rows)
    padded = [row + [""] * (width - len(row)) for row in rows]

    def cell(value: str) -> str:
        return value.replace("|", "\\|")

    header = padded[0]
    lines = [
        "| " + " | ".join(cell(value) for value in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in padded[1:]:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow(row)


def save_crop(page: fitz.Page, bbox: list[float], path: Path, dpi: int) -> bool:
    rect = fitz.Rect(bbox) & page.rect
    if rect.is_empty or rect.width < 2 or rect.height < 2:
        return False
    pixmap = page.get_pixmap(dpi=dpi, clip=rect, alpha=False)
    pixmap.save(path)
    return True


def find_caption_lines(lines: list[dict[str, Any]], pattern: re.Pattern[str]) -> list[dict[str, Any]]:
    found = []
    for line in lines:
        match = pattern.match(line["text"])
        if match:
            found.append({**line, "match": match})
    return found


def figure_crop_bbox(page: fitz.Page, caption: dict[str, Any]) -> list[float]:
    cap_top = caption["y0"]
    top = max(36.0, cap_top - 280)
    candidates = []
    for drawing in page.get_drawings():
        rect = drawing.get("rect")
        if rect is None:
            continue
        if rect.y1 <= cap_top + 2 and rect.y0 >= top - 4:
            candidates.append(float(rect.y0))
    for info in page.get_image_info():
        bbox = info.get("bbox")
        if bbox and bbox[3] <= cap_top + 2 and bbox[1] >= top - 4:
            candidates.append(float(bbox[1]))
    if candidates:
        top = max(36.0, min(candidates) - 6)
    return [36.0, top, float(page.rect.width) - 36, float(caption["y1"]) + 2]


def collect_citations(text: str, page_number: int, label: str | None) -> list[dict[str, Any]]:
    found = []
    seen: set[tuple[str, str, int]] = set()
    for regex, kind in ((CITATION_RE, "narrative"), (PAREN_CITATION_RE, "parenthetical")):
        for match in regex.finditer(text):
            key = (match.group(1), match.group(2), match.start())
            if key in seen:
                continue
            seen.add(key)
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 40)
            found.append(
                {
                    "page": page_number,
                    "page_label": label,
                    "kind": kind,
                    "authors": norm_space(match.group(1)),
                    "year": norm_space(match.group(2)),
                    "quote": match.group(0),
                    "context": norm_space(text[start:end]),
                }
            )
    return found


def collect_numbers(text: str, page_number: int, label: str | None) -> list[dict[str, Any]]:
    found = []
    for match in NUMBER_RE.finditer(text):
        raw = match.group(0)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = norm_space(text[start:end])
        digits = re.sub(r"[^\d]", "", raw.split("%")[0])
        year_like = bool(re.fullmatch(r"(?:19|20)\d{2}", digits)) and bool(
            re.search(r"\b(?:19|20)\d{2}\b", context)
        )
        found.append(
            {
                "page": page_number,
                "page_label": label,
                "text": raw.strip(),
                "context": context,
                "year_like": year_like and "(" in context,
            }
        )
    return found


def collect_crossrefs(text: str, page_number: int, label: str | None) -> list[dict[str, Any]]:
    found = []
    for match in CROSSREF_RE.finditer(text):
        found.append(
            {
                "page": page_number,
                "page_label": label,
                "kind": match.group(1),
                "label": match.group(2).strip("()"),
                "quote": match.group(0),
            }
        )
    return found


def collect_sections(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections = []
    for page in pages:
        for line in page["body_lines"]:
            text = line["text"].strip()
            if len(text) > 120 or text.endswith("."):
                continue
            if HEADING_RE.match(text):
                sections.append(
                    {
                        "heading": text,
                        "page": page["number"],
                        "page_label": page["label"],
                    }
                )
    return sections


def collect_references(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    started = False
    chunks: list[dict[str, Any]] = []
    buffer: list[str] = []
    anchor: dict[str, Any] | None = None

    def flush() -> None:
        nonlocal buffer, anchor
        text = norm_space(" ".join(buffer))
        if text and anchor is not None:
            chunks.append(
                {
                    "page": anchor["number"],
                    "page_label": anchor["label"],
                    "text": text,
                }
            )
        buffer = []
        anchor = None

    for page in pages:
        for line in page["body_lines"]:
            text = line["text"].strip()
            if REFERENCES_RE.match(text):
                flush()
                started = True
                continue
            if not started:
                continue
            if HEADING_RE.match(text) and not REFERENCES_RE.match(text):
                flush()
                return chunks
            new_entry = bool(re.match(r"^[A-Z][A-Za-z'’\-]+,", text)) and buffer
            if new_entry:
                flush()
            if anchor is None:
                anchor = page
            buffer.append(text)
    flush()
    return chunks


def parse_pdf(pdf_path: Path, out_root: Path, paper_id: str, dpi: int) -> dict[str, Any]:
    paper_dir = out_root / paper_id
    parsed = paper_dir / "parsed"
    if parsed.exists():
        shutil.rmtree(parsed)
    pages_dir = parsed / "pages"
    images_dir = parsed / "page_images"
    tables_dir = parsed / "tables"
    figures_dir = parsed / "figures"
    for directory in (pages_dir, images_dir, tables_dir, figures_dir):
        directory.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_path)
    if document.needs_pass:
        document.close()
        raise SystemExit(f"PDF is encrypted. Export an unlocked copy: {pdf_path}")

    plumber_doc = pdfplumber.open(pdf_path) if pdfplumber is not None else None
    raw_pages: list[dict[str, Any]] = []
    try:
        for index, page in enumerate(document):
            words = page.get_text("words") or []
            lines = group_lines(words)
            ordered, split = order_lines(lines, float(page.rect.width), float(page.rect.height))
            raw_pages.append(
                {
                    "index": index,
                    "number": index + 1,
                    "width": float(page.rect.width),
                    "height": float(page.rect.height),
                    "rotation": int(page.rotation or 0),
                    "lines": ordered,
                    "column_split": split,
                    "char_count": sum(len(line["text"]) for line in ordered),
                    "word_count": len(words),
                    "image_coverage": image_coverage(page),
                }
            )
        furniture = furniture_keys(raw_pages)
        page_records = []
        tables: list[dict[str, Any]] = []
        figures: list[dict[str, Any]] = []
        citations: list[dict[str, Any]] = []
        numbers: list[dict[str, Any]] = []
        crossrefs: list[dict[str, Any]] = []
        full_parts: list[str] = ["# Parsed paper", ""]

        for raw in raw_pages:
            page = document[raw["index"]]
            label = page_label(raw["lines"], raw["height"])
            body = drop_furniture(raw["lines"], furniture, raw["height"])
            text = lines_to_text(body)
            glyph = control_and_private_counts(text)
            scanned = raw["word_count"] == 0
            ocr_reason = None
            if scanned:
                ocr_reason = "no_native_text"
            elif raw["image_coverage"] >= 0.18 and raw["char_count"] < 400:
                ocr_reason = "large_image_with_little_text"
            warnings = []
            if raw["rotation"] not in (0, 180):
                warnings.append("page_rotation")
            if glyph["control"] or glyph["private_use"]:
                warnings.append("unresolved_glyphs")
            if ocr_reason:
                warnings.append(ocr_reason)

            page_md = pages_dir / f"page_{raw['number']:03d}.md"
            image_path = images_dir / f"page_{raw['number']:03d}.png"
            header = f"# Page {raw['number']}"
            if label:
                header += f" (label: {label})"
            if warnings:
                header += "\n\n> Extraction warning: " + ", ".join(warnings) + ". Read the page image before using numbers from this page."
            page_md.write_text(header + "\n\n" + text + "\n", encoding="utf-8")
            page.get_pixmap(dpi=dpi, alpha=False).save(image_path)

            record = {
                "number": raw["number"],
                "label": label,
                "body_lines": body,
                "text": text,
                "warnings": warnings,
                "ocr_reason": ocr_reason,
                "likely_scanned": scanned,
                "two_column": raw["column_split"] is not None,
                "rotation": raw["rotation"],
                "char_count": len(text),
                "image_coverage": round(raw["image_coverage"], 3),
                "glyph": glyph,
                "page_text": rel(page_md, paper_dir),
                "page_image": rel(image_path, paper_dir),
            }
            page_records.append(record)
            full_parts.append(header)
            full_parts.append("")
            full_parts.append(text)
            full_parts.append("")
            citations.extend(collect_citations(text, raw["number"], label))
            numbers.extend(collect_numbers(text, raw["number"], label))
            crossrefs.extend(collect_crossrefs(text, raw["number"], label))

            plumber_page = plumber_doc.pages[raw["index"]] if plumber_doc is not None else None
            merged_tables = merge_table_hits(extract_engine_tables(page, plumber_page))
            used_captions: set[str] = set()
            for table_index, table in enumerate(merged_tables, start=1):
                caption = caption_for_bbox(body, table["bbox"], TABLE_CAPTION_RE)
                label_text = None
                title = None
                if caption is not None:
                    label_text = caption["match"].group(2)
                    title = caption["match"].group(3).strip() or None
                    used_captions.add(caption["text"])
                stem = f"table_{raw['number']:03d}_{table_index:02d}"
                csv_path = tables_dir / f"{stem}.csv"
                md_path = tables_dir / f"{stem}.md"
                crop_path = tables_dir / f"{stem}.png"
                write_csv(csv_path, table["rows"])
                note = ""
                if table["status"] == "conflict":
                    note = (
                        "\n\nThe two extractors disagree. Neither grid is authoritative. "
                        "Read the crop.\n"
                    )
                    for alternate in table["alternates"]:
                        alt_path = tables_dir / f"{stem}.{alternate['source']}.csv"
                        write_csv(alt_path, alternate["rows"])
                elif table["status"] == "unsafe":
                    note = "\n\nCell extraction is incomplete. Empty cells were left blank. Read the crop.\n"
                md_path.write_text(
                    f"# Table extract {label_text or stem}\n\n"
                    f"Status: `{table['status']}`\n\n"
                    + markdown_table(table["rows"])
                    + note,
                    encoding="utf-8",
                )
                crop_box = table["bbox"]
                if caption is not None:
                    crop_box = [
                        min(crop_box[0], caption["bbox"][0]) - 4,
                        min(crop_box[1], caption["bbox"][1]) - 4,
                        max(crop_box[2], caption["bbox"][2]) + 4,
                        max(crop_box[3], caption["bbox"][3]) + 4,
                    ]
                save_crop(page, crop_box, crop_path, dpi)
                tables.append(
                    {
                        "page": raw["number"],
                        "page_label": label,
                        "label": label_text,
                        "title": title,
                        "status": table["status"],
                        "sources": table["sources"],
                        "n_rows": len(table["rows"]),
                        "csv": rel(csv_path, paper_dir),
                        "markdown": rel(md_path, paper_dir),
                        "crop": rel(crop_path, paper_dir),
                    }
                )

            for caption_line in find_caption_lines(body, FIGURE_CAPTION_RE):
                fig_label = caption_line["match"].group(1)
                stem = f"figure_p{raw['number']:03d}_{fig_label.replace('.', '_')}"
                crop_path = figures_dir / f"{stem}.png"
                crop_box = figure_crop_bbox(page, caption_line)
                saved = save_crop(page, crop_box, crop_path, dpi)
                figures.append(
                    {
                        "page": raw["number"],
                        "page_label": label,
                        "label": fig_label,
                        "caption": caption_line["text"],
                        "status": "ok" if saved else "caption_only",
                        "crop": rel(crop_path, paper_dir) if saved else None,
                    }
                )
    finally:
        document.close()
        if plumber_doc is not None:
            plumber_doc.close()

    sections = collect_sections(page_records)
    references = collect_references(page_records)
    (parsed / "full_text.md").write_text("\n".join(full_parts).rstrip() + "\n", encoding="utf-8")

    def public_page(record: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in record.items() if key not in {"body_lines", "text"}}

    write_json(parsed / "page_index.json", [public_page(record) for record in page_records])
    write_json(parsed / "sections.json", sections)
    write_json(parsed / "in_text_citations.json", citations)
    write_json(parsed / "reference_list.json", references)
    write_json(parsed / "numbers_in_text.json", numbers)
    write_json(parsed / "crossrefs.json", crossrefs)
    write_json(tables_dir / "table_inventory.json", tables)
    write_json(figures_dir / "figure_inventory.json", figures)

    quality = {
        "likely_scanned_pages": [r["number"] for r in page_records if r["likely_scanned"]],
        "ocr_recommended_pages": [r["number"] for r in page_records if r["ocr_reason"]],
        "glyph_warning_pages": [
            r["number"] for r in page_records if "unresolved_glyphs" in r["warnings"]
        ],
        "rotated_pages": [r["number"] for r in page_records if "page_rotation" in r["warnings"]],
        "unsafe_tables": [
            {"page": item["page"], "label": item["label"], "crop": item["crop"]}
            for item in tables
            if item["status"] in {"unsafe", "conflict"}
        ],
        "conflicting_tables": [
            {"page": item["page"], "label": item["label"], "crop": item["crop"]}
            for item in tables
            if item["status"] == "conflict"
        ],
        "ocr_used": False,
        "rule": "Empty or disagreed cells are blank. Do not invent a value from a crop.",
    }
    write_json(parsed / "quality.json", quality)
    manifest = {
        "paper_id": paper_id,
        "source_pdf": str(pdf_path),
        "source_pdf_sha256": sha256(pdf_path),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "tool_versions": {
            "python": sys.version.split()[0],
            "pymupdf": getattr(fitz, "VersionBind", None),
            "pdfplumber": getattr(pdfplumber, "__version__", None),
        },
        "settings": {"dpi": dpi, "ocr_used": False},
        "summary": {
            "page_count": len(page_records),
            "section_count": len(sections),
            "citation_count": len(citations),
            "reference_count": len(references),
            "number_count": len(numbers),
            "crossref_count": len(crossrefs),
            "table_count": len(tables),
            "figure_count": len(figures),
            **{key: quality[key] for key in (
                "likely_scanned_pages",
                "ocr_recommended_pages",
                "unsafe_tables",
                "conflicting_tables",
            )},
        },
    }
    write_json(parsed / "manifest.json", manifest)
    return {
        "status": "ok",
        "paper_id": paper_id,
        "parsed_dir": str(parsed),
        "page_count": len(page_records),
        "table_count": len(tables),
        "figure_count": len(figures),
        "ocr_recommended_pages": quality["ocr_recommended_pages"],
        "unsafe_tables": quality["unsafe_tables"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse an academic paper PDF into local artifacts.")
    parser.add_argument("--pdf", required=True, help="Path to the paper PDF")
    parser.add_argument("--out", default="paper-pdf-work", help="Output directory")
    parser.add_argument("--paper-id", default=None, help="Folder name; default is the file stem")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution for page and crop images")
    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.is_file():
        raise SystemExit(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise SystemExit(f"Expected a .pdf file, got: {pdf_path.name}")
    if args.dpi < 72 or args.dpi > 300:
        raise SystemExit("--dpi must be between 72 and 300")

    paper_id = slugify(args.paper_id or pdf_path.stem)
    out_root = Path(args.out).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    result = parse_pdf(pdf_path, out_root, paper_id, args.dpi)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
