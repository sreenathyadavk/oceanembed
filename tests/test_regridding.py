"""
Unit tests for spatial regridding functionality.
"""

import xarray as xr
import numpy as np
import pytest
from src.data.regridding import SpatialRegridder


def test_regrid_dataarray_shape():
    regridder = SpatialRegridder(
        lat_min=5.0, lat_max=30.0, lon_min=45.0, lon_max=105.0, resolution=0.25
    )
    # Create coarse 1° source grid
    src_lats = np.arange(4.0, 32.0, 1.0)
    src_lons = np.arange(44.0, 106.0, 1.0)
    data = np.random.rand(len(src_lats), len(src_lons)).astype(np.float32)

    da_src = xr.DataArray(
        data,
        coords={"latitude": src_lats, "longitude": src_lons},
        dims=["latitude", "longitude"],
    )

    da_regridded = regridder.regrid_dataarray(da_src, method="linear")
    assert da_regridded.shape == (101, 241)
