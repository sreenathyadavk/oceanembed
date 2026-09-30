"""
Spatial Regridding Layer for OceanEmbed
Regrids arbitrary source grids onto the canonical 0.25° North Indian Ocean target grid [101, 241].
"""

import numpy as np
import xarray as xr
from typing import Optional, Tuple


class SpatialRegridder:
    """Regrids dataset or dataarray onto the canonical 0.25° grid."""

    def __init__(
        self,
        lat_min: float = 5.0,
        lat_max: float = 30.0,
        lon_min: float = 45.0,
        lon_max: float = 105.0,
        resolution: float = 0.25,
    ):
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.resolution = resolution

        # Create exact grid vectors: 101 lat cells, 241 lon cells
        self.target_lats = np.arange(lat_min, lat_max + resolution / 2.0, resolution)
        self.target_lons = np.arange(lon_min, lon_max + resolution / 2.0, resolution)

        assert len(self.target_lats) == 101, f"Expected 101 lats, got {len(self.target_lats)}"
        assert len(self.target_lons) == 241, f"Expected 241 lons, got {len(self.target_lons)}"

    def regrid_dataarray(
        self,
        da: xr.DataArray,
        method: str = "linear",
        extrapolate: bool = False,
    ) -> xr.DataArray:
        """Regrids a DataArray to the canonical target grid (101 x 241)."""
        # Ensure dimensions match latitude and longitude
        if "latitude" not in da.dims or "longitude" not in da.dims:
            raise ValueError(f"DataArray must have 'latitude' and 'longitude' dimensions. Found: {list(da.dims)}")

        # Subset slightly wider than target bounding box to prevent boundary NaNs
        lat_pad = self.resolution * 2
        lon_pad = self.resolution * 2
        
        sub_da = da.sel(
            latitude=slice(self.lat_min - lat_pad, self.lat_max + lat_pad),
            longitude=slice(self.lon_min - lon_pad, self.lon_max + lon_pad),
        )
        if sub_da.size == 0:
            sub_da = da  # Fallback to full array if slice empty

        # Interpolate onto target grid
        regridded = sub_da.interp(
            latitude=self.target_lats,
            longitude=self.target_lons,
            method=method,
            kwargs={"fill_value": "extrapolate" if extrapolate else np.nan},
        )
        
        return regridded

    def regrid_dataset(
        self,
        ds: xr.Dataset,
        method: str = "linear",
    ) -> xr.Dataset:
        """Regrids all variables in a Dataset to the canonical target grid."""
        regridded_ds = xr.Dataset(attrs=ds.attrs)
        for var in ds.data_vars:
            if "latitude" in ds[var].dims and "longitude" in ds[var].dims:
                regridded_ds[var] = self.regrid_dataarray(ds[var], method=method)
            else:
                regridded_ds[var] = ds[var]
        return regridded_ds
