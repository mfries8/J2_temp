# Darkflight Strewn Field Methodology (Blacksville, GA Example)

> NOTE: This documentation reverse-engineers the provided Excel workbook ("GA Blacksville 26 June 2025 1624 UTC 01.xlsx"). All sonic boom related sheets / calculations are intentionally excluded. Where exact cell formulas were not yet programmatically extracted, placeholders identify intended extraction targets.

## Table of Contents
1. Overview
2. Data Inputs
3. Coordinate & Reference Frames
4. Phase Segmentation (Luminous -> Darkflight)
5. Initial Conditions Computation
6. Atmospheric & Wind Model Integration
7. Deceleration & Drag Modeling
8. Ablation & Mass Loss Modeling
9. Trajectory Integration Loop
10. Wind Drift & Lateral Dispersion
11. Fragmentation Handling (if present)
12. Ground Intersection & Impact Metrics
13. Strewn Field Construction
14. Uncertainty Propagation (Monte Carlo)
15. Validation Checks
16. Assumptions & Exclusions
17. Error Sources & Mitigations
18. Future Improvements

---
## 1. Overview
The spreadsheet models the darkflight descent of meteorite fragments after luminous ablation largely ceases. It converts initial event parameters (velocity vector, altitude, mass estimations) plus atmospheric wind profiles into predicted impact points. The final output is a strewn field: a set of points (and often an elliptical dispersion shape) representing probable landing locations for different fragment masses.

Core modeling chain:
Event Inputs -> Derive Fragment Physical Properties -> Atmospheric Profile Interpolation -> Time-stepping Integration (drag + gravity + ablation) -> Wind Drift Accumulation -> Ground Intersection -> Aggregation into Strewn Field Products -> Uncertainty Analysis.

---
## 2. Data Inputs
| Category | Description | Symbol | Units |
|----------|-------------|--------|-------|
| Event Time | UTC timestamp of luminous end or fragmentation | t0 | s (epoch) |
| Latitude / Longitude | Geodetic coordinates of endpoint used as start of darkflight | lat0, lon0 | deg |
| Altitude | Starting altitude above mean sea level | h0 | m |
| Velocity Magnitude | Speed at darkflight start | v0 | m/s |
| Velocity Azimuth | Bearing (clockwise from North) | ψ0 | deg |
| Velocity Elevation | Angle above horizon | θ0 | deg |
| Fragment Mass (or mass classes) | Initial mass per fragment class | m0 | kg |
| Bulk Density | Material density | ρ_b | kg/m^3 |
| Shape Factor / Drag Coefficient Inputs | Empirical factor mapping | C_d, A_ref | dimensionless, m^2 |
| Atmospheric Profile | Layered wind (u,v), density, temperature, pressure vs altitude | profile(z) | varied |
| Gravity Model | Local gravitational acceleration | g | m/s^2 |

Placeholder (Excel range references to be extracted): `[[RANGE_EVENT_INPUTS]]`.

---
## 3. Coordinate & Reference Frames
The model typically transforms geodetic (lat, lon, altitude) and initial velocity vector into a local tangent plane (ENU: East, North, Up) for integration.

Conversion from speed + azimuth + elevation:
Let speed v0, azimuth ψ (from North, clockwise), elevation θ.
East component: v_E = v0 * sin(ψ)
North component: v_N = v0 * cos(ψ)
Up component: v_U = v0 * sin(θ)
Forward horizontal magnitude: v_H = v0 * cos(θ)

Local Cartesian initial state vector:
X0 = (x=0, y=0, z=h0) with z positive upward.
V0 = (v_E, v_N, v_U).

Geographic projection for final points: After termination, displacements Δx (east), Δy (north) converted back:
lat = lat0 + (Δy / R_earth) * (180/π)
lon = lon0 + (Δx / (R_earth * cos(lat0))) * (180/π)

---
## 4. Phase Segmentation (Luminous -> Darkflight)
The workbook demarcates the end of significant ablation/brightness (end of luminous flight) and begins darkflight integration from altitude h0 with velocity v0. Any transonic / sonic boom analysis sections are ignored here.

Criterion (typical, placeholder):
Darkflight start when Mach number M < M_threshold_lum (~2–3) OR luminous intensity proxy < threshold.
Placeholder formula: `[[CELL_MACH_THRESHOLD]]`.

