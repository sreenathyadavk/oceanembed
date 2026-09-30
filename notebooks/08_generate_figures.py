import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.tc_resunet import TCResUNet
from src.baselines.climatology import MonthlyClimatologyBaseline
from src.data.dataset import OceanEmbedDataset
import xarray as xr
from torch.utils.data import DataLoader
import torch
import numpy as np
import pickle
import matplotlib.pyplot as plt

def main():
    DATA_DIR = "data/processed"
    FIG_DIR = "reports/figures"
    os.makedirs(FIG_DIR, exist_ok=True)
    
    DEPTH_LEVELS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]
    
    Y_train_ds = xr.open_dataset(os.path.join(DATA_DIR, "Y_train.nc"))
    X_test_ds = xr.open_dataset(os.path.join(DATA_DIR, "X_test.nc"))
    Y_test_ds = xr.open_dataset(os.path.join(DATA_DIR, "Y_test.nc"))
    
    Y_train = Y_train_ds['thetao'] if 'thetao' in Y_train_ds.data_vars else list(Y_train_ds.data_vars.values())[0]
    X_test = X_test_ds['__xarray_dataarray_variable__'] if '__xarray_dataarray_variable__' in X_test_ds else list(X_test_ds.data_vars.values())[0]
    Y_test = Y_test_ds['thetao'] if 'thetao' in Y_test_ds.data_vars else list(Y_test_ds.data_vars.values())[0]
    
    Y_arr = Y_test.values
    test_mask = ~np.isnan(Y_arr)
    # spatial mask
    geo_mask = test_mask.any(axis=0)[..., 0] 
    
    climatology = MonthlyClimatologyBaseline()
    climatology.fit(Y_train)
    clim_pred = climatology.predict(Y_test)
    clim_pred = clim_pred.transpose(0, 3, 1, 2)
    Y_arr_trans = Y_arr.transpose(0, 3, 1, 2)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = TCResUNet(in_channels=49, out_channels=15, base_c=32).to(device)
    model.load_state_dict(torch.load("checkpoints/tc_resunet_best.pt", map_location=device, weights_only=True))
    model.eval()
    
    test_dataset = OceanEmbedDataset(X_test, Y_test, window_size=7)
    test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)
    
    with open(os.path.join(DATA_DIR, "norm_params.pkl"), "rb") as f:
        norm_stats = pickle.load(f)
        y_mean = float(norm_stats['Y']['mean'])
        y_std = float(norm_stats['Y']['std'])

    net_preds = []
    net_targets = []
    with torch.no_grad():
        for batch in test_loader:
            X = batch['X'].to(device)
            Y = batch['Y'].numpy()
            pred = model(X).cpu().numpy()
            pred_denorm = pred * y_std + y_mean
            Y_denorm = Y * y_std + y_mean
            net_preds.append(pred_denorm)
            net_targets.append(Y_denorm)
            
    net_preds = np.concatenate(net_preds, axis=0) # [104, 15, H, W]
    Y_arr_sliced = Y_arr_trans[6:] # [104, 15, H, W]
    clim_pred_sliced = clim_pred[6:] # [104, 15, H, W]
    
    # METRICS FOR PLOTTING
    num_depths = net_preds.shape[1]
    net_rmse, net_corr, clim_rmse, clim_corr = [], [], [], []
    for d in range(num_depths):
        p_d = net_preds[:, d, :, :]
        c_d = clim_pred_sliced[:, d, :, :]
        t_d = Y_arr_sliced[:, d, :, :]
        valid = ~np.isnan(t_d[0])
        p_v = p_d[:, valid].flatten()
        c_v = c_d[:, valid].flatten()
        t_v = t_d[:, valid].flatten()
        
        net_rmse.append(np.sqrt(np.mean((p_v - t_v)**2)))
        clim_rmse.append(np.sqrt(np.mean((c_v - t_v)**2)))
        
        std_t = np.std(t_v)
        if std_t > 0:
            net_corr.append(np.cov(p_v, t_v)[0,1] / (np.std(p_v)*std_t))
            clim_corr.append(np.cov(c_v, t_v)[0,1] / (np.std(c_v)*std_t))
        else:
            net_corr.append(np.nan)
            clim_corr.append(np.nan)
            
    # Figure 1: RMSE Comparison
    plt.figure(figsize=(8,6))
    plt.plot(net_rmse, DEPTH_LEVELS, marker='o', label='TC-ResUNet Prototype', color='blue')
    plt.plot(clim_rmse, DEPTH_LEVELS, marker='s', label='Monthly Climatology', color='orange')
    plt.gca().invert_yaxis()
    plt.xlabel('RMSE (°C)')
    plt.ylabel('Depth (m)')
    plt.title('Depth-wise RMSE Comparison on Held-out Test Set')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{FIG_DIR}/rmse_comparison.png", dpi=300)
    plt.close()
    
    # Figure 2: Correlation Comparison
    plt.figure(figsize=(8,6))
    plt.plot(net_corr, DEPTH_LEVELS, marker='o', label='TC-ResUNet Prototype', color='blue')
    plt.plot(clim_corr, DEPTH_LEVELS, marker='s', label='Monthly Climatology', color='orange')
    plt.gca().invert_yaxis()
    plt.xlabel('Pearson Correlation')
    plt.ylabel('Depth (m)')
    plt.title('Depth-wise Correlation Coefficient')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{FIG_DIR}/corr_comparison.png", dpi=300)
    plt.close()

    # Figure 3: Example Maps (Target vs Prediction vs Error) at 100m Depth for mid-index
    t_idx = net_preds.shape[0] // 2 
    d_idx = 7 # 100m
    
    t_map = Y_arr_sliced[t_idx, d_idx].copy()
    p_map = net_preds[t_idx, d_idx].copy()
    err_map = np.abs(p_map - t_map)
    
    # Drop lands
    t_map[~geo_mask] = np.nan
    p_map[~geo_mask] = np.nan
    err_map[~geo_mask] = np.nan
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    im1 = axes[0].imshow(t_map, cmap='viridis', origin='lower')
    axes[0].set_title(f'GLORYS Truth (100m)')
    fig.colorbar(im1, ax=axes[0])
    
    im2 = axes[1].imshow(p_map, cmap='viridis', origin='lower')
    axes[1].set_title(f'TC-ResUNet Predicted (100m)')
    fig.colorbar(im2, ax=axes[1])
    
    im3 = axes[2].imshow(err_map, cmap='Reds', origin='lower')
    axes[2].set_title('Absolute Error (|Pred - Truth|)')
    fig.colorbar(im3, ax=axes[2])
    
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/example_maps.png", dpi=300)
    plt.close()
    
    # Figure 4: Vertical Profile at random point
    # Find a valid ocean point
    valid_ys, valid_xs = np.where(geo_mask)
    if len(valid_ys) > 0:
        rp = 42
        cy, cx = valid_ys[rp], valid_xs[rp]
        
        prof_t = Y_arr_sliced[t_idx, :, cy, cx]
        prof_p = net_preds[t_idx, :, cy, cx]
        prof_c = clim_pred_sliced[t_idx, :, cy, cx]
        
        plt.figure(figsize=(6,8))
        plt.plot(prof_t, DEPTH_LEVELS, marker='o', label='GLORYS Truth', color='black')
        plt.plot(prof_p, DEPTH_LEVELS, marker='v', label='TC-ResUNet', color='blue')
        plt.plot(prof_c, DEPTH_LEVELS, marker='s', label='Climatology', color='orange')
        plt.gca().invert_yaxis()
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Depth (m)')
        plt.title('Vertical Temperature Profile Matchup')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{FIG_DIR}/vertical_profile.png", dpi=300)
        plt.close()
        
    print("Figures successfully written natively.")
    
if __name__ == "__main__":
    main()
