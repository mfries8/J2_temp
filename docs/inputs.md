# Input Files & Templates for the Darkflight Pipeline

This guide explains every JSON artifact the pipeline consumes. Copy the templates from `docs/templates/`, place the populated files under `data/events/<event_id>/raw/` (or another configured directory), and update the values with real observations. All files **must**:

- be UTF-8 encoded JSON
- include a `$schema` pointer to the matching definition in `docs/schemas/`
- carry a `meta.units` map and `meta.provenance` block when used in real runs (templates include simple placeholders)

Required inputs:

1. `event.json` – describes the state vector at the end of luminous flight (darkflight start)
2. `fragments.json` – fragment hypotheses to propagate through the atmosphere
3. `atmos_profile.json` – merged atmospheric profile aligned with the event time/location
4. `radar_metadata.json` (optional) – pointers to raw radar volumes used to derive winds

---

## 1. `event.json`

Represents the initial conditions entering darkflight. Vectors use a local tangent plane (East, North, Up). Elevation is the angle **above the local horizon** of the velocity vector; azimuth is measured **clockwise from true north**.

| Field | Type | Units | Description |
| --- | --- | --- | --- |
| `$schema` | string | — | Relative/absolute path to schema (template uses `../schemas/event.schema.json`). |
| `meta.units` | object | — | Optional description of units for human readers. |
| `meta.provenance` | object | — | Source, timestamps, hashes, processing notes. |
| `event_id` | string | — | Unique identifier for the run/event. |
| `luminous_end` | object | — | Nested structure describing the velocity/position at darkflight onset. |

### `luminous_end` object

| Field | Type | Units | Meaning |
| --- | --- | --- | --- |
| `time_utc` | string | ISO 8601 (UTC) | Timestamp when luminous flight transitions to darkflight. |
| `lat` | number | degrees (WGS84) | Geodetic latitude (positive north). |
| `lon` | number | degrees (WGS84) | Geodetic longitude (positive east; west longitudes are negative). |
| `altitude_m` | number | metres (m) | Altitude above mean sea level at darkflight start. |
| `speed_mps` | number | metres per second (m/s) | Magnitude of the velocity vector at darkflight start. |
| `azimuth_deg` | number | degrees | Horizontal bearing of the velocity vector, clockwise from true north. |
| `elevation_deg` | number | degrees | Angle between the velocity vector and the local horizontal plane (entry angle). |

**Example**

```json
{
  "$schema": "../schemas/event.schema.json",
  "meta": {
    "units": {
      "luminous_end": {
        "altitude_m": "metres",
        "speed_mps": "metres per second",
        "azimuth_deg": "degrees clockwise from true north",
        "elevation_deg": "degrees above local horizon"
      }
    },
    "provenance": {
      "agent": "templates",
      "notes": "Example event template"
    }
  },
  "event_id": "BlacksvilleGA_2025",
  "luminous_end": {
    "time_utc": "2025-09-27T01:14:32Z",
    "lat": 33.11234,
    "lon": -84.56789,
    "altitude_m": 27500,
    "speed_mps": 11800,
    "azimuth_deg": 215.4,
    "elevation_deg": 28.7
  }
}
```

**Legacy defaults (use only when observations are missing)**
- Declination / elevation: ~40° above the horizon per Fries Jörmungandr v2 spreadsheet.
- Luminous-end speed: ~3,000 m/s.
- Azimuth: derived from eyewitness track bearings when instrumented data is absent.

These heuristics come from the legacy Excel workflow (see `docs/methodology.md` §19) and should be replaced with measured values whenever possible.

---

## 2. `fragments.json`

Defines the set of fragments (or representative mass bins) to simulate. Provide at least one entry.

| Field | Type | Units | Meaning |
| --- | --- | --- | --- |
| `id` | string | — | Fragment label (e.g., "A", "5kg"). |
| `mass_kg` | number | kilograms (kg) | Initial fragment mass at darkflight start. |
| `density_kgm3` | number | kilograms per cubic metre (kg/m³) | Bulk density used to estimate cross-sectional area. |
| `cd` | number | dimensionless | Drag coefficient to apply during darkflight. |
| `shape_factor` | number (optional) | dimensionless | Modifies drag/area assumptions relative to a sphere. |

**Example**

```json
[
  { "id": "A", "mass_kg": 5.0, "density_kgm3": 3400, "cd": 1.3, "shape_factor": 1.2 },
  { "id": "B", "mass_kg": 0.8, "density_kgm3": 3400, "cd": 1.4, "shape_factor": 1.1 }
]
```

---

## 3. `atmos_profile.json`

A canonical vertical profile aligned with the event time/location. Levels must be sorted by `altitude_m` ascending. You may provide pressure/temperature in alternative units; the ingestion step will normalise them.

