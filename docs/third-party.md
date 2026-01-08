# Third-party Python Libraries (recommended)

This document lists free/open-source Python libraries that are useful for the darkflight / strewn-field project. For each library: name, URL, a short description, and how it may be useful for this project.

## Atmosphere, meteorology & interpolation

- MetPy — https://github.com/Unidata/MetPy
  - Description: Meteorological toolkit for reading model/sounding data, unit-aware calculations, and thermodynamic routines.
  - Usefulness: Parse radiosonde/model output, compute derived quantities (density, pressure/altitude conversions), lapse rates, and interpolation. Useful for canonical atmosphere handling and sanity checks.
  - Used in modules: `atmos_source`, `atmos_fusion`, `validation`

- Siphon — https://github.com/Unidata/siphon
  - Description: Data access library for Unidata/NOAA services (including sounding and model datasets).
  - Usefulness: Fetch radiosonde (RAOB) data via IGRA/NOAA web services so the slice-by-slice workflow matches the legacy spreadsheet without bespoke HTTP code.
  - Used in modules: `atmos_source`, `atmos_fusion`

- xarray — https://xarray.dev/ (GitHub: https://github.com/pydata/xarray)
  - Description: Labeled N-dimensional arrays built on NumPy, excellent for netCDF model datasets.
  - Usefulness: Load and slice NWP model grids (GDAS/HRRR), vertically sample profiles along a track, and export canonical atmos profiles.
  - Used in modules: `atmos_source`, `atmos_fusion`

- cfgrib / ecCodes bindings — https://github.com/ecmwf/cfgrib
  - Description: Read GRIB files into xarray via ECMWF ecCodes.
  - Usefulness: Programmatic access to GRIB model files when users provide NWP data.
  - Used in modules: `atmos_source`

## Radar & wind retrieval

- Py-ART — https://github.com/ARM-DOE/pyart
  - Description: Radar Level-II/III processing toolkit (VAD, moments, Cartesian grids, QC).
  - Usefulness: Extract radial velocity fields, perform VAD/VWP to derive vertical wind profiles, QC reflectivity, and produce radar-derived winds to blend into atmos profiles.
  - Used in modules: `atmos_source`, `atmos_fusion`, `validation`

- wradlib — https://github.com/wradlib/wradlib
  - Description: Radar processing and hydrometeor retrieval library.
  - Usefulness: Complementary radar processing (regridding, attenuation correction) alongside or instead of Py-ART.
  - Used in modules: `atmos_source`, `atmos_fusion`

## Units & dimensional checks

- Pint — https://pint.readthedocs.io/ (GitHub: https://github.com/hgrecco/pint)
  - Description: Units library for Python enabling arithmetic with units and conversions.
  - Usefulness: Encode units explicitly, prevent unit-mixing bugs, and make unit assertions in tests for spreadsheet-to-code parity.
  - Used in modules: `physics_core`, `event_ingest`, `validation`, `sim_kernel`

## Numerical math, integrators & performance

- SciPy — https://www.scipy.org/ (GitHub: https://github.com/scipy/scipy)
  - Description: Scientific computing (ODE integrators, optimization, interpolation).
  - Usefulness: Robust ODE solvers (solve_ivp) for darkflight integration and root-finding for ground intersection.
  - Used in modules: `physics_core`, `sim_kernel`, `uncertainty_post`

- numba — https://numba.pydata.org/ (GitHub: https://github.com/numba/numba)
  - Description: JIT compiler to speed numeric Python code.
  - Usefulness: Accelerate inner-loop physics (drag, ablation) for large ensembles while keeping Python code.
  - Used in modules: `physics_core`, `sim_kernel`, `ensemble_driver`

- JAX — https://github.com/google/jax
  - Description: High-performance array library with autodiff and JIT compilation.
  - Usefulness: For later gradient-based calibration or GPU acceleration of simulation kernels.
  - Used in modules (optional): `physics_core`, `ensemble_driver`, `validation` (for calibration)

## Geospatial, projections & export

