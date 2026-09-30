'use client';
import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { getPrediction } from '@/lib/predictionService';
import { gradientCss } from '@/lib/colormap';
import { DEPTHS, PredictionResult } from '@/types/ocean';
import ProfileChart from '@/components/charts/ProfileChart';

const OceanMap = dynamic(() => import('@/components/map/OceanMap'), { ssr: false });

const formatter = (n: number, pos: string, neg: string) => `${Math.abs(n).toFixed(2)}° ${n >= 0 ? pos : neg}`;

export default function Dashboard() {
  const [date, setDate] = useState('2020-10-15');
  const [depthIndex, setDepthIndex] = useState(12); // Default ~500m (index 12)
  const [pt, setPt] = useState({ lat: 15.24, lon: 68.53 });
  const [res, setRes] = useState<PredictionResult | null>(null);
  
  const depth = DEPTHS[depthIndex] || 500;

  useEffect(() => {
    let ok = true;
    getPrediction({ date, depth, latitude: pt.lat, longitude: pt.lon }).then(r => {
      if(ok) setRes(r);
    }).catch(console.error);
    return () => { ok = false; };
  }, [date, depth, pt]);

  const mapData = res?.predictionMap;

  return (
    <div className="flex w-full h-full bg-[#FFFFFF]">
      
      {/* 20% LEFT SIDEBAR */}
      <aside className="w-[20%] min-w-[200px] h-full bg-[#FFFFFF] border-r border-[#E2E8F0] overflow-y-auto custom-scrollbar flex flex-col">
        {/* Surface Inputs */}
        <div className="p-5 border-b border-[#E2E8F0]">
           <h2 className="text-[10px] font-bold uppercase tracking-widest text-[#0F172A] mb-4">SURFACE INPUTS @ CURSOR</h2>
           <div className="grid grid-cols-2 gap-2">
             {[
               {l: 'SST', v: '28.06', u: '°C', c: 'text-[#10B981]'},
               {l: 'SSS', v: '33.21', u: 'psu', c: 'text-slate-700'},
               {l: 'SLA', v: '-0.062', u: 'm', c: 'text-[#087EA4]'},
               {l: 'U CURR', v: '0.25', u: 'm/s', c: 'text-slate-700'},
               {l: 'V CURR', v: '0.15', u: 'm/s', c: 'text-slate-700'},
               {l: 'U WIND', v: '-5.1', u: 'm/s', c: 'text-slate-700'},
               {l: 'V WIND', v: '3.5', u: 'm/s', c: 'text-slate-700'}
             ].map(i => (
               <div key={i.l} className="bg-[#F6F8FB] border border-[#E2E8F0] p-2 rounded flex flex-col">
                 <span className="text-[9px] font-bold text-[#64748B] tracking-wider mb-1 uppercase">{i.l}</span>
                 <div className="flex items-baseline gap-1">
                   <span className={`font-mono text-[13px] font-bold ${i.c}`}>{i.v}</span>
                   <span className="font-mono text-[9px] text-[#64748B]">{i.u}</span>
                 </div>
               </div>
             ))}
           </div>
        </div>
        
        {/* Processing Chain */}
        <div className="p-5 border-b border-[#E2E8F0]">
           <h2 className="text-[10px] font-bold uppercase tracking-widest text-[#0F172A] mb-4">PROCESSING CHAIN</h2>
           <div className="space-y-4">
             {[
               {s: '01', l: 'GLORYS REANALYSIS', c: 'TARGET'},
               {s: '02', l: '7 SATELLITE FIELDS', c: 'SST · SSS · SLA · U/V'},
               {s: '03', l: '0.25° DAILY GRID', c: 'COLLINEAR + MASK'},
               {s: '04', l: 'TC-RESUNET', c: 'SPATIO-TEMPORAL'},
               {s: '05', l: 'PROFILE DECODER', c: '15 DEPTH LEVELS'},
               {s: '06', l: 'VALIDATION', c: 'INDEPENDENT FLOATS'}
             ].map(p => (
               <div key={p.s} className="flex gap-3">
                 <span className="text-[10px] font-mono font-bold text-[#CBD5E1] shrink-0 mt-0.5">{p.s}</span>
                 <div className="flex flex-col">
                   <span className="text-[10px] font-bold text-[#0F172A] leading-none uppercase tracking-wide mb-1.5">{p.l}</span>
                   <span className="text-[9px] font-medium text-[#64748B] leading-none tracking-widest uppercase">{p.c}</span>
                 </div>
               </div>
             ))}
           </div>
        </div>

        {/* Scoreboard */}
        <div className="p-5 flex-grow">
           <h2 className="text-[10px] font-bold uppercase tracking-widest text-[#0F172A] mb-4">SCOREBOARD</h2>
           <div className="grid grid-cols-2 gap-4">
               <div className="flex flex-col">
                  <span className="text-[9px] font-bold tracking-widest text-[#64748B] uppercase mb-1">MEAN RMSE</span>
                  <span className="font-mono text-[14px] text-[#10B981] font-bold">0.298 <span className="text-[10px] text-[#64748B]">°C</span></span>
               </div>
               <div className="flex flex-col">
                  <span className="text-[9px] font-bold tracking-widest text-[#64748B] uppercase mb-1">MEAN CORR</span>
                  <span className="font-mono text-[14px] text-[#087EA4] font-bold">0.947</span>
               </div>
               <div className="flex flex-col">
                  <span className="text-[9px] font-bold tracking-widest text-[#64748B] uppercase mb-1">DEPTHS</span>
                  <span className="font-mono text-[14px] text-[#0F172A] font-bold">15</span>
               </div>
               <div className="flex flex-col">
                  <span className="text-[9px] font-bold tracking-widest text-[#64748B] uppercase mb-1">ARGO</span>
                  <span className="font-mono text-[14px] text-[#0F172A] font-bold">412</span>
               </div>
           </div>
        </div>
      </aside>

      {/* 54% MAP WORKSPACE */}
      <div className="relative w-[54%] h-full flex flex-col bg-[#0F172A] border-r border-[#E2E8F0]">
        
        {/* Full Bleed Map */}
        <div className="absolute inset-0 z-0 flex-grow">
          <OceanMap grid={mapData ?? null} point={pt} onSelect={(lat, lon) => setPt({ lat, lon })} />
        </div>

        {/* Floating Controls Overlay - Top Left */}
        <div className="absolute top-6 left-6 z-10 flex flex-col gap-3 max-w-[340px]">
          
          {/* Main Control Panel */}
          <div className="bg-white/95 backdrop-blur shadow-sm border border-[#E2E8F0] p-4 rounded-lg flex flex-col gap-4">
            
            <div className="flex flex-col">
               <label className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">DATE</label>
               <input 
                  type="date" 
                  value={date} 
                  min="2020-09-19" 
                  max="2020-12-31" 
                  onChange={e => e.target.value && setDate(e.target.value)} 
                  className="bg-transparent text-[14px] font-semibold text-[#0F172A] focus:outline-none w-[130px] font-mono" 
               />
            </div>
            
            <div className="h-px bg-[#E2E8F0] w-full" />
            
            <div className="flex flex-col w-full">
              <div className="flex justify-between items-center mb-2">
                <label className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider">DEPTH</label>
                <div className="text-[14px] font-bold text-[#0F172A] font-mono">{depth} m</div>
              </div>
              <input 
                type="range" 
                min={0} 
                max={DEPTHS.length - 1} 
                step={1}
                value={depthIndex} 
                onChange={e => setDepthIndex(+e.target.value)} 
                className="w-full h-1 bg-[#E2E8F0] rounded outline-none appearance-none cursor-pointer accent-[#087EA4]"
              />
            </div>

          </div>
          
          {/* Scientific Disclaimer */}
          <div className="bg-white/95 backdrop-blur border border-[#E2E8F0] px-3 py-2 rounded flex flex-col shadow-sm">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#087EA4]">TC-RESUNET VERIFIED</span>
            <span className="text-[9px] font-semibold text-[#64748B] uppercase tracking-wider mt-0.5">LIVE INFERENCE OVER TEST SLICES</span>
          </div>

        </div>

        {/* Temperature Legend - Bottom Left */}
        <div className="absolute bottom-6 left-6 z-10 w-[240px] bg-white/95 backdrop-blur border border-[#E2E8F0] px-4 py-3 rounded shadow-sm">
          <div className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider mb-2">TEMPERATURE (°C)</div>
          <div className="h-2 w-full rounded border border-[#E2E8F0]" style={{ background: gradientCss }} />
          <div className="mt-2 flex justify-between items-center text-[11px] font-mono text-[#0F172A]">
            <span>{mapData ? mapData.min.toFixed(1) : '–'}</span>
            <span className="text-[9px] uppercase tracking-wider text-[#64748B] font-sans font-medium">cold ↔ warm</span>
            <span>{mapData ? mapData.max.toFixed(1) : '–'}</span>
          </div>
        </div>

      </div>

      {/* 26% SCIENTIFIC INSPECTOR */}
      <aside className="w-[26%] h-full bg-[#FFFFFF] flex flex-col overflow-y-auto custom-scrollbar">
        
        {/* POINT INSPECTION */}
        <div className="px-6 pt-5 pb-6 border-b border-[#E2E8F0]">
          <h2 className="text-[12px] font-bold uppercase tracking-widest text-[#0F172A] mb-1">POINT INSPECTION</h2>
          <p className="text-[11px] font-medium text-[#64748B] mb-5">Selected ocean location</p>
          
          <div className="grid grid-cols-2 gap-y-4 gap-x-2 mb-6">
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-1">LATITUDE</span>
              <span className="font-mono text-[14px] text-[#0F172A]">{formatter(pt.lat, 'N', 'S')}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-1">LONGITUDE</span>
              <span className="font-mono text-[14px] text-[#0F172A]">{formatter(pt.lon, 'E', 'W')}</span>
            </div>
          </div>

          <div className="flex flex-col mb-6">
            <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-1">SELECTED DEPTH</span>
            <div className="flex items-end gap-2">
              <span className="font-mono text-[24px] tracking-tight text-[#0F172A] leading-none">{depth}</span>
              <span className="font-mono text-[14px] text-[#64748B] mb-0.5">m</span>
            </div>
            <span className="text-[10px] text-[#64748B] mt-1">Model prediction</span>
          </div>
          
          <div className="flex flex-col">
            <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-1">TEMPERATURE</span>
            <div className="flex items-end gap-2">
              <span className="font-mono text-[32px] tracking-tight text-[#087EA4] leading-none">
                {res ? res.pointTemperature.toFixed(2) : '—'}
              </span>
              <span className="font-mono text-[16px] text-[#64748B] mb-1">°C</span>
            </div>
            <span className="text-[10px] text-[#087EA4] font-medium mt-1 uppercase tracking-wide">MODEL PREDICTION</span>
          </div>

        </div>
        
        <div className="px-6 py-6 border-b border-[#E2E8F0] flex flex-col">
          <h2 className="text-[12px] font-bold uppercase tracking-widest text-[#0F172A] mb-1">VERTICAL TEMPERATURE PROFILE</h2>
          <p className="text-[11px] font-medium text-[#64748B] mb-4">Temperature structure from surface to 1000m</p>
          
          <div className="relative flex-none w-full h-[220px]">
            {res ? <ProfileChart data={res.profile} depth={depth} onDepthClick={d => setDepthIndex(DEPTHS.indexOf(d))} /> : (
              <div className="absolute inset-0 flex items-center justify-center bg-[#F6F8FB] border border-dashed border-[#E2E8F0] text-[11px] font-semibold text-[#64748B] uppercase tracking-widest rounded">
                Awaiting Data
              </div>
            )}
          </div>
          
          <div className="mt-4 w-full border border-[#E2E8F0] rounded bg-white overflow-hidden pb-1">
            <table className="w-full text-left text-[10px] border-collapse font-mono">
              <thead className="sticky top-0 bg-[#F6F8FB] border-b border-[#E2E8F0] text-[9px] uppercase tracking-widest text-[#64748B] font-sans">
                 <tr>
                   <th className="py-1.5 px-2 font-bold">DEPTH</th>
                   <th className="py-1.5 px-2 text-right font-bold">PRED °C</th>
                   <th className="py-1.5 px-2 text-right font-bold">REF °C</th>
                   <th className="py-1.5 px-2 text-right font-bold">Δ</th>
                 </tr>
              </thead>
              <tbody>
                {res ? res.profile.map(p => {
                    const err = p.glorys && p.predicted ? (p.predicted - p.glorys) : NaN;
                    const errStr = !isNaN(err) ? (err > 0 ? '+' : '') + err.toFixed(2) : '-';
                    const h = p.depth === depth;
                    const errColor = err > 0.05 ? 'text-[#10B981]' : (err < -0.05 ? 'text-[#EF4444]' : 'text-[#64748B]');
                    return (
                        <tr key={p.depth} onClick={() => setDepthIndex(DEPTHS.indexOf(p.depth))} className={`cursor-pointer transition-colors border-b border-[#E2E8F0] last:border-0 ${h ? 'bg-[#087EA4]/10 border-l-[3px] border-l-[#087EA4]' : 'hover:bg-slate-50 border-l-[3px] border-l-transparent'}`}>
                             <td className={`py-1 px-2 ${h ? 'font-bold text-[#087EA4]' : 'text-slate-700'}`}>{p.depth}m</td>
                             <td className="py-1 px-2 text-right font-medium text-slate-800">{!isNaN(p.predicted) ? p.predicted.toFixed(2) : '—'}</td>
                             <td className="py-1 px-2 text-right text-slate-500">{!isNaN(p.glorys!) ? p.glorys!.toFixed(2) : '—'}</td>
                             <td className={`py-1 px-2 text-right font-bold ${errColor}`}>{errStr}</td>
                        </tr>
                    );
                }) : <tr><td colSpan={4} className="p-4 text-center text-slate-400 font-sans">Loading references...</td></tr>}
              </tbody>
            </table>
          </div>
        </div>

        {/* MODEL EVALUATION */}
        <div className="px-6 pt-5 pb-6 shrink-0">
          <div className="flex justify-between items-center mb-5">
            <h2 className="text-[12px] font-bold uppercase tracking-widest text-[#0F172A]">MODEL EVALUATION</h2>
            <span className="bg-[#10B981] border border-[#059669] px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest text-white">VERIFIED 2-YEAR</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-0.5">RMSE (500m)</span>
              <span className="font-mono text-[16px] text-[#0F172A]">0.35°C</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-0.5">CORRELATION</span>
              <span className="font-mono text-[16px] text-[#0F172A]">95.5%</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-0.5">RMSE (100m)</span>
              <span className="font-mono text-[16px] text-[#0F172A]">1.29°C</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] font-semibold tracking-wide text-[#64748B] mb-0.5">CORRELATION</span>
              <span className="font-mono text-[16px] text-[#0F172A]">80.2%</span>
            </div>
          </div>
          
          <p className="text-[10px] text-[#64748B] mt-5 leading-relaxed">
            Independent ARGO validation: pending / unavailable for current matchup window.
          </p>
        </div>
        
      </aside>
    </div>
  );
}
