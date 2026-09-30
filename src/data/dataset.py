import torch
from torch.utils.data import Dataset
import numpy as np
import pickle
import os
import xarray as xr

class OceanEmbedDataset(Dataset):
    def __init__(self, X_xr, Y_xr, window_size=7):
        """
        X_xr: harmonized Xarray DataArray [time, variable, lat, lon]
        Y_xr: harmonized Yarray DataArray [time, depth, lat, lon]
        """
        # Ensure safe extraction of values from either DataArrays or Datasets gracefully
        if hasattr(X_xr, 'data_vars'): X_xr = list(X_xr.data_vars.values())[0]
        if hasattr(Y_xr, 'data_vars'): Y_xr = list(Y_xr.data_vars.values())[0]
        
        self.X_data = X_xr
        self.Y_data = Y_xr
        
        self.window_size = window_size
        self.num_samples = len(self.X_data) - window_size + 1
        
        try:
            with open("data/processed/norm_params.pkl", "rb") as f:
                stats = pickle.load(f)
                self.x_mean = np.array(stats['X']['mean']).reshape((1, -1, 1, 1)).astype(np.float32)
                self.x_std = np.array(stats['X']['std']).reshape((1, -1, 1, 1)).astype(np.float32)
                self.y_mean = float(stats['Y']['mean'])
                self.y_std = float(stats['Y']['std'])
        except Exception as e:
            print(f"Warning: Norm params locally missing! {e}")
            self.x_mean, self.x_std = 0.0, 1.0
            self.y_mean, self.y_std = 0.0, 1.0
        
    def __len__(self):
        return self.num_samples
        
    def __getitem__(self, idx):
        # Extract purely temporal lagging window [t, t+window_size-1] lazily dynamically
        x_window = self.X_data.isel(time=slice(idx, idx + self.window_size)).values.astype(np.float32)
        y_target = self.Y_data.isel(time=idx + self.window_size - 1).values.astype(np.float32)
        # Transform Y from Xarray (Lat, Lon, Depth) to PyTorch native canonical (Depth, Lat, Lon)
        y_target = y_target.transpose(2, 0, 1)
        
        # Apply strict parameters seamlessly resolving normalization on-the-fly dynamically
        x_window = (x_window - self.x_mean) / self.x_std
        y_target = (y_target - self.y_mean) / self.y_std
        
        C, V, H, W = x_window.shape
        x_flat = x_window.transpose(1, 0, 2, 3).reshape(C * V, H, W)
        
        # Native representations preserve NaNs explicitly.
        # Deep learning models cannot interpret NaNs perfectly without explicit structural padding zeros + masking flags.
        # To handle this dynamically, we synthesize an input mask locating valid numeric points:
        x_mask = ~np.isnan(x_flat)
        y_mask = ~np.isnan(y_target)
        
        # Fill NaNs with 0 in the payload array (the network will multiply by masks theoretically, or gradients ignore them natively)
        x_clean = np.nan_to_num(x_flat, nan=0.0)
        y_clean = np.nan_to_num(y_target, nan=0.0)
        
        return {
            'X': torch.tensor(x_clean),
            'X_mask': torch.tensor(x_mask).float(),
            'Y': torch.tensor(y_clean),
            'Y_mask': torch.tensor(y_mask).float()
        }
