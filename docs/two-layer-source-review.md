# Two-layer source review

Reviewed on September 14, 2026 for non-RF two-layer PCB guidance. This extends
the existing stackup/EMC workflow using publisher material. It is an editorial
knowledge library, not a compliance prediction or a complete engineering textbook.

## Capture and provenance

Of 21 selected resources, 14 downloaded and parsed successfully: 11 PDFs and
three HTML pages. Seven ADI/ST downloads failed on both attempts through timeout
or connection closure; their content was readable through publisher web extraction.
Those source records retain null checksums. No alternate edition was silently
substituted. All seven previously recorded hashes among successful captures matched.

Originals, extracted text and attempt manifests are local under
`out/knowledge/sources/`, which Git ignores. PDF text includes physical page
numbers. Filenames include the complete SHA-256, so later snapshots retain earlier
editions. The archive README links each captured original and its text.
Full vendor documents are not distributed in the package or indexed at runtime.
The captured originals have since been [converted to Markdown](source-markdown.md),
with page anchors, structured table metadata and visual-review notes.

The repeatable authoring command takes explicit IDs from `sources.json`:

```powershell
python examples/scripts/capture_knowledge_sources.py ti-spma056 ti-slva959b microchip-touch-an0208
```

It records URL, final URL, capture time, edition, byte count, checksum, MIME type,
page count, extraction paths, catalogue-hash comparison and failures. The command
does not promote downloaded text into trusted guidance or modify the catalogue.
HTML extraction can include navigation or an error page: a successful capture
still requires editorial review. Hash changes require edition/content review;
HTML hashes identify a response, not a stable edition.

## Selected publisher resources

