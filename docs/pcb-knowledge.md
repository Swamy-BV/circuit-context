# Shared engineering knowledge

Circuit Context includes offline guidance for PCB, schematic, EMC and mechanical review.
`search_guidelines` returns concise summaries with applicability, limitations
and citations. `get_guideline` adds required inputs, suggested verification
and `related_ids` for explicit follow-up reads of supporting guidance.
The calling AI uses that evidence when reasoning; no model runs inside this
module and no CAD constraints are applied automatically.

## Use

```json
{"query": "return path", "limit": 3}
```

Pass this to `search_guidelines`, then pass a returned ID to
`get_guideline`, for example `{"id": "reference-plane-continuity"}`.
Read `circuit-context://catalogue` for filter values, IDs and source editions.
Clients that cannot read resources can still use both tools.
The standalone server uses CAD-independent tool and resource names.

For a two-layer design, start with
`get_guideline({"id": "two-layer-emc-workflow"})`. It links stackup,
placement, return paths, power, interfaces, connectors and testing in a review
sequence. Read relevant links as needed and reuse their evidence; the server
does not fetch linked guides automatically. The human-readable version is
[Two-layer stackup and EMC design review](two-layer-emc.md).

For GPIO, UART, SPI and I2C, start with the family overview. See
[Basic interface guidance](basic-interfaces.md) for patterns, text diagrams,
device scope and the explicit retrieval sequence. Search and catalogue entries
include `kind`; full reads return pattern details only for routing-pattern records.
For USB-C, start with `usb-c-overview`; see [USB-C hardware guidance](usb-c-guidance.md).
For impedance selection, read `impedance-requirement-selection` before choosing a target.

Use optional filters to narrow the evidence:

```json
{"query": "termination", "level": "interface", "interface": "can", "domain": "schematic"}
```

```json
{"query": "shield aperture", "level": "mechanical", "topic": "emc"}
```

`level` distinguishes general principles, interface guidance and mechanical
integration. `domain` identifies where a guide applies: schematic, PCB or
mechanical. `interface` selects an explicitly tagged family. Filters intersect;
an interface filter excludes untagged general guidance. Search general return
paths separately if needed. Empty filters impose no restriction; values are
lowercase and exact, such as `can`, `rs485`, `i2c`, `usb`, `ethernet`, `wireless`.

Search is SQLite FTS5/BM25 with English stemming. It treats operators and
punctuation as ordinary query text and removes common question stopwords.
Use short engineering terms. The default `match="all"` requires every remaining
term; `match="any"` explicitly broadens retrieval. There is no automatic semantic
expansion or fallback. A missing result can mean unmatched wording or missing
coverage; it is not a design answer. `limit` is 1-5, default 3; unknown filter
values are rejected. CAN remains a searchable interface term even though it is
also an English word.

Retrieve relevant guidance when planning or reviewing a design topic, and reuse
it until assumptions change. Read exact device requirements and current
fabrication data before selecting constraints. Use live MCP observations for
board state. A citation or a search hit does not prove that a board follows it.

## Sources and coverage

The catalogue contains 98 entries from 49 source documents or pages:

| Collection | Entries | Coverage |
| --- | ---: | --- |
| General PCB | 11 | Stackup, returns, grounding, decoupling, impedance selection, routing and placement |
| Two-layer design and EMC | 23 | Stackup, returns, power, interfaces, testing, motor sensing, touch exceptions, thermal offsets and reference-design reuse |
| General EMC | 12 | Coupling, emissions/immunity, reset recovery, edges, cables, filters, buck loops and ESD routing |
| Interfaces | 12 | USB channels; CAN and RS-485 termination; I2C pull-ups/buffers; Ethernet PHY/MAC and magnetics boundaries |
| Basic interface families | 17 | GPIO, UART, SPI and I2C overviews, routing patterns and scoped STM32 configuration |
| USB-C and PD | 14 | Power/data roles, CC, orientation routing, contracts, cables, protection, mechanics and verification |
| Mechanical | 9 | MLCC flex, screws and depanelization; connector tolerance/access; flex contact mapping; shielding and module clearance |

The general PCB and EMC collections use `level="general"`; the two-layer
collection also includes scoped motor-driver, capacitive-touch and analog guidance.
Schematic-relevant
entries cover electrical decisions such as pull-ups, termination, supply
filtering and reset behavior; this is not a schematic drawing-style library.

