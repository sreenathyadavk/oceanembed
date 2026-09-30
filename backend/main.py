from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import torch
import xarray as xr
import numpy as np
import pickle
import os
import sys

# Ensure model can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.models.tc_resunet import TCResUNet

app = FastAPI(title="OceanEmbed Scientific Prototype API")

# Enable CORS for NextJS Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
MODEL = None
X_TEST = None
Y_TEST = None
Y_MEAN = 0.0
Y_STD = 1.0
GEO_MASK = None

DEPTHS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]

@app.on_event("startup")
def startup_event():
    global MODEL, X_TEST, Y_TEST, Y_MEAN, Y_STD, GEO_MASK
    print("Loading TC-ResUNet Prototype Checkpoint...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    MODEL = TCResUNet(in_channels=49, out_channels=15, base_c=32)
    MODEL.load_state_dict(torch.load("checkpoints/tc_resunet_best.pt", map_location=device, weights_only=True))
    MODEL.to(device)
    MODEL.eval()
    
    print("Loading Native Dataset Arrays...")
    DATA_DIR = "data/processed"
    
    with open(os.path.join(DATA_DIR, "norm_params.pkl"), "rb") as f:
        params = pickle.load(f)
        Y_MEAN = float(params['Y']['mean'])
        Y_STD = float(params['Y']['std'])
        
    x_test_ds = xr.open_dataset(os.path.join(DATA_DIR, "X_test.nc"))
    y_test_ds = xr.open_dataset(os.path.join(DATA_DIR, "Y_test.nc"))
    
    X_TEST = x_test_ds['__xarray_dataarray_variable__'].values if '__xarray_dataarray_variable__' in x_test_ds else list(x_test_ds.data_vars.values())[0].values
    Y_TEST = y_test_ds['thetao'].values if 'thetao' in y_test_ds else list(y_test_ds.data_vars.values())[0].values
    
    test_mask = ~np.isnan(Y_TEST)
    GEO_MASK = test_mask.any(axis=0)[..., 0] # [101, 241]
    
    print("Backend Fully Loaded Safely.")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "TC-ResUNet",
        "parameters": 1963407,
        "device": 'cuda' if torch.cuda.is_available() else 'cpu',
        "channels_in": 49,
        "channels_out": 15,
        "window_size": 7
    }

@app.get("/api/predict")
def predict_slice(time_idx: int = 50):
    """
    time_idx ranges from 0 to 103 (since test set is 110 days, 110-6 = 104 samples)
    """
    if time_idx < 0 or time_idx >= (len(X_TEST) - 6):
        time_idx = 50 
        
    # Temporal Lag Extraction natively
    # X_TEST is [T, Var, Lat, Lon] = [110, 7, 101, 241]
    x_window = X_TEST[time_idx : time_idx + 7] # [7, 7, 101, 241]
    
    # Ground target is the last day of the window (index: time_idx + 6)
    # Y_TEST is [T, Lat, Lon, Depth]
    target_dt = time_idx + 6
    y_target = Y_TEST[target_dt] # [101, 241, 15]
    
    # Flatten variables and time natively cleanly
    with open("data/processed/norm_params.pkl", "rb") as f:
        params = pickle.load(f)
        x_mean = np.array(params['X']['mean']).reshape((1, -1, 1, 1)).astype(np.float32)
        x_std = np.array(params['X']['std']).reshape((1, -1, 1, 1)).astype(np.float32)
    
    x_norm = (x_window - x_mean) / x_std
    x_norm = np.nan_to_num(x_norm, nan=0.0)
    
    C, V, H, W = x_norm.shape
    x_flat = x_norm.transpose(1, 0, 2, 3).reshape(C * V, H, W)
    
    x_tensor = torch.tensor(x_flat).unsqueeze(0).float()
    if torch.cuda.is_available():
        x_tensor = x_tensor.cuda()
        
    with torch.no_grad():
        pred = MODEL(x_tensor).cpu().numpy()[0] # [15, 101, 241]
        
    pred_denorm = (pred * Y_STD) + Y_MEAN # [15, 101, 241]
    
    # Ensure targets natively cleanly follow [15, 101, 241]
    y_target_trans = y_target.transpose(2, 0, 1) # [15, 101, 241]
    
    return {
        "time_index": time_idx,
        "depths": DEPTHS,
        "lats": np.linspace(5, 30, 101).tolist(),
        "lons": np.linspace(45, 105, 241).tolist(),
        "predictions": np.nan_to_num(pred_denorm, nan=-999.0).tolist(),
        "ground_truth": np.nan_to_num(y_target_trans, nan=-999.0).tolist(),
        "mask": GEO_MASK.tolist()
    }
