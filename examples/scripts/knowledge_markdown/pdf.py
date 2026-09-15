"""Convert captured PDF pages to reviewable Markdown using existing PyMuPDF."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import pymupdf

CAPTION = re.compile(r"^(?:Figure|FIGURE|Fig\.)\s*\d")


def cell(value: str | None) -> str:
    """Escape table syntax without inventing missing or merged cell values."""
    return (value or "").replace("|", r"\|").replace("\n", "<br>").strip()


def markdown_table(rows: list[list[str | None]]) -> str:
    """Preserve the cell matrix with a neutral header when none is established."""
    width = max((len(row) for row in rows), default=0)
    if not width:
        return ""
    # Do not assume the first extracted row is a column header.
    header = [f"Column {i + 1}" for i in range(width)]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in rows:
        padded = list(row) + [None] * (width - len(row))
        lines.append("| " + " | ".join(cell(v) for v in padded) + " |")
    return "\n".join(lines)


def line_text(line: dict[str, Any]) -> str:
    """Preserve printed wording, normalizing whitespace and common ligatures."""
    value = "".join(span["text"] for span in line["spans"])
    for before, after in (("ﬁ", "fi"), ("ﬂ", "fl")):
        value = value.replace(before, after)
    return re.sub(r"\s+", " ", value).strip()


def heading(line: dict[str, Any], body_size: float) -> bool:
    """Use typography for presentation only, never for engineering inference."""
    text = line_text(line)
    if not text or len(text) > 150 or CAPTION.match(text):
        return False
    spans = [s for s in line["spans"] if s["text"].strip()]
    large = min(s["size"] for s in spans) > body_size + 0.7
    bold = all(s["flags"] & 16 for s in spans)
    numbered = bool(re.match(r"^\d+(?:\.\d+)*\.?\s+\S", text))
    return bold and (large or numbered)


def paragraphs(lines: list[dict[str, Any]], body_size: float) -> str:
    """Reflow paragraphs while retaining lists, captions and section breaks."""
    result: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            result.append(" ".join(paragraph))
            paragraph.clear()

    for line in lines:
        text = line_text(line)
        if not text:
            continue
        if heading(line, body_size):
            flush()
            result.append("### " + text)
        elif CAPTION.match(text):
            flush()
            result.append("**" + text.replace("**", "") + "**")
        elif re.search(r"\.{4,}\s*\d+$", text):
            flush()
            result.append("- " + text)
        elif re.match(r"^[•●▪]\s*", text):
            flush()
            paragraph.append("- " + re.sub(r"^[•●▪]\s*", "", text))
        else:
            paragraph.append(text)
    flush()
    return "\n\n".join(result)


def emit_table(
    i: int,
    matrices: list[Any],
    parts: list[str],
    emitted: set[int],
) -> None:
    """Insert a detected table once at its first associated text line."""
    if i not in emitted:
        parts.append(f"#### Extracted table {i + 1}\n\n" + markdown_table(matrices[i]))
        parts.append(
            "*Table structure is machine-extracted. Blank/merged cells "
            "and header relationships require source review.*"
        )
        emitted.add(i)


def convert_pdf(
    source: Path,
    assets: Path,
    notes: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Retain page anchors, extracted tables and visual fallbacks with an audit."""
    assets.mkdir(parents=True, exist_ok=True)
    sections: list[str] = []
    audit: dict[str, Any] = {
        "pages": [],
        "tables": [],
        "visual_pages": [],
        "unclassified_grids": [],
    }
    with pymupdf.open(source) as document:
        for index, page in enumerate(document):
            number = index + 1
            blocks = [b for b in page.get_text("dict")["blocks"] if b["type"] == 0]
            sizes: Counter[float] = Counter()
            for block in blocks:
                for line in block["lines"]:
                    for span in line["spans"]:
                        sizes[round(span["size"], 1)] += len(span["text"])
            body_size = sizes.most_common(1)[0][0] if sizes else 10.0
            warnings: list[str] = []
            try:
                finder = page.find_tables(strategy="lines_strict")
                labels = [
                    line
                    for block in blocks
                    for line in block["lines"]
                    if re.match(r"^(?:Table|TABLE)\s*\d", line_text(line))
                ]
                tables = []
                for candidate in finder.tables:
                    # Diagram outlines also form grids. A nearby numbered table
                    # caption is required to interpret a grid as tabular text.
                    labeled = any(
                        0 <= candidate.bbox[1] - line["bbox"][3] <= 160
                        for line in labels
                    )
                    if labeled:
                        tables.append(candidate)
                    else:
                        audit["unclassified_grids"].append(
                            {
                                "page": number,
                                "bbox": list(candidate.bbox),
                                "reason": "No nearby numbered table caption",
                            }
                        )
                matrices = [table.extract() for table in tables]
            except Exception as exc:
                tables, matrices = [], []
                warnings.append(f"Table extraction failed: {type(exc).__name__}")
            parts: list[str] = []
            emitted: set[int] = set()
            captions: list[str] = []

            for block in blocks:
                remaining = []
                for line in block["lines"]:
                    text = line_text(line)
                    if CAPTION.match(text):
                        captions.append(text)
                    bbox = pymupdf.Rect(line["bbox"])
                    owner = next(
                        (
                            i
                            for i, table in enumerate(tables)
                            if pymupdf.Rect(table.bbox).contains(bbox)
                        ),
                        None,
                    )
                    if owner is not None:
                        if remaining:
                            parts.append(paragraphs(remaining, body_size))
                            remaining = []
                        emit_table(owner, matrices, parts, emitted)
                    else:
                        remaining.append(line)
                if remaining:
                    parts.append(paragraphs(remaining, body_size))
            for i in range(len(tables)):
                emit_table(i, matrices, parts, emitted)
                audit["tables"].append(
                    {
                        "page": number,
                        "index": i + 1,
                        "cells": matrices[i],
                        "bbox": list(tables[i].bbox),
                        "review_status": "unreviewed",
                    }
                )
            raw_text = page.get_text()
            if not raw_text.strip():
                warnings.append("No text extracted; visual review/OCR required")
            if any("\ue000" <= char <= "\uf8ff" for char in raw_text):
                warnings.append("Font-specific glyphs present; verify symbols/units")
            page_notes = notes.get(str(number), [])
            has_image = any(
                pymupdf.Rect(item["bbox"]).get_area() > page.rect.get_area() * 0.04
                for item in page.get_image_info()
            )
            has_grid = any(g["page"] == number for g in audit["unclassified_grids"])
            visual = bool(
                captions or tables or has_image or warnings or page_notes or has_grid
            )
            if visual:
                filename = f"page-{number:03}.png"
                page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(assets / filename)
                parts.append(f"[Page visual]({assets.name}/{filename})")
                parts.append(
                    "> Diagrams, equations and reading order are not fully "
                    "described by extracted text. Consult the page visual for "
                    "geometry and symbols; do not infer missing connections."
                )
                audit["visual_pages"].append(number)
            if page_notes:
                parts.append("#### Reviewed visual notes\n\n" + "\n\n".join(page_notes))
            if warnings:
                parts.append(
                    "#### Conversion checks\n\n" + "\n".join("- " + w for w in warnings)
                )
            sections.append(
                f'<a id="page-{number}"></a>\n\n## PDF page {number}\n\n'
                + "\n\n".join(part for part in parts if part.strip())
            )
            audit["pages"].append(
                {
                    "page": number,
                    "extracted_characters": len(raw_text),
                    "table_count": len(tables),
                    "captions": captions,
                    "reviewed_visual_notes": bool(page_notes),
                    "warnings": warnings,
                }
            )
    audit["page_count"] = len(audit["pages"])
    return "\n\n".join(sections) + "\n", audit
