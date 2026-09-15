# Architecture

The shared library is independent of KiCadFlow and of any particular AI client.

```text
Publisher documents -> local capture -> Markdown and review artifacts
                                            |
                                     editorial review
                                            |
                             versioned JSON guides and citations
                                            |
                             BM25 / semantic search -> RRF
                                            |
                                optional local reranking
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

The corpus lives in this standalone package; the embedded guidance was removed
from KiCadFlow. Clients configure this server separately using `search_guidelines`,
`get_guideline` and `circuit-context://catalogue`. CAD tools remain independent.

## Next steps

1. Expand evaluation to real AI sessions: correct applicability, missing inputs,
   incompatible revisions, unsupported claims and citation fidelity.
2. Compare source conversion with Docling while retaining footnotes, formulas,
   table conditions, diagrams and precise page ranges.
3. Expand the hybrid retrieval benchmark with independently authored questions
   and evaluate abstention before changing the default keyword strategy.
4. Add evidence-level revision handling and explicit supersession if original
   source passages become searchable alongside editorial records.

Optional local embeddings and reranking are described in
[hybrid retrieval](hybrid-retrieval.md). There is no graph database or generated
answer endpoint. Source review notes record specific reviewed pages; they do not
imply complete review of every document.
