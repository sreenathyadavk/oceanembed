import './globals.css';
import Header from '@/components/layout/Header';
import StatusBar from '@/components/layout/StatusBar';

export const metadata = {
  title: 'OCEANEMBED | Satellite-Driven Subsurface Ocean Intelligence',
  description: 'Reconstruct subsurface ocean temperature from satellite-derived surface observations using deep learning.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex flex-col h-[100vh] w-[100vw] overflow-hidden bg-[#F6F8FB] text-[#0F172A] font-sans antialiased m-0 p-0">
        <Header />
        <main className="flex-grow flex relative min-h-0 w-full overflow-hidden">
          {children}
        </main>
        <StatusBar />
      </body>
    </html>
  );
}
