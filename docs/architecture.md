# Architecture: Modular Python Darkflight & Strewn Field System

> Goal: Eliminate per‑event Excel duplication by providing a reproducible, testable, modular Python platform that ingests event & atmospheric/radar data and outputs validated strewn field products (GeoJSON & KML/KMZ for Google Earth) with full provenance.

## Table of Contents
1. Scope & Objectives
2. High-Level System Overview
3. Bounded Context Modules
4. Required Inputs & Schemas
5. Processing Pipeline & Data Flow
6. Data Contracts & Storage Layout
7. Google Earth & Geospatial Outputs
8. Core Physics & Simulation Engine
9. Uncertainty & Ensemble Framework
10. Orchestration & Caching Strategy
11. Extensibility & Plugin Interfaces
12. Testing & Quality Strategy
13. Logging, Monitoring & Provenance
14. AI SDLC & Automation Hooks
15. Non-Functional Requirements
16. Deployment & Runtime Modes
17. Future Extensions
18. Appendix (Sample Config)

---
## 1. Scope & Objectives
Replace ad‑hoc Excel workflow with a deterministic pipeline featuring:
- Modular, independently testable components (each with clear input/output contract).
- Strict schema validation & unit metadata.
- Reproducible runs (hash-based caching & provenance graph).
- Seamless generation of Google Earth artifacts (KML/KMZ) and GeoJSON.
- Extensible physics core allowing incremental sophistication (drag regimes, fragmentation, ablation improvements).
- AI-assisted code lifecycle (agent roles from `AGENTS.md` mapped to modules for automated reviews & documentation).

Success Criteria:
- Numerical parity with legacy Excel within defined tolerances (see methodology doc) across benchmark scenarios.
- New event integration end-to-end < 5 minutes manual overhead (provide CLI/API).
- All public functions type-annotated & documented; 80%+ coverage; physics core 100% critical path coverage.
- Google Earth KML loads with styled points, ellipses, time stamps, clickable metadata, and provenance link.

Out of Scope (initial release):
- Real-time streaming radar ingestion.
- Full 3D CFD modeling & complex turbulence.
- Automated ML calibration (deferred to later phase).
- Sonic boom / seismometer analysis (legacy workbook `Sound Travel` sheet documented but not implemented).

## 2. High-Level System Overview
A staged pipeline transforms raw event + environmental data into geospatial visualization products. Each stage consumes validated artifacts and emits immutable outputs with checksums. The orchestration layer decides incremental rebuilds based on content hashes.

Simplified flow:
Event Input -> Data Ingestion -> (Optional) Excel Reverse Extraction -> Physics Core Compilation -> Atmospheric Fusion -> Simulation Ensemble -> Uncertainty Post-Processing -> Validation & Parity -> Geospatial Export -> Publication (KML/GeoJSON + Provenance).

## 3. Bounded Context Modules

### 3.1 Quick Reference

