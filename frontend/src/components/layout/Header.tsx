'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Header() {
  const path = usePathname();

  const tabs = [
    { name: 'EXPLORE', href: '/' },
    { name: 'MODEL', href: '/model' },
    { name: 'EVALUATION', href: '/evaluation' },
    { name: 'DATA', href: '/data' },
  ];

  return (
    <header className="h-[68px] shrink-0 w-full bg-[#FFFFFF] border-b border-[#E2E8F0] flex items-center justify-between px-6 z-50">
      
      {/* LEFT: Branding */}
      <div className="flex items-center gap-3">
        {/* Restrained logo mark */}
        <div className="w-8 h-8 shrink-0 rounded flex items-center justify-center bg-[#F6F8FB] border border-[#E2E8F0] text-[#087EA4]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 6c.6 0 1.2-.2 1.8-.6L5.5 4a3.5 3.5 0 0 1 3.5 0l1.7 1.4A4 4 0 0 0 13.3 6h4.4A4 4 0 0 1 20 8M2 12c.6 0 1.2-.2 1.8-.6L5.5 10a3.5 3.5 0 0 1 3.5 0l1.7 1.4a4 4 0 0 0 2.6.6h2.2M2 18c.6 0 1.2-.2 1.8-.6L5.5 16a3.5 3.5 0 0 1 3.5 0l1.7 1.4a4 4 0 0 0 2.6.6h2.2" />
          </svg>
        </div>
        <div className="flex flex-col">
          <Link href="/" className="text-[17px] font-bold tracking-tight text-[#0F172A] leading-tight">OCEANEMBED</Link>
          <span className="text-[10px] uppercase font-semibold tracking-wider text-[#64748B] leading-none mt-1">SATELLITE-DRIVEN SUBSURFACE OCEAN INTELLIGENCE</span>
        </div>
      </div>
      
      {/* CENTER: Navigation */}
      <nav className="flex items-center h-full mx-auto justify-center">
        {tabs.map(t => {
          const act = path === t.href;
          return (
            <Link 
              key={t.name}
              href={t.href} 
              className={`h-full flex items-center px-5 text-[12px] font-semibold tracking-wider uppercase transition-colors relative ${act ? 'text-[#087EA4]' : 'text-[#64748B] hover:text-[#0F172A]'}`}
            >
              {t.name}
              {act && <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#087EA4]" />}
            </Link>
          )
        })}
      </nav>

      {/* RIGHT: Status tags */}
      <div className="flex items-center gap-4">
        <div className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wider">SIH26066</div>
        <div className="w-px h-4 bg-[#E2E8F0]"></div>
        <div className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wider">NEURAL NEXUS</div>
        <div className="w-px h-4 bg-[#E2E8F0]"></div>
        <div className="text-[11px] font-bold text-[#475569] uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#087EA4]"></span>
          DEMO MODE
        </div>
      </div>
      
    </header>
  );
}
