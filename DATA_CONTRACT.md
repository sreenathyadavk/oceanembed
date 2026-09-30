# OceanEmbed Scientific Data Contract

This document explicitly defines the canonical shape, grid coordinate system, variable ordering, unit standards, and missing-data conventions for OceanEmbed.

## 1. Domain & Canonical Grid
- **Region:** North Indian Ocean (5.0°N to 30.0°N, 45.0°E to 105.0°E)
- **Spatial Resolution:** 0.25° × 0.25°
- **Latitude Grid:** `[5.00, 5.25, 5.50, ..., 30.00]` (`H = 101` cells)
- **Longitude Grid:** `[45.00, 45.25, 45.50, ..., 105.00]` (`W = 241` cells)
- **Canonical Tensor Grid Shape:** `[101, 241]`

## 2. Input Tensor (X)
- **Shape:** `[T, 7, 101, 241]` (where $T \in \{3, 7, 14\}$, default $T=7$)
- **Variable Order Index:**
  0. `SST` — Sea Surface Temperature [°C]
  1. `SSS` — Sea Surface Salinity [PSU]
  2. `SLA` — Sea Level Anomaly [m]
  3. `U_current` — Surface Zonal Ocean Current [m/s]
  4. `V_current` — Surface Meridional Ocean Current [m/s]
  5. `U_wind` — Surface 10m Zonal Wind [m/s]
  6. `V_wind` — Surface 10m Meridional Wind [m/s]

## 3. Target Tensor (Y)
- **Shape:** `[15, 101, 241]`
- **Variable:** Subsurface Sea Water Potential Temperature [°C]
- **Depth Levels (15 levels):** `[0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000]` meters.

## 4. Quality & Missing Data Masking
- Land grid cells and invalid sensor observations are strictly represented as `NaN`.
- A boolean validity mask `target_mask` (`[15, 101, 241]`) and `input_mask` (`[T, 7, 101, 241]`) are stored alongside every tensor sample.
