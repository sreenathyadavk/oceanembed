import React from 'react';

export default function DataPage() {
  return (
    <div className="flex flex-col items-center justify-start w-full h-full p-10 overflow-y-auto custom-scrollbar">
      <div className="w-full max-w-4xl bg-white p-10 rounded shadow-sm border border-[#E2E8F0] mb-10">
        
        <h1 className="text-2xl font-bold text-[#0F172A] border-b pb-4 mb-8">Data Pipeline Reference</h1>

        <div className="mb-10">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4 border-b pb-2">Geographic Domain</h2>
            <div className="bg-[#F6F8FB] p-5 rounded border border-[#E2E8F0] shadow-sm grid grid-cols-2 gap-4">
               <div><strong className="text-slate-800 text-sm">Basin:</strong> <span className="text-slate-600 text-sm">North Indian Ocean</span></div>
               <div><strong className="text-slate-800 text-sm">Grid:</strong> <span className="text-slate-600 text-sm">0.25° Resolution</span></div>
               <div><strong className="text-slate-800 text-sm">Latitude:</strong> <span className="text-slate-600 text-sm">5°N to 30°N</span></div>
               <div><strong className="text-slate-800 text-sm">Dimensions:</strong> <span className="text-slate-600 text-sm">101 × 241 cells</span></div>
               <div><strong className="text-slate-800 text-sm">Longitude:</strong> <span className="text-slate-600 text-sm">45°E to 105°E</span></div>
            </div>
        </div>

        <div className="mb-10">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4 border-b pb-2">Temporal Coverage</h2>
            <p className="text-sm text-slate-600 mb-4">Total mapping tracks securely from 2019-01-01 through 2020-12-31 natively limiting constraints mathematically securely safely.</p>
            
            <div className="flex w-full h-12 rounded shadow-sm border border-[#E2E8F0] overflow-hidden text-[10px] font-bold tracking-widest uppercase text-white">
               <div className="w-[71%] bg-[#334155] flex items-center justify-center">TRAIN: 2019-01-01 → 2020-05-25</div>
               <div className="w-[15%] bg-[#087EA4] flex items-center justify-center">VALIDATION: 2020-05-26 → 2020-09-12</div>
               <div className="w-[14%] bg-[#10B981] flex items-center justify-center">TEST: 2020-09-13 → 2020-12-31</div>
            </div>
        </div>

        <div className="mb-10">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4 border-b pb-2">Surface Inputs</h2>
            <table className="w-full text-left text-sm border-collapse border border-[#E2E8F0]">
               <thead className="bg-[#F6F8FB] text-[#64748B] text-xs uppercase tracking-wider">
                   <tr>
                       <th className="border-b p-3">Variable</th>
                       <th className="border-b p-3">Role</th>
                       <th className="border-b p-3">Resolution</th>
                   </tr>
               </thead>
               <tbody className="bg-white">
                   {['SST', 'SSS', 'SLA', 'U Current', 'V Current', 'U Wind', 'V Wind'].map(v => (
                       <tr key={v} className="border-b">
                           <td className="p-3 font-semibold text-slate-800">{v}</td>
                           <td className="p-3 text-slate-600">Dynamic Neural Input Feature</td>
                           <td className="p-3 text-slate-600">0.25° Daily</td>
                       </tr>
                   ))}
               </tbody>
            </table>
        </div>

        <div className="mb-10">
           <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4 border-b pb-2">Target & Validation</h2>
           <div className="bg-[#F6F8FB] p-6 rounded shadow-sm border border-[#E2E8F0] space-y-4">
              <div>
                <strong className="text-slate-800 text-sm">Target Reconstruction Map:</strong> 
                <p className="text-sm text-slate-600 mt-1">GLORYS12V1 thetao distributed across 15 standard reference targets. Reference/training target — not direct observation.</p>
              </div>
              <div className="mt-4 pt-4 border-t border-[#E2E8F0]">
                <strong className="text-slate-800 text-sm">ARGO Validation:</strong> 
                <p className="text-sm text-slate-500 mt-1 italic font-semibold">Independent ARGO validation: pending / unavailable for current matchup window.</p>
              </div>
           </div>
        </div>
        
        <div>
           <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider mb-4 border-b pb-2">Data Pipeline</h2>
           <div className="flex items-center flex-wrap gap-2 text-xs font-mono font-bold text-[#087EA4] uppercase">
               <span className="bg-[#087EA4]/10 p-2 rounded border border-[#087EA4]/30">Raw observations</span> →
               <span className="bg-[#087EA4]/10 p-2 rounded border border-[#087EA4]/30">Harmonization</span> →
               <span className="bg-[#087EA4]/10 p-2 rounded border border-[#087EA4]/30">0.25° grid</span> →
               <span className="bg-[#087EA4]/10 p-2 rounded border border-[#087EA4]/30">7-day temporal stack</span> →
               <span className="bg-[#087EA4]/10 p-2 rounded border border-[#087EA4]/30">49 channels</span> →
               <span className="bg-[#087EA4]/10 p-2 rounded border border-[#087EA4]/30">TC-ResUNet</span> →
               <span className="bg-[#10B981]/10 p-2 rounded border border-[#10B981]/30 text-[#059669]">15-depth output</span>
           </div>
        </div>

      </div>
    </div>
  );
}
