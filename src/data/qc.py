"""
Quality Control (QC) Layer for OceanEmbed
Handles missing values, NaNs, impossible physical ranges, fill values, and quality flags.
"""

import numpy as np
import xarray as xr
from typing import Dict, Optional, Tuple, Union


class QualityControl:
    """Scientifically defensible Quality Control processor."""

    PHYSICAL_RANGES = {
        "SST": (-2.0, 40.0),       # °C
        "SSS": (0.0, 45.0),        # PSU
        "SLA": (-3.0, 3.0),        # meters
        "U_current": (-10.0, 10.0),# m/s
        "V_current": (-10.0, 10.0),# m/s
        "U_wind": (-60.0, 60.0),   # m/s
        "V_wind": (-60.0, 60.0),   # m/s
        "temperature_profile": (-2.0, 35.0), # °C
    }

    def __init__(self, physical_ranges: Optional[Dict[str, Tuple[float, float]]] = None):
        self.ranges = physical_ranges or self.PHYSICAL_RANGES

    def apply_qc(
        self,
        ds: Union[xr.Dataset, xr.DataArray],
        var_name: str,
        qc_flag_da: Optional[xr.DataArray] = None,
        valid_flags: Optional[list] = None,
    ) -> Union[xr.Dataset, xr.DataArray]:
        """Apply QC filters to dataset or dataarray, masking invalid observations with NaN.
        
        Preserves existing NaNs (land mask) and replaces physically impossible values or bad QC flags.
        """
        data = ds.copy(deep=True)
        
        # 1. Flag-based QC filtering if source flags are available
        if qc_flag_da is not None and valid_flags is not None:
            mask = qc_flag_da.isin(valid_flags)
            data = data.where(mask, np.nan)
        
        # 2. Physical range checking
        if var_name in self.ranges:
            low, high = self.ranges[var_name]
            if isinstance(data, xr.Dataset):
                if var_name in data:
                    data[var_name] = data[var_name].where(
                        (data[var_name] >= low) & (data[var_name] <= high), np.nan
                    )
            elif isinstance(data, xr.DataArray):
                data = data.where((data >= low) & (data <= high), np.nan)

        return data

    @staticmethod
    def get_validity_mask(array: np.ndarray) -> np.ndarray:
        """Returns boolean validity mask (True for valid data, False for NaN/land)."""
        return ~np.isnan(array)

    @staticmethod
    def calculate_missing_fraction(array: np.ndarray) -> float:
        """Calculate fraction of NaN values in array."""
        if array.size == 0:
            return 1.0
        return float(np.isnan(array).sum() / array.size)
