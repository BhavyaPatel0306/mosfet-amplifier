# Reproducible circuit study

Two circuits are included: the actual exported KiCad baseline and a separate experimental SPICE variant. The variant is not incorporated into the KiCad schematic and is not a fully compliant replacement.

## Run

Install Python 3.11 or later, the dependencies in `requirements.txt`, and a shared ngspice library. These results used Python 3.12.14, NumPy 2.3.5, and the ngspice 44 DLL bundled with KiCad 9.0.4 on Windows. See `results/summary.json` for the recorded Python version, which is authoritative.

```sh
python -m pip install -r simulations/requirements.txt
python scripts/run_simulations.py --library /path/to/libngspice.so --output build/simulation-results
```

On Windows, the runner detects `C:/Program Files/KiCad/9.0/bin/ngspice.dll` if present. You can also specify `--library` or set `NGSPICE_LIBRARY`. Only the shared-library interface is used; a standalone ngspice executable is not required. No user settings or schematic files are changed by the runner.

The default run uses 27 C, ngspice `ps` compatibility, `reltol=1e-4`, an 80 ms transient with a 200 ns maximum time step, and a 200-point/decade AC sweep from 1 Hz to 100 MHz. It may take several minutes. Results are saved as CSV, JSON, and a simulator log. Plot generation is separate from simulation and is not needed to reproduce numeric results.

## Circuit definitions

- `netlists/baseline.cir`: exported by KiCad 9.0.4 from the committed schematic; only its model include was made relative. The saved source has AC magnitude zero. The runner records that zero-response case, then uses AC magnitude 1 to measure transfer gain. Transient input remains the saved 1 mV peak at 100 kHz.
- `netlists/candidate.cir`: experimental bias/degeneration variant. It adds a 50-ohm source resistor, moves the 2 pF load to the external output, raises R1/R6/R13 to 39 kohm, revises bias dividers, doubles Q3 width to 40 um, and adds a 4.7 kohm unbypassed source resistor at Q4. Input is 0.75 mV peak at 100 kHz.

The baseline gain-stage order is Q1 → Q2 → Q4, followed by follower Q3. This differs from the report's reference designators. Both circuits use the original NMOS model unchanged.

## Measurement definitions

AC output is `Net-_C6-Pad1_`, relative to ground, divided by the source's 1 V AC amplitude. For the candidate this includes the added source resistor. Gain and loaded/unloaded comparison are measured at 100 kHz. The upper cutoff is a 3 dB drop from that reference, interpolated in log frequency.

For the unloaded case, R10 is replaced by 1 Tohm rather than deleted, providing an effectively open DC reference for the output coupling capacitor. All capacitors are retained. Deleting R10 makes the original output float and gives invalid unloaded measurements.

DC power includes the complete supply current. Device current and overdrive are extracted from the internal BSIM transistor (`m.xqN.m0`). Overdrive here means the model's `VGS - VTH`; it is not the model's `VDSAT`. Reported DC branch currents are distinct from transient peak current.

The final 100 us window is compared with the 100 us window 20 ms earlier. THD is the root-sum-square of harmonics 2–10 divided by the fundamental, using a sinusoidal least-squares fit at 100 kHz on a uniformly interpolated trace. This finite-window estimate is not a laboratory distortion measurement or a formal timestep-convergence proof.

## Evidence and limits

Read [the measured results](../docs/VERIFICATION.md). These are fresh simulator runs, but not a claim that every assignment requirement is met. In particular, do not call the experimental waveform distortion-free. Component/process corners, temperature sweeps, GUI/ERC verification, and fabrication checks are outside this release.

The exact netlist, schematic, model, and runner hashes are recorded in `results/summary.json`. Raw data and commands are retained in `results/`. The GitHub Actions workflow checks package integrity and documentation; it does not run ngspice or certify electrical performance.

## References

- [KiCad command-line export documentation](https://docs.kicad.org/9.0/en/cli/cli.html)
- [ngspice shared-library interface](https://ngspice.sourceforge.io/shared.html)

## Regenerate plots

Install `reportlab==4.4.9` and run `python scripts/plot_results.py`. This renders the saved CSV data; it does not rerun ngspice. The simulator logs a missing `spinit` warning in this environment; the runner explicitly sets compatibility and numerical options, and no convergence errors were reported in the saved final run.
