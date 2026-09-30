import xarray as xr
import os

def check_leakage():
    DATA_DIR = "data/processed"
    X_train = xr.open_dataset(os.path.join(DATA_DIR, "X_train_norm.nc"))
    X_val = xr.open_dataset(os.path.join(DATA_DIR, "X_val_norm.nc"))
    X_test = xr.open_dataset(os.path.join(DATA_DIR, "X_test_norm.nc"))
    
    t_train = X_train.time.values
    t_val = X_val.time.values
    t_test = X_test.time.values
    
    print("--- CHRONOLOGICAL LEAKAGE AUDIT ---")
    
    print(f"TRAIN : {t_train[0]} -> {t_train[-1]}")
    print(f"VAL   : {t_val[0]} -> {t_val[-1]}")
    print(f"TEST  : {t_test[0]} -> {t_test[-1]}")
    
    val_overlap = set(t_train).intersection(set(t_val))
    test_overlap = set(t_train).intersection(set(t_test))
    val_test_overlap = set(t_val).intersection(set(t_test))
    
    if len(val_overlap) == 0 and len(test_overlap) == 0 and len(val_test_overlap) == 0:
        if t_train[-1] < t_val[0] and t_val[-1] < t_test[0]:
            print("STATUS: PASSED. Zero temporal intersection. Perfect forward chronology maintained.")
            with open("reports/BASELINE_RESULTS.md", "a") as f:
                f.write("\\n## 4. Integrity Validations\\n")
                f.write("- **Leakage Test Status**: PASSED. Train, Validation, and Test windows are strictly chronological and possess exactly zero temporal intersections.\\n")
        else:
            print("STATUS: FAILED OVERLAP CHRONOLOGY!")
            
    else:
        print("STATUS: FAILED! Duplicate timesteps detected between splits!")
        
if __name__ == "__main__":
    check_leakage()
