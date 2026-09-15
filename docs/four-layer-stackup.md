# Four-layer stackup review

Start with `get_guideline({"id": "four-layer-workflow"})`. This collection adds
nine conditional guides, reusing the existing electrical and manufacturing rules.
Layer assignments are choices for the caller, not automatic CAD decisions.

| Review | Guide ID |
| --- | --- |
| Two inner ground references | `four-layer-dual-ground` |
| Dedicated inner power layer | `four-layer-power-plane` |
| Outer ground and buried routing | `four-layer-shielded` |
| Dielectric construction | `four-layer-dielectric-spacing` |
| Fast routes adjacent to power copper | `four-layer-power-reference` |
| Plane coupling and bypassing | `four-layer-pdn` |
| Vendor examples and heuristics | `four-layer-source-limits` |
| When more layers are needed | `four-layer-escalation` |

The workflow links to return continuity, signal transitions, impedance selection,
decoupling, power sizing and EMC planning. Retrieve those records as needed.
Request the actual fabrication construction and device requirements before
selecting widths, distances or component values. Validation must include the
assembled product; the database cannot establish compliance.

## Evidence and interpretation

- [ADI Part 4](https://www.analog.com/en/resources/technical-articles/passing-emi-compliance-testing-first-time-part-4.html):
  layer-selection discussion and its two numbered options. Its later prose uses
  confusing layer assignments; this corpus cites the explicit numbered options
  rather than silently reconciling that paragraph.
- [NXP AN10897](https://www.nxp.com/docs/en/application-note/AN10897.pdf):
  section 3.1.1.1, page 15. This older document provides construction and rework
  tradeoffs; its examples are not a manufacturing prescription.
- [NXP AN14395](https://www.nxp.com/docs/en/application-note/AN14395.pdf):
  revision 2.0, section 3.1, page 9. Retain its MCXA14x/15x scope. Example dimensions
  and edge heuristics remain conditional.
- [TI SCAA082A](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf):
  sections 2.1–2.4. Table 3's EMC ratings describe the compared examples; they do
  not prove that all four-layer products fail testing. Page 9 was rendered and
  visually reviewed during this update.
- [TI SLLA414A](https://www.ti.com/lit/an/slla414a/slla414a.pdf):
  January 2026 revision, section 3.5. Its high-speed interface guidance is more
  restrictive about power references than a generic layer-assignment example.

This is an editorial reconciliation of differently scoped sources, not a claim
that all three publishers prescribe the same stackup. Device-specific guidance
must still be checked, particularly for isolation and precision analog circuits.

## Capture status

TI originals were captured locally on 2026-09-15 and converted with the existing
Markdown pipeline. NXP web PDF extraction was available, but direct capture
returned HTTP 404 for both notes. A fresh ADI HTML capture timed out. Available
older local captures remain separate from the current web review. Missing bytes
are not represented as successful downloads or assigned invented checksums.

The maintained runtime evidence is the cited JSON guidance. Raw documents and
machine conversions remain ignored authoring artifacts, not query-time downloads.

## Verification

`examples/prompts/four_layer_knowledge.json` supplies nine new retrieval cases and
manual AI expectations. The standard MCP example runs them alongside the unchanged
existing fixtures. Corpus changes invalidate prepared semantic vectors; rebuild
with `circuit-context prepare-search --offline` before semantic queries.

On corpus 2026-09-15.1, all nine new cases passed with keyword, semantic, hybrid
and hybrid-plus-reranker retrieval. Keyword passed all 161 fixture cases in both
MCP modes. Hybrid passed 147/161: the 14 expected-empty cases still returned
neighbors, as in the prior benchmark. All 12 paraphrases passed hybrid retrieval;
reranking passed 11/12. These results do not evaluate AI engineering decisions.