Sources include TI's layout, CAN, RS-485, ESD and converter notes; NXP's EMC
guide and I2C specification; ADI's grounding and ferrite tutorials; ST's MCU EMC
and GPIO guides; Microchip/SMSC's protection and Ethernet notes; and Murata,
Samtec, Laird, Espressif, JLCPCB, KiCad and Tektronix guidance. Editions and section locators
are listed in the catalogue and returned with each hit. Older application notes are
engineering references, not evidence of current interface certification limits.

These are Circuit Context editorial summaries, not reproduced manuals or vendor
endorsements. Required inputs and verification steps are editorial prompts, not
claims that an automated checker exists for each item. The corpus has not had
independent hardware-engineer review. Antenna synthesis, safety insulation
coordination, quantitative thermal/current sizing, full converter design, detailed
interface compliance and product qualification limits remain outside coverage.
Mechanical entries do not establish enclosure strength, vibration or thermal performance.
USB-C guidance covers negotiation planning, not a PD implementation or full
normative specification ingestion; classical CAN guidance
does not establish CAN FD timing. Search rank is relevance, not confidence.

For ordinary two-layer MCU and sensor boards, search `two layer EMC stackup`;
retrieve `routing priority`, `power trace width` or `bottom layer jump` when
reviewing those decisions. The collection excludes RF
design, but fast digital edges and interface constraints still apply.
Provisional fabrication dimensions are examples; no dimensions, layer roles,
pin swaps or routing order are applied automatically. Power sizing guidance
identifies required inputs and external checks, not a bundled ampacity solver.

Each citation carries an edition, access date, locator and source URL. File
checksums identify downloaded source bytes; a null checksum explicitly means
the source was read through web extraction but its file was not captured.
Original PDFs are not shipped. The local capture archive and editorial decisions
are described in [Two-layer source review](two-layer-source-review.md).
Captured documents also have [individual Markdown conversions](source-markdown.md)
for editorial review, separate from the curated runtime guidance.
Source availability and freshness are not checked
at runtime. HTML checksums describe the captured response, including dynamic
page content; they are not stable document revision identifiers.

## Storage and maintenance

`src/circuit_context/data/` contains `sources.json` and twelve collections:
`general.json`, `two_layer.json`, `emc.json`, `interfaces.json` and
`mechanical.json`, plus `gpio.json`, `uart.json`, `spi.json`, `i2c.json`,
`usb_c.json`, `usb_c_layout.json` and `usb_pd.json`.
The loader fingerprints all thirteen files and validates source
references, unique IDs, related-guide links and classification before indexing. Interface-level
records require a family. A content-addressed SQLite cache is created lazily under
`~/.circuit-context/cache/`; override that directory with
`CIRCUIT_CONTEXT_DIR`. It contains only bundled guidance, never project
files or user queries. There are no network requests, API keys, vector database
services or generation-model calls at runtime. The separate authoring capture script
downloads only explicitly selected catalogue sources. Cache writes publish a complete index atomically.
Deleting an old cache database is safe; it will be rebuilt if needed. New corpus
content creates a new cache file, leaving older versions available until removed.

To extend the library, edit the corpus in a branch: verify primary sources,
record the edition and locator, write a brief original summary, and attach scope,
exceptions, required inputs and verification. Do not turn example dimensions
into unconditional rules or add unverified model output as engineering evidence.
Bump the corpus version and add retrieval cases. Restart the server after
updating the installed package; corpus contents are cached within the process.

Project requirements and evidence stay in the existing project-local documents.
They are not mixed into this shared index. Retrieved documents are reference
data and cannot override the user's instructions or authorize tool operations.

## Verification

Run `python examples/scripts/pcb_knowledge.py`. It exercises the original,
EMC, two-layer, basic-interface and USB-C prompt cases through `Client(mcp)` in both protocol modes,
including exact filter intersections, citations, missing coverage, invalid input,
limits, concurrent cold reads and rebuilding a corrupt cache. Results and response-size
measurements are written under `out/knowledge/`.

The example also follows the two-layer workflow through explicit MCP reads,
checking that its supporting guides resolve across the topic collections.
Adding a link does not increase normal search results or automatically load
the connected collection. Older entries without links return an empty list.

This checks retrieval behavior, not model reasoning. The accompanying prompt
cases also specify expected AI behavior for separate fresh-session evaluation.
Improved hardware outcomes require running those tasks with an actual AI and
reviewing the resulting decisions and designs.
