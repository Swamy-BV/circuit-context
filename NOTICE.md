# Origin and licensing

The initial implementation, editorial corpus, source-processing utilities and
retrieval examples were extracted from
[Swamy-BV/kicad-flow](https://github.com/Swamy-BV/kicad-flow), preserving its
AGPL-3.0-only license and existing notices.

The extraction includes the working tree's engineering-knowledge additions on
`codex/emc-guidance`. [The origin manifest](docs/origin.json) records the upstream
base commit and exact SHA-256 of each imported source file before adaptation.
This repository changes the package name, cache namespace and MCP adapter to run
independently. KiCadFlow remains unchanged by this extraction.

Publisher documents are identified by their own citations and source metadata.
Their original text, diagrams and captures are not covered by this repository's
code license. Raw captures and generated full-text conversions are excluded from
Git and package distributions. Editorial summaries are not vendor endorsements.

No implementation from the separately reviewed `datasheet-rag` repository was
copied into this project.
