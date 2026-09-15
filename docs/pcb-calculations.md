# PCB materials, calculations and grounding

The maintained corpus now includes material construction/loss, a bounded
microstrip approximation, calculation records, ground-loop review and shared
return impedance. Existing impedance and mixed-signal guides link to these.

| Question | Entry ID |
| --- | --- |
| Which dielectric constant applies? | `pcb-material-construction` |
| What about dielectric loss? | `pcb-material-loss` |
| How is the approximate microstrip calculation defined? | `microstrip-width-estimate` |
| Which width calculation is needed? | `trace-width-calculation-record` |
| Are multiple system ground paths a problem? | `ground-loop-review` |
| Is load current disturbing a reference? | `shared-return-impedance` |

## Calculation evidence

RAG retrieves methods and assumptions; it does not replace numerical execution.
`examples/scripts/pcb_calculation_example.py` independently executes the cited
TI approximation and checks its source example, unit conversion and inverse
arithmetic. It is an educational example, not an MCP tool or field solver.

With er=4, h=0.254 mm and t=0.03556 mm, inverse evaluation for 50 ohms gives
w=0.4543 mm (rounded). The source's w=0.508 mm geometry evaluates to 46.177 ohms.
These numbers describe that approximation only. They do not select a width for
a user's board or account for soldermask and manufacturing variation.

For an actual result, record source/model/version, named inputs and units,
geometry type, omitted effects, validity range, output units and tolerances.
Verify using the fabrication-approved model and construction. Evaluate current,
voltage drop, thermal rise and vias separately. No thermal or impedance
qualification is inferred from passing arithmetic checks.

## Sources and parsing review

- [TI SPRABV0](https://www.ti.com/lit/an/sprabv0/sprabv0.pdf), Appendix B,
  pages 117–118: equation page visually reviewed; source example independently
  evaluated. The approximation's scope is retained in the guide.
- [Isola FR408HR Revision D](https://www.isola-group.com/wp-content/uploads/data-sheets/FR408HR__Dk_Df_Tables.pdf),
  October 25, 2019: page 1 visually reviewed. Frequency cells contain both Dk and
  Df. An alternate publisher file named `FR408HR_Dk_Df_Construction_Table__Dk_Df_Tables.pdf`
  rendered with missing table bodies and was not used for numeric evidence.
- [ADI MT-031](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf):
  current-path reasoning and multicard grounding. Ground-loop diagnosis does not
  imply blanket ground-plane splitting.
- The versioned KiCad calculator source already in the catalogue distinguishes
  transmission-line, conductor-heating and via calculations. Its documented
  algorithm must not be attributed to every later software version.

The new TI and Isola sources were captured, hashed and passed through Markdown
conversion. Visual notes are tied to those hashes. Machine extraction is still
not complete engineering review of every page.

## Measured checks

Corpus 2026-09-15.2 contains 113 guides and 52 sources. All 167 keyword fixture
cases pass in both MCP modes. Hybrid passes 153/167; it still returns neighbors
for the 14 expected-empty cases. Hybrid retrieves all 12 paraphrases; reranking
retrieves 11/12. Semantic-only retrieval passes 149/167. These are retrieval and
arithmetic checks, not engineering sign-off or demonstrated PCB improvements.
