"""
Data Sources Package
Contains adapters for Copernicus Marine (CMEMS), NOAA OISST / ERDDAP, ECMWF ERA5, and ARGO.
"""

from .copernicus_adapter import CopernicusMarineAdapter
from .noaa_adapter import NOAAOISSTAdapter
from .era5_adapter import ERA5Adapter

__all__ = [
    "CopernicusMarineAdapter",
    "NOAAOISSTAdapter",
    "ERA5Adapter",
]
