"""Export trajectories and ellipses to GeoJSON and KML/KMZ."""
from typing import Any, List

from pyproj import Transformer

from meteor_darkflight.sim_kernel import TrajectoryResult


def export_geojson(trajectories: Any, out_path: str) -> None:
    """Write GeoJSON feature collection for trajectories/points."""
    raise NotImplementedError()


def export_kml(trajectories: List[TrajectoryResult], out_path: str) -> None:
    """Write KML for Google Earth consumption.

    Args:
        trajectories: List of TrajectoryResult objects.
        out_path: Output file path (e.g. 'output.kml').
    """

    # UTM Zone 16N to WGS84
    transformer = Transformer.from_crs("epsg:32616", "epsg:4326", always_xy=True) # Lon, Lat

    kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Meteor Trajectories</name>
    <Style id="yellowLineGreenPoly">
      <LineStyle>
        <color>7f00ffff</color>
        <width>4</width>
      </LineStyle>
      <PolyStyle>
        <color>7f00ff00</color>
      </PolyStyle>
    </Style>
"""
    kml_footer = """  </Document>
</kml>
"""

    body = ""

    for i, result in enumerate(trajectories):
        coords_str = ""
        for state in result.states:
            lon, lat = transformer.transform(state.x, state.y)
            alt = state.z
            coords_str += f"{lon},{lat},{alt} "

        # Impact Point
        if result.impact_state:
            lon_imp, lat_imp = transformer.transform(result.impact_state.x, result.impact_state.y)
            body += f"""
    <Placemark>
      <name>Impact {i+1}</name>
      <Point>
        <coordinates>{lon_imp},{lat_imp},0</coordinates>
      </Point>
    </Placemark>
"""

        # Trajectory Line
        body += f"""
    <Placemark>
      <name>Trajectory {i+1}</name>
      <styleUrl>#yellowLineGreenPoly</styleUrl>
      <LineString>
        <extrude>1</extrude>
        <tessellate>1</tessellate>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>
          {coords_str}
        </coordinates>
      </LineString>
    </Placemark>
"""

    with open(out_path, "w") as f:
        f.write(kml_header + body + kml_footer)

