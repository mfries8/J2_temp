# Public data feeds (US Govt & related)

This document lists publicly available data sources that are useful input feeds for the darkflight / strewn-field pipeline. For each source: data type, applicability & use, programmatic access methods, and a URL for details.

## 1) NOAA/NWS - NCEP Global Data Assimilation System (GDAS) / Global Forecast System (GFS)
- Data type: Numerical weather model analyses and forecasts (pressure, temperature, winds, humidity) on global grids
- Applicability & use: Provide background atmospheric profiles and wind fields to derive canonical `atmos_profile.json`. Useful for filling gaps where radiosonde coverage is sparse and for temporal interpolation around event time.
- Programmatic access: FTP/HTTP via NOAA NOMADS; GRIB/NetCDF formats. Tools: xarray + cfgrib, OPeNDAP endpoints for subset queries.
- URL: https://nomads.ncep.noaa.gov/ and https://www.ncei.noaa.gov/products/weather-models

## 2) NOAA - Radiosonde / Upper-Air Soundings (IGRA / NOAA Radiosonde archives)
- Data type: Radiosonde vertical profiles (temperature, pressure, humidity, wind) from operational soundings.
- Applicability & use: High-fidelity local vertical profile for fusion into atmos profiles; preferred source near event time/location for blending.
- Programmatic access: NOAA IGRA dataset (FTP/HTTP); NOAA upper-air archives accessible via REST/FTP; MetPy and Siphon wrappers can help.
- URL: https://www.ncei.noaa.gov/products/weather-balloon and https://www.ncdc.noaa.gov/data-access/weather-balloon/upper-air

## 3) NCEI/NOAA - Radiosonde archive and sounding data (e.g., Integrated Global Radiosonde Archive - IGRA)
- Data type: Historical radiosonde measurements (pressure, temp, dewpoint, wind) in station/time pairs.
- Applicability & use: Create ground-truth vertical profiles for validation and fusion.
- Programmatic access: FTP/HTTP bulk downloads and station-level queries.
- URL: https://www.ncei.noaa.gov/products/upper-air-station-data/igra

## 4) NOAA - NEXRAD Level II (NEXRAD radar reflectivity & radial velocity)
- Data type: Doppler radar Level II/III (reflectivity, radial velocity, spectrum width) from the WSR-88D network.
- Applicability & use: Compute vertical wind profiles (VAD/VWP), derive local wind shear and near-surface winds to improve drift modeling.
- Programmatic access: Amazon S3 public bucket (noaa-nexrad-level2) or NOAA FTP archives. Tools: Py-ART, wradlib.
- URL: https://www.ncdc.noaa.gov/data-access/radar-data/ and https://registry.opendata.aws/noaa-nexrad/

## 5) NOAA - NAM/HRRR (High-Resolution Rapid Refresh)
- Data type: High-resolution short-term regional model (wind, temperature, pressure) — HRRR best for convective-scale features.
- Applicability & use: When event is recent and high-res wind structure matters (e.g., strong shear), HRRR helps produce more accurate profiles near the event time.
- Programmatic access: NOMADS, Amazon AWS Registry (HRRR on S3) or NOAA download services. Access via GRIB/netCDF via cfgrib/xarray.
- URL: https://rapidrefresh.noaa.gov/ and https://nomads.ncep.noaa.gov/

## 6) NOAA - Global Forecast System (GFS) via NOMADS
- Data type: Global forecast model; similar to GDAS/GFS references; repeated for clarity.
- Applicability & use: Baseline model fields for atmospheric profile extraction and temporal interpolation.
- Programmatic access: NOMADS (HTTP/FTP), OPeNDAP.
- URL: https://nomads.ncep.noaa.gov/

## 7) NOAA - National Data Buoy Center (NDBC) and Surface Observations (METAR/ASOS)
- Data type: Surface observations (wind speed/direction, pressure, temperature) from buoys, METAR stations, ASOS stations.
- Applicability & use: Near-surface boundary conditions for blending into the lowest model levels and for QC.
- Programmatic access: REST APIs and FTP; NDBC and NOAA API endpoints.
- URL: https://www.ndbc.noaa.gov/, https://www.ncdc.noaa.gov/data-access/land-based-station-data

