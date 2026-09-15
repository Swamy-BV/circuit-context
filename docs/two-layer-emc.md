# Two-layer stackup and EMC design review

This is a design and verification workflow for non-RF MCU, sensor and control
products. It supports work toward passing the applicable emissions and immunity
tests. It cannot guarantee a pass or replace the selected device documentation,
fabricator construction, product requirements or measurements.

In the RAG, start with `get_guideline("two-layer-emc-workflow")`, or search
`two layer EMC stackup`. Read its `related_ids` for the relevant details. These
are editorial reading links, not automatic tool actions. Record design decisions
and measurement evidence in the project, not the shared knowledge database.

## 1. Establish the requirements

Before choosing construction, record:

- Product environment, intended markets, applicable standard editions, required
  emissions and immunity tests, and functional acceptance criteria.
- Actual MCU, regulator and interface devices; packages; clock sources;
  loaded rise/fall times; power currents and operating modes.
- Board outline, mechanical anchors, enclosure, cables, connector pinouts,
  external loads and power source.
- Fabricator and assembly constraints, copper weight, thickness tolerance,
  available stackups and the current quote.

Do not derive test levels or acceptance criteria from the MCU's component rating.
An emissions result does not establish immunity. Identify requirements with the
product team and test laboratory. [ST AN1709, sections 2-3](https://www.st.com/resource/en/application_note/an1709-emc-design-guide-for-stm8-stm32-and-legacy-mcus-stmicroelectronics.pdf)

## 2. Specify the physical stackup

Use this as a candidate arrangement, subject to device requirements and routing
feasibility. Record the actual construction in the fabrication specification.

| Physical layer, top to bottom | Role and information to record |
| --- | --- |
| Top solder mask | Fabricator material and thickness when relevant to impedance; assembly openings |
| F.Cu | Components, short signals, power distribution and useful connected GND copper; finished copper thickness |
| FR4 core | Actual dielectric thickness and material properties supplied by the fabricator |
| B.Cu | Mostly continuous GND, especially beneath critical top routes; finished copper thickness |
| Bottom solder mask | Fabricator construction and assembly openings |

Consider 1 oz finished copper as a starting fabrication candidate, then check
current, thermal and routing needs. Specify finished copper rather than assuming
base foil and plated copper are interchangeable. Track widths, clearances and
via dimensions still require separate selection.

| Candidate board thickness | When to consider it | Required review |
| --- | --- | --- |
| 0.8 mm | Reduced signal-to-reference separation is useful and the mechanics allow it | Connector fit, support, assembly deflection, tolerances and price |
| 1.6 mm | Assembly or mechanical requirements favor this thickness | Greater separation makes short paths, local returns and edge control more important |

**1.6 mm does not automatically fail EMI/EMC. 0.8 mm does not guarantee a pass.**
Changing thickness does not imply a proportional change in emissions. On two
layers, core thickness largely determines reference separation; on four layers,
a nearby internal ground can provide smaller separation at the same overall
board thickness. [TI SPMA056, section 3.2](https://www.ti.com/lit/an/spma056/spma056.pdf)

Top-only components are a layout preference. Bottom components and limited bottom
routing are possible when assembly and reference continuity permit them. If a
critical route must use B.Cu, establish its actual return path; do not assume the
top layer has become a suitable reference automatically. Confirm manufacturing
dimensions against the selected process. [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)

RAG: `two-layer-planning`, `board-thickness-choice`, `fabrication-profile`,
`surface-finish-selection`.

## 3. Place around current paths

Establish connectors, mounting holes and enclosure constraints first. Group
related circuitry and keep noisy power regions away from sensitive measurements.
Reserve space for critical connections before filling the remaining placement.
This ordering is an editorial workflow; coordinates come from the actual design.

- Inspect the full IC supply-pin, bypass-capacitor and ground-return connection.
  A short body-to-body distance alone does not establish good decoupling.
- Place switching-loop components according to the exact converter reference
  layout. Keep crystal and load components close to their oscillator pins.
- Check permitted pin mappings before swapping MCU connections. Update schematic
  and firmware consistently, preserving required boot and debug access.

Use actual device bypass values and oscillator loading. [ADI MT-031, decoupling](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf),
[ST AN4899, pin configuration](https://www.st.com/resource/en/application_note/DM00315319-.pdf)

RAG: `functional-placement`, `decoupling-loop`, `crystal-placement`,
`mcu-pin-assignment`.

## 4. Preserve returns throughout routing

Inspect filled copper along critical signals, not just a GND net name or pour
percentage. Avoid return detours caused by ground gaps and merged via clearances.
Connect useful top ground to the intended bottom reference near the circuits it
serves. Nearby connected ground may help close a local loop; an isolated guard
strip does not provide that return.

Review bottom jumps by their effect on returns. A run shorter than 2 mm is not a
pass criterion. Ground vias help only when they connect the relevant copper.
Keep fast routes away from board edges and ground gaps with spacing selected for
the actual construction and coupling problem. [TI SCAA082A, sections 1.6 and 2.5](https://www.ti.com/lit/an/scaa082a/scaa082a.pdf)

Refill after changes. Inspect islands, narrow ground necks, shared return paths
and device keepouts. Do not automatically split analog and digital ground or
join isolation domains. KiCad's island-removal setting has an exception for
wholly unconnected zones, so inspect the actual result. [KiCad zone documentation](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html)

RAG: `ground-pour-stitching`, `two-layer-bottom-jump`,
`reference-plane-continuity`, `mixed-signal-grounding`.

## 5. Control power noise and digital edges

For a switching regulator, identify the current paths in each switching state.
Keep the changing loop compact. Minimize unnecessary switch-node copper while
meeting thermal/current needs; keep feedback and sense connections away from
noisy nodes. Follow device-specific ground and copper keepouts rather than
applying a universal pour rule. A ground plane cannot compensate for poor local
power placement. [TI AN-1229, sections 3, 6-8](https://www.ti.com/lit/an/snva054c/snva054c.pdf)

Select power widths, neck-downs and vias using current, copper, voltage-drop and
thermal requirements. Size bulk capacitance for actual supply/load transients
and regulator stability. Evaluate input-filter interaction, ferrite bias and
resonance before adding filtering; no universal bead or capacitor value applies.

Use the slowest supported GPIO slew that meets the interface's timing and load.
Evaluate source termination only for a suitable topology. Avoid floating digital
inputs while preserving boot and debug needs; check exact MCU reset states.
Check waveforms at the receiver, not only at the driver. [ST AN1709, sections
4.2.3 and 5.1](https://www.st.com/resource/en/application_note/an1709-emc-design-guide-for-stm8-stm32-and-legacy-mcus-stmicroelectronics.pdf)

RAG: `two-layer-power-layout`, `power-conductor-sizing`,
`emc-converter-input-filter`, `emc-filter-resonance`,
`two-layer-critical-routing`, `emc-source-termination`.

## 6. Review interfaces, connectors and enclosure

USB, SPI, I2C, CAN, RS-485 and Ethernet do not share one set of routing rules.
Record the actual interface version, topology and endpoint requirements. Apply
impedance, skew, pull-ups and termination where required, then set and read back
the caller-selected net-class properties. Added top ground must be included in
controlled-impedance calculations. [TI signal-conditioner/interface guidance](https://www.ti.com/lit/an/slla414a/slla414a.pdf)

Provide appropriate cable return conductors and plan any shield/chassis bonds
with the enclosure. Place suitable protection at exposed ports and keep exposed
routing from coupling into protected circuitry. Give protection currents a short
intended path. Do not connect chassis, signal ground and protective earth without
system requirements. [TI SZZA009, sections 2.5.3-2.5.4](https://www.ti.com/lit/an/szza009/szza009.pdf),
[TI ESD layout guide](https://www.ti.com/lit/an/slva680a/slva680a.pdf)

Review enclosure seams, apertures, connector mating and mechanical access.
Include intended cables and enclosure in testing. Review reset/recovery and
unintended output behavior separately from whether the firmware restarts.

RAG: `two-layer-interface-review`, `two-layer-connector-boundary`,
`emc-brownout-recovery`; follow their links for each applicable interface.

## 7. Verify and retain evidence

| Stage | Evidence to retain |
| --- | --- |
| CAD review | Root connectivity, effective rules, ERC/DRC/DFM findings, filled-copper inspection and rendered layout |
| Electrical bench review | Supply/receiver/reset waveforms, startup, load transients, heating and functional results |
| Diagnostic EMI work | Noise-source locations and comparisons with cable-current and antenna measurements |
| Precompliance | Representative setup, corrections, operating modes and results against the chosen test plan |
| Formal product testing | Tested hardware/firmware revision, cables/enclosure, required emissions and immunity results, acceptance criteria and unresolved failures |

Near-field probes locate noise; their readings are not direct radiated-emissions
pass/fail measurements. Use the relevant measurement network/LISN, antenna,
detectors, bandwidths and correction factors for applicable tests. Exercise modes
that can change emissions, including switching-load and communications activity.
Precompliance does not replace formal product testing. [Tektronix troubleshooting
and precompliance guide](https://www.tek.com/en/documents/application-note/emi-pre-compliance-testing-and-troubleshooting-tektronix-emcvu)

The product plan determines which ESD, EFT/burst, surge, conducted/radiated
immunity and supply-disturbance tests apply, with what levels and performance
criteria. Record not evaluated for unperformed checks. Retest affected functions
after changes; use no universal margin or assumed immunity level.

RAG: `two-layer-emc-test-plan`, `emc-emissions-immunity-plan`.

## 8. Know when to change the stackup

Propose four layers when critical references cannot remain continuous, required
interface geometry cannot fit, or unresolved measurement results justify the
change. Compare actual fabricator constructions with close signal/reference
spacing. Preserve the user's mechanical constraints and recalculate affected
geometry. The caller chooses the layer count. Four layers still require layout
review and product tests; they are not a compliance certificate.

RAG: `two-layer-escalation`, `stackup-planning`.

## Device-specific follow-up

The workflow links additional guidance when the circuit calls for it:

| Situation | RAG guide |
| --- | --- |
| Physical requirements absent from connectivity | `layout-intent-handoff` |
| Several supply domains compete for routing space | `two-layer-power-return-budget` |
| Compact motor driver and shunt feedback | `motor-ground-grid`, `motor-current-sense-kelvin` |
| Capacitive-touch sensor interconnect | `capacitive-touch-ground-exception` |
| Sensor offset changes with heating | `precision-analog-thermal-gradients` |
| Flex connector contact-side or folding ambiguity | `touch-fpc-orientation` |
| Reusing an evaluation board for production | `two-layer-reference-design-transfer` |

These are conditional review branches. Consult the exact device documentation
before applying a keepout, ground connection or sensing topology. See the
[source review](two-layer-source-review.md) for downloads, page references and
recommendations deliberately kept out of the general rules.
