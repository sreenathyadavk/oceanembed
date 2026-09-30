import os
import json
import torch
import numpy as np
import xarray as xr
from pathlib import Path
import pickle
import sys

# Ensure src module is discoverable
sys.path.append(os.getcwd())
from src.models.tc_resunet import TCResUNet

def run():
    print("Exporting static arrays for Netlify offline demo...")
    frontend_data_dir = Path("/home/sreenath/Downloads/oceanembed/public/data/oceanembed")
    frontend_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Data
    X_TEST = xr.open_dataset('data/processed/X_test.nc')
    Y_TEST = xr.open_dataset('data/processed/Y_test.nc')
    
    x_test_vars = X_TEST['__xarray_dataarray_variable__'].values if '__xarray_dataarray_variable__' in X_TEST else list(X_TEST.data_vars.values())[0].values
    y_test_vars = Y_TEST['thetao'].values if 'thetao' in Y_TEST else list(Y_TEST.data_vars.values())[0].values
    
    # 2. Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = TCResUNet(in_channels=49, out_channels=15).to(device)
    model.load_state_dict(torch.load('checkpoints/tc_resunet_best.pt', map_location=device, weights_only=True))
    model.eval()
    
    # Export specific indices representing the test split
    demo_indices = [0, 25, 50, 75, 100]
    
    with open('data/processed/norm_params.pkl', 'rb') as f:
        params = pickle.load(f)
        Y_MEAN = float(params['Y']['mean'])
        Y_STD = float(params['Y']['std'])
        x_mean = np.array(params['X']['mean']).reshape((1, -1, 1, 1)).astype(np.float32)
        x_std = np.array(params['X']['std']).reshape((1, -1, 1, 1)).astype(np.float32)
    
    for idx in demo_indices:
        print(f"Exporting frame {idx}...")
        try:
            # Match exactly how backend/main.py extracted windows
            x_window = x_test_vars[idx : idx + 7] # [7, 7, 101, 241]
            target_dt = idx + 6
            y_target = y_test_vars[target_dt] # [101, 241, 15]

            # Normalize inputs
            x_norm = (x_window - x_mean) / x_std
            x_norm = np.nan_to_num(x_norm, nan=0.0)

            C, V, H, W = x_norm.shape
            x_flat = x_norm.transpose(1, 0, 2, 3).reshape(C * V, H, W)

            x_tensor = torch.tensor(x_flat).unsqueeze(0).float().to(device)
            with torch.no_grad():
                pred = model(x_tensor).cpu().numpy()[0] # [15, 101, 241]
            
            # Denormalize predictions
            pred_denorm = (pred * Y_STD) + Y_MEAN # [15, 101, 241]
            
            # Transpose targets to match [15, 101, 241]
            y_target_trans = y_target.transpose(2, 0, 1)
            
            predictions = []
            ground_truth = []
            for d in range(15):
                # Apply land mask accurately from truth
                p_layer = np.where(np.isnan(y_target_trans[d]), -999.0, pred_denorm[d])
                g_layer = np.where(np.isnan(y_target_trans[d]), -999.0, y_target_trans[d])
                
                # Rounding vastly reduces JSON payload size safely
                predictions.append(np.round(p_layer, 2).tolist())
                ground_truth.append(np.round(g_layer, 2).tolist())
            
            payload = {
                "time_index": idx,
                "depths": [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000],
                "predictions": predictions,
                "ground_truth": ground_truth
            }
            
            with open(frontend_data_dir / f"predict_{idx}.json", "w") as f:
                json.dump(payload, f)
        except Exception as e:
            print(f"Error at {idx}: {e}")

    meta = {
        "model": "TC-ResUNet",
        "checkpoint": "checkpoints/tc_resunet_best.pt",
        "test_period": "2020-09-13 to 2020-12-31",
        "region": "5-30N, 45-105E",
        "grid": "0.25 deg",
        "temporal_input": "7 days",
        "variables": 7,
        "input_channels": 49,
        "output_depths": 15,
        "target": "GLORYS12V1 thetao",
        "current_input": "GLOBCURRENT total surface u/v currents",
        "argo_status": "pending",
        "available_indices": demo_indices
    }
    with open(frontend_data_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Done exporting static demo data!")

if __name__ == '__main__':
    run()