| # | Module / Agent | Core Responsibility | Primary Outputs | Escalation Path |
|---|----------------|---------------------|-----------------|-----------------|
| 1 | **Ingestor** (`event_ingest`, `atmos_source`) | Normalize raw event, radar, and atmosphere data | `event.json`, `atmos_profile.json`, `radar_slices/` | Raise data-quality issue; notify AtmoFusion when gaps remain |
| 2 | **FormulaGraph** (`workbook_extract`) | Extract Excel formulas into machine-readable graph | `formula_graph.json`, `graph_issues.md` | Flag unresolved Excel constructs to domain reviewer |
| 3 | **PhysicsSynth** (`physics_core`) | Derive physics modules from formula graph | `physics_core/drag.py`, `physics_core/trajectory.py`, `MODEL_ASSUMPTIONS.md` | Tag physics reviewer; document assumptions |
| 4 | **AtmoFusion** (`atmos_fusion`) | Merge atmospheric sources + radar winds | `wind_profile_compiled.json`, `vertical_grid.json` | Return to Ingestor for missing layers; log QC annotations |
| 5 | **DarkflightSim** (`sim_kernel`, `ensemble_driver`) | Integrate trajectories / ensembles | `trajectories/*.json`, `strewn_field_points.geojson`, stats | Escalate instability to PhysicsSynth; preserve failing seeds |
| 6 | **ParityGuard** (`validation`) | Validate outputs against goldens & tolerances | `validation_report.md` (Doc-reviewed: ±1 m offsets, ±0.5 s fall time, ±1 m/s terminal velocity, ±2 m / ±0.01 km drift; guardrails: density ±0.01 g/cm^3, volume ±0.5 cm^3, radius ±1e-4 cm / ±1e-6 m, cross-section ±1e-8 m^2, mph conversion ±0.5) | Block release; require reviewer sign-off for physics tolerances |
| 7 | **OptimusUQ** (`uncertainty_post`) | Optimisation & uncertainty quantification | `calibrated_params.json`, `uncertainty_ellipses.geojson` | Defer updates when evidence insufficient; note limitations |
| 8 | **Coordinator** (`provenance`, orchestration layer) | Orchestrate pipeline & provenance logging | `provenance_graph.json`, run manifest | Escalate on repeated cache divergence or dependency failure |
| 9 | **DocSmith** (`docs/`) | Keep documentation current | Updated README/docs | Require documentation updates before merges |
|10 | **DevTools** (`tooling/ci`) | Maintain lint/type/test hygiene | Tooling configs, fixtures | Quarantine flaky tooling; update parking lot |

### 3.2 Module Responsibilities

#### Ingestor (Data Ingestion & Normalization)
- **Purpose**: Acquire event metadata, Excel workbook, radar volumes, and atmospheric sources; emit canonical JSON artifacts.
- **Inputs → Outputs**: Raw observations → `event.json`, `atmos_profile.json`, `radar_slices/*.json`, ingestion logs.
- **Core tasks**: Unit coercion, schema validation, workbook extraction metadata, radar QC flags.
- **Escalation**: File a data-quality issue with offending artifact path and validation trace; notify AtmoFusion on missing layers.

#### FormulaGraph (Excel Reverse Engineering)
- **Purpose**: Translate Excel cell dependencies into an abstract, topologically sortable graph.
- **Outputs**: `formula_graph.json`, `graph_issues.md` when unresolved patterns remain.
- **Core tasks**: Tokenise formulas, detect circular references, fold constants, tag domain-specific segments (drag, ablation, wind drift).
- **Escalation**: Annotate unresolved references and request reviewer guidance before PhysicsSynth proceeds.

#### PhysicsSynth (Physics Model Derivation)
- **Purpose**: Convert graph segments into Python physics modules with explicit units and assumptions.
- **Outputs**: `physics_core/` modules, updated `MODEL_ASSUMPTIONS.md`.
- **Core tasks**: Maintain unit consistency, add unit tests, simplify expressions, coordinate with DocSmith for documentation.
- **Escalation**: When assumptions diverge from legacy workbook, flag in assumptions log and seek domain sign-off.

#### AtmoFusion (Atmospheric & Radar Integration)
- **Purpose**: Blend atmospheric profile(s) and radar-derived winds into simulation-ready vertical slices.
- **Outputs**: `wind_profile_compiled.json`, `vertical_grid.json`, QC annotations.
- **Core tasks**: Temporal interpolation, shear smoothing, outlier detection, uncertainty propagation, emit integration altitude grid aligned with RAOB interpolation (`docs/schemas/vertical_grid.schema.json`).
- **Escalation**: Report sparse coverage to Coordinator; request synthetic uncertainty treatment from DarkflightSim if needed; coordinate with DarkflightSim when grid assumptions diverge.

