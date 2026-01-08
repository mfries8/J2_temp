"""Load raw atmospheric data from multiple source formats."""
from typing import Any


def load_model(nc_path: str) -> Any:
    """Load NWP model reanalysis (netCDF) and return raw structure."""
    raise NotImplementedError()


def load_radiosonde(json_path: str) -> Any:
    """Load radiosonde JSON and return raw structure."""
    raise NotImplementedError()
