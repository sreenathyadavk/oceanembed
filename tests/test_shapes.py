"""
Unit tests asserting exact tensor shape contracts [T, 7, 101, 241] and [15, 101, 241].
"""

import numpy as np
import pytest
from src.data.validation import DataValidator


def test_data_validator_contract():
    window_size_days = 7
    H, W = 101, 241

    sample = {
        "x": np.zeros((window_size_days, 7, H, W), dtype=np.float32),
        "y": np.zeros((15, H, W), dtype=np.float32),
        "input_mask": np.ones((window_size_days, 7, H, W), dtype=bool),
        "target_mask": np.ones((15, H, W), dtype=bool),
        "latitude": np.arange(5.0, 30.25, 0.25),
        "longitude": np.arange(45.0, 105.25, 0.25),
    }

    is_valid, msg = DataValidator.validate_sample(sample, window_size_days=window_size_days)
    assert is_valid, f"Validation failed: {msg}"
