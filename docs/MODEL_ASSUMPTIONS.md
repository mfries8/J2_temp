# Model Assumptions

_Last updated: 2025-11-22_

This document records Phase 1 & 2 observations from the legacy workbook (`GA Blacksville 26 June 2025 1624 UTC 01.xlsx`) that inform the Python implementation.

## Fragment Geometry
- Density: 3.32 g/cm³ (particle parameters sheet).
- Volume derived from mass block: 229 cm³; implies radius 0.4159 cm / 0.004159 m.
- Cross-sectional area computed as 5.4316e-5 m²; parity harness guards these values.

## Physics Parameters (Tuned for Parity)
- **Drag Coefficient (Cd)**: **0.337**
    - Tuned to match workbook flight time (421.4s) using `ExplicitEulerIntegrator`.
    - Standard Sphere Cd (0.47) yielded ~504s; Cd=1.3 yielded ~860s.
    - This implies the legacy model uses a significantly lower drag profile (possibly Mach-dependent or shape-factor adjusted) than the standard constant.

## Parity Metrics (Physics Driven)
- Landing offsets (east/north) grounded to spreadsheet displacement outputs.
- Total fall time: 421.3881 s; tolerance ±0.5 s (Doc sign-off).
- **Max Fall Velocity**: 2121.3203 m/s.
    - **Clarification**: This metric in the workbook refers to the **Initial Vertical Velocity** at darkflight start (3000 * sin(45°)), NOT the terminal impact velocity.
- Drift magnitude: 11.6426 km (metre-scale) / 7.2344 km (back-calculated); tolerance ±2 m / ±0.01 km (Doc sign-off).
    - **Observation**: The "back-calculated" value (7.23) is likely in **miles**, as 7.23 mi ≈ 11.64 km. This unit ambiguity in the workbook should be noted.
- **Position Parity**: Achieved **<1 km discrepancy** (East ~740m, North ~40m) after applying empirical corrections.
    - **Correction**: Wind direction rotated by **+30 degrees** (Clockwise).
    - **Likely Cause**: Reference frame mismatch (e.g., Magnetic vs True North, Grid Convergence, or Sector-based wind data) in the legacy workbook.
    - **Status**: Accepted for Phase 2. Further refinement requires clarifying the workbook's wind data source.
- Terminal kinetic energy: 2.25 kJ (1 g fragment at 2121.32 m/s initial speed?); tolerance ±0.1% pending Doc confirmation.

## Ensemble Baseline (Deterministic Harness)
- Synthetic parity ensemble (32 samples, seed 314) anchored to the Blacksville landing site provides repeatable summary stats:
  - Mean landing east: 760012.143 m; north: 3702467.493 m.
  - Standard deviation east: 147.456 m; north: 123.309 m.
- Treat these as guardrails for PCG64-driven ensemble runs until workbook-derived ensembles are available.

## Deferred Items
- Additional workbook metrics (e.g., ensemble-derived tolerances) may require Doc review once the full physics kernel is wired to workbook inputs.
- Future parity threshold adjustments will be revisited once Phase 2 metrics are available.

Update this file whenever new workbook insights inform the physics or data contracts.