#### DarkflightSim (Simulation & Ensemble Execution)
- **Purpose**: Integrate darkflight trajectories and ensembles across fragment hypotheses.
- **Outputs**: `trajectories/*.json`, `strewn_field_points.geojson`, summary statistics.
- **Core tasks**: Step integrators, handle ablation/fragment mass loss, enforce invariants (mass ≥ 0, altitude monotonic post-entry), consume `vertical_grid.json` from AtmoFusion to preserve workbook slice parity.
- **Escalation**: On numerical instability, coordinate with PhysicsSynth to adjust models or step sizes; log failing seeds for ParityGuard; loop in AtmoFusion if grid boundaries require adjustment.

#### ParityGuard (Validation, Parity & QA)
- **Purpose**: Compare pipeline outputs to goldens and physical tolerances before publication.
- **Outputs**: `validation_report.md`, diff metrics.
- **Core tasks**: Compute error statistics, track tolerance drift, flag regressions in CI, ingest workbook-derived goldens (landing offsets, fall time, terminal velocity, drift magnitude) with baseline tolerances defined in `validation/parity.py` (1 m offsets, 0.5 s fall time, 1 m/s terminal velocity, 2 m / 0.01 km drift magnitude).
- **Escalation**: Block merge until reviewer sign-off when tolerances change or metrics exceed thresholds.

#### OptimusUQ (Optimisation & Uncertainty Quantification)
- **Purpose**: Calibrate uncertain parameters and quantify dispersion.
- **Outputs**: `calibrated_params.json`, `uncertainty_ellipses.geojson`.
- **Core tasks**: Parameter search (grid/Bayesian), sensitivity analysis, ellipse fitting.
- **Escalation**: If evidence is insufficient, defer to baseline parameters and document limitation in status notes.

#### Coordinator (Orchestration & Provenance)
- **Purpose**: Schedule agents, manage cache/lineage, and assemble run manifests.
- **Outputs**: `provenance_graph.json`, cached artifact registry.
- **Core tasks**: Dependency resolution, cache invalidation, reproducibility logging.
- **Escalation**: On repeated cache divergence, force upstream rebuild and notify DevTools.

#### DocSmith (Documentation & Knowledge Base)
- **Purpose**: Keep README, assumptions, and how-to guides aligned with code changes.
- **Outputs**: Updated documentation (`README.md`, `MODEL_ASSUMPTIONS.md`, `docs/phases/*`).
- **Core tasks**: Track documentation drift, produce diagrams or changelogs, ensure assumptions accompany physics changes.
- **Escalation**: Block merges when public APIs or assumptions change without documentation updates.

#### DevTools (Tooling & Developer Experience)
- **Purpose**: Maintain lint/type/test hygiene, fixtures, and performance tooling.
- **Outputs**: Tooling configs, CI scripts (when enabled), test fixtures.
- **Core tasks**: Run ruff/mypy/pytest, manage parking-lot items, quarantine flaky tests.
- **Escalation**: Add issues to tooling backlog when blockers arise; coordinate with Coordinator for automation priorities.

## 4. Required Inputs & Schemas
Inputs are validated with Pydantic models; JSON Schemas reside in `docs/schemas/` and templates in `docs/templates/`. All user-supplied artifacts include `$schema`, `meta.units`, and `meta.provenance` blocks for traceability.

### 4.1 Event Input (`event.json`)
Fields:
- `event_id` — unique identifier for the run/event.
- `luminous_end` — object capturing darkflight initial state:
  - `time_utc` (ISO8601 UTC timestamp)
  - `lat`, `lon` (degrees, WGS84)
  - `altitude_m` (metres above mean sea level)
  - `speed_mps` (metres per second)
  - `azimuth_deg` (degrees clockwise from true north)
  - `elevation_deg` (degrees above local horizon; entry angle)
- `meta.units` / `meta.provenance` optional but recommended.

### 4.2 Fragment Definitions (`fragments.json`)
Array of fragment hypotheses. Each element must provide:
- `id`
- `mass_kg`
- `density_kgm3`
- `cd`
Optional: `shape_factor`. At least one fragment is required to run a trajectory.

