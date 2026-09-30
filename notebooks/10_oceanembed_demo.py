import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import torch
from src.models.tc_resunet import TCResUNet

def run_demo(target_date_idx=10):
    DATA_DIR = "data/processed"
    
    # 1. Load trained model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = TCResUNet(in_channels=49, out_channels=15, base_c=32).to(device)
    model.load_state_dict(torch.load("checkpoints/tc_resunet_best.pt", map_location=device, weights_only=True))
    model.eval()
    
    # 2. Select Date
    X_test = xr.open_dataset(os.path.join(DATA_DIR, "X_test_norm.nc"))
    Y_test = xr.open_dataset(os.path.join(DATA_DIR, "Y_test.nc"))
    
    # Extract 7 days (Window)
    X_v = list(X_test.data_vars.values())[0] if hasattr(X_test, 'data_vars') else X_test
    Y_v = list(Y_test.data_vars.values())[0] if hasattr(Y_test, 'data_vars') else Y_test
    window_X = X_v.values[target_date_idx : target_date_idx + 7]
    target_Y = Y_test['thetao'].values[target_date_idx + 6]
    target_datetime = Y_test['time'].values[target_date_idx + 6]
    
    print(f"\\n--- OCEANEMBED SIH DEMO ---")
    print(f"Target Date Analyzed: {target_datetime}")
    
    # Prepare PyTorch payload
    C, V, H, W = window_X.shape
    x_flat = window_X.reshape(C * V, H, W)
    x_clean = np.nan_to_num(x_flat, nan=0.0)
    
    X_tensor = torch.tensor(x_clean).unsqueeze(0).to(device).float()
    
    try:
        import pickle
        with open(os.path.join(DATA_DIR, "norm_params.pkl"), "rb") as f:
            norm_stats = pickle.load(f)
            y_mean = float(norm_stats['Y']['mean'])
            y_std = float(norm_stats['Y']['std'])
    except Exception as e:
        print(f"Warning: Failed to fetch Y denormalization attributes! Defaulting. ({e})")
        y_mean, y_std = 0.0, 1.0
        
    # Inference
    with torch.no_grad():
        pred_Y = model(X_tensor).cpu().numpy()[0]
        pred_Y = pred_Y * y_std + y_mean
        
    y_mask = ~np.isnan(target_Y)
    pred_Y_masked = np.where(y_mask, pred_Y, np.nan)
    
    DEPTH_LEVELS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]
    
    target_depths_idx = [0, 7, 12, 14] # 0m, 100m, 500m, 1000m
    
    print("Saving Visualizations to reports/figures/...")
    os.makedirs("reports/figures", exist_ok=True)
    
    # Plot Maps
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle(f"OceanEmbed TC-ResUNet Map - {np.datetime_as_string(target_datetime, unit='D')}", fontsize=16)
    
    for i, d_idx in enumerate(target_depths_idx):
        depth_label = DEPTH_LEVELS[d_idx]
        
        ax_true = axes[0, i]
        im_true = ax_true.imshow(target_Y[d_idx], origin='lower', cmap='turbo')
        ax_true.set_title(f"Target (GLORYS) - {depth_label}m")
        plt.colorbar(im_true, ax=ax_true, fraction=0.046, pad=0.04)
        
        ax_pred = axes[1, i]
        im_pred = ax_pred.imshow(pred_Y_masked[d_idx], origin='lower', cmap='turbo')
        ax_pred.set_title(f"Prediction - {depth_label}m")
        plt.colorbar(im_pred, ax=ax_pred, fraction=0.046, pad=0.04)
        
    plt.tight_layout()
    plt.savefig("reports/figures/sih_demo_maps.png")
    plt.close()
    
    # 5. Vertical Profile Comparison at a specific central coordinate
    lat_idx, lon_idx = H//2, W//2  # center of grid (roughly 17.5N, 75E depending on grid)
    
    prof_true = target_Y[:, lat_idx, lon_idx]
    prof_pred = pred_Y_masked[:, lat_idx, lon_idx]
    
    if np.isnan(prof_true).all():
        print("Warning: Central coordinate is on land. Selecting arbitrary water column...")
        # find first valid water column
        water_cols = np.where(y_mask[0])
        if len(water_cols[0]) > 0:
            lat_idx, lon_idx = water_cols[0][0], water_cols[1][0]
            prof_true = target_Y[:, lat_idx, lon_idx]
            prof_pred = pred_Y_masked[:, lat_idx, lon_idx]
            
    fig2 = plt.figure(figsize=(6, 8))
    plt.plot(prof_true, DEPTH_LEVELS, 'k-', linewidth=2, label="GLORYS Target")
    plt.plot(prof_pred, DEPTH_LEVELS, 'r--', linewidth=2, label="TC-ResUNet")
    plt.gca().invert_yaxis()
    plt.title(f"Vertical Temperature Profile ({X_test.latitude.values[lat_idx]:.1f}N, {X_test.longitude.values[lon_idx]:.1f}E)")
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Depth (m)")
    plt.legend()
    plt.grid(True)
    plt.savefig("reports/figures/sih_demo_profile.png")
    plt.close()
    
    print("Demo execution successfully output visualization grids!")

if __name__ == "__main__":
    run_demo(10)
    
