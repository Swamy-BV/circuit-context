# Engineering evidence format and RAGFlow assessment

RAG is an architecture, not a universal documentation file format. Frameworks
use their own document/chunk schemas. Our stable exchange layer is versioned
JSON validated by Pydantic; Markdown provides readable authoring and review notes.
Embeddings and database indexes remain disposable derivatives.

## Our authoring convention

Keep one actionable principle or explicitly scoped pattern per guide. Keep
conditions, units, exceptions and source identity in the same record. If a
source table requires a footnote, the evidence is incomplete without that footnote.

| Information | Current representation |
| --- | --- |
| Stable identity | `id` |
| Discovery and scope | `title`, `keywords`, `topic`, `domains`, `interfaces`, `applies_to` |
| Recommendation | `summary` |
| Inputs and verification | `required_inputs`, `verification` |
| Exceptions and model limits | `limitations` |
| Traceable evidence | `citations` with `source_id` and locator |
| Source edition and integrity | Source revision, URL, access date and optional SHA-256 |
| Related evidence | `related_ids` |

For calculation guidance, name the model, dimensions/units, validity range and
omitted effects explicitly. For computed results, preserve the actual inputs and
execution output; do not represent a source's example as a new calculation.
The PCB calculation example demonstrates this distinction.

Pydantic validates structure and references. It does not currently enforce
dimensional analysis, verify citation entailment or certify engineering review.
Formal reviewer identity/status, supersession and machine-readable quantity
constraints remain future schema work. Do not imply that these are already enforced.

## Is RAGFlow appropriate?

[RAGFlow](https://github.com/infiniflow/ragflow) is an ingestion and retrieval
platform, not an engineering evidence standard. Its current README lists at least
4 CPU cores, 16 GB RAM and 50 GB disk plus Docker/Compose prerequisites.
Its [chunker documentation](https://github.com/infiniflow/ragflow/blob/main/docs/guides/agent/ingestion_pipeline/configure_chunker_component.md)
supports token/overlap settings and hierarchical title-based splitting.

For our present curated corpus, my recommendation is to keep the existing runtime.
We already have hybrid retrieval, optional reranking, offline inference, exact
filters and citations. Replacing those with a service stack has no demonstrated
engineering-quality benefit here. No RAGFlow installation or benchmark was performed.

RAGFlow becomes a reasonable ingestion pilot when document volume and editorial
workflow justify it. Compare it with the current converter using the same PDFs:

1. Recover tables, equations, units, footnotes and page locators accurately.
2. Keep incomplete captures and conflicting editions visibly separate.
3. Measure retrieval and unsupported-question behavior with unchanged fixtures.
4. Measure author correction effort, latency and operating requirements.

Only reviewed output should enter our maintained guide corpus. A parser's chunk,
a retrieval score or a generated citation is not approval of an engineering rule.
