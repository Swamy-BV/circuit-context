# Schematic visual layout and readability

This collection covers 24 review topics. It is a broad starting catalogue, not
an exhaustive drafting standard. All records use `domain: schematic`; the MCP
entry point is `schematic-visual-workflow`.

## Documents worth reading

- [KiCad 9 Schematic Editor](https://docs.kicad.org/9.0/en/eeschema/eeschema.html):
  electrical drawing semantics and tool-specific checks.
- [KiCad pin grouping](https://klc.kicad.org/symbol/s4/s4.2/),
  [text sizing](https://klc.kicad.org/symbol/s3/s3.2/),
  [multi-unit symbols](https://klc.kicad.org/symbol/s3/s3.8/) and
  [active-low names](https://klc.kicad.org/symbol/s4/s4.7/): official-library conventions.
- [Altium: Elegant and Readable Schematics](https://resources.altium.com/p/creating-elegant-and-readable-schematics):
  Mark Harris's drafting recommendations, updated January 2024.
- [Altium: Useful Schematic Symbols](https://resources.altium.com/p/guidelines-creating-useful-schematic-symbols):
  symbol-design recommendations, updated March 2021.
- [Cadence: Schematic Readability](https://resources.academic.cadence.com/pcb-design-and-analysis-resources/2020-schematic-tips-for-better-electronic-design-readability):
  text, symbol and review quality; the page displays September 2025 despite its URL.

The two Altium articles and the KiCad KLC use different power-pin placement
conventions. The corpus preserves this distinction instead of combining them into
one mandatory style. KLC governs library contributions; it does not require
redrawing every existing circuit. The CAD manual is versioned to KiCad 9.

Four documents were captured and converted to local Markdown. Direct KLC
downloads returned HTTP 403, so those four records identify web-reviewed text
without claiming an archived original. No runtime query downloads these pages.
Cadence required gzip transport decoding; the capture utility now bounds both
compressed and decoded sizes and records hashes for each. Altium conversions
use explicit article-body selectors to avoid selecting the site's logo article.

## Coverage

| Area | Guide IDs |
| --- | --- |
| Review entry point | `schematic-visual-workflow` |
| Main signal path | `schematic-signal-flow` |
| Functional sections | `schematic-functional-groups` |
| Sheet organization | `schematic-hierarchy` |
| Repeated circuitry | `schematic-repeated-channels` |
| Space for symbols and annotations | `schematic-whitespace` |
| Electrical connection grid | `schematic-grid` |
| Logical symbol arrangement | `schematic-functional-symbols` |
| Traceable wire paths | `schematic-wire-paths` |
| Crossings and connections | `schematic-junction-clarity` |
| Local/global/hierarchical labels | `schematic-label-scope` |
| Bus membership | `schematic-bus-members` |
| Signal naming | `schematic-net-names` |
| Active-low meaning | `schematic-active-low` |
| Interface pin ordering | `schematic-pin-order` |
| Unused pins | `schematic-no-connect-display` |
| Text overlaps | `schematic-text-collisions` |
| Text scale | `schematic-text-scale` |
| Supply-symbol orientation | `schematic-power-orientation` |
| Multi-unit power visibility | `schematic-multiunit-power` |
| Feedback, bias and supporting parts | `schematic-local-support` |
| Connector views | `schematic-connector-view` |
| Values, DNP and explanatory notes | `schematic-design-notes` |
| Export review and color independence | `schematic-final-render` |

The maintained records are divided into `schematic_layout.json`,
`schematic_connections.json` and `schematic_review.json`.

## Editorial conventions versus source requirements

The following records explicitly mark their recommendations as editorial:
workflow, repeated channels, whitespace, wire paths, local supporting circuits,
connector views, design notes and final rendering. Their citations identify
supporting background, not a claim that the publisher mandates every detail.

Useful editorial review prompts include:

- Keep local circuit relationships visible; do not replace every short connection
  with a label solely to reduce wire count.
- Check annotations after rotation, mirroring or movement. Text and pin-number
  bounds matter alongside the symbol body.
- Give sheets an informative title and revision context; use enough space for
  labels, rather than shrinking a crowded page until it fits.
- Use consistent presentation for repeated channels and make exceptions visible.
- Review in grayscale as well as color when the output may be printed.

These are preferences to apply with judgment. They supply no universal gap,
page-utilization percentage, maximum wire length or readability score.

## Small review examples

These textual sketches illustrate editorial review criteria, not CAD files or
verified connectivity. They are not publisher figure reproductions.

**Preserve a local feedback path.**

```text
Harder to review: amplifier here; its feedback divider elsewhere via labels.
Clearer:         amplifier + nearby divider + visible feedback loop.
```

**Move text, not the electrical endpoint, when only text overlaps.**

```text
Before: R7 / 10k text crosses a neighboring wire.
After:  R7 / 10k remains beside the resistor, clear of that wire.
Check:  component identity and nets remain unchanged.
```

**Do not mistake visual grouping for an electrical connection.**

```text
Before: several labeled signals appear to enter a drawn bus.
Review: inspect each member name and actual resulting net.
After:  only the intended member connections remain, with readable labels.
```

## Using the guidance

```json
{"query": "schematic text overlaps", "domain": "schematic"}
```

Read the returned guide with `get_guideline`, including its limitations. A
readability correction should be followed by connectivity checks and inspection
of the exported drawing. RAG supplies review criteria; it does not inspect a
schematic scene or move symbols. KiCadFlow primitives are unchanged.

The prompt fixture records manual AI expectations. Automated retrieval checks do
not prove that an AI can clean up a schematic while preserving its circuit.

## Measured checks

For corpus `2026-09-15.5`, all 218 keyword cases pass in both MCP modes. The
24 new schematic cases pass with each retrieval strategy. Across the full suite:

| Strategy | Main cases | Paraphrases |
| --- | ---: | ---: |
| Keyword | 218/218 | 0/12 |
| Semantic | 201/218 | 12/12 |
| Hybrid | 205/218 | 12/12 |
| Hybrid with reranking | 205/218 | 11/12 |

The existing 13 expected-empty queries still receive neighbors under hybrid
search; reranking also misses the two-layer-escalation paraphrase. Ranking logic
is unchanged. Lint, strict typing and installed-wheel offline MCP checks passed.
`source_capture_contract.py` checks plain/gzip HTML, provenance and failure limits
without contacting a publisher. No AI-generated schematic or hardware behavior
was evaluated in this change.
