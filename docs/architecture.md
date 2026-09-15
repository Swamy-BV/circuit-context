# Architecture

The shared library is independent of KiCadFlow and of any particular AI client.

```text
Publisher documents -> local capture -> Markdown and review artifacts
                                            |
                                     editorial review
                                            |
                             versioned JSON guides and citations
                                            |
                                  SQLite keyword retrieval
                                            |
                               Python / CLI / read-only MCP
                                            |
                                  caller reasoning and CAD
```

The source-processing tools support authoring. They do not automatically publish
extracted content to the runtime index. Local captures imported during extraction
stay in ignored `out/knowledge/` and must be recreated on a fresh clone using the
capture commands. Some publisher downloads may remain unavailable.

## Extraction boundary

This first version copies the existing knowledge corpus and retrieval behavior
into a standalone package. It does not remove the embedded copy from KiCadFlow
or switch existing clients. KiCadFlow's old tool names remain there; this server
uses `search_guidelines`, `get_guideline` and `hardware-knowledge://catalogue`.
Consolidating the duplicate corpus and updating integrations is a separate change.

## Next steps

1. Expand evaluation to real AI sessions: correct applicability, missing inputs,
   incompatible revisions, unsupported claims and citation fidelity.
2. Compare source conversion with Docling while retaining footnotes, formulas,
   table conditions, diagrams and precise page ranges.
3. Benchmark semantic retrieval and reranking against the current lexical baseline.
   Introduce new dependencies only with measured benefit on this corpus.
4. Add evidence-level revision handling and explicit supersession if original
   source passages become searchable alongside editorial records.

The initial version has no embedding model, reranker, graph database or generated
answer endpoint. Source review notes record specific reviewed pages; they do not
imply complete review of every document.
