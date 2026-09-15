"""Archive selected catalogue sources for manual review, never runtime ingestion.

Usage: python examples/scripts/capture_knowledge_sources.py ti-spma056 ti-scaa082a
Originals and page-marked text stay in ignored out/knowledge/sources/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / "src/circuit_context/data/sources.json"
OUT = ROOT / "out/knowledge/sources"
MAX_BYTES = 32 * 1024 * 1024


class PageText(HTMLParser):
    """Extract review text without executing page scripts or following links."""

    def __init__(self) -> None:
        """Initialize the text accumulator."""
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden: list[str] = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        """Skip executable/style content and retain heading boundaries."""
        if tag in {"script", "style", "noscript"}:
            self.hidden.append(tag)
        if not self.hidden and tag in {"p", "div", "h1", "h2", "h3", "li", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        """Finish a skipped element."""
        if self.hidden and self.hidden[-1] == tag:
            self.hidden.pop()

    def handle_data(self, data: str) -> None:
        """Retain visible text for manual comparison with the original."""
        if not self.hidden:
            self.parts.append(data)


def capture(source: dict[str, Any]) -> dict[str, Any]:
    """Download one bounded response and record provenance or its failure."""
    row = {key: source[key] for key in ("id", "title", "url", "revision")}
    row["captured_at"] = datetime.now(timezone.utc).isoformat()
    row["expected_sha256"] = source["sha256"]
    try:
        request = Request(
            source["url"], headers={"User-Agent": "CircuitContext/0.1"}
        )
        with urlopen(request, timeout=25) as response:
            raw = response.read(MAX_BYTES + 1)
            row["final_url"] = response.url
            row["content_type"] = response.headers.get_content_type()
            encoding = response.headers.get_content_charset() or "utf-8"
        if len(raw) > MAX_BYTES:
            raise ValueError("response exceeds 32 MiB capture limit")
        digest = hashlib.sha256(raw).hexdigest()
        row.update(bytes=len(raw), sha256=digest)
        row["matches_catalogue"] = (
            digest == source["sha256"] if source["sha256"] else None
        )
        if raw.startswith(b"%PDF-"):
            suffix = ".pdf"
            with pymupdf.open(stream=raw, filetype="pdf") as document:
                row["pages"] = len(document)
                content = "\n\n".join(
                    f"--- PDF page {i + 1} ---\n{page.get_text()}"
                    for i, page in enumerate(document)
                )
        elif row["content_type"] == "text/html":
            if source["url"].split("?")[0].lower().endswith(".pdf"):
                raise ValueError("expected PDF but received HTML")
            suffix = ".html"
            parser = PageText()
            parser.feed(raw.decode(encoding, errors="replace"))
            content = "\n".join(
                line.strip() for line in "".join(parser.parts).splitlines()
                if line.strip()
            )
        else:
            raise ValueError(f"unsupported content type: {row['content_type']}")
        if not content.strip():
            raise ValueError("no extractable text; manual image/OCR review needed")
        # Hash-named snapshots retain earlier downloads and editions.
        stem = f"{source['id']}-{digest}"
        original = OUT / (stem + suffix)
        extracted = OUT / (stem + ".txt")
        original.write_bytes(raw)
        extracted.write_text(content, encoding="utf-8")
        row.update(original=original.name, text=extracted.name, status="captured")
    except Exception as exc:
        row.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    return row


def main() -> int:
    """Capture explicit source IDs without editing the trusted corpus."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_ids", nargs="+", help="IDs in sources.json")
    args = parser.parse_args()
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    sources = {source["id"]: source for source in catalogue["sources"]}
    unknown = set(args.source_ids) - sources.keys()
    if unknown:
        parser.error(f"unknown source IDs: {', '.join(sorted(unknown))}")
    OUT.mkdir(parents=True, exist_ok=True)
    selected = [sources[key] for key in dict.fromkeys(args.source_ids)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(capture, selected))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    manifest = OUT / f"manifest-{stamp}.json"
    manifest.write_text(json.dumps({
        "corpus_version": catalogue["version"],
        "review_status": "Captured text is untrusted; editorial review is required.",
        "sources": results,
    }, indent=2) + "\n", encoding="utf-8")
    for row in results:
        print(f"{row['id']}: {row['status']} {row.get('error', '')}")
    print(f"Manifest: {manifest}")
    return int(any(row["status"] == "failed" for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
