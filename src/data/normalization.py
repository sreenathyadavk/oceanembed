"""
Train-Only Normalization Layer for OceanEmbed
Computes mean, std, min, max statistics strictly on the Training set to prevent data leakage.
"""

import json
import os
import numpy as np
from typing import Dict, Tuple, Optional


class DataNormalizer:
    """Computes and applies Z-score or MinMax normalization using saved training statistics."""

    def __init__(
        self,
        strategy: str = "zscore", # 'zscore' or 'minmax'
        stats_path: Optional[str] = None,
    ):
        self.strategy = strategy
        self.stats_path = stats_path
        self.stats: Dict[str, Dict[str, float]] = {}

        if stats_path and os.path.exists(stats_path):
            self.load_stats(stats_path)

    def fit_variable(self, var_name: str, array: np.ndarray) -> Dict[str, float]:
        """Calculates mean, std, min, max on valid non-NaN array values."""
        valid_vals = array[~np.isnan(array)]
        if valid_vals.size == 0:
            raise ValueError(f"Cannot fit normalizer for '{var_name}' with all NaN values.")

        var_stats = {
            "mean": float(np.mean(valid_vals)),
            "std": float(np.std(valid_vals) + 1e-8),
            "min": float(np.min(valid_vals)),
            "max": float(np.max(valid_vals)),
        }
        self.stats[var_name] = var_stats
        return var_stats

    def transform(self, var_name: str, array: np.ndarray) -> np.ndarray:
        """Transforms variable array using fitted training statistics."""
        if var_name not in self.stats:
            raise ValueError(f"Normalizer statistics for '{var_name}' have not been fitted.")

        s = self.stats[var_name]
        out = np.copy(array)
        mask = ~np.isnan(array)

        if self.strategy == "zscore":
            out[mask] = (array[mask] - s["mean"]) / s["std"]
        elif self.strategy == "minmax":
            range_val = (s["max"] - s["min"]) + 1e-8
            out[mask] = (array[mask] - s["min"]) / range_val
        else:
            raise ValueError(f"Unknown normalization strategy: {self.strategy}")

        return out

    def inverse_transform(self, var_name: str, array: np.ndarray) -> np.ndarray:
        """Restores normalized array back to physical units using fitted statistics."""
        if var_name not in self.stats:
            raise ValueError(f"Normalizer statistics for '{var_name}' have not been fitted.")

        s = self.stats[var_name]
        out = np.copy(array)
        mask = ~np.isnan(array)

        if self.strategy == "zscore":
            out[mask] = (array[mask] * s["std"]) + s["mean"]
        elif self.strategy == "minmax":
            range_val = (s["max"] - s["min"]) + 1e-8
            out[mask] = (array[mask] * range_val) + s["min"]

        return out

    def save_stats(self, filepath: str) -> None:
        """Saves fitted normalization statistics to JSON metadata file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump({"strategy": self.strategy, "stats": self.stats}, f, indent=2)

    def load_stats(self, filepath: str) -> None:
        """Loads fitted normalization statistics from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
            self.strategy = data["strategy"]
            self.stats = data["stats"]