| Field | Type | Units | Meaning |
| --- | --- | --- | --- |
| `$schema` | string | — | Path to schema (`../schemas/atmos_profile.schema.json`). |
| `meta.profile_time_utc` | string | ISO 8601 (UTC) | Time at which the profile is valid. |
| `meta.location.lat` | number | degrees | Associated latitude (centre of profile). |
| `meta.location.lon` | number | degrees | Associated longitude. |
| `levels` | array | — | Ordered atmospheric levels. |

### `levels` entries

| Field | Units | Notes |
| --- | --- | --- |
| `altitude_m` | metres (m) | Geopotential/mean sea level altitude. |
| `pressure_Pa` | pascals (Pa) | Provide either `pressure_Pa` or `pressure_hPa` (hectopascals). |
| `pressure_hPa` | hectopascals (hPa) | Optional alternative; 1 hPa = 100 Pa. |
| `temperature_K` | kelvin (K) | Provide either `temperature_K` or `temperature_C`. |
| `temperature_C` | degrees Celsius | Converted internally to kelvin. |
| `wind_u_mps` | m/s | East–west wind component (positive eastward). |
| `wind_v_mps` | m/s | North–south wind component (positive northward). |
| `wind_w_mps` | m/s (optional) | Vertical wind component (positive upward). |
| `wind_speed_mps` | m/s (optional) | If provided with `wind_dir_deg`, components are derived automatically. |
| `wind_dir_deg` | degrees (meteorological) | Direction wind is blowing **from**; used with `wind_speed_mps`. |

**Example**

```json
{
  "$schema": "../schemas/atmos_profile.schema.json",
  "meta": {
    "profile_time_utc": "2025-09-27T01:00:00Z",
    "location": { "lat": 33.11, "lon": -84.56 }
  },
  "levels": [
    { "altitude_m": 0, "pressure_Pa": 101325, "temperature_K": 288.15, "wind_u_mps": -1.2, "wind_v_mps": 2.3 },
    { "altitude_m": 1000, "pressure_Pa": 89875, "temperature_K": 281.65, "wind_u_mps": -2.1, "wind_v_mps": 3.5 }
  ]
}
```

**Tips**
- Ensure altitude levels ascend; the validator rejects descending sequences.
- If you only have wind speed/direction, omit `wind_u_mps`/`wind_v_mps` and supply `wind_speed_mps` + `wind_dir_deg`; the ingestion step converts them using meteorological convention (`u = -speed * sin(dir)`, `v = -speed * cos(dir)`).

---

## 4. `radar_metadata.json` (optional)

If radar-derived winds are available, provide metadata linking to the Level II/Level III volumes. Derived winds themselves will appear later as `radar_slices/*.json` and `wind_profile_compiled.json` outputs.

| Field | Type | Units | Meaning |
| --- | --- | --- | --- |
| `$schema` | string | — | Path to schema (`../schemas/radar_metadata.schema.json`). |
| `radar_site_id` | string | — | Radar identifier (e.g., NEXRAD four-letter code). |
| `volume_time_utc` | string | ISO 8601 (UTC) | Timestamp of the radar volume used for winds. |
| `level2_files` | array of strings | paths/URIs | List of local or remote paths to the raw volume files. |
| `notes` | string (optional) | — | Free-form comments (e.g., QC notes). |

**Example**

```json
{
  "$schema": "../schemas/radar_metadata.schema.json",
  "radar_site_id": "KLRX",
  "volume_time_utc": "2012-08-22T06:17:04Z",
  "level2_files": ["/path/to/KLRX20120822_061704_V06.gz"],
  "notes": "Raw Level II needed for pyart VAD processing"
}
```

---

## Validating Your Inputs

After populating the JSON files for an event, run the CLI validator:

```bash
python -m meteor_darkflight.cli_api.cli validate \
  --event data/events/<event_id>/raw/event.json \
  --dir data/events/<event_id>/raw/
```

The command prints `Validation passed for event inputs` when all files satisfy the schemas. If issues appear (missing fields, unit mismatches, invalid JSON), the validator lists them so you can fix the data before running simulations.

---

## Helpful References

- Templates: `docs/templates/`
- Schemas: `docs/schemas/`
- Test fixture examples: `tests/fixtures/events/`
- Architecture & methodology background: `docs/architecture.md`, `docs/methodology.md`

### Intermediate Artifacts (for reference)
- AtmoFusion emits `vertical_grid.json` following `docs/schemas/vertical_grid.schema.json`; see `docs/templates/vertical_grid.json` for a workbook-aligned example that DarkflightSim consumes when building integration slices.

Keep templates, schemas, and fixtures synchronised whenever you introduce new fields or change assumptions.
