# Circuit Context

Source-backed hardware engineering guidance for engineers and AI assistants.
Search recommendations, read their conditions and exceptions, and follow citations
to the publisher. Covers schematics, PCB layout, interfaces, EMI/EMC and mechanical
integration.

## Start

Requires Python 3.10 or newer.

```sh
python -m pip install ".[mcp]"
circuit-context serve
```

`serve` runs a read-only MCP server over stdio. Configure an MCP client to run
`circuit-context` with the argument `serve`. It exposes:

| Interface | Purpose |
| --- | --- |
| `search_guidelines` | Find bounded, cited summaries with explicit filters |
| `get_guideline` | Read one guide's inputs, verification, limitations and sources |
| `circuit-context://catalogue` | Browse coverage, IDs, filter values and source editions |

For example, search `{"query": "return path", "domain": "pcb"}`, then read a
returned ID with `get_guideline`. A two-layer review can start directly with
`{"id": "two-layer-emc-workflow"}`.

## Other ways to use it

```sh
circuit-context search "return path" --domain pcb
circuit-context get two-layer-emc-workflow
circuit-context catalogue
```

```python
from circuit_context import get_guideline, search_guidelines

hits = search_guidelines("termination", interface="can")
guide = get_guideline("can-end-termination")
```

The base package supports Python and CLI retrieval without FastMCP. Install the
`mcp` extra for the server. The AI client performs reasoning and uses separate CAD
tools for design work; this package does not place parts, route boards or generate
answers with an internal LLM.

## Knowledge and retrieval

The corpus has 107 editorial guides and 50 source records, expanded from
KiCadFlow's engineering guidance. JSON is the maintained source; SQLite FTS5/BM25
provides offline keyword retrieval by default. Optional local semantic search
handles paraphrases; hybrid search combines both using reciprocal rank fusion.
An optional cross-encoder reranks the candidates.

```sh
python -m pip install ".[mcp,search]"
circuit-context prepare-search --reranker
circuit-context search "Where does returning current go when a signal changes layers?" --method hybrid
```

Model downloads happen only during explicit preparation. Queries run locally.
Use `--rerank` to enable the second stage, or MCP arguments
`{"query": "...", "method": "hybrid", "rerank": true}`. Neither semantic
similarity nor reranking establishes that the corpus contains an answer.
See [setup and measured tradeoffs](docs/hybrid-retrieval.md).

Applicability, required inputs, verification, limitations and source editions stay
attached to each guide. Missing coverage is reported. The corpus has not undergone
independent hardware-engineer review and does not establish product compliance.

The generated index lives in `~/.circuit-context/cache/`; override it with
`CIRCUIT_CONTEXT_DIR`. It contains guidance, not user queries or project files.

- [Coverage and authoring](docs/pcb-knowledge.md)
- [Two-layer stackup and EMC](docs/two-layer-emc.md)
- [Four-layer stackup choices and review](docs/four-layer-stackup.md)
- [GPIO, UART, SPI and I2C](docs/basic-interfaces.md)
- [USB-C and PD](docs/usb-c-guidance.md)
- [Source capture and Markdown conversion](docs/source-markdown.md)
- [Architecture and next steps](docs/architecture.md)

## Development

```sh
python -m pip install -e ".[mcp,dev,ingest,search]"
python -m ruff check .
python -m mypy
python examples/scripts/pcb_knowledge.py
python examples/scripts/hybrid_contract.py
python -m build
```

The example checks actual MCP retrieval, citations, bounds and cache recovery in
both protocol modes. Its prompt fixtures also describe AI expectations; passing
retrieval checks does not measure model reasoning or hardware outcomes.

Publisher captures, extracted Markdown, page images and generated reports stay
under ignored `out/`. They are not distributed with the package.

AGPL-3.0-only. See [LICENSE](LICENSE) and [provenance](NOTICE.md).