### 4.3 Atmospheric Profile (`atmos_profile.json`)
Merged vertical profile aligned to event time/location. Levels must be sorted by altitude and include:
- `altitude_m`
- `pressure_Pa` (or `pressure_hPa`, normalised during ingest)
- `temperature_K` (or `temperature_C`)
- `wind_u_mps`, `wind_v_mps` (alternate input via `wind_speed_mps` + `wind_dir_deg`)
Optional fields: `wind_w_mps`, `density_kg_m3`, QC metadata. The profile carries `meta.profile_time_utc` and `meta.location`.

### 4.4 Radar Metadata (`radar_metadata.json`, optional)
Pointers to raw radar volumes used for wind derivation:
- `radar_site_id`
- `volume_time_utc`
- `level2_files` (paths/URIs)
- `notes` (optional)
Downstream agents generate derived products (`radar_slices/*.json`, `wind_profile_compiled.json`).

### 4.5 Raw Atmospheric Sources
- `model_reanalysis/*.nc` (e.g., GFS/HRRR netCDF) with metadata (run_time, grid, interpolation modes).
- `radar_vad/*.json` derived vertical wind profiles (altitude_m, wind components, source="radar_vad").
- `radiosonde/*.json` similar to `atmos_profile` but limited altitude.

### 4.6 Physics Configuration (`physics_config.json`)
- drag_model: enum(simple_constant, mach_regime, reynolds_curve)
- ablation: { enabled: bool, method: enum(simple, classical), params: { k_ab?: float, sigma?: float, Q_star?: float } }
- gravity_model: enum(constant, wgs84_local)
- integration: { method: enum(rk4, rkf45, semi_implicit), dt_initial_s: float, dt_min_s: float, dt_max_s: float }

### 4.7 Ensemble Configuration (`ensemble_config.json`)
- mode: enum(mass_grid, monte_carlo)
- samples: int
- distributions: { parameter_name: { dist: enum(normal, lognormal, uniform), params: {...} } }
- random_seed: int

### 4.8 Validation Spec (`validation_spec.json`)
- tolerances: { centroid_error_m: float, point_error_m: float }
- metrics: [enum(centroid_delta, max_point_delta, runtime, mass_rmse)]
- golden_events: [ { id: string, artifact_hash: string } ]

### 4.7 Output Manifest (output_manifest.json)
Generated after run:
- event_id
- produced_utc
- artifacts: [ { path, sha256, type, bytes } ]
- kml_summary: { features: int, ellipses: int }
- provenance_hash

Mandatory Presence Before Simulation:
1. event.json
2. atmos_profile.json (canonical fused)
3. physics_config.json
4. ensemble_config.json (if ensemble)

## 5. Processing Pipeline & Data Flow
Each stage declares: Inputs (hash set) -> Transform -> Outputs. Coordinator computes a composite cache key (sorted sha256 of inputs + stage version). If cache hit, stage skipped.

