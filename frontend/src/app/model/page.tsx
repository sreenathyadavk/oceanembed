import React from 'react';

export default function ModelPage() {
  return (
    <div className="flex flex-col items-center justify-start w-full h-full p-10 overflow-y-auto custom-scrollbar">
      <div className="w-full max-w-4xl bg-white p-10 rounded shadow-sm border border-[#E2E8F0] mb-10">
        
        {/* A. Model Overview */}
        <div className="mb-10 border-b pb-8">
            <h1 className="text-2xl font-bold text-[#0F172A] mb-2">TC-ResUNet</h1>
            <p className="text-[#64748B] font-medium uppercase tracking-widest text-xs mb-6">Temporal-Channel Residual U-Net for subsurface temperature reconstruction.</p>
            <div className="grid grid-cols-3 gap-y-4 gap-x-2 text-sm">
                <div><span className="text-slate-500">Parameters:</span> <strong className="text-slate-800">1,963,407</strong></div>
                <div><span className="text-slate-500">Input channels:</span> <strong className="text-slate-800">49</strong></div>
                <div><span className="text-slate-500">Temporal context:</span> <strong className="text-slate-800">7 days</strong></div>
                <div><span className="text-slate-500">Output depths:</span> <strong className="text-slate-800">15</strong></div>
                <div><span className="text-slate-500">Grid:</span> <strong className="text-slate-800">0.25°</strong></div>
                <div><span className="text-slate-500">Region:</span> <strong className="text-slate-800">North Indian Ocean</strong></div>
            </div>
        </div>

        {/* B. Architecture Diagram */}
        <div className="mb-10 border-b pb-8">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4">Architecture</h2>
            <div className="bg-[#F6F8FB] border border-[#E2E8F0] p-6 rounded flex flex-col items-center gap-2 font-mono text-xs text-[#087EA4] uppercase font-bold tracking-widest">
                <div className="bg-white px-4 py-2 rounded shadow-sm border border-[#E2E8F0]">7 Surface Variables</div>
                <div className="text-slate-400">↓</div>
                <div className="bg-white px-4 py-2 rounded shadow-sm border border-[#E2E8F0]">7-Day Temporal Window</div>
                <div className="text-slate-400">↓</div>
                <div className="bg-white px-4 py-2 rounded shadow-sm border border-[#E2E8F0] border-l-4 border-l-[#087EA4]">49 Input Channels</div>
                <div className="text-slate-400">↓</div>
                <div className="bg-white px-4 py-2 rounded shadow-sm border border-[#E2E8F0]">Encoder</div>
                <div className="text-slate-400">↓</div>
                <div className="bg-white px-4 py-2 rounded shadow-sm border border-[#E2E8F0]">Residual Bottleneck</div>
                <div className="text-slate-400">↓</div>
                <div className="bg-white px-4 py-2 rounded shadow-sm border border-[#E2E8F0]">Decoder</div>
                <div className="text-slate-400">↓</div>
                <div className="bg-[#10B981]/10 px-4 py-2 rounded shadow-sm border border-[#10B981]/30 text-[#059669]">15 Temperature Fields</div>
            </div>
        </div>

        {/* C. Input variables */}
        <div className="mb-10 border-b pb-8">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4">Input variables</h2>
            <ul className="space-y-3">
                {[
                    {n: 'SST', d: 'Sea Surface Temperature directly capturing upper thermal variations.'},
                    {n: 'SSS', d: 'Sea Surface Salinity tracking density-driven mixing indicators.'},
                    {n: 'SLA', d: 'Sea Level Anomaly identifying deep mesoscale eddie activities.'},
                    {n: 'U Current', d: 'Zonal surface current velocity component for advection.'},
                    {n: 'V Current', d: 'Meridional surface current velocity component for advection.'},
                    {n: 'U Wind', d: 'Zonal surface wind stress proxying physical atmospheric forcing.'},
                    {n: 'V Wind', d: 'Meridional surface wind stress proxying physical atmospheric forcing.'}
                ].map(v => (
                    <li key={v.n} className="flex gap-4 items-baseline bg-slate-50 p-2 rounded">
                        <span className="shrink-0 w-24 font-bold text-xs text-[#087EA4] uppercase tracking-wider">{v.n}</span>
                        <span className="text-sm text-slate-600 font-medium">{v.d}</span>
                    </li>
                ))}
            </ul>
        </div>

        {/* D. Output structure */}
        <div className="mb-10 border-b pb-8">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4">Output structure (Depths)</h2>
            <div className="flex flex-wrap gap-2">
                {[0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 300, 500, 700, 1000].map(d => (
                    <span key={d} className="bg-slate-800 text-white font-mono text-[11px] px-2 py-1 rounded shadow-sm border border-slate-900">{d} m</span>
                ))}
            </div>
        </div>

        {/* E. Training configuration */}
        <div className="mb-10 border-b pb-8 grid grid-cols-2 gap-4">
            <div>
                <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4">Training Splits</h2>
                <div className="space-y-1 text-sm text-slate-600">
                    <p><strong className="text-slate-800">Dataset:</strong> 2019-01-01 → 2020-12-31</p>
                    <p><strong className="text-slate-800">Train:</strong> 2019-01-01 → 2020-05-25</p>
                    <p><strong className="text-slate-800">Validation:</strong> 2020-05-26 → 2020-09-12</p>
                    <p><strong className="text-slate-800">Test:</strong> 2020-09-13 → 2020-12-31</p>
                </div>
            </div>
            <div>
                <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4">Hyperparameters</h2>
                <div className="space-y-1 text-sm text-slate-600">
                    <p><strong className="text-slate-800">Optimizer:</strong> AdamW</p>
                    <p><strong className="text-slate-800">Initial LR:</strong> 1e-3</p>
                    <p><strong className="text-slate-800">Batch:</strong> 8</p>
                    <p><strong className="text-slate-800">AMP:</strong> Enabled</p>
                </div>
            </div>
        </div>

        {/* F. Verification */}
        <div>
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4">Model Verification</h2>
            <div className="bg-[#F6F8FB] border border-[#E2E8F0] p-4 rounded text-sm text-slate-700 font-medium">
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Full 2-year training</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Temporal leakage audit</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Dataset overlap</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">NaN/mask audit</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Physical sanity</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Numerical stability</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Input sensitivity</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2 border-b border-white/50"><span className="uppercase tracking-wider text-xs">Regional stress test</span> <span className="bg-[#10B981] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">PASS</span></div>
                <div className="flex justify-between items-center py-2"><span className="uppercase tracking-wider text-xs">Temporal shuffle</span> <span className="bg-[#F59E0B] text-white px-2 rounded-sm text-[10px] font-bold tracking-widest">WARNING</span></div>
            </div>
        </div>

      </div>
    </div>
  );
}