---
## 5. Initial Conditions Computation
Inputs: (h0, v0, ψ0, θ0, m0, ρ_b, shape parameters)
Derived quantities:
- Fragment radius (assuming sphere): r = (3 m0 / (4 π ρ_b))^(1/3)
- Cross-sectional area: A = π r^2
- Ballistic coefficient: β = m0 / (C_d A)
- Reference area to mass ratio: A/m0 = A / m0

If shape_factor S modifies drag: C_d = C_d_base * S.

---
## 6. Atmospheric & Wind Model Integration
Atmospheric profile provides discrete altitude levels z_i with density ρ_i, temperature T_i, pressure P_i, horizontal wind components (u_i, v_i).
Interpolation for current altitude z:
For any scalar q (e.g., density ρ): q(z) = LinearInterp(z; z_i, q_i) or log-linear for density/pressure.
Wind vector at z: W(z) = (u(z), v(z)). Vertical wind w usually neglected or assumed 0.
Air-relative velocity: V_rel = V - W.

Air density model (if pressure & temp given): ρ = P / (R_specific * T).
Placeholder cell references: `[[RANGE_ATMOS_PROFILE]]`.

---
## 7. Deceleration & Drag Modeling
Drag force magnitude:
F_D = (1/2) * ρ * C_d * A * |V_rel|^2.
Acceleration due to drag (vector): a_D = - (F_D / m) * (V_rel / |V_rel|).
Gravity acceleration: a_g = (0, 0, -g).
Total acceleration (without ablation mass change): a = a_g + a_D.
Update velocity (simplified Euler step): V_{t+Δt} = V_t + a * Δt.

More accurate integration in spreadsheet may use piecewise small Δt and repeated recalculation (placeholder: `[[LOOP_DRAG_CELLS]]`).

---
## 8. Ablation & Mass Loss Modeling
If ablation continues into darkflight (often minimal):
Mass loss rate (classical single body approximation): dm/dt = -σ * A * ρ * |V_rel|^3 / (2 Q^*)
Simplified workbook variant often: dm/dt = -k_ab * ρ * |V_rel|^3.
Updated mass: m_{t+Δt} = m_t + (dm/dt) Δt.
Recompute r, A, β each step when mass changes.
Placeholder references: `[[CELL_ABLATION_COEFF]]`.

If ablation considered negligible in given altitude regime: set dm/dt ≈ 0.

---
## 9. Trajectory Integration Loop
Initialization: state S0 = (x=0, y=0, z=h0, V0, m0).
Loop while z > 0 and iteration < N_max and |V| > V_min:
1. Interpolate atmosphere at current z.
2. Compute V_rel, drag, gravity.
3. Update mass if ablation active.
4. Integrate velocity & position:
   - V_{n+1} = V_n + a_n Δt
   - X_{n+1} = X_n + V_{n+1} Δt (semi-implicit) or X_n + V_n Δt + 0.5 a_n Δt^2
5. Accumulate wind drift via difference between ground track and air-relative path.
6. Store state (time, position, velocity, mass).
7. Adaptive Δt (optional): Δt_new = clamp( Δt * sqrt(v_ref / |V|), Δt_min, Δt_max ).
Placeholder loop cell block: `[[RANGE_INTEGRATION_LOOP]]`.

---
## 10. Wind Drift & Lateral Dispersion
Horizontal displacement primarily from integration of horizontal velocity components which include wind influence. Because V_rel = V - W, the ground track velocity is V_ground = V_rel + W = V.
Lateral dispersion across fragment masses arises from differing ballistic coefficients β causing varied time aloft (longer flight -> more wind drift).
Approx analytic drift for constant wind: Δx ≈ W_x * t_fall, Δy ≈ W_y * t_fall.

---
## 11. Fragmentation Handling (if present)
If the workbook includes fragmentation events (mass splits at altitude z_f):
- At event: Partition mass m into m_i (i=1..k), conserve momentum approximately.
- In sheet: new fragment rows/columns replicate integration with adjusted radii and β_i.
Formulas placeholder: `[[RANGE_FRAGMENT_EVENTS]]`.
If no fragmentation data for event: skip this step.

