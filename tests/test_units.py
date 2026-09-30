"""
Unit tests for unit conversion and harmonization logic.
"""

import xarray as xr
import numpy as np
import pytest
from src.data.harmonization import UnitHarmonizer


def test_kelvin_to_celsius_conversion():
    da_kelvin = xr.DataArray(
        np.array([298.15, 300.15], dtype=np.float32),
        dims=["time"],
        attrs={"units": "Kelvin"},
    )
    da_converted = UnitHarmonizer.convert_units(da_kelvin, "SST")
    assert np.allclose(da_converted.values, [25.0, 27.0])
    assert da_converted.attrs["units"] == "degC"


def test_celsius_preservation():
    da_celsius = xr.DataArray(
        np.array([25.0, 27.0], dtype=np.float32),
        dims=["time"],
        attrs={"units": "degC"},
    )
    da_converted = UnitHarmonizer.convert_units(da_celsius, "SST")
    assert np.allclose(da_converted.values, [25.0, 27.0])