| Source ID / resource | Local capture | Contribution |
| --- | --- | --- |
| `ti-scaa082a` / [TI High-Speed Layout Guidelines](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf) | PDF | Existing return-path, coupling and layout guidance |
| `ti-slla414a` / [TI Signal Conditioners and USB Hubs](https://www.ti.com/lit/an/slla414a/slla414a.pdf) | PDF | Existing interface/reference constraints |
| `microchip-an2587` / [Microchip AN2587](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/00002587A.pdf) | PDF | Existing MCU hardware/layout review |
| `ti-spma056` / [TI TM4C129x System Design](https://www.ti.com/lit/an/spma056/spma056.pdf) | PDF | Conditional two-layer use and physical stackup, sections 3.2.1–3.2.2 |
| `st-emc-rev5` / [ST AN1709 Rev. 5](https://www.st.com/resource/en/application_note/an1709-emc-design-guide-for-stm8-stm32-and-legacy-mcus-stmicroelectronics.pdf) | Failed; web read | Existing product/MCU EMC distinctions |
| `st-gpio` / [ST AN4899](https://www.st.com/resource/en/application_note/DM00315319-.pdf) | Failed; web read | Existing GPIO configuration review |
| `ti-snva054c` / [TI SIMPLE SWITCHER Layout](https://www.ti.com/lit/an/snva054c/snva054c.pdf) | PDF | Existing converter layout exceptions |
| `ti-buck-emi` / [TI SNVA755](https://www.ti.com/lit/an/snva755/snva755.pdf) | PDF | Existing switching loops and EMI |
| `ti-esd-layout` / [TI SLVA680A](https://www.ti.com/lit/an/slva680a/slva680a.pdf) | PDF | Existing connector protection layout |
| `ti-szza009` / [TI PCB EMI Reduction](https://www.ti.com/lit/an/szza009/szza009.pdf) | PDF | Existing source/return/cable review |
| `adi-mt031` / [ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf) | Failed; web read | Existing mixed-signal grounding guidance |
| `murata-mounting` / [Murata MLCC mounting guidance](https://www.murata.com/-/media/webrenewal/support/faqs/products/capacitor/ceramiccapacitor/cncap.ashx?la=en) | PDF | Existing assembly and board-flex constraints |
| `jlcpcb-capabilities` / [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) | HTML | Current fabrication dimensions; recheck per order |
| `jlcpcb-finishes` / [JLCPCB HASL versus ENIG](https://jlcpcb.com/blog/hasl-vs-enig-surface-finishes) | HTML | Existing assembly/finish tradeoffs |
| `tek-emi-precompliance` / [Tektronix precompliance](https://www.tek.com/en/documents/application-note/emi-pre-compliance-testing-and-troubleshooting-tektronix-emcvu) | HTML | Existing diagnostic versus compliance measurements |
| `adi-emi-part3` / [ADI placement and grounding](https://www.analog.com/en/resources/technical-articles/passing-emi-compliance-testing-the-first-time-part-3.html) | Failed; web read | New layout-intent handoff |
| `adi-emi-part4` / [ADI power routing and stackup](https://www.analog.com/en/resources/technical-articles/passing-emi-compliance-testing-first-time-part-4.html) | Failed; web read | New power/return-space planning |
| `adi-emi-part5` / [ADI precision analog and thermal management](https://www.analog.com/en/resources/technical-articles/passing-emi-compliance-testing-the-first-time-part-5.html) | Failed; web read | New thermal-gradient review |
| `ti-slva959b` / [TI motor-driver layout](https://www.ti.com/lit/an/slva959b/slva959b.pdf) | PDF | New ground-grid and Kelvin-sense review |
| `microchip-touch-an0208` / [Microchip maXTouch layout](https://ww1.microchip.com/downloads/aemDocuments/documents/HMID/ApplicationNotes/ApplicationNotes/AN0208_Design_Guidelines_for_PCB_Layouts.pdf) | PDF | New sensor-reference exception and flex mapping |
| `adi-cn0282` / [ADI CN-0282](https://www.analog.com/media/en/reference-design-documentation/reference-designs/CN0282.pdf) | Failed; web read | New reference-design transfer review; July 2012 edition |

The [NXP staff two-layer discussion](https://community.nxp.com/t5/Kinetis-Motor-Suite-Knowledge/Latest-PCB-Guidelines-pdf/ta-p/1100711)
was also reviewed. The referenced attachment was not exposed in the accessible
page; it was not counted as a downloaded source or promoted as evidence for a
new rule. Its return-path theme was already covered by accessible primary notes.

## Conversion decisions

Eight original guidance records were added, each retaining applicability,
required inputs, verification, limitations, citations and explicit related-guide
links. Existing evidence was reused instead of creating duplicate rules.

| New guide | Evidence location | Scope |
| --- | --- | --- |
| `layout-intent-handoff` | ADI part 3, Schematics to Placement | Physical intent absent from net connectivity |
| `two-layer-power-return-budget` | ADI part 4, System Routing and For a 2-Layer Board | Power/return area and supply-domain feasibility |
| `motor-ground-grid` | TI SLVA959B, sections 1.1–1.2.1, pp. 3–6 | TI DRV grounding |
| `motor-current-sense-kelvin` | TI SLVA959B, sections 7.5–7.9, pp. 32–34 | Shunt terminal pickup |
| `capacitive-touch-ground-exception` | Microchip AN0208, sections 3.1, 3.4–3.7, pp. 4–6; 7.4, p. 17 | maXTouch sensor routing |
| `precision-analog-thermal-gradients` | ADI part 5, The Movement of Heat in the PCB | Measurement error from heat flow |
| `two-layer-reference-design-transfer` | ADI CN-0282, pp. 4–5 | Demonstrated functionality versus product evidence |
| `touch-fpc-orientation` | Microchip AN0208, sections 8.2–8.3, p. 19 | Assembled contact mapping |

TI's ground-grid figure and Microchip's stackup diagrams were rendered and
visually reviewed. Microchip section 3.1 explicitly distinguishes ordinary
signal returns from sensor X/Y routing; that distinction stays attached to the
retrieved exception. Ordinary board references must not be removed because a
touch sensor exists elsewhere on the board.

The editorial synthesis does not adopt universal 50-ohm routing, fixed via
spacing, unconditional ground splits, a mandatory top power pour, or fixed
two-layer frequency cutoffs. Those choices require circuit context. Application
note examples and article titles do not establish product EMC compliance.

## Verification

At the end of the two-layer source pass, the corpus had 66 guides and 36 source
records. The MCP example passed 104
retrieval cases in both `auto` and `legacy` modes and followed 59 linked guides
from the two-layer workflow through explicit reads. New prompt cases describe
the intended AI behavior separately; these runs did not measure model reasoning.

Ruff and strict mypy passed. Both unchanged CAD examples completed through MCP:
FC reported no ERC/layout findings or potential overlaps; LED reported zero
failed calls, zero unrouted connections and zero DRC errors, with 558 existing
other findings. FC and LED renders were inspected; the LED reference/silkscreen
crowding remains. These examples do not establish hardware EMC performance.

The local archive is useful for future review, but runtime search still reads
only the curated offline corpus. Updating files requires restarting the server;
no new framework, model service or automatic CAD policy was introduced.
