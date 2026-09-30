import os
import glob
import xarray as xr
import numpy as np

# Canonical Grid Defs
TARGET_LATS = np.linspace(5, 30, 101)   # 5 to 30 with 0.25 step -> 25 / 0.25 + 1 = 101
TARGET_LONS = np.linspace(45, 105, 241) # 45 to 105 with 0.25 step -> 60 / 0.25 + 1 = 241
TARGET_DEPTHS = [0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]

VARIABLES_ORDER = [
    'analysed_sst', 
    'sos', 
    'sla',
    'uo',
    'vo',
    'eastward_wind',
    'northward_wind'
]

def load_and_harmonize(subset_dir):
    """
    Loads raw NetCDF CMEMS files, regrids onto canonical coordinates,
    aggregates temporally, and returns unified X, Y datasets.
    """
    files = glob.glob(os.path.join(subset_dir, "*.nc"))
    
    datasets = {}
    print("Loading raw files...")
    wind_files = []
    
    for f in files:
        if "wind" in f.lower():
            wind_files.append(f)
            continue
            
        ds = xr.open_dataset(f, chunks={'time': 10})
        var_names = list(ds.data_vars)
        if 'thetao' in var_names: datasets['thetao'] = ds
        elif 'analysed_sst' in var_names: datasets['sst'] = ds
        elif 'sos' in var_names: datasets['sss'] = ds
        elif 'sla' in var_names: datasets['sla'] = ds
        elif 'uo' in var_names: datasets['currents'] = ds

    if wind_files:
        datasets['winds'] = xr.open_mfdataset(wind_files, combine='by_coords')
            
    print("Harmonizing Temporal structures...")
    # Wind Resampling
    if 'winds' in datasets:
        datasets['winds'] = datasets['winds'].resample(time="1D").mean()
        
    print("Harmonizing Spatial Grids into Canonical Format...")
    harmonized = {}
    
    # 1. Regrid predictors
    for k in ['sst', 'sss', 'sla', 'currents', 'winds']:
        if k not in datasets: continue
        ds = datasets[k]
        
        # Ensure dimensional names align (some might use 'lat' vs 'latitude')
        lat_col = 'latitude' if 'latitude' in ds.coords else 'lat'
        lon_col = 'longitude' if 'longitude' in ds.coords else 'lon'
        
        # If 'elevation' exists (e.g. currents), isolate surface
        if 'elevation' in ds.coords:
            ds = ds.sel(elevation=0.0, method='nearest')
        if 'depth' in ds.coords and k != 'thetao':
            ds = ds.sel(depth=0.0, method='nearest')
            
        ds = ds.interp({lat_col: TARGET_LATS, lon_col: TARGET_LONS}, method='linear')
        
        harmonized[k] = ds
        
    # 2. Extract and align Y target
    if 'thetao' in datasets:
        print("Interpolating Target Depths natively...")
        y_ds = datasets['thetao']
        lat_col = 'latitude' if 'latitude' in y_ds.coords else 'lat'
        lon_col = 'longitude' if 'longitude' in y_ds.coords else 'lon'
        
        y_ds = y_ds.interp({
            lat_col: TARGET_LATS, 
            lon_col: TARGET_LONS
        }, method='linear')
        
        # Scientifically correct 0m surface target handling without blindly extrapolating
        Y_deep = y_ds.interp(depth=TARGET_DEPTHS[1:], method='linear')
        
        # Find nearest valid GLORYS top surface level explicitly mapping it directly as 0m
        # GLORYS implicitly starts near ~0.494m
        Y_surface = y_ds.sel(depth=0.0, method='nearest')
        Y_surface = Y_surface.assign_coords(depth=0)
        
        y_ds = xr.concat([Y_surface, Y_deep], dim='depth')
        
        Y = y_ds['thetao']
    else:
        Y = None

    print("Fusing X structures...")
    # Expand and merge X lists
    x_arrays = []
    
    time_coords = None
    
    for var in VARIABLES_ORDER:
        found = False
        for k, ds in harmonized.items():
            if var in ds.data_vars:
                array = ds[var]
                if time_coords is None:
                    time_coords = array.time
                x_arrays.append(array)
                found = True
                break
        if not found:
            print(f"Warning: {var} not found in parsed files!")
            
    if x_arrays:
        # Guarantee identical chronological overlaps explicitly traversing array dimensions before concatenation natively
        common_time = x_arrays[0].time.values
        for arr in x_arrays[1:]:
            common_time = np.intersect1d(common_time, arr.time.values)
            
        common_time = np.sort(common_time)
        print(f"Resolving isolated common chronological intersection mapping exclusively: {len(common_time)} frames natively!")
        
        # Subselect safely eliminating outer bound discrepancies
        x_arrays = [arr.sel(time=common_time) for arr in x_arrays]
        if Y is not None:
             Y = Y.sel(time=common_time)
        
        X = xr.concat(x_arrays, dim='variable')
        X = X.assign_coords(variable=VARIABLES_ORDER)
        X = X.transpose('time', 'variable', 'latitude', 'longitude')
    else:
        X = None
        
    print(f"Harmonization Complete. X: {X.shape if X is not None else None}, Y: {Y.shape if Y is not None else None}")
    return X, Y
