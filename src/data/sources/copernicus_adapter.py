"""
Copernicus Marine Data Adapter for OceanEmbed
Handles downloading and extracting GLORYS12V1, OSTIA SST, MULTIOBS Salinity/Currents, and AVISO SLA datasets.
Enforces explicit error reporting without silent substitutions.
"""

import os
import sys
import yaml
import xarray as xr
from typing import Dict, Any, Optional, List


class CopernicusMarineAdapter:
    """Adapter for downloading and loading Copernicus Marine Service (CMEMS) datasets."""

    DATASET_IDS = {
        "GLORYS": "cmems_mod_glo_phy_my_0.083_P1D-m",       # thetao target
        "OSTIA_SST": "cmems_obs-sst_glo_phy-sst_my_l4_P1D-m",# analysed_sst
        "MULTIOBS_SSS": "cmems_obs-sl_glo_phy-sss_my_l4_P1D",# sos
        "AVISO_SLA": "cmems_obs-sl_glo_phy-sea_surface_height_my_l4_P1D-m",# sla
        "MULTIOBS_CURRENTS": "cmems_obs-sl_glo_phy-uv_my_l4_P1D-m",        # uo, vo
    }

    def __init__(self, raw_dir: str = "data/raw"):
        self.raw_dir = raw_dir
        os.makedirs(raw_dir, exist_ok=True)

    def fetch_glorys_target(
        self,
        start_date: str,
        end_date: str,
        lat_min: float = 5.0,
        lat_max: float = 30.0,
        lon_min: float = 45.0,
        lon_max: float = 105.0,
        output_filename: str = "glorys_target_sample.nc",
    ) -> str:
        """Fetch GLORYS subsurface ocean temperature dataset over specified domain and date range."""
        output_path = os.path.join(self.raw_dir, output_filename)
        
        try:
            import copernicusmarine
            print(f"[CMEMS Adapter] Requesting GLORYS dataset {self.DATASET_IDS['GLORYS']} from {start_date} to {end_date}...")
            
            copernicusmarine.subset(
                dataset_id=self.DATASET_IDS["GLORYS"],
                variables=["thetao"],
                start_datetime=f"{start_date}T00:00:00",
                end_datetime=f"{end_date}T23:59:59",
                minimum_longitude=lon_min,
                maximum_longitude=lon_max,
                minimum_latitude=lat_min,
                maximum_latitude=lat_max,
                minimum_depth=0.0,
                maximum_depth=1000.0,
                output_filename=output_path,
                force_download=True
            )
            print(f"[CMEMS Adapter] Successfully downloaded: {output_path}")
            return output_path

        except Exception as e:
            print("\n=== CMEMS AUTHENTICATION / ACCESS EXCEPTION ===")
            print("What failed: Downloading Copernicus Marine dataset (GLORYS12V1).")
            print(f"Dataset ID: {self.DATASET_IDS['GLORYS']}")
            print("Why: Copernicus Marine credentials missing, network connection blocked, or API rate limit.")
            print("Required Action: Please execute 'copernicusmarine login' or set COPERNICUSMARINE_SERVICE_USERNAME and COPERNICUSMARINE_SERVICE_PASSWORD environment variables.")
            print(f"Error details: {e}")
            raise RuntimeError(f"Copernicus Marine dataset download failed: {e}")
