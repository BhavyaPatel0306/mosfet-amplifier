# Contributing

Improvements to reproducibility, documentation, and the amplifier design are welcome.

For a simulation discrepancy, include KiCad/ngspice versions, circuit revision, source and load settings, analysis command, expected result, and observed result. Attach exported data or a readable plot.

For a design change, explain the trade-off and its effect on gain, bandwidth, output swing, power, and branch currents. Keep historical report values separate from new measurements.

Preserve original PDFs, model files, and the archive. Work on a separate branch and submit focused changes. Update documentation and run `python scripts/update_manifest.py` to regenerate `SHA256SUMS.txt` when distributed files change. The manifest covers all distributed files except itself.

Run `python scripts/verify_package.py` to check package integrity. A successful package check is not a simulation pass.
