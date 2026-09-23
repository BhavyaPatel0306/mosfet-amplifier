# Changelog

## 0.2.0

- Export the actual committed KiCad schematic and a portable baseline SPICE netlist.
- Add fresh DC, AC, loaded/unloaded, and long-transient ngspice results with raw CSV data, logs, model/device measurements, and source hashes.
- Add a separate experimental bias/degeneration variant; document both its improvements and remaining failures.
- Add reproducible simulation and release-building scripts.
- Add GitHub Actions checks for hashes, documentation links, result metadata, and release packaging.
- Preserve all original design and source materials.

This release establishes reproducible evidence, not full design compliance. The original circuit exceeds the DC power limit and clips. The variant improves power and distortion but still has overdrive and transient-current limitations.
