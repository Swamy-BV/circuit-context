# Peripheral interface guidance

This batch adds 12 guides: four entry overviews, six connection/routing patterns
and two review principles. Each retains required inputs, verification steps,
limitations and source locators. It extends the basic GPIO/UART/SPI/I2C guides.

| Family | Entry ID | Additional guides |
| --- | --- | --- |
| QSPI / OSPI | `serial-flash-overview` | `qspi-point-to-point`, `ospi-strobe-review` |
| SD / SDIO / eMMC | `sdmmc-overview` | `sd-card-routing`, `emmc-bringup` |
| I2S / TDM / PDM | `digital-audio-overview` | `i2s-tdm-routing`, `pdm-microphone-routing` |
| JTAG / SWD | `debug-port-overview` | `swd-connector`, `jtag-chain` |

## Retrieval workflow

Search with the relevant interface filter, read the full entry guide, then follow
its applicable pattern and shared-principle links. For example:

```json
{"query": "PDM microphone", "interface": "pdm"}
```

Read `pdm-microphone-routing` with `get_guideline`. Establish microphone and receiver
compatibility, clock and data-edge requirements before selecting connections.
The pattern supplies a textual connection diagram; it does not place components
or set constraints in CAD. Use exact endpoint documentation to establish timing,
voltage and geometry, then verify the implementation and hardware behavior.

These records do not prescribe universal trace lengths, length matching, pull
resistors or 50-ohm routing. Controller examples retain their device scope.

## Evidence and gaps

Sources reviewed on 2026-09-15:

| Source | Scope used | Capture status |
| --- | --- | --- |
| [ST XSPI interoperability](https://wiki.st.com/stm32mcu/wiki/Introduction_to_external_serial_memories_XSPI_interoperability_for_STM32), revision 83752 | Protocol and controller compatibility | Web text reviewed; direct download timed out |
| [ST AN5050](https://www.st.com/resource/en/application_note/an5050-octospi-interface-on-stm32-microcontrollers-stmicroelectronics.pdf), Rev 14, June 2026 | Strobe-capable interfaces and calibration review | Web extraction; direct download failed |
| [ST AN4488](https://www.st.com/resource/en/application_note/dm00115714.pdf), Rev 7, October 2018 | QSPI, SDMMC and debug review | Web extraction; direct download failed |
| [TI SWPA221](https://www.ti.com/lit/an/swpa221/swpa221.pdf), September 2012 | OMAP44xx SD/MMC bring-up and troubleshooting | Captured locally |
| [TI PCMD3140-Q1](https://www.ti.com/lit/ds/symlink/pcmd3140-q1.pdf), SBASAH3A, September 2022 | PDM conversion and digital audio formats | Captured locally |
| [TI SLAA920](https://www.ti.com/lit/an/slaa920/slaa920.pdf), January 2020 | TAS2563 audio connection/layout examples | Captured locally |
| [SEGGER interface description](https://www.segger.com/products/debug-probes/j-link/technology/interface-description/) | SWD and VTref wiring | Captured locally |
| [SEGGER UM08001](https://kb.segger.com/UM08001) | JTAG chains and probe configuration | Captured locally |

Captured originals and generated Markdown stay under ignored `out/knowledge/`.
Conversion is reference extraction, not approval of every page. Runtime retrieval
uses the curated records offline; it does not download documents.

Detailed eMMC HS200/HS400 channel and strobe constraints remain outside this batch.
Micron's TN-FC-62 download led to a sign-in/NDA page and was not reviewed. The
attempted NXP hardware-guide URL was unavailable. Neither is cited as evidence.
Obtain the selected controller and memory design guides before high-speed layout.
I3C, DDR memory channels, PCIe and MIPI are also outside this batch.

## Validation

`peripheral_knowledge.json` adds a retrieval case for each guide. The existing
OSPI query is preserved; its formerly empty expected result is explicitly migrated
to `ospi-strobe-review` because coverage has changed. Its AI expectation still
requires missing device-specific timing and routing constraints to be reported.
Other existing expectations are unchanged.

Measured with corpus `2026-09-15.3`: all 179 keyword cases pass in both MCP
client modes. The 12 new cases pass under keyword, semantic, hybrid and
hybrid-plus-reranker retrieval. Across the full suite:

| Strategy | Main cases | Paraphrases |
| --- | ---: | ---: |
| Keyword | 179/179 | 0/12 |
| Semantic | 162/179 | 12/12 |
| Hybrid | 166/179 | 12/12 |
| Hybrid with reranking | 166/179 | 11/12 |

The 13 hybrid main-case failures return neighboring material for queries whose
expected result is empty. Reranking also misses the two-layer-escalation
paraphrase. These limits remain; the new content does not fix abstention.
The installed wheel also passed offline stdio checks in both MCP modes, including
all retrieval strategies, citations and the new catalogue counts.

Passing retrieval checks shows that the MCP can return the material. It does not
establish that an AI applies it correctly or that a resulting PCB meets timing,
signal-integrity or EMC requirements.
