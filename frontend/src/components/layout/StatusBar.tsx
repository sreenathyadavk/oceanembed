export default function StatusBar() {
  return (
    <div className="h-[32px] w-full shrink-0 bg-[#F6F8FB] border-t border-[#E2E8F0] flex items-center justify-center px-4">
      <div className="flex items-center gap-3 text-[11px] font-medium text-[#64748B] tracking-wide">
        <span>TC-RESUNET</span>
        <span className="text-[#CBD5E1]">•</span>
        <span>7-DAY TEMPORAL CONTEXT</span>
        <span className="text-[#CBD5E1]">•</span>
        <span>49 INPUT CHANNELS</span>
        <span className="text-[#CBD5E1]">•</span>
        <span>15 DEPTH LEVELS</span>
        <span className="text-[#CBD5E1]">•</span>
        <span>0.25° GRID</span>
        <span className="text-[#CBD5E1]">•</span>
        <span>NORTH INDIAN OCEAN</span>
      </div>
    </div>
  );
}
