# Workbook Sheet Inventory & Module Mapping

This inventory links each worksheet in `GA Blacksville 26 June 2025 1624 UTC 01.xlsx` to the bounded-context modules from `docs/architecture.md` §3. Formula coverage counts come from the prototype extractor in `meteor_darkflight.workbook_extract` (`formula_cells` / `total_cells`).

| Worksheet | Primary Content | Mapped Modules | Formula Coverage | Notes |
|-----------|-----------------|----------------|------------------|-------|
| `particle parameters` | Fragment mass, density, drag configuration blocks and landing-site summary | `physics_core`, `sim_kernel`, `validation` | 28 / 183 | Seeds simulation parameters and reports landing offsets used by ParityGuard. |
| `Timing Altitude` | Radar return timing, altitude, and velocity catalog | `event_ingest`, `validation` | 292 / 839 | Feeds provenance for luminous end conditions; non-physics columns flagged for ingestion harness. |
| `Sound Travel` | Sonic boom/seismometer geometry calculations | (Deferred) | 29,598 / 54,646 | Out of scope per methodology §16; keep documented for future review but excluded from parity targets. |
| `Vz` | Vertical integration loop (altitude, velocity, drag state) | `physics_core`, `sim_kernel` | 103,505 / 139,587 | Core darkflight solver logic; highest formula density and top priority for graph extraction. |
| `RAOB input` | Raw radiosonde profile pasted from source | `atmos_source` | 58,300 / 61,391 | Captures original wind/thermo layers; mainly data with lookups for units. |
| `RAOB interpolated` | Height-normalised profile, interpolation helpers | `atmos_fusion`, `physics_core` | 4,800 / 5,468 | Bridges ingestion and simulation altitude grid; limited but high-value formulas. |
| `RAOB Used for Calcs` | Final blended profile consumed by solver | `atmos_fusion`, `sim_kernel` | 45,282 / 86,904 | Down-selected columns for simulation slices; dependencies across multiple atmos sheets. |
| `wind velocity` | Component wind speeds per altitude, smoothing | `atmos_fusion`, `physics_core` | 31,499 / 36,054 | Provides Vx/Vy used directly in drag equations. |
| `wind graphs` | Chart support for winds | `geospatial_export` (visual QC) | 0 / 0 | No formula cells; purely chart cache. |
| `P,T` | Pressure and temperature reference grid | `atmos_source` | 22,500 / 22,514 | Supplies density inputs; mostly formulas converting units. |
| `vertical grid` | Integration altitude step table | `physics_core`, `sim_kernel` | 22,504 / 22,522 | Establishes simulation slices and ties to RAOB interpolated sheet. |
| `lateral displacement` | Horizontal drift integration | `physics_core`, `sim_kernel` | 85,504 / 108,080 | Cross-sheet references to `RAOB Used for Calcs`; key for reproducing strewn-field offsets. |
| `displacement graphs` | Chart cache for displacement | `geospatial_export` (visual QC) | 0 / 0 | No formulas; safe to exclude from parity graph. |
| `Force graph` | Drag force per altitude | `physics_core` | 13,501 / 13,518 | Derived data for QA; cross-check against `Vz` calculations. |
| `Vmet graph` | Meteor-relative velocity smoothing | `physics_core` | 22,500 / 22,518 | Smoothed wind-relative velocity used for drift corrections. |
| `position` | Position integration (UTM) | `sim_kernel`, `geospatial_export` | 13,502 / 13,515 | Converts displacement into lat/lon outputs referenced by export pipeline. |

## Coverage Observations

- Computational sheets (`Vz`, `lateral displacement`, `wind velocity`, `RAOB Used for Calcs`) contain the majority of the 453,315 formula cells and must be prioritised for dependency graph extraction.
- Visualisation sheets (`wind graphs`, `displacement graphs`) hold no formulas and can be deprioritised for extraction effort.
- The seismometer/sonic boom sheet (`Sound Travel`) remains out of scope for Python parity (see `docs/methodology.md` §16) but is catalogued here for completeness so future contributors understand its location.
- Cross-sheet dependencies are heavily concentrated between `lateral displacement` and `RAOB Used for Calcs`, validating the shared-data contract modeled between `atmos_fusion` and `sim_kernel` in the architecture doc.

This mapping satisfies the Phase 1 requirement for a workbook inventory and will be updated as additional events or workbook revisions appear.
