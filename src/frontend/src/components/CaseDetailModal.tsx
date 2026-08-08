'use client';

import React from 'react';
import { X, Calendar, Clock, AlertTriangle, CheckCircle2, User, FileText, Activity } from 'lucide-react';
import { Case } from '../lib/types';
import { getFullImageUrl } from '../lib/api';

interface CaseDetailModalProps {
  selectedCase: Case | null;
  onClose: () => void;
}

export default function CaseDetailModal({ selectedCase, onClose }: CaseDetailModalProps) {
  if (!selectedCase) return null;

  const isReferral = selectedCase.result === 'refer';
  const confidencePct = Math.round(selectedCase.confidence * 100);
  const formattedDate = new Date(selectedCase.created_at).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      
      <div 
        className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`flex items-center justify-between px-6 py-4 border-b ${
          isReferral ? 'bg-amber-50 border-amber-200' : 'bg-emerald-50 border-emerald-200'
        }`}>
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-xl text-white ${isReferral ? 'bg-amber-600' : 'bg-emerald-600'}`}>
              {isReferral ? <AlertTriangle className="h-5 w-5" /> : <CheckCircle2 className="h-5 w-5" />}
            </div>
            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-500">Case ID: {selectedCase.case_id.slice(0, 8)}...</span>
              <h3 className="text-lg font-bold text-slate-900 leading-tight">
                {isReferral ? 'Referral Flagged Case' : 'Routine Case Record'}
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 grid grid-cols-1 sm:grid-cols-12 gap-6">
          
          {/* Image */}
          <div className="sm:col-span-5">
            <div className="aspect-square w-full rounded-2xl overflow-hidden border border-slate-200 bg-slate-900 shadow-inner">
              <img
                src={getFullImageUrl(selectedCase.image_url)}
                alt="Case lesion photo"
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300?text=Lesion+Photo';
                }}
              />
            </div>
          </div>

          {/* Details */}
          <div className="sm:col-span-7 space-y-4">
            
            {/* Status & Confidence Badge */}
            <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-200">
              <div>
                <span className="block text-[10px] uppercase tracking-wider font-semibold text-slate-400">Decision Tag</span>
                <span className={`inline-block mt-0.5 px-2.5 py-0.5 rounded-md text-xs font-extrabold uppercase tracking-wide ${
                  isReferral ? 'bg-amber-100 text-amber-900' : 'bg-emerald-100 text-emerald-900'
                }`}>
                  {isReferral ? 'REFER FOR REVIEW' : 'NO FLAG RAISED'}
                </span>
              </div>

              <div className="text-right">
                <span className="block text-[10px] uppercase tracking-wider font-semibold text-slate-400">Confidence</span>
                <span className={`text-xl font-black ${isReferral ? 'text-amber-600' : 'text-emerald-600'}`}>
                  {confidencePct}%
                </span>
              </div>
            </div>

            {/* Patient & Time Metadata */}
            <div className="space-y-2 text-xs">
              <div className="flex items-center space-x-2 text-slate-700">
                <User className="h-4 w-4 text-cyan-600 shrink-0" />
                <span className="font-semibold text-slate-900">Patient ID:</span>
                <span>{selectedCase.patient_id || 'Anonymous Patient'}</span>
              </div>

              <div className="flex items-center space-x-2 text-slate-700">
                <Calendar className="h-4 w-4 text-cyan-600 shrink-0" />
                <span className="font-semibold text-slate-900">Recorded:</span>
                <span>{formattedDate}</span>
              </div>

              <div className="flex items-center space-x-2 text-slate-700">
                <Clock className="h-4 w-4 text-cyan-600 shrink-0" />
                <span className="font-semibold text-slate-900">Processing Time:</span>
                <span className="font-mono">{selectedCase.processing_time_ms} ms</span>
              </div>
            </div>

            {/* Clinical Notes */}
            <div className="pt-2 border-t border-slate-100">
              <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-900 mb-1">
                <FileText className="h-4 w-4 text-slate-500" />
                <span>Health Worker Notes</span>
              </div>
              <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-200 min-h-[60px]">
                {selectedCase.notes || 'No specific clinical notes entered during triage session.'}
              </p>
            </div>

          </div>

        </div>

        {/* Footer */}
        <div className="flex justify-end px-6 py-3 bg-slate-50 border-t border-slate-200">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold transition"
          >
            Close Detail
          </button>
        </div>

      </div>

    </div>
  );
}
