"""
ERA5 Surface Wind Data Adapter for OceanEmbed
Fetches ECMWF ERA5 10m zonal (u10) and meridional (v10) wind components using cdsapi.
"""

import os
from typing import List, Optional


class ERA5Adapter:
    """Adapter for requesting ECMWF ERA5 surface wind data via CDS API."""

    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = raw_dir
        os.makedirs(raw_dir, exist_ok=True)

    def fetch_surface_winds(
        self,
        year: str,
        month: str,
        days: List[str],
        lat_min: float = 5.0,
        lat_max: float = 30.0,
        lon_min: float = 45.0,
        lon_max: float = 105.0,
        output_filename: str = "era5_winds_sample.nc",
    ) -> str:
        """Download ERA5 10m U/V winds over North Indian Ocean bounding box."""
        output_path = os.path.join(self.raw_dir, output_filename)
        
        try:
            import cdsapi
            client = cdsapi.Client()
            print(f"[ERA5 Adapter] Requesting ERA5 10m wind components for {year}-{month}...")
            
            # North, West, South, East bounding box format for ERA5
            area = [lat_max, lon_min, lat_min, lon_max]

            client.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "product_type": "reanalysis",
                    "variable": ["10m_u_component_of_wind", "10m_v_component_of_wind"],
                    "year": year,
                    "month": month,
                    "day": days,
                    "time": [f"{h:02d}:00" for h in range(24)],
                    "area": area,
                    "format": "netcdf",
                },
                output_path,
            )
            print(f"[ERA5 Adapter] Successfully downloaded: {output_path}")
            return output_path

        except Exception as e:
            print("\n=== ECMWF CDS AUTHENTICATION EXCEPTION ===")
            print("What failed: Requesting ERA5 wind dataset via cdsapi.")
            print("Why: ~/.cdsapirc file missing or invalid API key.")
            print("Required Action: Create ~/.cdsapirc with url and key from https://cds.climate.copernicus.eu/api-how-to")
            print(f"Error details: {e}")
            raise RuntimeError(f"ERA5 download failed: {e}")
