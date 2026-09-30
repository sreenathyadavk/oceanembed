# OceanEmbed Data Sources & Provenance

This document details all scientific datasets candidate for OceanEmbed Phase 0, their providers, native resolutions, variables, coverage, and provenance requirements.

## Dynamic Overlap Verification
- **Candidate Products:**
  1. **Subsurface Target Temperature (GLORYS12V1):** CMEMS `GLOBAL_MULTIYEAR_PHY_001_030` (`thetao` [°C], daily, 1/12° ~ 0.083°, 0 to 1000m depth across 15 depth levels).
  2. **Sea Surface Temperature (OSTIA / OISST):** CMEMS `SST_GLO_SST_L4_REP_OBSERVATIONS_010_011` or NOAA High-Res OISST v2.1 (`analysed_sst` converted to °C, daily, 0.05° to 0.25°).
  3. **Sea Surface Salinity (MULTIOBS):** CMEMS `MULTIOBS_GLO_PHY_S_SURFACE_MYNRT_015_013` (`sos` [PSU], daily, 0.25°).
  4. **Sea Level Anomaly (AVISO / CMEMS SLA):** CMEMS `SEALEVEL_GLO_PHY_L4_MY_008_047` (`sla` [m], daily, 0.25°).
  5. **Surface Currents (MULTIOBS):** CMEMS `MULTIOBS_GLO_PHY_TSUV_3D_MYNRT_015_012` (`uo`, `vo` [m/s], daily, 0.25°).
  6. **Surface Winds (ERA5):** ECMWF ERA5 Reanalysis / Copernicus CDS (`u10`, `v10` [m/s], daily, 0.25°).

- **Verified Temporal Overlap Status:** `COMMON_OVERLAP = TO_BE_DETERMINED` (Verified dynamically during preprocessing).

## Provenance Enforcement Rules
- **No Silent Fallbacks:** If a dataset or API source is unavailable, an explicit error is produced indicating the dataset name, provider, failure cause, and required credentials.
- **Dataset Version Locking:** Every extracted training sample metadata records the dataset name, provider, version identifier, and extraction timestamp.
