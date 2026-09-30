"""
NOAA OISST / ERDDAP Data Adapter for OceanEmbed
Fetches NOAA High-Resolution Sea Surface Temperature (OISST) v2.1.
"""

import os
import xarray as xr
from typing import Optional


class NOAAOISSTAdapter:
    """Adapter for accessing NOAA High-Resolution Daily OISST v2.1."""

    ERDDAP_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg.nc"

    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = raw_dir
        os.makedirs(raw_dir, exist_ok=True)

    def fetch_oisst_subset(
        self,
        start_date: str,
        end_date: str,
        lat_min: float = 5.0,
        lat_max: float = 30.0,
        lon_min: float = 45.0,
        lon_max: float = 105.0,
        output_filename: str = "noaa_oisst_sample.nc",
    ) -> str:
        """Downloads NOAA OISST daily surface temperature dataset."""
        output_path = os.path.join(self.raw_dir, output_filename)
        
        try:
            url = f"{self.ERDDAP_URL}?sst[({start_date}T12:00:00Z):1:({end_date}T12:00:00Z)][(0.0):1:(0.0)][({lat_min}):1:({lat_max})][({lon_min}):1:({lon_max})]"
            print(f"[NOAA Adapter] Accessing OISST subset via ERDDAP: {url}")
            ds = xr.open_dataset(url)
            ds.to_netcdf(output_path)
            print(f"[NOAA Adapter] Successfully downloaded: {output_path}")
            return output_path
        except Exception as e:
            print(f"[NOAA Adapter Error] Failed to access NOAA OISST ERDDAP endpoint: {e}")
            raise RuntimeError(f"NOAA OISST download failed: {e}")
