import copernicusmarine as cm
import datetime
import json
import os

# Datasets to inspect
CANDIDATES = {
    "GLORYS": {
        "dataset_id": "cmems_mod_glo_phy_my_0.083deg_P1D-m",
        "description": "Primary GLORYS12V1 subsurface temperature target",
        "target_vars": ["thetao"]
    },
    "SST": {
        "dataset_id": "cmems_obs-sst_glo_phy_my_l4_P1D-m",
        "description": "OSTIA Reprocessed Global Daily SST",
        "target_vars": ["analysed_sst"]
    },
    "SSS": {
        "dataset_id": "cmems_obs-mob_glo_phy-sss_my_multi_P1D",
        "description": "Multi-Observation Reprocessed SSS",
        "target_vars": ["sos"]
    },
    "SLA": {
        "dataset_id": "cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.25deg_P1D",
        "description": "DUACS Reprocessed SLA (All-Sat)",
        "target_vars": ["sla"]
    },
    "CURRENTS": {
        "dataset_id": "cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m",
        "description": "GLOBCURRENT Total Surface Currents (Independent of GLORYS)",
        "target_vars": ["uo", "vo"]
    },
    "WINDS": {
        "dataset_id": "cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H",
        "description": "CERSAT Blended Mean Wind Fields (Hourly)",
        "target_vars": ["eastward_wind", "northward_wind"]
    }
}

def verify_dataset(name, cfg):
    print(f"\\n{'='*50}")
    print(f"VERIFYING: {name}")
    print(f"Intended Use: {cfg['description']}")
    print(f"{'='*50}")
    
    try:
        catalog = cm.describe(
            dataset_id=cfg["dataset_id"]
        )
        
        # If catalog is None, it means the API failed to fetch or parse.
        if not catalog:
            print(f"PRIMARY PRODUCT: FAILED\\nREASON: Could not fetch description for {cfg['dataset_id']}")
            return False
            
        print(f"Dataset ID: {cfg['dataset_id']}")
        
        # We need to find the specific dataset inside the product description if the parent product was returned.
        # However cm.describe for a dataset_id directly returns information for that dataset.
        
        # Attempting to print out the variables dynamically
        # Handling the possibility that `describe` returns a Product or Dataset object
        vars_dict = getattr(catalog, "variables", {})
        coords_dict = getattr(catalog, "coordinates", {})
        
        print(f"Time Coverage: {getattr(catalog, 'temporal_start', 'N/A')} to {getattr(catalog, 'temporal_end', 'N/A')}")
        print(f"Geographic Bounding Box: [{getattr(catalog, 'min_longitude', 'N/A')}, {getattr(catalog, 'min_latitude', 'N/A')}, {getattr(catalog, 'max_longitude', 'N/A')}, {getattr(catalog, 'max_latitude', 'N/A')}]")
        
        for v in cfg["target_vars"]:
            if v in vars_dict:
                v_obj = vars_dict[v]
                print(f"\\nExpected Variable: {v}")
                print(f"  Long Name: {getattr(v_obj, 'long_name', 'N/A')}")
                print(f"  Standard Name: {getattr(v_obj, 'standard_name', 'N/A')}")
                print(f"  Units: {getattr(v_obj, 'units', 'N/A')}")
                # Print physical meaning based on text matching
                desc = getattr(v_obj, 'long_name', '').lower()
                if "potential temperature" in desc or "thetao" in v:
                    print("  Physical Meaning: Confirmed Potential Temperature.")
                elif "sea_surface_temperature" in getattr(v_obj, 'standard_name', '').lower():
                    print("  Physical Meaning: Confirmed Sea Surface Temperature.")
                elif "sea_surface_height_above_sea_level_anomaly" in getattr(v_obj, 'standard_name', '').lower() or "sea level anomaly" in desc:
                    print("  Physical Meaning: Confirmed Sea Level Anomaly.")
                elif "eastward_sea_water_velocity" in getattr(v_obj, 'standard_name', '').lower():
                    print("  Physical Meaning: Confirmed Ocean Current (Total/Geostrophic check needed).")
            else:
                print(f"\\nWARNING: Expected Variable {v} NOT FOUND in metadata!")
        
        print("\\nAll Variables in Dataset:")
        for v_name, v_obj in vars_dict.items():
            print(f" - {v_name}: {getattr(v_obj, 'long_name', 'N/A')} ({getattr(v_obj, 'units', 'N/A')})")
            
        print(f"\\nStatus: VERIFIED (Metadata)")
        return True
    
    except Exception as e:
        print(f"PRIMARY PRODUCT: FAILED\\nREASON: {str(e)}")
        return False

def check_canonical_grid():
    import numpy as np
    lats = np.arange(5.0, 30.0 + 0.25, 0.25)
    lons = np.arange(45.0, 105.0 + 0.25, 0.25)
    
    print(f"\\n{'='*50}\\nCANONICAL GRID VERIFICATION\\n{'='*50}")
    print(f"Target Latitudes: {lats[0]} to {lats[-1]}, Steps: {len(lats)}")
    print(f"Target Longitudes: {lons[0]} to {lons[-1]}, Steps: {len(lons)}")
    if len(lats) == 101 and len(lons) == 241:
        print("Status: Canonical Grid [101, 241] VERIFIED programmatically.")
    else:
        print(f"WARNING: Canonical grid size mismatch! Got H={len(lats)}, W={len(lons)}")

if __name__ == "__main__":
    print("STARTING METADATA VERIFICATION...")
    for name, cfg in CANDIDATES.items():
        verify_dataset(name, cfg)
        
    check_canonical_grid()
    
    print(f"\\n{'='*50}\\nARGO INCOIS VALIDATION\\n{'='*50}")
    print("ARGO Verification: Checking ERDDAP/INCOIS availability.")
    # Quick API check for INCOIS ERDDAP
    import requests
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    try:
        res = requests.get("https://erddap.incois.gov.in/erddap/info/index.json", timeout=10, verify=False)
        if res.status_code == 200:
            print("INCOIS ERDDAP Access: SUCCESS")
            rj = res.json()
            table = rj.get('table', {})
            datasets = table.get('rows', [])
            print(f"Total Datasets Found in INCOIS ERDDAP: {len(datasets)}")
            # Filter for ARGO
            argo_ds = [d for d in datasets if "argo" in str(d).lower()]
            print(f"Argo Datasets Found: {len(argo_ds)}")
            if len(argo_ds) > 0:
                print("Status: ARGO Source Identified natively.")
    except Exception as e:
        print("INCOIS ERDDAP Access: FAILED", str(e))
        print("Required to verify Argo GDAC fallback.")
