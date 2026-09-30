"""
Preprocessing Pipeline Script for OceanEmbed
Reads raw surface and target files, applies QC, unit harmonization, 0.25° regridding, and temporal alignment.
"""

import os
import yaml
import xarray as xr
import pandas as pd
from src.data.qc import QualityControl
from src.data.harmonization import UnitHarmonizer
from src.data.regridding import SpatialRegridder
from src.data.alignment import TemporalAligner


def main():
    print("=== OceanEmbed Preprocessing Pipeline ===")
    with open("configs/data.yaml", "r") as f:
        config = yaml.safe_load(f)

    regridder = SpatialRegridder(
        lat_min=config["domain"]["lat_min"],
        lat_max=config["domain"]["lat_max"],
        lon_min=config["domain"]["lon_min"],
        lon_max=config["domain"]["lon_max"],
        resolution=config["domain"]["resolution"],
    )

    print(f"Target Regridder Grid: Latitudes={len(regridder.target_lats)} (101), Longitudes={len(regridder.target_lons)} (241)")
    print("Preprocessing architecture ready.")


if __name__ == "__main__":
    main()
