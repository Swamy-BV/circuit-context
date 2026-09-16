"""Check compressed source capture and size limits without network access."""

from __future__ import annotations

import gzip
import hashlib
import io
import tempfile
from email.message import Message
from pathlib import Path
from unittest.mock import patch

import capture_knowledge_sources as capture


class Response(io.BytesIO):
    """Provide a bounded in-memory publisher response."""

    def __init__(self, payload: bytes, encoding: str) -> None:
        """Attach the response metadata used by the capture utility."""
        super().__init__(payload)
        self.url = "https://example.invalid/source"
        self.headers = Message()
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        self.headers["Content-Encoding"] = encoding


def main() -> None:
    """Verify decoded hashes, text and failure behavior on real gzip bytes."""
    source = {
        "id": "capture-example", "title": "Capture example",
        "url": "https://example.invalid/source", "revision": "fixture",
        "sha256": None,
    }
    html = b"<article><h1>Review</h1><p>Readable schematic guidance.</p></article>"
    compressed = gzip.compress(html)
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        with patch.object(capture, "OUT", output), patch.object(
            capture, "MAX_BYTES", 512
        ):
            for payload, encoding in ((html, ""), (compressed, "gzip"),
                                      (compressed, "")):
                with patch.object(capture, "urlopen", return_value=Response(
                    payload, encoding
                )):
                    result = capture.capture(source)
                assert result["status"] == "captured", result
                assert result["sha256"] == hashlib.sha256(html).hexdigest()
                assert (output / result["original"]).read_bytes() == html
                assert "Readable schematic guidance." in (
                    output / result["text"]
                ).read_text()
                if payload == compressed:
                    assert result["transport_sha256"] == hashlib.sha256(
                        compressed
                    ).hexdigest()
            files = {p.name: p.read_bytes() for p in output.iterdir()}
            for payload, encoding in (
                (gzip.compress(b"x" * 1024), "gzip"),
                (b"x" * 513, ""),
                (compressed[:8], "gzip"),
                (html, "br"),
            ):
                with patch.object(capture, "urlopen", return_value=Response(
                    payload, encoding
                )):
                    result = capture.capture(source)
                assert result["status"] == "failed", result
                assert {p.name: p.read_bytes() for p in output.iterdir()} == files
    print("PASS: plain/gzip text, decoded and transport hashes, bounded failures.")


if __name__ == "__main__":
    main()
