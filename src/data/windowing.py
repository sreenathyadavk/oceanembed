"""
Temporal Window Generator for OceanEmbed
Constructs trailing T-day temporal window feature tensors [T, 7, 101, 241] ending on target day t.
"""

import numpy as np
import pandas as pd
import xarray as xr
from typing import List, Tuple, Dict, Optional


class WindowGenerator:
    """Constructs temporal sliding windows [T, 7, H, W] for model inputs."""

    FEATURE_ORDER = [
        "SST",
        "SSS",
        "SLA",
        "U_current",
        "V_current",
        "U_wind",
        "V_wind",
    ]

    def __init__(self, window_size_days: int = 7):
        self.window_size_days = window_size_days

    def create_window_sample(
        self,
        surface_ds: xr.Dataset,
        target_date: pd.Timestamp,
    ) -> Tuple[np.ndarray, List[pd.Timestamp]]:
        """Constructs input feature tensor [T, 7, H, W] for target_date t, using trailing dates [t-T+1, ..., t].
        
        Returns:
            X: numpy array of shape [T, 7, H, W]
            window_dates: list of T Timestamps
        """
        target_ts = pd.to_datetime(target_date)
        window_dates = [
            target_ts - pd.Timedelta(days=d)
            for d in reversed(range(self.window_size_days))
        ]

        # Verify all window dates exist in dataset
        available_times = pd.to_datetime(surface_ds["time"].values)
        for date in window_dates:
            if date not in available_times:
                raise ValueError(
                    f"Required date {date.strftime('%Y-%m-%d')} for T={self.window_size_days} window "
                    f"ending on {target_ts.strftime('%Y-%m-%d')} is missing from dataset."
                )

        # Extract [T, 7, H, W] tensor
        T = self.window_size_days
        num_vars = len(self.FEATURE_ORDER)
        
        # Determine spatial dimensions
        H = len(surface_ds["latitude"])
        W = len(surface_ds["longitude"])

        X = np.empty((T, num_vars, H, W), dtype=np.float32)

        for t_idx, date in enumerate(window_dates):
            date_ds = surface_ds.sel(time=date)
            for v_idx, var_name in enumerate(self.FEATURE_ORDER):
                if var_name not in date_ds:
                    raise KeyError(f"Variable '{var_name}' missing in surface dataset for date {date}.")
                X[t_idx, v_idx, :, :] = date_ds[var_name].values

        return X, window_dates
