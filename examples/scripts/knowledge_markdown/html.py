"""Convert captured publisher HTML without scripts, navigation or network calls."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from .pdf import markdown_table

VOID = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SKIP = {
    "script",
    "style",
    "noscript",
    "nav",
    "aside",
    "footer",
    "header",
    "form",
    "button",
    "svg",
    "iframe",
}


@dataclass
class Node:
    """Retain source markup structure for conversion and table-span metadata."""

    tag: str
    attrs: dict[str, str | None] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)

    def descendants(self, tag: str) -> list[Node]:
        """Return matching descendant elements in document order."""
        result = []
        for child in self.children:
            if isinstance(child, Node):
                if child.tag == tag:
                    result.append(child)
                result.extend(child.descendants(tag))
        return result


class Tree(HTMLParser):
    """Parse markup as inert data; never execute code or fetch resources."""

    def __init__(self) -> None:
        """Initialize the document and open-element stack."""
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Append an element and enter it unless it is void."""
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        """Close the nearest matching element, tolerating unmatched end tags."""
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle explicitly self-closing markup."""
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        """Retain source text nodes."""
        self.stack[-1].children.append(data)


def plain(node: Node | str) -> str:
    """Collect text while excluding non-content subtrees."""
    if isinstance(node, str):
        return re.sub(r"\s+", " ", node)
    if node.tag in SKIP:
        return ""
    return "".join(plain(child) for child in node.children)


def safe_url(base: str, value: str | None) -> str:
    """Retain only ordinary web links in the generated document."""
    result = urljoin(base, value or "")
    return result if value and urlparse(result).scheme in {"http", "https"} else ""


def table_data(node: Node) -> tuple[list[list[str | None]], list[dict[str, Any]]]:
    """Represent merged cells explicitly without copying values into blanks."""
    cells: list[dict[str, Any]] = []
    occupied: set[tuple[int, int]] = set()
    values: dict[tuple[int, int], str] = {}
    for y, row in enumerate(node.descendants("tr")):
        x = 0
        for child in row.children:
            if not isinstance(child, Node) or child.tag not in {"td", "th"}:
                continue
            while (y, x) in occupied:
                x += 1
            rowspan = max(1, min(1000, int(child.attrs.get("rowspan") or "1")))
            colspan = max(1, min(100, int(child.attrs.get("colspan") or "1")))
            text = plain(child).strip()
            cells.append(
                {
                    "row": y,
                    "column": x,
                    "rowspan": rowspan,
                    "colspan": colspan,
                    "text": text,
                    "header": child.tag == "th",
                }
            )
            values[y, x] = text
            occupied.update(
                (r, c) for r in range(y, y + rowspan) for c in range(x, x + colspan)
            )
            x += colspan
    width = max((x + 1 for _, x in occupied), default=0)
    height = max((y + 1 for y, _ in occupied), default=0)
    return [[values.get((y, x)) for x in range(width)] for y in range(height)], cells


def convert_html(
    source: Path,
    url: str,
    content_class: str = "",
) -> tuple[str, dict[str, Any]]:
    """Select publisher article/main content and preserve HTML headings/tables."""
    tree = Tree()
    tree.feed(source.read_text(encoding="utf-8", errors="replace"))
    candidates = tree.root.descendants("div") + tree.root.descendants("main")
    selected = next(
        (
            n
            for n in candidates
            if content_class and content_class in (n.attrs.get("class") or "").split()
        ),
        None,
    )
    if selected is None:
        selected = next(iter(tree.root.descendants("article")), None)
    if selected is None:
        selected = next(iter(tree.root.descendants("main")), None)
    if selected is None:
        raise ValueError("No article/main content found; choose a reviewed selector")
    audit: dict[str, Any] = {
        "tables": [],
        "images": [],
        "headings": [],
        "selector": content_class or selected.tag,
    }

    def render(node: Node | str) -> str:
        if isinstance(node, str):
            return re.sub(r"\s+", " ", node)
        if node.tag in SKIP:
            return ""
        classes = (node.attrs.get("class") or "").split()
        if node.tag == "table" or "el-table" in classes:
            rows, cells = table_data(node)
            audit["tables"].append(
                {"cells": cells, "rows": rows, "review_status": "unreviewed"}
            )
            return (
                "\n\n"
                + markdown_table(rows)
                + "\n\n*Merged cells remain blank in Markdown; "
                "the companion JSON preserves spans and header metadata.*\n\n"
            )
        if node.tag == "img":
            target = safe_url(url, node.attrs.get("src") or node.attrs.get("data-src"))
            alt = node.attrs.get("alt") or "Source illustration"
            audit["images"].append(
                {"url": target, "alt": alt, "review_status": "caption_only"}
            )
            if not target:
                return "\n\n[Illustration unavailable in captured markup]\n\n"
            label = alt.replace("[", "").replace("]", "")
            return f"\n\n[Illustration: {label}](<{target}>)\n\n"
        raw = "".join(render(child) for child in node.children)
        value = raw.strip()
        if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if not value:
                return ""
            audit["headings"].append(plain(node).strip())
            return "\n\n" + "#" * min(6, int(node.tag[1]) + 1) + " " + value + "\n\n"
        if node.tag == "a":
            if node.descendants("img"):
                return raw
            target = safe_url(url, node.attrs.get("href"))
            return f"[{value}](<{target}>)" if value and target else value
        if node.tag in {"strong", "b"}:
            return f"**{value}**" if value else ""
        if node.tag in {"em", "i"}:
            return f"*{value}*" if value else ""
        if node.tag == "br":
            return "\n"
        if node.tag == "li":
            return "\n- " + value + "\n"
        if node.tag in {"p", "div", "section", "ul", "ol", "figure", "figcaption"}:
            return "\n\n" + value + "\n\n"
        # Preserve spaces around inline nodes; their absence can join words.
        return raw

    result = render(selected)
    result = re.sub(r"\n[ \t]+", "\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    if not result:
        raise ValueError("Selected HTML content contains no text")
    return result + "\n", audit
