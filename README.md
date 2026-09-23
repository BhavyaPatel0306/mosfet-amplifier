# MOSFET Amplifier Design

An ELE404 Electronics I project: a 3.3 V, four-stage MOSFET voltage amplifier designed in KiCad 9. The original report describes three common-source gain stages followed by a common-drain output buffer.

## Open the project

1. Extract this entire archive to a folder.
2. Open `hardware/ELE404Project.kicad_pro` in KiCad 9 or a compatible later version, then open its schematic.
3. Transistor model files are included in `hardware/models/`. All four schematic model references now use `models/nmos_t.txt`, relative to the project directory.
4. The saved simulator workbook is `hardware/ELE404Project.wbk` and contains AC, transient, and operating-point setups.

## Files

- `hardware/`: schematic, project, saved simulator workbook, and original PCB placeholder.
- `hardware/models/`: original NMOS and PMOS model contents. The schematic uses NMOS; PMOS is supplied for completeness.
- `docs/project-report.pdf`: unchanged original ten-page report.
- `docs/design-guidelines.pdf`: unchanged original three-page assignment guidelines.
- `originals/MOSFET AMPLIFIER DESIGN.zip`: exact original upload, including its backups and local settings.
- `RECOVERY.md`: packaging changes and verification scope.
- `SHA256SUMS.txt`: file checksums, excluding this checksum file itself.

## Performance status

No simulations were run as part of this recovery. The following values are reported in the original PDF and have not been independently reproduced: 63.8 dB loaded gain, 64.6 dB unloaded gain, approximately 20 MHz bandwidth, and 0.828 mW DC power.

The report records approximately 1.33 Vpp output swing, below the specified 1.5 Vpp minimum. Do not describe this project as meeting all requirements.

The report's 1.54% load-sensitivity figure is not a linear voltage-gain reduction. From the rounded reported gains, the reduction is `100 * (1 - 10 ** ((63.8 - 64.6) / 20))`, approximately 8.80%. This is arithmetic on reported values, not a new simulation result.

## Before rerunning simulations

The saved schematic input source V2 has `Sim.Params` set to `ac=0`. Configure an appropriate nonzero small-signal AC magnitude for AC analysis. The saved workbook sweep ends at 10 MHz, so it cannot establish the report's claimed 20 MHz bandwidth; extend the sweep when checking that claim. Check the source waveform and amplitude before transient analysis. These original settings were preserved to avoid silently changing the design.

The PCB file is a minimal placeholder, not a completed board layout. This package has been checked for archive integrity and file preservation, not electrical correctness or simulator execution.

## Attribution

Original project, report, assignment, and model files are preserved from the supplied attachments. No new license or ownership claim is assigned to those materials.

