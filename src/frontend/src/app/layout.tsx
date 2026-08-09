import type { Metadata } from 'next';
import './globals.css';
import Navbar from '../components/Navbar';

export const metadata: Metadata = {
  title: 'MelanOpsis AI — Open Source Clinical Lesion Triage Platform',
  description: 'Production-grade open-source AI decision support and dermatoscopic skin lesion triage platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 font-sans antialiased selection:bg-cyan-100 selection:text-cyan-900">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        
        <footer className="border-t border-slate-200 bg-white/80 py-4 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>MelanOpsis AI v1.0.0 — Open Source Clinical Decision Support Platform</span>
            <span>Empowering Global Primary Healthcare & Tele-Dermatology Triage</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
