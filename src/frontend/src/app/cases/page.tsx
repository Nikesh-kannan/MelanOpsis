'use client';

import React, { useEffect, useState } from 'react';
import { Search, Filter, Calendar, AlertTriangle, CheckCircle2, ChevronLeft, ChevronRight, Eye, RefreshCw, ClipboardList, User } from 'lucide-react';
import { getCases, getFullImageUrl } from '../../lib/api';
import { Case } from '../../lib/types';
import CaseDetailModal from '../../components/CaseDetailModal';

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [limit] = useState<number>(10);
  const [search, setSearch] = useState<string>('');
  const [resultFilter, setResultFilter] = useState<string>('');
  
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);

  const fetchCaseHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getCases({
        search: search.trim() || undefined,
        result: resultFilter || undefined,
        page,
        limit,
      });
      setCases(data.cases);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch case history');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCaseHistory();
  }, [page, resultFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCaseHistory();
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-blue-700">
            <ClipboardList className="h-4 w-4" />
            <span>Clinical Case Registry</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight sm:text-3xl">
            Triage Case Logs
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Historical records of skin lesion photos analyzed by community health workers.
          </p>
        </div>

        <button
          onClick={fetchCaseHistory}
          className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin text-cyan-600' : ''}`} />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
        
        {/* Search Form */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search Patient ID, Notes, Case ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-cyan-500 focus:bg-white focus:outline-none"
          />
        </form>

        {/* Filter Dropdown */}
        <div className="flex items-center space-x-2 w-full md:w-auto">
          <Filter className="h-4 w-4 text-slate-400 shrink-0" />
          <span className="text-xs font-semibold text-slate-600 shrink-0">Filter:</span>
          <select
            value={resultFilter}
            onChange={(e) => {
              setResultFilter(e.target.value);
              setPage(1);
            }}
            className="w-full md:w-48 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-800 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
          >
            <option value="">All Triage Results</option>
            <option value="refer">Referral Required</option>
            <option value="no_flag">No Flag Raised (Routine)</option>
          </select>
        </div>

      </div>

      {/* Table / Card List */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <RefreshCw className="h-8 w-8 animate-spin mx-auto text-cyan-600" />
            <p className="text-xs font-medium">Loading case history from database...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-amber-700 bg-amber-50">
            <p className="text-xs font-bold">{error}</p>
          </div>
        ) : cases.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <ClipboardList className="h-10 w-10 text-slate-300 mx-auto" />
            <h3 className="text-sm font-bold text-slate-700">No Case Records Found</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              No skin lesion triage cases match your criteria yet. Analyze a lesion image on the Capture screen to generate your first case record!
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  <th className="py-3.5 px-4">Lesion Photo</th>
                  <th className="py-3.5 px-4">Patient / Case ID</th>
                  <th className="py-3.5 px-4">Triage Decision</th>
                  <th className="py-3.5 px-4">Confidence</th>
                  <th className="py-3.5 px-4">Timestamp</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {cases.map((c) => {
                  const isReferral = c.result === 'refer';
                  const formattedDate = new Date(c.created_at).toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  });

                  return (
                    <tr key={c.case_id} className="hover:bg-slate-50/80 transition group">
                      {/* Photo */}
                      <td className="py-3 px-4">
                        <div className="h-12 w-12 rounded-xl overflow-hidden border border-slate-200 bg-slate-900 shrink-0">
                          <img
                            src={getFullImageUrl(c.image_url)}
                            alt="Case lesion"
                            className="h-full w-full object-cover group-hover:scale-105 transition-transform"
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/100?text=Lesion';
                            }}
                          />
                        </div>
                      </td>

                      {/* Patient / Case ID */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-1.5 font-bold text-slate-900">
                          <User className="h-3.5 w-3.5 text-cyan-600 shrink-0" />
                          <span>{c.patient_id || 'Anonymous'}</span>
                        </div>
                        <span className="block text-[10px] font-mono text-slate-400 truncate max-w-[120px]">
                          ID: {c.case_id.slice(0, 8)}...
                        </span>
                      </td>

                      {/* Triage Decision */}
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-extrabold uppercase tracking-wide ${
                          isReferral ? 'bg-amber-100 text-amber-900 border border-amber-200' : 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                        }`}>
                          {isReferral ? <AlertTriangle className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3" />}
                          <span>{isReferral ? 'REFERRAL' : 'NO FLAG'}</span>
                        </span>
                      </td>

                      {/* Confidence */}
                      <td className="py-3 px-4 font-bold">
                        <span className={isReferral ? 'text-amber-600' : 'text-emerald-600'}>
                          {Math.round(c.confidence * 100)}%
                        </span>
                      </td>

                      {/* Timestamp */}
                      <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                        {formattedDate}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setSelectedCase(c)}
                          className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-cyan-50 hover:bg-cyan-100 text-cyan-800 text-xs font-semibold transition"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          <span>View Detail</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {total > 0 && (
          <div className="flex items-center justify-between px-6 py-4 bg-slate-50 border-t border-slate-200 text-xs text-slate-600">
            <span>
              Showing {((page - 1) * limit) + 1} - {Math.min(page * limit, total)} of {total} total cases
            </span>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="font-bold text-slate-800">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail View Drawer/Modal */}
      <CaseDetailModal
        selectedCase={selectedCase}
        onClose={() => setSelectedCase(null)}
      />

    </div>
  );
}
