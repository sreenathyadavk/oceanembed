import { PredictionRequest, PredictionResult } from '@/types/ocean';

let cache: any = null;
let cachedDate: string = "";

export async function getPrediction(req: PredictionRequest): Promise<PredictionResult> {
  const dDate = new Date(req.date);
  const baseDate = new Date('2020-09-19'); // Test set target start date roughly mapped.
  let dDiff = Math.floor((dDate.getTime() - baseDate.getTime()) / (1000 * 3600 * 24));
  dDiff = Math.max(0, Math.min(103, dDiff)); 

  // Find closest available explicitly extracted prototype test slice natively bridging
  const available = [0, 25, 50, 75, 100];
  const closest = available.reduce((a, b) => Math.abs(b - dDiff) < Math.abs(a - dDiff) ? b : a);

  if (cachedDate !== req.date || !cache) {
    const res = await fetch(`/data/oceanembed/predict_${closest}.json`);
    cache = await res.json();
    cachedDate = req.date;
  }
  
  const depthIdx = cache.depths.indexOf(req.depth) >= 0 ? cache.depths.indexOf(req.depth) : 12;
  const latIdx = Math.max(0, Math.min(100, Math.round((req.latitude - 5) / 0.25)));
  const lonIdx = Math.max(0, Math.min(240, Math.round((req.longitude - 45) / 0.25)));
  
  const depthData = cache.predictions[depthIdx];
  const gridData = [];
  let min = 999, max = -999;
  for (let j = 0; j < 101; j++) {
    for (let i = 0; i < 241; i++) {
        const val = depthData[j][i];
        if (val === -999.0) {
            gridData.push(NaN);
        } else {
            gridData.push(val);
            if (val < min) min = val;
            if (val > max) max = val;
        }
    }
  }
  
  const pointTemperature = depthData[latIdx][lonIdx];
  
  const profile = cache.depths.map((d: number, i: number) => {
      const p = cache.predictions[i][latIdx][lonIdx];
      const g = cache.ground_truth[i][latIdx][lonIdx];
      return { depth: d, predicted: p === -999.0 ? NaN : p, glorys: g === -999.0 ? NaN : g };
  });
  
  return {
    predictionMap: { w: 241, h: 101, data: gridData, min, max },
    pointTemperature: pointTemperature === -999.0 ? NaN : pointTemperature,
    profile,
    metrics: null,
    source: 'model'
  };
}
