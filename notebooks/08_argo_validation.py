import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import xarray as xr
import pandas as pd
import requests
import torch
import warnings
from src.models.tc_resunet import TCResUNet

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

DEPTH_LEVELS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]

def datetime64_to_str(dt64):
    import pandas as pd
    ts = pd.to_datetime(str(dt64))
    return ts.strftime('%Y-%m-%dT%H:%M:%SZ')

def fetch_argo(start_str, end_str):
    print(f"Fetching ARGO data securely via ERDDAP CSV from {start_str} to {end_str}...")
    url = (
        "https://erddap.incois.gov.in/erddap/tabledap/Indian_ARGO_Floats.csv?"
        "time,latitude,longitude,PRES,TEMP&"
        f"time>={start_str}&time<={end_str}&"
        "latitude>=5&latitude<=30&longitude>=45&longitude<=105"
    )
    r = requests.get(url, timeout=60, verify=False)
    if r.status_code == 200:
        lines = r.text.strip().split('\\n')
        # skip header and unit line
        data = []
        for line in lines[2:]:
            parts = line.split(',')
            if len(parts) >= 5 and parts[3] != 'NaN' and parts[4] != 'NaN':
                # Parse to list safely
                try:
                    data.append({
                        'time': str(parts[0]),
                        'lat': float(parts[1]),
                        'lon': float(parts[2]),
                        'pres': float(parts[3]),
                        'temp': float(parts[4])
                    })
                except:
                    pass
        df = pd.DataFrame(data)
        if not df.empty:
            df['time'] = pd.to_datetime(df['time'])
        return df
    else:
        print(f"FAILED ARGO FETCH: {r.status_code}")
        return pd.DataFrame()

def main():
    DATA_DIR = "data/processed"
    print("Loading Processed splits and model...")
    X_test = xr.open_dataset(os.path.join(DATA_DIR, "X_test_norm.nc"))
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = TCResUNet(in_channels=49, out_channels=15, base_c=32).to(device)
    model.load_state_dict(torch.load("checkpoints/tc_resunet_best.pt", map_location=device, weights_only=True))
    model.eval()

    try:
        import pickle
        with open(os.path.join(DATA_DIR, "norm_params.pkl"), "rb") as f:
            norm_stats = pickle.load(f)
            y_mean = float(norm_stats['Y']['mean'])
            y_std = float(norm_stats['Y']['std'])
    except Exception as e:
        print(f"Warning: Failed to fetch Y denormalization attributes! Defaulting. ({e})")
        y_mean, y_std = 0.0, 1.0

    times = X_test.time.values
    t_start = datetime64_to_str(times[0])
    t_end = datetime64_to_str(times[-1])
    
    argo_df = fetch_argo(t_start, t_end)
    if argo_df.empty:
        print("No valid ARGO data retrieved to validate against.")
        return
        
    print(f"Retrieving matched predictions sequentially for {len(argo_df)} ARGO float elements...")
    
    lats_grid = X_test.latitude.values
    lons_grid = X_test.longitude.values
    
    # We load predictions in bulk to save execution iteration
    pred_cube = []
    with torch.no_grad():
        for t_i in range(len(times) - 7):
            window_X = X_test['__xarray_dataarray_variable__'].values[t_i : t_i + 7]
            C, V, H, W = window_X.shape
            x_flat = window_X.reshape(C * V, H, W)
            x_clean = np.nan_to_num(x_flat, nan=0.0)
            X_tensor = torch.tensor(x_clean).unsqueeze(0).to(device).float()
            pred_Y = model(X_tensor).cpu().numpy()[0]
            pred_Y = pred_Y * y_std + y_mean
            
            pred_cube.append(pred_Y)
            
    # [T_test, 15, H, W]
    pred_cube = np.stack(pred_cube)
    
    pred_vals = []
    target_vals = []
    
    for _, row in argo_df.iterrows():
        # Match time
        dt = row['time']
        # Convert to daily matching string roughly natively
        time_mask = pd.to_datetime(times[7:]) == pd.to_datetime(dt.date())
        if not time_mask.any(): continue
        
        t_idx = np.where(time_mask)[0][0]
        
        # Match lat lon
        # nearest index
        lat_idx = np.abs(lats_grid - row['lat']).argmin()
        lon_idx = np.abs(lons_grid - row['lon']).argmin()
        
        # Match depth (nearest out of 15)
        d_idx = np.abs(np.array(DEPTH_LEVELS) - row['pres']).argmin()
        
        # Guard max disparity 
        if np.abs(DEPTH_LEVELS[d_idx] - row['pres']) > 20: 
            continue # Drop if ARGO depth significantly mismatched target index bounds
            
        p_val = pred_cube[t_idx, d_idx, lat_idx, lon_idx]
        if not np.isnan(p_val) and p_val != 0.0:
            pred_vals.append(p_val)
            target_vals.append(row['temp'])
            
    if len(pred_vals) == 0:
        print("No geometric valid matches!")
        return
        
    preds = np.array(pred_vals)
    targs = np.array(target_vals)
    
    error = preds - targs
    rmse = np.sqrt(np.mean(error**2))
    mae = np.mean(np.abs(error))
    bias = np.mean(error)
    corr = np.corrcoef(preds, targs)[0,1]
    
    print(f"\\n--- ARGO PROTOTYPE VALIDATION STATISTICS ---")
    print(f"Matched Float Points: {len(preds)}")
    print(f"ARGO RMSE: {rmse:.4f} °C")
    print(f"ARGO MAE:  {mae:.4f} °C")
    print(f"ARGO Bias: {bias:.4f} °C")
    print(f"ARGO Corr: {corr:.4f}")
    
    with open("reports/BASELINE_RESULTS.md", "a") as f:
        f.write("\\n## 3. ARGO Observational Validation\\n")
        f.write("> *GLORYS is used as the dense training/reference target, while ARGO provides an observational validation dataset. Because ARGO observations may contribute to GLORYS data assimilation, ARGO validation is not statistically independent of the training reference.*\\n\\n")
        f.write(f"- Matches: {len(preds)}\\n")
        f.write(f"- RMSE: {rmse:.4f}\\n")
        f.write(f"- MAE: {mae:.4f}\\n")
        f.write(f"- Bias: {bias:.4f}\\n")
        f.write(f"- Correlation: {corr:.4f}\\n")
        
if __name__ == "__main__":
    main()
