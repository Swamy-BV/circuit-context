# USB-C hardware guidance

Start with `get_guideline({"id": "usb-c-overview"})`. Specify the power role,
data generation, required power and PD support before choosing circuitry.

| Area | Entry points |
| --- | --- |
| Reference editions | `usb-c-specifications` |
| Fixed 5 V sink | `usb-c-sink-cc` |
| Source and dual-role ports | `usb-c-source-port`, `usb-c-dual-role` |
| Reversible USB 2.0 data | `usb-c-usb2-routing` |
| SuperSpeed lane selection | `usb-c-superspeed-routing` |
| VCONN and cable capability | `usb-c-vconn-cable` |
| PD contracts and power paths | `usb-pd-contract`, `usb-pd-power-path` |
| SPR/EPR and programmable supplies | `usb-pd-epr-pps` |
| Protection, mechanics and testing | `usb-c-port-protection`, `usb-c-mechanical-review`, `usb-c-verification` |

The collection has 14 records, including five text routing patterns. Search with
`interface="usb-c"`; the three PD records also support `interface="usb-pd"`.
Related guides reuse existing return-path, ESD, power and differential-routing
guidance. Details load only on explicit reads.

## Rules that prevent common mistakes

- Keep sink CC1 and CC2 terminations independent. Check integrated Rd before
  adding external resistors; two pull-downs alone do not authorize 3 A or PD.
- Join duplicate USB 2.0 D+ contacts and duplicate D- contacts near the receptacle
  where the connector exposes them separately. Check both plug orientations.
- Use supported lane selection for SuperSpeed; its alternate lane groups are
  not joined like USB 2.0 duplicate contacts.
- Coordinate source VBUS with attachment and faults. Review PD startup,
  negotiation, fallback, power-path ratings and cable capability together.
- Distinguish ESD clamping from sustained short-to-VBUS protection, including
  the voltage envelope of any EPR design.

`impedance-requirement-selection` makes the general rule explicit: 50 ohms is not
a default for every trace or an automatic termination resistor value. Establish
interface requirements, edge rates, route delay and the fabrication stackup.
Distinguish characteristic impedance from DC resistance and differential from
single-ended targets. Read this guide explicitly before selecting impedance targets. USB 2.0 high-speed guidance includes
its common 90-ohm differential target, subject to the PHY and channel requirements.

## Sources and limits

The [USB-IF Type-C 2.5 release page](https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25)
and [PD release page](https://www.usb.org/document-library/usb-power-delivery)
identify normative references. On September 14, 2026, the latter linked
`USB_PD_R3.2_V1.2(3).zip`. Only these HTML release listings were captured and
converted; the ZIP specifications have not been downloaded or fully ingested.

Four TI PDFs were captured and converted: [SLYY109B](https://www.ti.com/lit/slyy109),
[TUSB320](https://www.ti.com/lit/ds/symlink/tusb320.pdf),
[SLYY105](https://www.ti.com/lit/wp/slyy105/slyy105.pdf) and
[SSZTD49A](https://www.ti.com/lit/ta/ssztd49a/ssztd49a.pdf).
Existing SLLA414A supplies additional channel-layout guidance. Runtime records
also cite the captured [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf)
as a mechanical-review example; its dimensions are specific to that connector.
All records
carry exact editions, source hashes and section locators. Full source content
stays under ignored `out/knowledge/`; see [the Markdown workflow](source-markdown.md).

Historical 100 W/20 V examples are not current universal PD limits. Old power
tables and generic USB3/USB4 layout tables are not substitutes for the selected
revision, channel and device requirements. No automatic USB compliance checker,
PD firmware implementation or complete USB4/alternate-mode channel design is
provided. Device and product qualification still require the applicable tests.

## Verification and existing example finding

`examples/prompts/usb_c_knowledge.json` adds impedance and USB-C retrieval cases,
plus expected AI behavior for separate evaluation. Run
`python examples/scripts/pcb_knowledge.py` to exercise real MCP retrieval,
source reads, linked-guide traversal and exact filters in both modes.

A read of the existing FC root netlist through MCP found `USB_DP` connected to
J2.A6 and U3.45, and `USB_DM` to J2.A7 and U3.44. J2.B6 and J2.B7 remain on
individual unconnected nets; the example input marks both no-connect. This does
not implement the duplicate-contact connection recommended for a reversible
USB 2.0 receptacle. Its clean ERC result therefore does not establish USB-C
correctness. The example input has not been changed to hide this finding.
The readback is saved locally as `out/knowledge/fc-usbc-net-review.json`.
