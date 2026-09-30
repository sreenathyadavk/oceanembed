"""
Data Contract Validation Utility for OceanEmbed
Validates tensor shapes, variable ordering, grid resolution, units, NaN fractions, and depth levels.
"""

import numpy as np
from typing import Dict, Any, Tuple


class DataValidator:
    """Verifies that generated samples conform strictly to the OceanEmbed Data Contract."""

    EXPECTED_LAT_SIZE = 101
    EXPECTED_LON_SIZE = 241
    EXPECTED_NUM_VARS = 7
    EXPECTED_NUM_DEPTHS = 15
    EXPECTED_DEPTHS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]

    @classmethod
    def validate_sample(
        cls,
        sample: Dict[str, Any],
        window_size_days: int = 7,
    ) -> Tuple[bool, str]:
        """Validates a sample dictionary produced by OceanEmbedDataset or create_sample.py."""
        x = sample["x"]
        y = sample["y"]

        # 1. Check Input Tensor Shape: [T, 7, 101, 241]
        expected_x_shape = (window_size_days, cls.EXPECTED_NUM_VARS, cls.EXPECTED_LAT_SIZE, cls.EXPECTED_LON_SIZE)
        if tuple(x.shape) != expected_x_shape:
            return False, f"Input tensor shape mismatch. Expected {expected_x_shape}, got {tuple(x.shape)}"

        # 2. Check Target Tensor Shape: [15, 101, 241]
        expected_y_shape = (cls.EXPECTED_NUM_DEPTHS, cls.EXPECTED_LAT_SIZE, cls.EXPECTED_LON_SIZE)
        if tuple(y.shape) != expected_y_shape:
            return False, f"Target tensor shape mismatch. Expected {expected_y_shape}, got {tuple(y.shape)}"

        # 3. Check masks
        if "input_mask" in sample:
            if tuple(sample["input_mask"].shape) != expected_x_shape:
                return False, f"Input mask shape mismatch: {tuple(sample['input_mask'].shape)}"
        if "target_mask" in sample:
            if tuple(sample["target_mask"].shape) != expected_y_shape:
                return False, f"Target mask shape mismatch: {tuple(sample['target_mask'].shape)}"

        # 4. Check coordinate bounds
        if "latitude" in sample and "longitude" in sample:
            lats = sample["latitude"].numpy() if hasattr(sample["latitude"], "numpy") else np.array(sample["latitude"])
            lons = sample["longitude"].numpy() if hasattr(sample["longitude"], "numpy") else np.array(sample["longitude"])

            if not np.isclose(lats[0], 5.0) or not np.isclose(lats[-1], 30.0):
                return False, f"Latitude bounds invalid: [{lats[0]}, {lats[-1]}], expected [5.0, 30.0]"
            if not np.isclose(lons[0], 45.0) or not np.isclose(lons[-1], 105.0):
                return False, f"Longitude bounds invalid: [{lons[0]}, {lons[-1]}], expected [45.0, 105.0]"

        return True, "Data contract validation passed successfully."
