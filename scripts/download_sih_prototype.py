import os
import subprocess
import argparse
from pathlib import Path

# SIH PROTOTYPE CONFIGURATION
# 2 Years of data provides 730 days, creating a comfortable 510/110/110 split avoiding severe download lags.
START_DATE = "2019-01-01"
END_DATE = "2020-12-31"

OUT_DIR = "data/raw/sih_prototype"

# Copernicus Dataset IDs (Verified in Phase 0)
TARGETS = {
    "cmems_mod_glo_phy_my_0.083deg_P1D-m": ["thetao"],
    "cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m": ["uo", "vo"],
    "METOFFICE-GLO-SST-L4-REP-OBS-SST": ["analysed_sst"],
    "cmems_obs-mob_glo_phy-sss_my_multi_P1D": ["sos"],
    "cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D": ["sla"],
    "cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H": ["eastward_wind", "northward_wind"]
}

def run_cmems_subset(dataset_id, variables, start, end):
    print(f"\\n{'='*50}\\n--- Downloading {dataset_id} ---\\n{'='*50}")
    
    var_args = []
    for var in variables:
        var_args.extend(["--variable", var])
        
    cmd = [
        "copernicusmarine", "subset",
        "--dataset-id", dataset_id,
        "--start-datetime", start,
        "--end-datetime", end,
        "--minimum-longitude", "45",
        "--maximum-longitude", "105",
        "--minimum-latitude", "5",
        "--maximum-latitude", "30",
        "--output-directory", OUT_DIR,
        "--force-download"
    ] + var_args
    
    # Restrict depth for GLORYS to max 1100m to explicitly encapsulate 1000m target without extrapolating
    if dataset_id == "cmems_mod_glo_phy_my_0.083deg_P1D-m":
        cmd.extend(["--minimum-depth", "0", "--maximum-depth", "1100"])
        
    try:
        subprocess.run(cmd, check=True)
        print(f"SUCCESS: {dataset_id}")
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {dataset_id} | error: {e}")

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"EXECUTING SIH PROTOTYPE ACCELERATED DOWNLOAD: {START_DATE} to {END_DATE}")
    
    for ds_id, v_list in TARGETS.items():
        run_cmems_subset(ds_id, v_list, START_DATE, END_DATE)
        
    print("\\nAll requested SIH routines dispatched.")