## 8) NASA - MERRA-2 / Modern-Era Retrospective analysis
- Data type: Global reanalysis datasets (meteorological fields over historical periods).
- Applicability & use: Historical reconstructions for validation cases and long-term studies.
- Programmatic access: NASA GES DISC, FTP, OPeNDAP, and cloud-hosted datasets.
- URL: https://gmao.gsfc.nasa.gov/merra/

## 9) USGS - Digital Elevation Models (DEM)
- Data type: Terrain elevation rasters (DEM, 1/3 arc-second, 1 arc-second, etc.).
- Applicability & use: Adjust final landing positions for terrain height, compute slope effects for recovery planning, and mask improbable water/urban areas.
- Programmatic access: USGS TNM APIs, Amazon S3 hosting, and HTTP endpoints.
- URL: https://elevation.usgs.gov/ and https://www.usgs.gov/core-science-systems/ngp/3dep

## 10) NOAA / NESDIS - Satellite-derived winds & products
- Data type: Satellite retrievals (e.g., atmospheric motion vectors), cloud-top winds, and other remote-sensing products.
- Applicability & use: Supplement wind fields where radiosonde or radar coverage is limited (marine or remote areas).
- Programmatic access: NOAA/NESDIS archives, AWS public datasets, OPeNDAP.
- URL: https://www.nesdis.noaa.gov/

## 11) US Space Force / CSpOC / 18th Space Control Squadron (SFS) re-entries and TLEs
- Data type: Two-Line Element (TLE) data and re-entry notices (space object tracking).
- Applicability & use: If integrating initial ballistic trajectory from orbital objects or using TLEs to estimate entry times; often less applicable for meteorites but useful for spacecraft reentry scenarios.
- Programmatic access: Space-Track API (requires login/terms) and public aggregator APIs (Celestrak).
- URL: https://celestrak.com/ and https://www.space-track.org/

## 12) NOAA - Storm Events and Recovered Meteorite Catalogs (for validation)
- Data type: Storm/recovery reports, historical recovered fragments (where available), observational reports.
- Applicability & use: Ground-truth validation and cross-checking of predicted strewn fields.
- Programmatic access: NCEI archives, data.gov datasets.
- URL: https://www.ncdc.noaa.gov/stormevents/ and data.gov searches

## 13) NOAA / NCEI - Radar Metadata & Archived Records (for provenance)
- Data type: Radar archive metadata, radar site characteristics, calibration data.
- Applicability & use: Record provenance of radar sources used in fusion and QC of radar-derived winds.
- Programmatic access: NOAA archives and site APIs.
- URL: https://www.ncei.noaa.gov/

## 14) NOAA - Tides/Water Level (for coastal recovery planning)
- Data type: Tide gauge water-level observations and predictions.
- Applicability & use: If strewn field intersects coastal areas, tide predictions and high-water flags help determine when fragments might be submerged or accessible.
- Programmatic access: NOAA CO-OPS APIs (REST).
- URL: https://tidesandcurrents.noaa.gov/api/

## Programmatic access notes
- Most model products (GFS, HRRR, NAM) are available as GRIB/NetCDF and accessible via NOMADS, AWS Open Data, or OPeNDAP; recommend using `xarray` + `cfgrib` or OPeNDAP for efficient subsetting.
- NEXRAD Level II is available via AWS public S3 buckets (`noaa-nexrad-level2`) and NOAA FTP archives; use Py-ART/wradlib for processing.
- Radiosonde data (IGRA) can be bulk downloaded via FTP/HTTP; MetPy has helpers for parsing standard sounding formats.
- DEMs and geospatial layers are typically accessible through USGS APIs; rasterio can read common raster formats when downloaded.

---

## Quick links
- NOMADS (NOAA): https://nomads.ncep.noaa.gov/
- NOAA NEXRAD on AWS: https://registry.opendata.aws/noaa-nexrad/
- IGRA / Radiosonde: https://www.ncei.noaa.gov/products/upper-air-station-data/igra
- USGS Elevation APIs: https://elevation.usgs.gov/
- NASA MERRA: https://gmao.gsfc.nasa.gov/merra/
- NOAA CO-OPS Tides API: https://tidesandcurrents.noaa.gov/api/


---

*If you want, I can also create small example scripts that download a single sounding, extract a vertical profile, and serialize to the repository's `docs/templates/atmos_profile.json` format.*