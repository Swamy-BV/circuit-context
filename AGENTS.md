# Circuit Context

A CAD-independent library and read-only MCP server for engineering guidance.

## Boundaries

- `src/circuit_context/data/`: editorial guidance and source metadata.
- `models.py`, `corpus.py`: validation, identities and corpus fingerprint.
- `index.py`: offline retrieval and rebuildable cache; no model or CAD imports.
- `server.py`: thin MCP adapter. `__main__.py`: CLI adapter.
- `examples/scripts/`: MCP checks and offline source-processing utilities.
- `docs/`: authoring, architecture and source-review notes.

Preserve scope, exceptions, units, source edition and section/page locators.
Extracted text and model output are not reviewed engineering guidance. Keep
project-specific decisions outside the shared corpus. Never infer CAD decisions
or claim compliance from retrieved advice.

## Checks

Before committing, run `python -m ruff check .`, `python -m mypy`, and
`python examples/scripts/pcb_knowledge.py`. For packaging changes, build a wheel
and exercise its packaged corpus from outside the source tree. Keep prompt cases
intact when adapting an API; report regressions rather than weakening expectations.

Network access belongs to explicit authoring capture commands. Runtime retrieval
is offline. Source captures and generated indexes/reports belong under ignored
paths. Preserve the inherited AGPL license and provenance. Do not add retrieval
frameworks or change ranking behavior without a task and comparative evaluation.
