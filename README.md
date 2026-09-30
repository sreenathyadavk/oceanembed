# OceanEmbed (SIH 26066)

Subsurface temperature reconstruction for the North Indian Ocean using surface satellite observations.

We built a custom Temporal-Channel ResUNet (TC-ResUNet) architecture that pulls surface fields (SST, SSS, SLA, Winds, Currents) and reliably reconstructs vertical temperature profiles down to 1000m depth across 15 standard reference levels.

Our main goal was keeping the ML backend rigid natively in PyTorch for the heavy lifting (canonical 0.25deg grids spanning 5-30N, 45-105E), while maintaining an incredibly fast, statically deployable frontend UI (built on Next.js and MapLibre).

### Repo Structure

- `/src`, `/backend`, `/notebooks`, `/scripts`: Our core PyTorch architecture, training loops, and preprocessing pipeline.
- `/frontend`: Next.js frontend application. Fully static SPA deployment configuration.
- `/checkpoints`: Contains the final verified `tc_resunet_best.pt` model weights (~7MB).
- `/data`: *Note*: Due to GitHub's max payload limits (>100MB), all massive training dataset `.nc` slices (GLORYS/Satellite arrays) are strictly git-ignored.

### Running 

**Run the UI Locally (Offline Static)**:
The frontend natively fetches compressed static JSON frames exported directly from our test splits so you don't even need the python server running!
```bash
cd frontend
npm install
npm run build
npx serve out/
```

**Run the Live PyTorch Backend API**:
If you want to perform real-time model inference, drop your own `X_test.nc` and `Y_test.nc` into `data/processed/` and spin up the router:
```bash
source venv/bin/activate
uvicorn backend.main:app --port 8000 --reload
```
