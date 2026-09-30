import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.harmonizer import load_and_harmonize
from src.data.preprocessing import chronological_split, fit_transform_normalization
import numpy as np
import pickle
import argparse

def main():
    SUBSET_DIR = "data/raw/sih_prototype"
    OUT_DIR = "data/processed"
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print("Stage 1: Harmonization")
    X, Y = load_and_harmonize(SUBSET_DIR)
    
    if X is None or Y is None:
        print("Fatal Error: Raw subset files were missing or corrupted!")
        return

    print("Stage 2: Splitting")
    # 70% 15% 15% 
    (X_train, Y_train), (X_val, Y_val), (X_test, Y_test) = chronological_split(X, Y, train_ratio=0.7, val_ratio=0.15)
    
    # Save the unnormalized arrays for evaluation (Climatology needs them native, or normalized, native is easier)
    # Actually saving everything as NetCDF allows flawless tracking iteratively
    print("Saving intermediate Unnormalized Splits...")
    Y_train.to_netcdf(os.path.join(OUT_DIR, "Y_train.nc"))
    Y_val.to_netcdf(os.path.join(OUT_DIR, "Y_val.nc"))
    Y_test.to_netcdf(os.path.join(OUT_DIR, "Y_test.nc"))
    
    print("Stage 3: Normalization Param Extraction (Lazy)")
    norm_params = fit_transform_normalization(X_train, X_val, X_test)
    y_norm_params = fit_transform_normalization(Y_train, Y_val, Y_test)
    
    with open(os.path.join(OUT_DIR, "norm_params.pkl"), "wb") as f:
        pickle.dump({'X': norm_params, 'Y': y_norm_params}, f)
        
    print("Saving UNNORMALIZED Input Splits explicitly avoiding mapping local memory blowups...")
    X_train.to_netcdf(os.path.join(OUT_DIR, "X_train.nc"))
    X_val.to_netcdf(os.path.join(OUT_DIR, "X_val.nc"))
    X_test.to_netcdf(os.path.join(OUT_DIR, "X_test.nc"))
    
    print(f"Preparation Complete! Files written securely to {OUT_DIR}.")

if __name__ == "__main__":
    main()
