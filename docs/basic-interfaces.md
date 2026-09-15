# Basic interface guidance

Start with an interface overview, select the applicable routing pattern, then
read its shared principles and the exact device requirements. The MCP supplies
reference material; the caller chooses the circuit, constraints and coordinates.

For QSPI/OSPI, SD/SDIO/eMMC, audio and debug interfaces, see
[peripheral interface guidance](peripheral-interfaces.md).

| Family / entry ID | Initial patterns |
| --- | --- |
| `gpio-overview` | Push-pull point-to-point; open-drain shared interrupt |
| `uart-overview` | Direct TX/RX; logic-level debug header; external transceiver |
| `spi-overview` | Single target; independent chip selects; supported daisy chain; off-board link |
| `i2c-overview` | Shared bus; translated/buffered segments; cable connection |

These collections add 17 records: four overviews, 12 routing patterns and one
STM32 GPIO configuration note. They reuse existing pull-up, termination,
return-path and protection guidance through `related_ids`.

## Retrieval

Call `search_guidelines` with short terms and an optional family filter:

```json
{"query": "overview", "interface": "spi", "topic": "interface-overview"}
```

Read `spi-overview` with `get_guideline`. For several independently selected
targets, read its `spi-shared-bus` link. That record describes:

```text
Controller SCK/MOSI --> shared nets --> Target 1, Target 2
Controller CS1 ---------------------> Target 1 CS
Controller CS2 ---------------------> Target 2 CS
Controller MISO <--- selected target SDO; inactive outputs must release
```

This is a logical topology, not a placement template. Before drawing it, the
caller obtains the devices, operating mode, chip-select/output-release timing,
edge rates and board loading. The guide identifies contention and branch timing
checks. It supplies no fixed resistor, trace length or automatic topology choice.

`kind` distinguishes `principle`, `overview`, `routing-pattern` and `device-note`.
Search returns compact summaries and `kind`. Only an explicit full read returns
`pattern`: `diagram`, `placement`, `routing`, `return_path` and `pitfalls`.
Applicability, required inputs, verification, limitations and citations remain
attached to the record. Existing records default to `principle` with no pattern.
Related records are never expanded automatically. No CAD tool signature changes.

Record selected assumptions and device requirements in the project, use live CAD
tools to inspect the design, and verify both electrical connectivity and layout.
Simulation or bench checks remain necessary where the guide calls for them;
retrieving a record does not perform those checks or establish EMC compliance.

## Sources and editorial boundaries

Primary references include ADI's [SPI introduction](https://www.analog.com/en/resources/analog-dialogue/articles/introduction-to-spi-interface.html)
and [AN-1248](https://www.analog.com/en/resources/app-notes/an-1248.html), TI's
[I2C guide](https://www.ti.com/lit/an/sbaa565/sbaa565.pdf), NXP's
[UM10204](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/nxp-designs/931/1/UM10204.pdf),
and TI's [CMOS input note](https://www.ti.com/lit/an/scba004e/scba004e.pdf).
Each runtime record includes source editions and section locators. Routing
patterns are original editorial syntheses, not reproduced vendor drawings.

The [ADI UART article](https://www.analog.com/media/en/analog-dialogue/volume-54/number-4/uart-a-hardware-communication-protocol.pdf)
supports basic connectivity and framing. Its broad baud-tolerance, parity and
security claims are not adopted: determine clock-error limits from the selected
receiver, and do not treat parity or framing as proof of error-free or secure
communication. The historical RS-232 article supports the physical-layer
distinction, not present-day certification limits. STM32 configuration guidance
retains its device scope.

Three source downloads succeeded in this pass: TI SBAA565, TI SCBA004E and NXP
UM10204. They were converted into individual local Markdown documents using the
[source conversion workflow](source-markdown.md). ADI's four downloads and ST's
GPIO download failed; their primary-source web reviews remain cited with null
checksums. No local Markdown is claimed for those five sources. Captures and
conversion audit files are under ignored `out/knowledge/`; only curated
guidance enters the runtime index. Figures flagged for visual review are not
automatically considered reviewed.

## Coverage limits and checks

This first set excludes synchronous USART, dedicated flow-control layouts,
single-wire UART, LIN, I3C, SMBus/PMBus, QSPI/OSPI, DDR and high-speed memory
channels. Add those as separate families or patterns with their own sources.

Run `python examples/scripts/pcb_knowledge.py`. The basic interface prompt file
adds retrieval cases and expected AI decisions for later fresh-session review.
The script checks real MCP retrieval, citations, explicit links, family/topic
filters and bounded responses in both protocol modes. It does not measure AI
reasoning or prove that generated hardware follows the guidance.
