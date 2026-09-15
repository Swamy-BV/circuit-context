"""Convert local publisher captures to Markdown, tables and review metadata.

Run after capture_knowledge_sources.py. No downloads, runtime indexing or corpus
edits happen here. Generated files stay under ignored out/knowledge/markdown/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from knowledge_markdown.html import convert_html
from knowledge_markdown.pdf import convert_pdf

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "out/knowledge/sources"
OUT = ROOT / "out/knowledge/markdown"
NOTES = ROOT / "docs/knowledge-source-notes.json"
SELECTORS = {
    "altium-placement-grids": "field--name-body",
    "altium-teardrops": "field--name-body",
    "ti-sszt935": "conbody",
    "segger-um08001": "mw-parser-output",
    "jlcpcb-finishes": "jlc-article-page-container",
    "jlcpcb-capabilities": "jlc-wm-capabilities",
    "tek-emi-precompliance": "main-content",
}


def convert(
    source: dict[str, Any], capture: dict[str, Any], notes: dict[str, Any]
) -> dict[str, Any]:
    """Verify the archived bytes before generating a source-specific document."""
    identifier = source["id"]
    if not re.fullmatch(r"[a-z][a-z0-9-]+", identifier):
        raise ValueError("invalid source ID")
    original = (ARCHIVE / capture["original"]).resolve()
    if original.parent != ARCHIVE.resolve():
        raise ValueError("capture path is outside the source archive")
    digest = hashlib.sha256(original.read_bytes()).hexdigest()
    if digest != capture["sha256"] or source["sha256"] not in (None, digest):
        raise ValueError("source checksum changed; edition review is required")
    folder = OUT / f"{identifier}-{digest[:12]}"
    folder.mkdir(parents=True, exist_ok=True)
    matching_notes = notes.get(identifier, {})
    if matching_notes and matching_notes["sha256"] != digest:
        raise ValueError("visual review notes belong to different source bytes")
    if original.suffix == ".pdf":
        content, audit = convert_pdf(
            original, folder / "assets", matching_notes.get("pages", {})
        )
    elif original.suffix == ".html":
        content, audit = convert_html(
            original, source["url"], SELECTORS.get(identifier, "")
        )
    else:
        raise ValueError("unsupported capture format")
    header = {
        "source_id": identifier,
        "publisher": source["publisher"],
        "revision": source["revision"],
        "source_url": source["url"],
        "source_sha256": digest,
        "captured_at": capture["captured_at"],
        "conversion": "machine_extracted_with_explicit_review_notes",
        "trusted_guidance": False,
    }
    front = (
        "---\n"
        + "\n".join(f"{k}: {json.dumps(v)}" for k, v in header.items())
        + "\n---\n"
    )
    intro = (
        f"\n# {source['title']}\n\n"
        f"[Publisher source](<{source['url']}>) · "
        f"[Archived original](../../sources/{original.name}) · "
        "[Structured tables and conversion audit](review.json)\n\n"
        "> Source text, not approved design rules. Conversion preserves source "
        "claims, including examples and outdated statements. Verify applicability, "
        "units, tables, equations and diagrams before curating new guidance. "
        "Page images retain visual evidence; only explicitly labeled notes have "
        "been visually reviewed.\n\n"
    )
    destination = folder / "source.md"
    destination.write_text(front + intro + content, encoding="utf-8")
    audit.update(header)
    audit["markdown_sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()
    (folder / "review.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "id": identifier,
        "status": "converted",
        "markdown": destination.relative_to(OUT).as_posix(),
        "source_sha256": digest,
        "pages": audit.get("page_count", 0),
        "tables": len(audit["tables"]),
        "visual_pages": len(audit.get("visual_pages", [])),
        "external_images": len(audit.get("images", [])),
    }


def main() -> int:
    """Convert selected captures, with explicit unavailable/failed records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source_ids", nargs="*", help="default: IDs in capture manifests"
    )
    args = parser.parse_args()
    catalogue = json.loads(
        (ROOT / "src/circuit_context/data/sources.json").read_text(
            encoding="utf-8"
        )
    )
    sources = {source["id"]: source for source in catalogue["sources"]}
    captures: dict[str, Any] = {}
    attempted: set[str] = set()
    for path in sorted(ARCHIVE.glob("manifest-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8"))["sources"]:
            attempted.add(row["id"])
            if row["status"] == "captured":
                captures[row["id"]] = row
    selected = list(dict.fromkeys(args.source_ids)) or sorted(attempted)
    if not selected:
        parser.error("no capture manifests found; capture sources first")
    if set(selected) - sources.keys():
        parser.error("unknown source IDs")
    notes = json.loads(NOTES.read_text(encoding="utf-8")) if NOTES.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for identifier in selected:
        if identifier not in captures:
            row = {
                "id": identifier,
                "status": "unavailable",
                "reason": "No captured original; a web summary is not a full document",
            }
        else:
            try:
                row = convert(sources[identifier], captures[identifier], notes)
            except Exception as exc:
                row = {
                    "id": identifier,
                    "status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
        results.append(row)
        print(f"{identifier}: {row['status']}", flush=True)
    index = [
        "# Publisher sources in Markdown",
        "",
        "Machine conversion is not engineering approval. See each source's "
        "review metadata; the runtime RAG still uses curated JSON only.",
        "",
        "| Source | Markdown | PDF pages | Tables | Status |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in results:
        link = f"[Read]({row['markdown']})" if "markdown" in row else "Unavailable"
        index.append(
            f"| {row['id']} | {link} | {row.get('pages', 0)} "
            f"| {row.get('tables', 0)} | {row['status']} |"
        )
    index.extend(
        [
            "",
            "HTML illustrations remain publisher links; PDF visual "
            "fallbacks are local page images. Failed downloads have no "
            "fabricated Markdown substitute.",
        ]
    )
    (OUT / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    (OUT / "manifest.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    return int(any(row["status"] != "converted" for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