---
## 12. Ground Intersection & Impact Metrics
Condition: Detect first index where z_{n+1} <= 0. Interpolate touchdown time t_touch for higher precision:
Δ = z_n / (z_n - z_{n+1}); t_touch = t_n + Δ Δt; X_touch = X_n + Δ (X_{n+1} - X_n).
Impact speed: v_imp = |V_touch|.
Impact kinetic energy: E_imp = 0.5 m_touch v_imp^2.
Store (lat, lon) converted from (Δx, Δy).
Placeholder: `[[CELL_GROUND_INTERSECT]]`.

---
## 13. Strewn Field Construction
Aggregate all fragment landing points into dataset.
Optional ellipse fit: Use covariance of (Δx, Δy) across fragments (or Monte Carlo points) to derive principal axes (eigenvectors, eigenvalues) → ellipse parameters.
Ellipse major/minor axes: a = sqrt(λ_max), b = sqrt(λ_min) (scaled by desired confidence multiplier κ for chosen probability level assuming approximate bivariate normal dispersion).

---
## 14. Uncertainty Propagation (Monte Carlo)
Parameters sampled: mass m0, C_d, density ρ_b, wind components W(z), initial velocity vector components.
Sampling approach: Latin Hypercube or simple random draws N runs.
For each run j: perform integration → landing point (x_j, y_j).
Uncertainty radius for point estimate: r_conf ≈ sqrt( χ^2_{2,α} * λ_avg ).
Placeholder: `[[RANGE_UNCERTAINTY_SECTION]]`.

---
## 15. Validation Checks
Suggested spreadsheet checks:
- Mass non-negative: m >= 0.
- Monotonic altitude descent after darkflight onset.
- Energy consistency: detect unrealistic kinetic energy increases.
- Drag coefficient bounds: C_d_min <= C_d <= C_d_max.
- Reasonable terminal velocity convergence (dv/dt near zero near ground).
Placeholder cells: `[[RANGE_VALIDATION_FLAGS]]`.

---
## 16. Assumptions & Exclusions
Included physics:
- Standard gravity constant g (no latitude variation in sheet, assumed).
- Constant or smoothly varying C_d (speed/Regime variation simplified).
- Linear or log-linear interpolation of atmospheric properties.
Excluded / simplified:
- Sonic boom analysis (explicitly ignored per requirement).
- Complex turbulence / gust modeling (average winds only).
- Vertical wind components (w ≈ 0) unless explicitly provided.
- Non-spherical fragment shapes beyond simple shape factor.
- Coriolis force (negligible for descent duration & scale).

---
## 17. Error Sources & Mitigations
| Source | Effect | Mitigation |
|--------|--------|-----------|
| Wind profile temporal mismatch | Horizontal position bias | Use time-interpolated winds, cross-check radar & model data |
| Density / C_d uncertainty | Landing range error | Monte Carlo sampling, sensitivity ranking |
| Fragment mass estimate error | Over/under dispersion | Provide mass class range rather than single value |
| Numerical step size too large | Integration instability | Adaptive Δt, convergence test |
| Simplified ablation model | Overestimated mass at ground | Use improved heat transfer coefficient if data available |
| Ignored vertical winds | Slight altitude/time error | Bound analysis with ±w sensitivity runs |

---
## 18. Future Improvements
- Introduce variable drag regime (Mach-dependent C_d curve) transitioning through transonic region.
- Incorporate high-resolution mesoscale model winds with shear layers.
- Add DEM-based ground elevation for more precise intersection altitudes.
- Calibrate β using recovered fragment finds.
- Probabilistic ellipse computation with kernel density estimation instead of Gaussian assumption.

---
## 20. Revised Workflow (Radar-Centric)
The simulation follows a two-phase process centered on Weather Radar signatures, replacing the simple "Terminus -> Ground" forward integration.

### Phase 1: Terminus to Radar (Mass Finding)
**Goal**: Determine the fragment mass that would traverse from the Fireball Terminus to the observed Weather Radar Signature in the observed time ($\Delta t_{obs}$).

1.  **Inputs**:
    *   **Terminus**: Altitude ($h_{term}$), Time ($t_{term}$).
    *   **Radar Signature**: Altitude ($h_{radar}$), Time ($t_{radar}$), Centroid ($x_{radar}, y_{radar}$).
    *   **Observed Duration**: $\Delta t_{obs} = t_{radar} - t_{term}$.
