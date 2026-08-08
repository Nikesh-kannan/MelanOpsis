'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, ShieldCheck, ClipboardList, BarChart3, UserCheck, Stethoscope } from 'lucide-react';
import { getHealth } from '../lib/api';

export default function Navbar() {
  const pathname = usePathname();
  const [isOnline, setIsOnline] = useState<boolean>(true);

  useEffect(() => {
    getHealth().then((res) => setIsOnline(res.status === 'healthy')).catch(() => setIsOnline(false));
    const interval = setInterval(() => {
      getHealth().then((res) => setIsOnline(res.status === 'healthy')).catch(() => setIsOnline(false));
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { label: 'Triage Capture', href: '/', icon: Stethoscope },
    { label: 'Case Log', href: '/cases', icon: ClipboardList },
    { label: 'Analytics Dashboard', href: '/dashboard', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo & Clinical Subtitle */}
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-2 group">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
                <Activity className="h-6 w-6 stroke-[2.5]" />
              </div>
              <div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-xl font-bold tracking-tight text-slate-900 font-sans">DermScan</span>
                  <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 uppercase tracking-wider">AI</span>
                </div>
                <p className="text-[11px] font-medium text-slate-500 hidden sm:block">Open Clinical Decision Support Platform</p>
              </div>
            </Link>
          </div>

          {/* Center Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 bg-slate-100/80 p-1.5 rounded-xl border border-slate-200/80">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-white text-blue-700 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right Side: Open Source Software Reputation Badges */}
          <div className="flex items-center space-x-3">
            {/* System Status & Release Version Badge */}
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200/80 text-slate-700 text-xs font-medium">
              <span className={`h-2 w-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              <span className="font-medium">{isOnline ? 'Clinical Engine Online' : 'Connecting...'}</span>
              <span className="text-slate-300">|</span>
              <span className="font-mono text-[11px] text-slate-500 font-semibold">v1.0.0</span>
            </div>

            {/* Reputable Open Source Software Badge */}
            <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-blue-50/80 border border-blue-100 text-blue-900 text-xs font-medium">
              <ShieldCheck className="h-4 w-4 text-blue-600" />
              <span className="font-semibold tracking-tight text-blue-950">Open Source Medical AI</span>
            </div>
          </div>

        </div>

        {/* Mobile Navigation Bar */}
        <div className="flex md:hidden border-t border-slate-100 py-2 justify-around">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center space-y-1 text-xs px-3 py-1 rounded-lg ${
                  isActive ? 'text-cyan-700 font-semibold' : 'text-slate-500'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

      </div>
    </header>
  );
}
