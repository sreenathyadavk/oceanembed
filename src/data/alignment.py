"""
Temporal Alignment Layer for OceanEmbed
Aligns raw data to daily timestamps, verifies gaps, and builds daily synchronized datasets.
"""

import numpy as np
import pandas as pd
import xarray as xr
from typing import Optional, Tuple, List


class TemporalAligner:
    """Resamples raw time series to clean daily mean timestamps without silent gap filling."""

    def __init__(self, max_allowed_gap_days: int = 1):
        self.max_allowed_gap_days = max_allowed_gap_days

    @staticmethod
    def align_to_daily(
        ds: xr.Dataset,
        time_dim: str = "time",
        method: str = "mean",
    ) -> xr.Dataset:
        """Aggregates sub-daily measurements to daily mean timestamps normalized to 00:00:00."""
        if time_dim not in ds.dims and time_dim not in ds.coords:
            raise ValueError(f"Time dimension '{time_dim}' not found in dataset.")

        # Floor timestamps to start of day YYYY-MM-DD
        daily_ds = ds.resample({time_dim: "1D"}).mean(dim=time_dim, skipna=True)
        return daily_ds

    def check_temporal_continuity(
        self,
        time_index: pd.DatetimeIndex,
    ) -> Tuple[bool, List[pd.Timestamp]]:
        """Checks if a daily timestamp index is continuous without gaps larger than max_allowed_gap_days."""
        if len(time_index) <= 1:
            return True, []

        diffs = (time_index[1:] - time_index[:-1]).days
        gap_indices = np.where(diffs > self.max_allowed_gap_days)[0]
        
        missing_gaps = []
        for idx in gap_indices:
            missing_start = time_index[idx] + pd.Timedelta(days=1)
            missing_end = time_index[idx + 1] - pd.Timedelta(days=1)
            missing_gaps.append((missing_start, missing_end))

        is_continuous = len(gap_indices) == 0
        return is_continuous, missing_gaps