2.  **Process**:
    *   Run a forward simulation from $h_{term}$ to $h_{radar}$.
    *   Iteratively adjust the **Fragment Mass** ($m$) until the simulated flight time matches $\Delta t_{obs}$.
    *   **Solver/Optimization**: Use a root-finding algorithm (e.g., Bisection or Newton-Raphson) to minimize $|t_{sim}(m) - \Delta t_{obs}|$.

### Phase 2: Radar to Ground (Forward Integration)
**Goal**: Calculate the impact point of the mass determined in Phase 1.

1.  **Inputs**:
    *   **Mass**: $m_{found}$ (from Phase 1).
    *   **Start State**: Radar Signature location ($x_{radar}, y_{radar}, h_{radar}$) and velocity (from Phase 1 end state).
2.  **Process**:
    *   Run forward simulation from $h_{radar}$ to Ground ($h=0$).
    *   **Output**: Impact coordinates ($Lat_{impact}, Lon_{impact}$).

### Phase 3: Strewn Field Generation (Reverse Integration)
**Goal**: Estimate the "True Terminus" and generate the full strewn field.

1.  **Back Calculation**:
    *   For each radar signature, perform a **Reverse Integration** (negative time step) from the Radar state ($x_{radar}, y_{radar}, h_{radar}$) back to the Terminus altitude ($h_{term}$).
    *   This yields a "Calculated Terminus" ($x_{term\_i}, y_{term\_i}$) for each signature.
2.  **Centroid**:
    *   Calculate the centroid of all "Calculated Terminus" points: ($X_{cent}, Y_{cent}$).
    *   This ($X_{cent}, Y_{cent}, h_{term}$) becomes the **Simulated Terminus**.
3.  **Forward Generation**:
    *   From the **Simulated Terminus**, simulate the descent of a decadal suite of masses (e.g., 1g, 10g, 100g, 1kg, 10kg).
    *   The resulting impact points define the **Calculated Strewn Field**.

---
## 19. Legacy Reference: Fries Jörmungandr v2 Outline
The reference worksheet authored by Dr. M. D. Fries (`docs/reference/Fries Jormungandr LPSC 2023.pdf`) documents the legacy Excel implementation that this project must reproduce. Key takeaways:

- **Slice-by-slice RAOB integration**: Each radiosonde altitude slice tracks top (`i`) and bottom (`f`) state values with the lower slice inheriting the previous `f` as its new `i`. Vertical (`z`) motion is handled independently from horizontal drift, matching the staged interpolation described in §§6–10.
- **Seven-step solution order**: Within every slice the workbook solves (1) total path length and horizontal leg `j`, (2) velocity components along the path, (3) X/Y velocity decomposition, (4) wind vector decomposition, (5) effective wind relative to the fragment, (6) drag force along the full path before resolving into axes to avoid regime misclassification, and (7) position updates that seed the next slice. These steps align with placeholders `[[LOOP_DRAG_CELLS]]`, `[[RANGE_INTEGRATION_LOOP]]`, and `[[RANGE_ATMOS_PROFILE]]`.
- **Default startup assumptions**: When observations are incomplete the Excel model assumes a 40° declination from the horizontal and ~3,000 m/s luminous-end speed; azimuth is derived from eyewitness tracks. These defaults should inform template values in `event.json` and parity fixtures until real measurements are available.
- **Wind-dominated footprint**: The paper emphasises that crosswinds produce banana-shaped strewn fields, reinforcing the requirement that our wind fusion (§6) and drift accumulation (§10) preserve the legacy handling of horizontal shear.

Documenting these notes here keeps the methodology synchronized with the authoritative legacy description and provides a traceable target while we replace the spreadsheet formulas with extracted equivalents.

---
## Placeholder Extraction TODOs
The following placeholders correspond to Excel range/cell sets pending automated extraction:
- `[[RANGE_EVENT_INPUTS]]`
- `[[CELL_MACH_THRESHOLD]]`
- `[[RANGE_ATMOS_PROFILE]]`
- `[[LOOP_DRAG_CELLS]]`
- `[[CELL_ABLATION_COEFF]]`
- `[[RANGE_INTEGRATION_LOOP]]`
- `[[RANGE_FRAGMENT_EVENTS]]`
- `[[CELL_GROUND_INTERSECT]]`
- `[[RANGE_UNCERTAINTY_SECTION]]`
- `[[RANGE_VALIDATION_FLAGS]]`

These will later map to formula graph nodes and then Python module references.

---