- pyproj — https://pyproj4.github.io/pyproj/stable/ (GitHub: https://github.com/pyproj4/pyproj)
  - Description: PROJ bindings for cartographic projections and CRS conversions.
  - Usefulness: Convert downrange/crossrange offsets to lat/lon and handle reprojections for export.
  - Used in modules: `sim_kernel`, `geospatial_export`, `ensemble_driver`

- Shapely — https://shapely.readthedocs.io/ (GitHub: https://github.com/shapely/shapely)
  - Description: Geometry operations (polygons, ellipses, intersections).
  - Usefulness: Build uncertainty ellipses, geometry ops, and produce GeoJSON geometries.
  - Used in modules: `uncertainty_post`, `geospatial_export`, `validation`

- Fiona — https://fiona.readthedocs.io/ (GitHub: https://github.com/Toblerity/Fiona)
  - Description: Read/write vector GIS formats using OGR.
  - Usefulness: Write GeoJSON or shapefiles for external GIS tools.
  - Used in modules: `geospatial_export`, `validation`

- simplekml — https://simplekml.readthedocs.io/ (GitHub: https://github.com/simplekml/simplekml)
  - Description: Create KML files programmatically.
  - Usefulness: Generate Google Earth KML/KMZ outputs for trajectories and ellipses.
  - Used in modules: `geospatial_export`

- rasterio — https://rasterio.readthedocs.io/ (GitHub: https://github.com/rasterio/rasterio)
  - Description: Raster IO and DEM access (GDAL bindings).
  - Usefulness: Load DEM tiles if adjusting impacts for terrain elevation.
  - Used in modules: `geospatial_export`, `validation`

## Uncertainty quantification, sampling & statistics

- chaospy — https://github.com/jonathf/chaospy
  - Description: Probabilistic UQ toolkit (polynomial chaos, sampling).
  - Usefulness: Build UQ pipelines beyond simple Monte Carlo (surrogates, sensitivity).
  - Used in modules: `uncertainty_post`, `ensemble_driver`

- SALib — https://salib.readthedocs.io/ (GitHub: https://github.com/SALib/SALib)
  - Description: Sensitivity analysis (Sobol, Morris, FAST).
  - Usefulness: Determine which parameters (drag, density) most influence strewn-field dispersion.
  - Used in modules: `uncertainty_post`, `ensemble_driver`

- emcee — https://emcee.readthedocs.io/ (GitHub: https://github.com/dfm/emcee)
  - Description: MCMC ensemble sampler for Bayesian parameter estimation.
  - Usefulness: Calibrate uncertain parameters using recovered fragment observations.
  - Used in modules: `validation`, `ensemble_driver` (calibration workflows)

## Data handling & serialization

- pandas — https://pandas.pydata.org/ (GitHub: https://github.com/pandas-dev/pandas)
  - Description: Tabular data structures and IO.
  - Usefulness: Aggregate ensemble outputs, compute CSV reports and summary statistics.
  - Used in modules: `ensemble_driver`, `uncertainty_post`, `validation`, `geospatial_export`

- pyarrow / parquet — https://arrow.apache.org/ (GitHub: https://github.com/apache/arrow)
  - Description: Columnar data structures and Parquet storage.
  - Usefulness: Persist large ensembles/trajectories efficiently for later analysis.
  - Used in modules: `ensemble_driver`, `sim_kernel`, `uncertainty_post`

## Excel / spreadsheet parsing

- openpyxl — https://openpyxl.readthedocs.io/ (GitHub: https://github.com/openpyxl/openpyxl)
  - Description: Read/write Excel `.xlsx` files and access formulas.
  - Usefulness: Programmatically extract workbook formulas and named ranges for `formula_graph.json` when parity with the Excel model is required.
  - Used in modules: `workbook_extract`, `validation`

- xlrd / xlwings — https://xlrd.readthedocs.io/ ; https://www.xlwings.org/
  - Description: Excel readers and automation tools.
  - Usefulness: Alternative extraction approaches; `xlwings` can help with interactive debugging if Excel is available on the developer machine.
  - Used in modules: `workbook_extract`, `validation`

