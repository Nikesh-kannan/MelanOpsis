'use client';

import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Activity, 
  RefreshCw,
  Users,
  ShieldCheck
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';
import { getStats } from '../../lib/api';
import { StatsResponse } from '../../lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard stats');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-blue-700">
            <BarChart3 className="h-4 w-4" />
            <span>Clinical Performance Analytics</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight sm:text-3xl">
            Triage Metrics & Volume
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational statistics tracking referral rates, weekly volume, and average processing latency.
          </p>
        </div>

        <button
          onClick={fetchStats}
          className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin text-cyan-600' : ''}`} />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {isLoading ? (
        <div className="p-16 text-center text-slate-400 space-y-3">
          <RefreshCw className="h-10 w-10 animate-spin mx-auto text-cyan-600" />
          <p className="text-xs font-medium">Computing community health statistics...</p>
        </div>
      ) : error ? (
        <div className="p-8 text-center text-amber-700 bg-amber-50 rounded-2xl border border-amber-200">
          <p className="text-xs font-bold">{error}</p>
        </div>
      ) : stats ? (
        <div className="space-y-8">
          
          {/* Summary KPI Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Card 1: Total Cases */}
            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
              <div>
                <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Lesions Screened</span>
                <span className="text-3xl font-black text-slate-900 tracking-tight">{stats.total_cases}</span>
                <span className="block text-[11px] text-slate-500 mt-0.5">Primary Care Registry</span>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-cyan-50 border border-cyan-100 flex items-center justify-center text-cyan-600">
                <Users className="h-6 w-6" />
              </div>
            </div>

            {/* Card 2: Referral Rate */}
            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
              <div>
                <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Referral Rate %</span>
                <div className="flex items-baseline space-x-1">
                  <span className="text-3xl font-black text-amber-600 tracking-tight">{stats.referral_rate_pct}%</span>
                  <span className="text-xs text-slate-500 font-medium">({stats.referral_cases} cases)</span>
                </div>
                <span className="block text-[11px] text-slate-500 mt-0.5">High-Risk Lesion Flags</span>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
                <AlertTriangle className="h-6 w-6" />
              </div>
            </div>

            {/* Card 3: Cases This Week */}
            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
              <div>
                <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Cases This Week</span>
                <span className="text-3xl font-black text-slate-900 tracking-tight">{stats.cases_this_week}</span>
                <span className="block text-[11px] text-emerald-600 font-semibold mt-0.5 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-0.5 inline" /> Active Field Triage
                </span>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
                <CheckCircle2 className="h-6 w-6" />
              </div>
            </div>

            {/* Card 4: Avg Processing Latency */}
            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-xs flex items-center justify-between">
              <div>
                <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Avg Latency</span>
                <span className="text-3xl font-black text-slate-900 font-mono tracking-tight">{stats.avg_processing_time_ms}<span className="text-sm font-sans text-slate-400">ms</span></span>
                <span className="block text-[11px] text-slate-500 mt-0.5">Edge PyTorch Model Target &lt;2s</span>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
                <Clock className="h-6 w-6" />
              </div>
            </div>

          </div>

          {/* Recharts Case Volume Breakdown */}
          <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Weekly Triage Volume Breakdown</h3>
                <p className="text-xs text-slate-500">Distribution of High-Risk Referrals vs Low-Risk Routine logs over past 7 days</p>
              </div>
              <div className="flex items-center space-x-4 text-xs font-semibold">
                <span className="flex items-center space-x-1">
                  <span className="h-3 w-3 rounded-full bg-amber-500 inline-block" />
                  <span>Referrals</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="h-3 w-3 rounded-full bg-emerald-500 inline-block" />
                  <span>Routine</span>
                </span>
              </div>
            </div>

            <div className="h-80 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.weekly_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '12px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="referrals" name="High-Risk Referrals" fill="#f59e0b" radius={[6, 6, 0, 0]} stackId="a" />
                  <Bar dataKey="routine" name="Low-Risk Routine" fill="#10b981" radius={[6, 6, 0, 0]} stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      ) : null}

    </div>
  );
}
