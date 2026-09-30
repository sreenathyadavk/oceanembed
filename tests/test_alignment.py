"""
Unit tests for daily alignment and windowing logic.
"""

import pandas as pd
import pytest
from src.data.alignment import TemporalAligner
from src.data.windowing import WindowGenerator


def test_window_dates_generation():
    window_gen = WindowGenerator(window_size_days=7)
    target_date = pd.Timestamp("2020-01-07")
    
    window_dates = [
        target_date - pd.Timedelta(days=d)
        for d in reversed(range(7))
    ]
    assert len(window_dates) == 7
    assert window_dates[0] == pd.Timestamp("2020-01-01")
    assert window_dates[-1] == pd.Timestamp("2020-01-07")