## I/O, CLI & app tooling

- typer — https://typer.tiangolo.com/ (GitHub: https://github.com/tiangolo/typer)
  - Description: Simple, type-hinted CLI builder (based on Click).
  - Usefulness: Build the user-facing CLI quickly (validation, run, export).
  - Used in modules: `cli_api`

- pydantic — https://pydantic-docs.helpmanual.io/ (GitHub: https://github.com/pydantic/pydantic)
  - Description: Data validation and parsing using type hints.
  - Usefulness: Canonicalize and validate input artifacts (`event.json`, `atmos_profile.json`) with clear errors.
  - Used in modules: `event_ingest`, `config_registry`, `validation`

## Testing, linting & CI

- pytest — https://pytest.org/ (GitHub: https://github.com/pytest-dev/pytest)
  - Description: Test runner for unit and integration tests.
  - Used in modules: `tests` (project-wide)

- hypothesis — https://hypothesis.readthedocs.io/ (GitHub: https://github.com/HypothesisWorks/hypothesis)
  - Description: Property-based testing for asserting invariants (e.g., mass never increases).
  - Used in modules: `tests`, `validation`

- ruff / flake8 / mypy — Linters and type checkers to enforce style and catch type errors.
  - Used in modules: developer tooling / CI (project-wide)

## Visualization & notebooks

- plotly / matplotlib — https://plotly.com/python/ ; https://matplotlib.org/
  - Description: Interactive and static plotting libraries.
  - Usefulness: Plot trajectories, ensemble scatter, and wind profiles for reports and debugging.
  - Used in modules: `validation`, `geospatial_export`, `docs`

---

## Notes on licensing and inclusion
Most of the libraries above are permissively licensed (BSD/MIT), but check each project's LICENSE if you plan to redistribute the combined product. Radar toolkits and Unidata tools typically use BSD-style licenses.

## Recommended priority
1. Core validation & numerics: `pydantic`, `numpy`, `scipy`, `pint`, `xarray`, `pyproj`, `shapely`, `simplekml`, `openpyxl`.
2. Radar processing: `Py-ART` or `wradlib` (if Level-II data processing is needed).
3. Performance/UQ: add `numba` or `JAX` only after profiling identifies the bottlenecks.


## Submodule -> Libraries mapping

This section lists each project submodule and the third-party libraries from this document that that submodule would most likely use.

- `event_ingest`
  - pydantic, pint, openpyxl (when ingesting Excel), pandas

- `workbook_extract`
  - openpyxl, xlrd/xlwings, (optionally) sympy for symbolic formula analysis

- `physics_core`
  - numpy, scipy, pint, numba (optional), JAX (optional for advanced use)

- `atmos_source`
  - xarray, cfgrib (ecCodes), MetPy, Py-ART or wradlib (if ingesting radar-derived winds)

- `atmos_fusion`
  - xarray, MetPy, Py-ART / wradlib, pandas

- `sim_kernel`
  - numpy, scipy, pyproj, pint, numba

- `ensemble_driver`
  - numpy, pandas, pyarrow/parquet, numba, chaospy (optional), SALib (sensitivity workflows)

- `fragmentation`
  - numpy, pandas

- `uncertainty_post`
  - pandas, numpy, shapely, chaospy, SALib

- `validation`
  - pandas, numpy, pydantic, shapely, emcee (for calibration), hypothesis, pytest

- `geospatial_export`
  - shapely, fiona, simplekml, pyproj, rasterio, pandas

- `provenance`
  - pandas, pyarrow/parquet (for artifact storage), json (stdlib)

- `cli_api`
  - typer, pydantic

- `config_registry`
  - pydantic (for config models), toml/tomllib or yaml (for config files)

- `plugin_loader`
  - importlib.metadata (stdlib) and optional plugin helpers; no heavy external deps required

- `tests` (project-wide test helpers)
  - pytest, hypothesis, mypy/ruff (linting/type checks)

