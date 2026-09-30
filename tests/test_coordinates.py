"""
Unit tests for coordinate system grid bounds and target dimension sizes.
"""

import numpy as np
import pytest
from src.data.regridding import SpatialRegridder


def test_regridder_grid_dimensions():
    regridder = SpatialRegridder(
        lat_min=5.0,
        lat_max=30.0,
        lon_min=45.0,
        lon_max=105.0,
        resolution=0.25,
    )
    assert len(regridder.target_lats) == 101
    assert len(regridder.target_lons) == 241
    assert np.isclose(regridder.target_lats[0], 5.0)
    assert np.isclose(regridder.target_lats[-1], 30.0)
    assert np.isclose(regridder.target_lons[0], 45.0)
    assert np.isclose(regridder.target_lons[-1], 105.0)
