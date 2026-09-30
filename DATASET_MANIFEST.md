# OceanEmbed Dataset Manifest

| OceanEmbed variable | Provider | Product | Dataset ID | Exact variable | Units | Native resolution | Temporal resolution | Coverage | Access method | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| SST | Copernicus | OSTIA Reprocessed | `METOFFICE-GLO-SST-L4-REP-OBS-SST` | `analysed_sst` | °C | 0.05° | Daily | 1981-Present | CMEMS Subset API | VERIFIED |
| SSS | Copernicus | Multi-Obs Reprocessed | `cmems_obs-mob_glo_phy-sss_my_multi_P1D` | `sos` | PSU | 0.25° | Daily | 1993-Present | CMEMS Subset API | VERIFIED |
| SLA | Copernicus | DUACS Reprocessed All-Sat | `cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D` | `sla` | m | 0.125° | Daily | 1993-Present | CMEMS Subset API | VERIFIED |
| U current | Copernicus | GLOBCURRENT | `cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m` | `uo` (eastward total) | m/s | 0.25° | Daily | 1993-Present | CMEMS Subset API | VERIFIED (OBS) |
| V current | Copernicus | GLOBCURRENT | `cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m` | `vo` (northward total) | m/s | 0.25° | Daily | 1993-Present | CMEMS Subset API | VERIFIED (OBS) |
| U wind | Copernicus | CERSAT Blended Wind | `cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H` | `eastward_wind` (10m) | m/s | 0.125° | Hourly | 1992-Present | CMEMS Subset API | VERIFIED |
| V wind | Copernicus | CERSAT Blended Wind | `cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H` | `northward_wind` (10m) | m/s | 0.125° | Hourly | 1992-Present | CMEMS Subset API | VERIFIED |
| GLORYS temperature | Copernicus | GLORYS12V1 | `cmems_mod_glo_phy_my_0.083deg_P1D-m` | `thetao` (potential) | °C | 0.083° | Daily | 1993-Present | CMEMS Subset API | VERIFIED |
| ARGO temperature | INCOIS | Argo GDAC Mirror | `incois_argo_profiles` (via ERDDAP) | `temp` | °C | N/A (Profiles) | Irregular | 2000-Present | ERDDAP REST API | VERIFIED |
## Important Data Characteristics
- **NaN Interpretation**: Subset grids (especially SST and target datasets) frequently possess ~50% NaNs bounding this canonical region due to the massive land footprints of the Middle East, Indian Subcontinent, and Sri Lanka. These missing values are rigidly preserved in Phase 0 as "raw masks" and are **not** arbitrarily filled or interpolated out, isolating the exact product observations.
- **Vertical Target Reconstruction**: GLORYS Subsurface Temperature is explicitly interpolated natively via `interp(depth=[...])` from strictly preserved native 'Z' coordinate slices brackets.
- **Hourly Aggregations**: CERSAT winds are aggregated iteratively across the 24-hour slices using Xarray deterministic `resample('1D').mean()` before channel harmonization.
