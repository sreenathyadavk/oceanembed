import subprocess
import argparse
import os

SUBSET_DIR = "data/raw/subset_test"

def run_cmems_subset(dataset_id, variables, start_date, end_date):
    print(f"\\n--- Downloading {dataset_id} ---")
    var_args = []
    for v in variables:
        var_args.extend(["--variable", v])
        
    cmd = [
        "copernicusmarine", "subset",
        "--dataset-id", dataset_id,
        "--start-datetime", start_date,
        "--end-datetime", end_date,
        "--minimum-longitude", "45",
        "--maximum-longitude", "105",
        "--minimum-latitude", "5",
        "--maximum-latitude", "30",
        "--output-directory", SUBSET_DIR,
        "--force-download"
    ] + var_args
    
    # Restrict depth for GLORYS to max 1100m to encapsulate 1000m target without extrapolating
    if dataset_id == "cmems_mod_glo_phy_my_0.083deg_P1D-m":
        cmd.extend(["--minimum-depth", "0", "--maximum-depth", "1100"])
        
    try:
        subprocess.run(cmd, check=True)
        print(f"SUCCESS: {dataset_id}")
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {dataset_id} | error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download OceanEmbed tiny subset test.")
    parser.add_argument("--start", type=str, default="2020-01-01", help="TEST_SUBSET_DATE_RANGE start")
    parser.add_argument("--end", type=str, default="2020-01-07", help="TEST_SUBSET_DATE_RANGE end")
    args = parser.parse_args()

    os.makedirs(SUBSET_DIR, exist_ok=True)
    
    print(f"EXECUTING TEST SUBSET DOWNLOAD: {args.start} to {args.end}")
    
    targets = {
        "cmems_mod_glo_phy_my_0.083deg_P1D-m": ["thetao"],
        "cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m": ["uo", "vo"],
        "METOFFICE-GLO-SST-L4-REP-OBS-SST": ["analysed_sst"],
        "cmems_obs-mob_glo_phy-sss_my_multi_P1D": ["sos"],
        "cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D": ["sla"],
        "cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H": ["eastward_wind", "northward_wind"]
    }
    
    for ds_id, v_list in targets.items():
        run_cmems_subset(ds_id, v_list, args.start, args.end)
        
    print("\\nAll requested subset routines dispatched.")
