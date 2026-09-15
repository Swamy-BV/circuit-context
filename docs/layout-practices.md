# Placement and manufacturing guidance

The video notes are useful review prompts, but several are choices or
process-specific recommendations. This collection adds 12 scoped guides and
clarifies the existing surface-finish guide. It changes the knowledge corpus,
not KiCadFlow primitives or CAD settings.

| Claim to review | Treatment in the database | Guide ID |
| --- | --- | --- |
| Use a 0.25 mm grid | Optional placement convention; preserve footprints and mechanical datums | `placement-grid-selection` |
| Group analog, digital and power | Group by function and current path; do not automatically split ground | `functional-placement-zones` |
| Put connectors on the perimeter | Use mating geometry and enclosure access; internal connectors are exceptions | `connector-edge-access` |
| Avoid minimum-clearance routing | Check coupling as well as fabrication clearance; preserve differential-pair geometry | `crosstalk-spacing-review` |
| Always enter the pad center to avoid acid traps | Center entry is a useful default; evaluate actual narrow copper features and connectivity | `pad-entry-geometry` |
| Add teardrops | Optional connection reinforcement; recheck clearance and transitions | `teardrop-review` |
| Use symmetry and rounded corners | Enclosure fit and internal milling radius govern; external symmetry is optional | `enclosure-outline-review` |
| Add a perimeter ground trace for shielding | Evaluate a stitched guard tied to the correct planes, with measurement | `edge-guard-stitching` |
| Never print over copper or vias | Review exposed areas, openings and via treatment | `silkscreen-exposed-copper` |
| Use a named font, inverted text and 1.5-2 mm minimum | Review final rendered geometry against the ordered process; these choices are not universal rules | `silkscreen-readability` |
| Mark polarity and pin one | Match the exact datasheet and assembly orientation | `polarity-marking-review` |
| Matte black is just aesthetic | Check mask capability, visibility and the current quote | `soldermask-color-selection` |
| ENIG gives longer lifespan | Distinguish flatness and bare-board storage from assembled-product reliability | `surface-finish-selection` |

The collection deliberately supplies no universal crosstalk separation or
edge-fence pitch. ADI's edge-guard evidence concerns iCoupler test boards; the
guide retains that scope and the possible increase in plane noise. Never connect
isolated ground domains merely to complete a perimeter ring.

## Sources

Reviewed on 2026-09-15. Each source record retains its URL, edition/access date,
capture status and checksum where available; each guide has section locators.

- Altium: [placement grids](https://www.altium.com/documentation/altium-designer/pcb/grids-guides)
  and [teardrop geometry](https://www.altium.com/documentation/altium-designer/pcb/removing-unused-pads-adding-teardrops).
- TI: [SCAA082A](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf), pages 10-12,
  and [SSZT935](https://www.ti.com/document-viewer/lit/html/SSZT935/GUID-0FCA647D-9DF5-4B70-AFC8-2E976F7A12D6), Figures 2-4 discussion.
- Analog Devices: [AN-1109](https://www.analog.com/en/resources/app-notes/an-1109.html), Edge Guarding.
- Eurocircuits: [copper geometry](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/copper-layers/),
  [mechanical outlines](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/mechanical-layer/),
  [legend rules](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/legend-print/)
  and [component orientation](https://www.eurocircuits.com/technical-guidelines/pcb-assembly-guidelines/component-orientation/).
- JLCPCB: [capabilities](https://jlcpcb.com/capabilities/pcb-capabilities),
  [via treatment](https://jlcpcb.com/help/article/pcb-via-covering)
  and [surface finishes](https://jlcpcb.com/blog/hasl-vs-enig-surface-finishes).
- Existing GCT USB4105 drawing and Samtec mating guidance support connector review.

The source URLs, not the unverified video timestamps, provide the citations.
No exact font recommendation, acid-trap failure prediction or product-lifetime
guarantee is treated as established evidence.

Eight new publisher pages were captured and converted to local Markdown.
The AN-1109 download timed out; its record cites the reviewed web extraction and
has no local checksum. Generated source material remains under ignored
`out/knowledge/`; the packaged corpus contains curated guidance, not these pages.

## Retrieval checks

`examples/prompts/layout_practices.json` includes 15 cases, including prompts
that challenge overbroad rules. Their `ai_expectation` fields describe desired
reasoning; the automated examples only check retrieval and provenance.
Run `pcb_knowledge.py` and `hybrid_benchmark.py` for measured results.

For corpus `2026-09-15.4`, all 194 keyword cases pass in both MCP modes. All 15
new cases pass under every strategy. The full offline benchmark reports:

| Strategy | Main cases | Paraphrases |
| --- | ---: | ---: |
| Keyword | 194/194 | 0/12 |
| Semantic | 177/194 | 12/12 |
| Hybrid | 181/194 | 12/12 |
| Hybrid with reranking | 181/194 | 11/12 |

Hybrid still returns neighbors for 13 expected-empty cases. Reranking still
misses the two-layer-escalation paraphrase. This batch changes no ranking logic
and fixes neither limitation. Lint, strict typing and installed-wheel offline
stdio checks also passed; no AI-driven PCB build or hardware test was run.

Search, for example, `{"query": "pad entry"}`, then read `pad-entry-geometry`
with `get_guideline`. Its limits remain attached to the retrieved advice.
