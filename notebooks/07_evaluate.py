import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.tc_resunet import TCResUNet
from src.baselines.climatology import MonthlyClimatologyBaseline
from src.evaluation.metrics import calculate_depthwise_metrics
from src.data.dataset import OceanEmbedDataset
import xarray as xr
from torch.utils.data import DataLoader
import torch
import numpy as np
import json

DEPTH_LEVELS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]

def md_table_row(depth, rmse, mae, bias, corr):
    return f"| {depth}m | {rmse:.4f} | {mae:.4f} | {bias:.4f} | {corr:.4f} |\\n"

def main():
    DATA_DIR = "data/processed"
    REPORT_PATH = "reports/BASELINE_RESULTS.md"
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    
    print("Loading Processed NetCDF Splits...")
    Y_train_ds = xr.open_dataset(os.path.join(DATA_DIR, "Y_train.nc"))
    X_test_ds = xr.open_dataset(os.path.join(DATA_DIR, "X_test.nc"))
    Y_test_ds = xr.open_dataset(os.path.join(DATA_DIR, "Y_test.nc"))
    
    Y_train = list(Y_train_ds.data_vars.values())[0] if hasattr(Y_train_ds, 'data_vars') else Y_train_ds
    X_test = list(X_test_ds.data_vars.values())[0] if hasattr(X_test_ds, 'data_vars') else X_test_ds
    Y_test = list(Y_test_ds.data_vars.values())[0] if hasattr(Y_test_ds, 'data_vars') else Y_test_ds
    
    Y_arr = Y_test.values
    test_mask = ~np.isnan(Y_arr)
    # Use spatial geographic mask dropping zero variance bounds explicitly natively
    geo_mask = test_mask.any(axis=0)[..., 0]
    
    # ---------------------------
    # CLIMATOLOGY BASELINE
    # ---------------------------
    print("Executing Climatology Baseline...")
    climatology = MonthlyClimatologyBaseline()
    climatology.fit(Y_train)
    
    # Extract prediction natively
    clim_pred = climatology.predict(Y_test)
    clim_pred = clim_pred.transpose(0, 3, 1, 2)
    Y_arr_trans = Y_arr.transpose(0, 3, 1, 2)
    
    clim_metrics = calculate_depthwise_metrics(clim_pred, Y_arr_trans, geo_mask)
    
    # ---------------------------
    # TC-RESUNET TEST PASS
    # ---------------------------
    print("Executing TC-ResUNet Inference...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = TCResUNet(in_channels=49, out_channels=15, base_c=32).to(device)
    model.load_state_dict(torch.load("checkpoints/tc_resunet_best.pt", map_location=device, weights_only=True))
    model.eval()
    
    test_dataset = OceanEmbedDataset(
        X_test['__xarray_dataarray_variable__'] if '__xarray_dataarray_variable__' in X_test else X_test, 
        Y_test['thetao'] if 'thetao' in Y_test else Y_test, 
        window_size=7
    )
    test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)
    
    net_preds = []
    net_targets = []
    
    try:
        with open(os.path.join(DATA_DIR, "norm_params.pkl"), "rb") as f:
            import pickle
            norm_stats = pickle.load(f)
            # The format we saved was: pickle.dump({'X': norm_params, 'Y': y_norm_params}, f)
            y_mean = float(norm_stats['Y']['mean'])
            y_std = float(norm_stats['Y']['std'])
    except Exception as e:
        print(f"Warning: Failed to fetch Y denormalization attributes! Defaulting. ({e})")
        y_mean, y_std = 0.0, 1.0
        
    with torch.no_grad():
        for batch in test_loader:
            X = batch['X'].to(device)
            # Y inside DataLoader is natively Y_test NORMALIZED 
            Y = batch['Y'].numpy()
            
            pred = model(X).cpu().numpy()
            
            # Explicitly reverse normalization returning values smoothly to absolute geometries
            pred_denorm = pred * y_std + y_mean
            Y_denorm = Y * y_std + y_mean
            
            # We don't transpose to match climatology anymore. Model natively yields [B, 15, H, W]
            pass
            
            net_preds.append(pred_denorm)
            net_targets.append(Y_denorm)
            
    net_preds = np.concatenate(net_preds, axis=0)      # [T-window, 15, H, W]
    net_targets = np.concatenate(net_targets, axis=0)
    
    # Slice the temporal arrays matching identical evaluation matrix sizes identically cleanly organically
    Y_arr_sliced = Y_arr[6:]
    Y_arr_sliced = Y_arr_sliced.transpose(0, 3, 1, 2)
    
    # Asserting dimensions explicitly as requested
    assert net_preds.shape == (104, 15, 101, 241), f"Prediction shape mismatch! Found {net_preds.shape}"
    assert Y_arr_sliced.shape == (104, 15, 101, 241), f"Target shape mismatch! Found {Y_arr_sliced.shape}"
    
    net_metrics = calculate_depthwise_metrics(net_preds, Y_arr_sliced, geo_mask)
    
    # ---------------------------
    # GENERATE REPORT
    # ---------------------------
    print("Writing BASELINE_RESULTS.md...")
    with open(REPORT_PATH, "w") as f:
        f.write("# OceanEmbed Evaluation Report (SIH Prototype)\\n\\n")
        f.write(f"**Test Split Dates:** {Y_test.time.values[0]} to {Y_test.time.values[-1]}\\n")
        f.write(f"**Geographic Scope:** 5N-30N, 45E-105E (0.25°)\\n\\n")
        
        f.write("## 1. Climatology Baseline\\n")
        f.write("| Depth | RMSE | MAE | Bias | Correlation |\\n")
        f.write("|---|---|---|---|---|\\n")
        for i, d in enumerate(DEPTH_LEVELS):
            f.write(md_table_row(d, clim_metrics['rmse'][i], clim_metrics['mae'][i], clim_metrics['bias'][i], clim_metrics['corr'][i]))
            
        f.write("\\n## 2. TC-ResUNet Prototype\\n")
        f.write("| Depth | RMSE | MAE | Bias | Correlation |\\n")
        f.write("|---|---|---|---|---|\\n")
        for i, d in enumerate(DEPTH_LEVELS):
            f.write(md_table_row(d, net_metrics['rmse'][i], net_metrics['mae'][i], net_metrics['bias'][i], net_metrics['corr'][i]))

if __name__ == "__main__":
    main()
