# Reproducing the analysis

This is a procedure for a future verification run, not a record of simulations completed during repository preparation.

## Open and inspect

1. Use KiCad 9, the version recorded in the schematic header. Other versions have not been tested here.
2. Open `hardware/ELE404Project.kicad_pro`, then its schematic.
3. Confirm the transistor library resolves to `hardware/models/nmos_t.txt` and the selected subcircuit is `nmos_3p3`.
4. Open the simulator and load `hardware/ELE404Project.wbk` if needed. It contains operating-point, AC, and transient setups.
5. Save experiments in a separate working copy or branch. Record KiCad and ngspice versions with the results.

## Known differences

The report and supplied project are not demonstrably the same simulation revision:

- The saved source is V2 with value `SINE(0 1m 100k)` and `Sim.Params` of `ac=0`. The report schematic shows V5, 1.45 mV peak at 100 kHz, and `ac=1`.
- The saved AC sweep is `.ac dec 100 1 10Meg`. The report describes 1 kHz to 100 MHz. A 10 MHz endpoint cannot establish a 20 MHz upper cutoff.
- The saved transient setup is `.tran 50n 100u 0 50n`. Confirm settling before measuring; extend the run if coupling or bypass capacitor startup is still visible.
- Saved traces refer to auto-generated node names. Check that each still maps to the intended input, interstage, or output node.

Reconcile these differences explicitly before claiming the report is reproduced. Original circuit settings have been preserved.

## DC operating point

Run `.op`. Record gate, drain, source, and bulk voltages, branch currents, and supply current. Check operating regions using actual model operating-point data where available. Calculate total power from supply voltage and current, accounting for the simulator's sign convention and including divider currents.

Compare against the guideline limits: 3.3 V supply, at most 1 mW total DC power, and at most 200 uA per branch.

## AC gain and bandwidth

Configure a nonzero small-signal AC magnitude, such as 1 V, in the source model editor. This AC normalization is separate from the small transient input amplitude.

Sweep beyond the expected cutoff; the report used 1 kHz to 100 MHz. Measure `V(out)/V(in)` and specify where input voltage is measured relative to the 50-ohm source resistor. Keep that definition consistent.

Find midband gain and the upper frequency where gain has dropped 3 dB from midband. Do not confuse this with an absolute gain of -3 dB. Extend the lower sweep when assessing the coupling-capacitor cutoff.

## Load sensitivity

Save separate loaded and unloaded configurations. State exactly which load elements change; the specified load is 10 kohm in parallel with 2 pF. Hold source settings, bias, and measurement frequency constant.

```text
gain reduction (%) = 100 × (1 − |A_loaded| / |A_unloaded|)
                   = 100 × (1 − 10^((G_loaded_dB − G_unloaded_dB)/20))
```

Do not calculate voltage-gain sensitivity by dividing a difference in dB by a dB value.

## Transient output swing

Start with a small sinusoid and sweep amplitude while staying within the 10 mVpp input limit. The report used 1.45 mV peak, or 2.9 mVpp, at 100 kHz.

After settling, inspect input and output, record output extrema, and check for flattened peaks or asymmetric clipping. Define a distortion criterion before calling the swing clean. A peak-to-peak measurement alone does not establish linear operation.

## Save reproducible evidence

Retain circuit revision, source settings, commands, simulator versions, load configuration, measurement definitions, raw exported data, and plots. Report failures and discrepancies alongside successful measurements.

See [RESULTS.md](RESULTS.md) for historical values and [ROADMAP.md](ROADMAP.md) for next steps.
