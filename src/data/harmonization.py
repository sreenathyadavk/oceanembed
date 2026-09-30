"""
Unit Harmonization Module for OceanEmbed
Standardizes variable names, coordinate systems, and unit conventions across providers.
"""

import xarray as xr
import numpy as np
from typing import Dict, Optional


class UnitHarmonizer:
    """Harmonizes raw data coordinates and units to canonical OceanEmbed standards."""

    CANONICAL_UNITS = {
        "SST": "degC",
        "SSS": "PSU",
        "SLA": "m",
        "U_current": "m/s",
        "V_current": "m/s",
        "U_wind": "m/s",
        "V_wind": "m/s",
        "temperature_profile": "degC",
    }

    VARIABLE_NAME_MAP = {
        "analysed_sst": "SST",
        "sst": "SST",
        "thetao": "temperature_profile",
        "sos": "SSS",
        "sss": "SSS",
        "sla": "SLA",
        "uo": "U_current",
        "vo": "V_current",
        "u10": "U_wind",
        "v10": "V_wind",
        "10u": "U_wind",
        "10v": "V_wind",
    }

    @classmethod
    def standardize_coordinates(cls, ds: xr.Dataset) -> xr.Dataset:
        """Standardizes dimension names to (time, depth, latitude, longitude) and sorts coordinates ascending."""
        coord_renames = {}
        for dim in ds.dims:
            dim_str = str(dim).lower()
            if dim_str in ["lat", "latitudes", "y"]:
                coord_renames[dim] = "latitude"
            elif dim_str in ["lon", "longitudes", "x"]:
                coord_renames[dim] = "longitude"
            elif dim_str in ["depth", "depth_m", "lev", "level", "z"]:
                coord_renames[dim] = "depth"
            elif dim_str in ["t", "time_counter", "valid_time"]:
                coord_renames[dim] = "time"
        
        if coord_renames:
            ds = ds.rename(coord_renames)
            
        # Ensure longitude is in [-180, 180] or [0, 360] canonical range (default Easting: 45 to 105)
        if "longitude" in ds.coords:
            lon_vals = ds["longitude"].values
            if np.any(lon_vals > 180):
                # Convert 0-360 to -180..180
                ds = ds.assign_coords(
                    longitude=(((ds.longitude + 180) % 360) - 180)
                )

        # Sort coordinates ascending
        for coord in ["latitude", "longitude", "depth", "time"]:
            if coord in ds.coords and len(ds[coord]) > 1:
                ds = ds.sortby(coord)
                
        return ds

    @classmethod
    def convert_units(cls, da: xr.DataArray, var_name: str) -> xr.DataArray:
        """Converts DataArray values to canonical unit (e.g., Kelvin -> °C)."""
        attrs = da.attrs
        unit = str(attrs.get("units", "")).lower()

        # Temperature Kelvin -> Celsius conversion check
        if var_name == "SST" or var_name == "temperature_profile":
            if "k" in unit or "kelvin" in unit or (da.mean(skipna=True) > 200.0):
                da = da - 273.15
                da.attrs["units"] = "degC"
            else:
                da.attrs["units"] = "degC"
        elif var_name in cls.CANONICAL_UNITS:
            da.attrs["units"] = cls.CANONICAL_UNITS[var_name]

        return da
