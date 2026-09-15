# Publisher documents in Markdown

The captured source documents now have individual Markdown versions under
`out/knowledge/markdown/`. Open its `README.md` to browse them. This is a
local source library for reading and editorial work; the runtime RAG continues
to retrieve the reviewed JSON guidance in `knowledge/data/`.

## Reproduce the conversion

```powershell
python examples/scripts/capture_knowledge_sources.py ti-slva959b ti-spma056
python examples/scripts/convert_knowledge_sources.py
```

The converter operates offline on capture manifests. With no IDs, it processes
all source IDs listed in those manifests. Pass explicit source IDs to restrict
a run. Missing captures are recorded as unavailable, and any unavailable or
failed source produces a nonzero exit code. It never fabricates full documents
from web summaries or silently substitutes another edition.

Each generated source folder contains:

| File | Purpose |
| --- | --- |
| `source.md` | Source text, headings, lists, tables, page anchors and provenance |
| `review.json` | Table cells/spans, source and Markdown hashes, page coverage, image references and review flags |
| `assets/page-NNN.png` | Local PDF page visuals for diagrams, tables and extraction problems |

Folder names contain the source ID and a checksum prefix. Full SHA-256 values
are recorded inside the files. A capture or catalogue checksum mismatch stops
that source's conversion. Re-running regenerates these files: put editorial
notes in `docs/knowledge-source-notes.json`, not into generated Markdown.
Notes are tied to the exact source checksum and physical PDF page number.

## What is preserved

PDF conversion groups extracted lines into paragraphs and uses typography for
headings. Every physical page retains an anchor such as `#page-7`. Printed page
numbers remain in source text; they can differ from physical PDF indices.
Repeated source headers/footers are retained for traceability.

Detected grids are treated conservatively. A nearby numbered table caption is
required before a PDF grid becomes a Markdown table; unlabeled grids remain in
the review audit and page image. This avoids turning circuit outlines into
false data tables. Uncaptioned real tables can therefore remain unstructured.
Blank or merged cells are not filled by guessing. PDF table headers are retained
as rows under neutral column labels; HTML header/span metadata is explicit in JSON.

HTML conversion selects the captured article/main-content container, retains
headings and links, and removes scripts, navigation, forms and similar widgets.
It does not fetch anything or execute page content. Article images remain
publisher links, with supplied alternative text; those images are not an offline
archive. PDF diagrams have local image fallbacks. Neither is automatically
interpreted as engineering guidance.

## Review and limitations

Nine physical pages have explicit visual-review notes. These include ground-grid
connectivity, a via table's stated conditions, stackup figures, and a source
typo: TI SPMA056 Figure 5 prints `0.58 inches` for its core while nearby text uses
`0.058 inches`. Both remain visible and the discrepancy is called out. The I2C
bus diagram review distinguishes logical connectivity from physical placement.

The other diagrams, equations, glyphs and reading order are not comprehensively
reviewed. Dense columns, font-specific symbols and merged cells can still need
correction. This conversion is useful source material, not approved design rules.
Promoting a recommendation into the RAG still requires an original summary,
scope, exceptions, required inputs, verification and an exact citation.

The basic-interface pass produced 17 conversions: 407 PDF pages and three
webpages. USB-C adds five PDFs and two publisher release listings; these listings
are not conversions of the full USB-IF specifications. See
[USB-C guidance](usb-c-guidance.md) for source scope and
[Basic interfaces](basic-interfaces.md) for the earlier sources. Eleven failed
downloads still have no complete local Markdown version.
The manifest reports measured table/visual counts for the current converter.
Checks verified page coverage, hashes, local links, the motor-driver table cells,
rejection of known diagram grids and article-content selection. These checks do
not establish engineering correctness of the source claims.

Full publisher content and page images remain ignored local artifacts, not
redistributed in the package. The converter uses the existing PyMuPDF dependency
and Python's standard library; no framework or hosted ingestion service is added.