| Stage | Inputs | Outputs | Failure Modes | Recovery |
|-------|--------|---------|---------------|----------|
| S1 Event Ingestion | raw event.json (user) | event.json (normalized) | schema error, unit ambiguity | prompt correction |
| S2 Atmos Fusion | raw atmos sources | atmos_profile.json | missing levels, large gaps | fill w/ std atmosphere + warn |
| S3 Physics Compile | formula_graph.json OR templates | physics/*.py, model_manifest.json | unresolved variable | mark variable TODO & stub |
| S4 Fragment Prep | event.json, physics config | fragments.json | invalid mass splits | recompute splits or abort |
| S5 Simulation | fragments.json, atmos_profile.json, physics modules | trajectories/*.json | divergence, negative mass | reduce dt, clamp, log |
| S6 Ensemble | trajectories config, simulation kernel | ensemble_manifest.json, aggregated stats | RNG inconsistency | reseed & rerun |
| S7 Uncertainty Post | ensemble trajectories | uncertainty_ellipses.geojson | insufficient samples | increase sample size |
| S8 Validation | trajectories, golden set | validation_report.md | threshold breach | mark failure & block CI |
| S9 Geospatial Export | trajectories, ellipses | strewn_field_points.geojson, strewn_field.kml | projection error | fallback to WGS84 direct |
| S10 Provenance | all artifact manifests | provenance_graph.json | hash collision (unlikely) | re-hash w/ salt |

State Machine Notes:
- Validation failure halts downstream publication but preserves artifacts for inspection.
- Each stage includes a `stage_version` constant; bump on logic change to invalidate stale cache.

Sequential Execution (default) or DAG parallelism (optional) for non-dependent fragments.

---
## 6. Data Contracts & Storage Layout
Directory layout (proposed):
```
project_root/
  data/
    events/<event_id>/raw/
    events/<event_id>/processed/
  artifacts/<event_id>/
    atmos/
    physics/
    sim/
    ensemble/
    geo/
    validation/
  cache/
  logs/
```
Artifact Naming Conventions:
- `<event_id>__<artifact>__v<major>.json` (version bump on schema change).
- Hash suffix added only for external publication if needed.

Canonical JSON Fields:
- All contain `meta`: { schema_version, created_utc, producer, inputs: [ { path, sha256 } ] }.


## 7. Google Earth & Geospatial Outputs
Primary formats: GeoJSON (analysis interoperability) & KML/KMZ (Google Earth visualization). Generation performed by `geospatial_export` module.

### 7.1 strewn_field_points.geojson
FeatureCollection, each feature:
- geometry: Point (lon, lat, 0)
- properties: { fragment_id, mass_final_kg, impact_speed_mps, landing_time_utc, uncertainty_radius_m, energy_J }

### 7.2 strewn_field.kml Structure
Folders:
- Event Overview (description balloon: event metadata + provenance link)
- Fragments (Placemarks colored by mass class; style scale by sqrt(mass))
- Uncertainty Ellipses (Polygons with semi-transparent fill)
- Trajectories (optional LineString per representative mass)
- Heatmap (optional ground probability raster overlay; future)

Styling Guidelines:
- Mass classes mapped to gradient (small=yellow -> large=red).
- Ellipse outline: #FF0000, fill: rgba(255,0,0,64).
- Trajectories: thin lines (#8888FF) with altitude extruded (optional 3D mode on demand).

KML ExtendedData Fields:
- ballistic_coefficient
- time_alof_s
- beta (alias of ballistic coefficient)
- density_kg_m3
- drag_coefficient

KMZ Packaging:
- Root doc.kml + `media/legend.png` generated legend.
- README.txt with run summary & validation status.

### 7.3 Ellipse Computation Metadata
Stored in `uncertainty_ellipses.geojson` properties:
- covariance_matrix: [[xx, xy],[xy, yy]]
- confidence_level (e.g., 0.90)
- major_axis_m, minor_axis_m, orientation_deg

### 7.4 CRS & Precision
- All geographic outputs in WGS84 (EPSG:4326), 6 decimal places lat/lon (~0.11 m precision) by default; may reduce to 5 decimals to control file size.
- Distances & axes computed in local ENU plane then reprojected.

### 7.5 Provenance Embedding
KML Document description includes a JSON snippet (escaped) summarizing: event_id, git_commit, run_id, artifacts & hashes. GeoJSON top-level `meta` replicates same.

---
## 8. Core Physics & Simulation Engine
Architecture:
- Pure function layer (`physics_core`): stateless computations (drag_force, ablation_rate, integration_step) with explicit inputs & returns.
- Integrator strategies implementing `Integrator` ABC.
- State vector: dataclass { t, x, y, z, vx, vy, vz, mass }.
- Deterministic random stream (PCG64) seeded once per ensemble run, substream per fragment.

Legacy parity guardrails (Fries Jörmungandr v2):
- Atmospheric slices from radiosonde data propagate top/bottom state pairs; each slice inherits the previous `f` state as its next `i` state.
- Force calculations resolve along the full path length `l` before distributing into axis components to avoid drag-regime misclassification.
- Within each slice, preserve the seven-step solve order (path geometry → velocity components → wind decomposition → effective wind → drag/acceleration → position update) described in `docs/methodology.md` §19.

Performance Enhancements (later phase): numba JIT for inner loop, optional vectorization (batched fragments), early termination detection.

## 9. Uncertainty & Ensemble Framework
- Distribution sampling performed before simulation; each sample writes a row in `ensemble_manifest.json` referencing parameter draws.
- Supports stratified Latin Hypercube plug-in implementing `SamplingStrategy` ABC.
- Reuse identical draws for multiple physics variants to enable paired statistical tests.

## 10. Orchestration & Caching Strategy
- Coordinator constructs DAG from declared stage descriptors (YAML list or Python registry).
- Cache key: sha256( concat(sorted(input_hashes)) + stage_version + config_hash ).
- Cache store: `cache/<stage>/<key>/<artifact files>`.
- Dry-run mode: prints planned execution graph and cache hits/misses.

## 11. Extensibility & Plugin Interfaces
### 11.1 Abstract Base Classes
```
class AtmosphericSource(ABC):
    def load(self) -> AtmosphericRaw: ...

class AtmosFusionStrategy(ABC):
    def fuse(self, raws: list[AtmosphericRaw]) -> AtmosphericProfile: ...

class DragModel(ABC):
    def cd(self, mach: float, reynolds: float, shape_factor: float) -> float: ...

class AblationModel(ABC):
    def dm_dt(self, state: State, atmos: AtmosSlice) -> float: ...

class Integrator(ABC):
    def step(self, state: State, dt: float, env: EnvProvider) -> State: ...

class SamplingStrategy(ABC):
    def sample(self, n: int, distributions: dict, seed: int) -> list[dict]: ...
```

### 11.2 Plugin Registration
- Entry points group: `meteor.darkflight.plugins`.
- Discovery: `importlib.metadata.entry_points(group=...)`.
- Each plugin exposes `plugin_manifest()` returning: { name, version, provides: [interfaces], config_schema }.

### 11.3 Configuration Resolution
Layer precedence (lowest -> highest): default -> environment profile -> user file -> CLI flags.
Conflict resolution: last-writer-wins but logged diff of overrides.

### 11.4 Error Isolation
- Each plugin executed within try/except wrapper; on failure can be disabled dynamically.
- Non-critical plugin (e.g., alternative sampling) failure downgrades to baseline implementation.

---
## 12. Testing & Quality Strategy
Test Taxonomy:
1. Unit Tests (fast, <100 ms each): physics functions, interpolation, coordinate transforms.
2. Contract Tests: Validate JSON artifacts against schemas & invariants (monotonic altitude, non-negative mass).
3. Golden Parity Tests: Compare trajectories & landing points vs stored legacy outputs for benchmark events.
4. Property-Based Tests: Hypothesis to ensure invariants (mass decreases or constant; altitude non-increasing after darkflight; energy not increasing spuriously).
5. Performance Benchmarks: Track runtime for N fragments & ensemble size; fail if > X% regression.
6. Integration Scenario Tests: End-to-end run with synthetic atmosphere & two fragment masses.
7. Plugin Compatibility Tests: Ensure discovery & fallback behavior.

CI Pipeline Stages:
- lint/type (ruff + mypy)
- unit+contract
- property (nightly for broader search space)
- golden parity (on PRs touching physics or simulation modules)
- performance benchmark (compare to baseline JSON of metrics)

Coverage Targets:
- physics_core: 100% lines/branches
- integrators: 95% lines
- rest: >=80%

Failure Handling:
- Golden parity deviation triggers detailed diff artifact (JSON with per-fragment delta). Publish as build artifact.
- Performance regression beyond tolerance posts comment with top slow tests.

Fixtures & Data:
- `tests/fixtures/events/*.json`
- `tests/fixtures/atmos/*.json`
- `tests/golden/` stores canonical landing outputs with metadata hash.

---
## 13. Logging, Monitoring & Provenance
Logging:
- Structured JSON logs (python-json-logger) with fields: timestamp, level, module, event_id, fragment_id?, message, metrics{}.
- Verbosity tiers: INFO (default), DEBUG (physics fine-grain), TRACE (optional per run flag).
Metrics:
- Exposed via optional FastAPI endpoint or Prometheus client: simulation_runtime_s, fragments_per_second, cache_hit_ratio, validation_pass_rate.
Provenance Graph:
- Node: artifact (path, sha256, schema_version, created_utc, producer, stage_version)
- Edge: dependency (from input artifact -> output artifact)
- Stored in `provenance_graph.json` & visualizable via DOT export.

## 14. AI SDLC & Automation Hooks
Agent Mapping (from AGENTS.md):
- Ingestor -> event_ingest, atmos_source modules (auto schema diff PRs)
- FormulaGraph -> workbook_extract (optional legacy parity path)
- PhysicsSynth -> physics_core generation & docstring enrichment
- AtmoFusion -> atmos_fusion interpolation validation
- DarkflightSim -> sim_kernel performance guardrails
- ParityGuard -> validation stage gating merges
- OptimusUQ -> ensemble_driver & uncertainty_post parameter optimization
- DocSmith -> auto-updates architecture & methodology cross references
- DevTools -> CI templates, lint/type config

Automation Points:
- Pre-commit hook: run fast unit + schema validation.
- PR bot: attach validation diff & coverage delta.
- Nightly job: run extended property-based tests / large ensemble stress test.
- Doc sync job: regenerate API reference from source docstrings.

AI Safety & Guardrails:
- Physics function auto-generation requires human review label before merge.
- Automated parameter optimization cannot change golden baseline without parity re-run.
- Agent actions confined to module directories; no cross-module mutation without doc update.

---
## 15. Non-Functional Requirements
Performance:
- Target: 10k particle ensemble < 60 s on 8-core modern CPU; single fragment trajectory < 50 ms.
- Memory: < 1 GB for typical ensemble run; streaming write of trajectories to avoid large in-memory arrays.
Reliability:
- Deterministic outputs given identical inputs & seed.
- Graceful degradation (partial outputs preserved on failure with status flags).
Security / Integrity:
- Reject untrusted workbook formula tokens outside allowlist.
- Validate all inbound JSON against schemas before processing.
Observability:
- Emit per-stage timing & counts.
- Provide debug artifact summarizing top drag regimes & time spent above threshold Mach (if available).
Portability:
- Pure Python + optional compiled extras (numba) kept optional.
- Works cross-platform (Linux, macOS, Windows). CI matrix tests 3.11, 3.12.

## 16. Deployment & Runtime Modes
Modes:
1. CLI Batch: `darkflight run --event event.json --atmos atmos_profile.json --config physics_config.json`
2. API Service: FastAPI exposing `/simulate` endpoint for interactive queries.
3. Notebook / Research: High-level Python API imported in Jupyter.
4. Agent Automation: GitHub Actions workflow invoking CLI for new events.

Packaging:
- `pyproject.toml` with optional extras: `[extras] vad = ["pyart"]`, `[extras] speed = ["numba"]`.
- Publish to internal PyPI or artifact registry.

Configuration Files:
- `darkflight.toml` (global defaults)
- `events/<id>/override.toml`

## 17. Future Extensions
- DEM Terrain Adjustment Module
- Variable Drag Mach Curve & Regime Transition Model
- Machine Learning Parameter Calibration
- Real-Time Ingestion & Progressive Updating
- 3D Visualization Export (Cesium 3D Tiles)
- Spatial Probability Raster Generation (GeoTIFF)

## 18. Appendix (Sample Config)
```
[physics]
drag_model = "simple_constant"
cd_base = 1.3
ablation = { enabled = false }

[integration]
method = "rk4"
dt_initial_s = 0.05
dt_min_s = 0.005
dt_max_s = 0.2

[ensemble]
mode = "mass_grid"
samples = 12
random_seed = 123456

[output]
geo_precision_decimals = 6
kml_generate = true
geojson_generate = true
```
