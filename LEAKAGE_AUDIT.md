# OceanEmbed Data Leakage Audit & Mitigation Protocol

To ensure rigorous scientific validity, OceanEmbed enforces strict leakage mitigation rules across all data preparation and modeling steps.

## 1. Temporal Leakage
- **Threat:** Shuffling daily samples across time causes future ocean states to leak into training datasets.
- **Safeguard:** Strict chronological splitting ONLY (e.g., Train: 2010–2017, Validation: 2018–2019, Test: 2020–2021). No random day/grid cell splits permitted.

## 2. Temporal Window Leakage
- **Threat:** A trailing temporal input window $[t-T+1, \dots, t]$ at the start of validation/test set accesses dates from the training set.
- **Safeguard:** Enforce a margin of $T$ buffer days completely excluded at fold boundaries.

## 3. Normalization Leakage
- **Threat:** Computing mean/std scaling across train + validation + test leaks global statistics into evaluation sets.
- **Safeguard:** Normalization statistics (mean, std, min, max) are fitted strictly on the **Training set only**. Validation/test sets use fitted training statistics.

## 4. GLORYS Reanalysis Assimilation Leakage
- **Threat:** GLORYS12V1 assimilates satellite SST (OSTIA) and SLA (AVISO) observations.
- **Safeguard:** Explicit track distinction:
  - **Track A (Diagnostic):** GLORYS surface -> GLORYS subsurface.
  - **Track B (Primary Model):** Independent satellite surface -> GLORYS subsurface.
  - **Track C (Observational Validation):** Independent satellite surface -> OceanEmbed prediction -> ARGO profiles.

## 5. Duplicate Observation & Interpolation Leakage
- **Safeguard:** Regridding interpolators use backward-looking or instantaneous spatial methods, never temporal future-looking interpolation.
