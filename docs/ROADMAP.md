# Engineering roadmap

## 1. Establish a reproducible baseline

Fresh runs, exact netlists, raw data, and a runner are now included in v0.2.0. The remaining task is full requirement coverage and model/operating-condition validation.

- Reconcile source settings and sweep range with the original report.
- Run DC, loaded and unloaded AC, and transient analyses with recorded versions and raw data.
- Map each assignment requirement to a measurement definition and result.

Completion means another reader can reproduce measurements from the committed circuit and recorded commands.

## 2. Investigate output swing

A separate variant now demonstrates 1.568 Vpp at 4.00% THD and 0.9201 mW DC power. Resolve its low gain-stage overdrive and transient current before promoting it to the KiCad project.

- Measure headroom, device currents, and clipping onset over input amplitude.
- Define a distortion criterion for acceptable swing.
- Evaluate bias changes and alternative output stages against the 1 mW power and 200 uA branch-current limits.

Completion means demonstrating at least 1.5 Vpp under the specified load and distortion criterion without violating another requirement.

## 3. Test robustness

- Sweep supply and temperature over explicitly selected ranges.
- Explore component and model variation where supported.
- Measure sensitivity to load resistance and capacitance.

Completion means documented sensitivity results and clearly identified supported conditions.

## 4. Consider physical implementation

The PCB is a placeholder. Physical implementation requires a separate technology and component plan, suitable models, layout, and validation. The supplied process-model simulation is not a ready-to-build discrete circuit.
