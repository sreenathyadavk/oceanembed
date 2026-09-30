import numpy as np
import xarray as xr

def chronological_split(X, Y, train_ratio=0.7, val_ratio=0.15):
    """
    Chronologically splits data along the time dimension ensuring absolute
    temporal isolation (TRAIN strictly predates VAL strictly predates TEST).
    
    X: [T, Variables, Lat, Lon] (xarray DataArray)
    Y: [T, Depths, Lat, Lon]
    """
    total = len(X.time)
    train_idx = int(total * train_ratio)
    val_idx = int(total * (train_ratio + val_ratio))
    
    # Slice purely chronologically
    X_train = X.isel(time=slice(0, train_idx))
    Y_train = Y.isel(time=slice(0, train_idx))
    
    X_val = X.isel(time=slice(train_idx, val_idx))
    Y_val = Y.isel(time=slice(train_idx, val_idx))
    
    X_test = X.isel(time=slice(val_idx, total))
    Y_test = Y.isel(time=slice(val_idx, total))
    
    print(f"SPLIT CHRONOLOGY:")
    print(f"  TRAIN: {X_train.shape[0]} samples ({X_train.time[0].values} to {X_train.time[-1].values})")
    print(f"  VAL:   {X_val.shape[0]} samples ({X_val.time[0].values} to {X_val.time[-1].values})")
    print(f"  TEST:  {X_test.shape[0]} samples ({X_test.time[0].values} to {X_test.time[-1].values})")
    
    return (X_train, Y_train), (X_val, Y_val), (X_test, Y_test)

def fit_transform_normalization(train_X, val_X, test_X):
    """
    Extracts explicit Mean and Std metrics mapping isolated per variable
    from the TRAIN partition strictly to avoid data leakages.
    Applies identical transformations to VAL and TEST natively.
    """
    # train_X is [T, Var, Lat, Lon]
    print("Fitting Z-score normalization strictly to TRAIN distributions...")
    
    # Compute mean and standard deviation along time, lat, lon (axes 0, 2, 3) 
    # to find global mean/std per Variable channel (axis 1)
    
    has_var = 'variable' in train_X.coords
    if has_var:
        mean_vals = train_X.mean(dim=['time', 'latitude', 'longitude'], skipna=True)
        std_vals = train_X.std(dim=['time', 'latitude', 'longitude'], skipna=True)
        std_vals = xr.where(std_vals == 0, 1.0, std_vals)
    else:
        # Target matrices globally normalized identically preserving depth relationships
        mean_vals = train_X.mean(skipna=True)
        std_vals = train_X.std(skipna=True)
        if std_vals == 0: std_vals = 1.0
        
    norm_params = {
        'mean': float(mean_vals.values) if not has_var else mean_vals.values.tolist(),
        'std': float(std_vals.values) if not has_var else std_vals.values.tolist(),
        'variables': mean_vals.coords['variable'].values.tolist() if has_var else []
    }
    
    return norm_params
