# OceanEmbed Data Overlap & Harmonzation Specifications

## Temporal Harmonization
- **Common Overlap Provisional Range:** `1993-01-01` to `Present` (Constrained by GLORYS and GLOBCURRENT MY availability).
- **Wind Temporal Aggregation:** The CERSAT Blended Wind product (`cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H`) is natively hourly. Oceanic target state variables are daily. During the preprocessing pipeline, we dynamically harmonize the winds using Xarray resampling:
  ```python
  winds_daily = winds.resample(time="1D").mean()
  ```

## Vertical Harmonization
- **GLORYS Depth Interpolation:** GLORYS12V1 natively relies on unevenly distributed standard 'Z' levels (e.g., 0.49m, 9.57m, 21.6m, ..., 902.34m, 1062.44m). The canonical target dictates 15 specific levels (0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000 m).
- To map target fields exactly without extrapolation, the download script is configured to bound depth to `1100m`, capturing the native level underneath 1000m.
- We then use linear interpolation internally:
  ```python
  thetao_target = thetao.interp(
      depth=[0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]
  )
  ```

## NaN Missingness Guidelines
- Surface and subsurface CMEMS grids yield a ~49-55% NaN fraction inside the `5-30N, 45-105E` domain.
- **NaN Interpretation Rule (Phase 0):** This missingness has NOT been decomposed explicitly. NaNs may indicate true geophysical land masks, near-coastal satellite retrieval gaps, quality-control filtering artifacts, or simple product-specific grid geometries.
- **Action:** Raw masks are preserved identically without implicit filling or assumptions.
