"""
Download Script for OceanEmbed
Programmatically downloads surface satellite/reanalysis input variables and GLORYS subsurface target subsets.
"""

import os
import sys
import yaml
import argparse
from src.data.sources import CopernicusMarineAdapter, NOAAOISSTAdapter, ERA5Adapter


def main():
    parser = argparse.ArgumentParser(description="Download OceanEmbed Data Subsets")
    parser.add_argument("--start-date", type=str, default="2020-01-01")
    parser.add_argument("--end-date", type=str, default="2020-01-07")
    parser.add_argument("--source", type=str, choices=["copernicus", "noaa", "era5", "all"], default="copernicus")
    args = parser.parse_args()

    with open("configs/data.yaml", "r") as f:
        data_config = yaml.safe_load(f)
    with open("configs/paths.yaml", "r") as f:
        path_config = yaml.safe_load(f)

    domain = data_config["domain"]
    raw_dir = path_config["paths"]["local"]["raw_dir"]

    print(f"=== OceanEmbed Data Downloader ===")
    print(f"Target Domain: {domain['lat_min']}°N–{domain['lat_max']}°N, {domain['lon_min']}°E–{domain['lon_max']}°E")
    print(f"Date Range:    {args.start_date} to {args.end_date}")

    if args.source in ["copernicus", "all"]:
        copernicus = CopernicusMarineAdapter(raw_dir=raw_dir)
        try:
            copernicus.fetch_glorys_target(
                start_date=args.start_date,
                end_date=args.end_date,
                lat_min=domain["lat_min"],
                lat_max=domain["lat_max"],
                lon_min=domain["lon_min"],
                lon_max=domain["lon_max"],
            )
        except Exception as e:
            print(f"Copernicus download encountered issue: {e}")

    if args.source in ["noaa", "all"]:
        noaa = NOAAOISSTAdapter(raw_dir=raw_dir)
        try:
            noaa.fetch_oisst_subset(
                start_date=args.start_date,
                end_date=args.end_date,
                lat_min=domain["lat_min"],
                lat_max=domain["lat_max"],
                lon_min=domain["lon_min"],
                lon_max=domain["lon_max"],
            )
        except Exception as e:
            print(f"NOAA OISST download encountered issue: {e}")


if __name__ == "__main__":
    main()
