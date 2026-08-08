'use client';

import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  User, 
  FileText, 
  ArrowRight, 
  RotateCcw,
  Info,
  Calendar,
  PhoneCall
} from 'lucide-react';
import { AnalyzeResponse, Case } from '../lib/types';
import { logCase, getFullImageUrl } from '../lib/api';

interface ResultCardProps {
  analysis: AnalyzeResponse;
  originalImageSrc: string;
  onReset: () => void;
  onLoggedSuccess: (loggedCase: Case) => void;
}

export default function ResultCard({ analysis, originalImageSrc, onReset, onLoggedSuccess }: ResultCardProps) {
  const isReferral = analysis.result === 'refer';

  const [patientId, setPatientId] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [isLogging, setIsLogging] = useState<boolean>(false);
  const [logError, setLogError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'original' | 'gradcam'>('original');

  const confidencePct = Math.round(analysis.confidence * 100);

  const handleSaveCase = async () => {
    setIsLogging(true);
    setLogError(null);
    try {
      const logged = await logCase({
        case_id: analysis.case_id,
        image_filename: `${analysis.case_id}.jpg`,
        image_url: analysis.image_url,
        result: analysis.result,
        confidence: analysis.confidence,
        risk_score: analysis.risk_score,
        patient_id: patientId.trim() || `PAT-${Math.floor(1000 + Math.random() * 9000)}`,
        notes: notes.trim(),
        processing_time_ms: analysis.processing_time_ms
      });
      onLoggedSuccess(logged);
    } catch (err: any) {
      setLogError(err.message || 'Failed to log case');
    } finally {
      setIsLogging(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/analyze/pdf?case_id=${analysis.case_id}&patient_id=${encodeURIComponent(patientId.trim() || 'PAT-8842')}`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Failed to generate PDF report from server');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `DermScan_Report_${analysis.case_id.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert(`PDF Export Error: ${err.message}`);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      
      {/* Main Result Card */}
      <div className={`rounded-3xl border shadow-xl overflow-hidden transition-all bg-white ${
        isReferral ? 'border-amber-300 ring-4 ring-amber-500/10' : 'border-emerald-300 ring-4 ring-emerald-500/10'
      }`}>

        {/* Card Header Banner */}
        <div className={`px-6 py-5 border-b flex flex-wrap items-center justify-between gap-4 ${
          isReferral ? 'bg-amber-500/10 border-amber-200' : 'bg-emerald-500/10 border-emerald-200'
        }`}>
          <div className="flex items-center space-x-3">
            <div className={`h-12 w-12 rounded-2xl flex items-center justify-center text-white shadow-md ${
              isReferral ? 'bg-gradient-to-tr from-amber-500 to-orange-600 shadow-amber-500/30' : 'bg-gradient-to-tr from-emerald-500 to-teal-600 shadow-emerald-500/30'
            }`}>
              {isReferral ? <AlertTriangle className="h-7 w-7" /> : <CheckCircle2 className="h-7 w-7" />}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                  isReferral ? 'bg-amber-100 text-amber-900' : 'bg-emerald-100 text-emerald-900'
                }`}>
                  Triage Decision
                </span>
                <span className="text-xs text-slate-500 font-mono flex items-center space-x-1">
                  <Clock className="h-3 w-3 inline" />
                  <span>{analysis.processing_time_ms}ms</span>
                </span>
              </div>
              <h2 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
                {isReferral ? 'REFER FOR REVIEW' : 'NO FLAG RAISED'}
              </h2>
            </div>
          </div>

          {/* Confidence Gauge Pill */}
          <div className="text-right bg-white/90 backdrop-blur-xs px-4 py-2 rounded-2xl border border-slate-200 shadow-xs">
            <span className="block text-[10px] uppercase tracking-wider font-semibold text-slate-500">AI Confidence</span>
            <div className="flex items-baseline space-x-1">
              <span className={`text-2xl font-black ${isReferral ? 'text-amber-600' : 'text-emerald-600'}`}>
                {confidencePct}%
              </span>
              <span className="text-xs text-slate-400 font-medium">score</span>
            </div>
          </div>
        </div>

        {/* Card Body */}
        <div className="p-6 sm:p-8 grid grid-cols-1 md:grid-cols-12 gap-6">
          
          {/* Left Column: Image Preview & Grad-CAM Heatmap Toggle */}
          <div className="md:col-span-5 space-y-3">
            {/* View Mode Toggle Tabs */}
            {analysis.gradcam_heatmap_url && (
              <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-medium">
                <button
                  type="button"
                  onClick={() => setActiveTab('original')}
                  className={`flex-1 py-1 px-2 rounded-lg transition ${
                    activeTab === 'original' ? 'bg-white text-slate-900 shadow-xs font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Original Photo
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('gradcam')}
                  className={`flex-1 py-1 px-2 rounded-lg transition ${
                    activeTab === 'gradcam' ? 'bg-blue-600 text-white shadow-xs font-bold' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Grad-CAM 🔥
                </button>
              </div>
            )}

            <div className="relative aspect-square w-full rounded-2xl overflow-hidden border border-slate-200 shadow-inner bg-slate-900">
              <img
                src={activeTab === 'gradcam' && analysis.gradcam_heatmap_url ? getFullImageUrl(analysis.gradcam_heatmap_url) : originalImageSrc}
                alt="Analyzed Lesion"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-2 left-2 bg-slate-950/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-1 rounded border border-slate-700">
                {activeTab === 'gradcam' ? 'PyTorch Grad-CAM Attention Overlay' : 'Processed with OpenCV CLAHE'}
              </div>
            </div>

            <div className="bg-slate-50 rounded-xl p-3 border border-slate-200 text-xs space-y-1">
              <div className="flex justify-between text-slate-600">
                <span>High-Risk Probability:</span>
                <span className="font-bold text-slate-900">{(analysis.risk_score * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Cutoff Threshold:</span>
                <span className="font-mono text-slate-500">20.0% (Clinical Standard)</span>
              </div>
            </div>

            {/* Export PDF Referral Button */}
            <button
              type="button"
              onClick={handleExportPDF}
              className="w-full inline-flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-sm transition"
            >
              <FileText className="h-4 w-4 text-blue-400" />
              <span>Export PDF Referral Slip</span>
            </button>
          </div>

          {/* Right Column: Clinical Action & 7-Class Subdiagnoses */}
          <div className="md:col-span-7 space-y-5">
            
            {/* Plain-Language Explanation */}
            <div className={`p-4 rounded-2xl border text-sm leading-relaxed ${
              isReferral ? 'bg-amber-50/70 border-amber-200 text-amber-950' : 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
            }`}>
              <h4 className="font-bold mb-1 flex items-center space-x-1.5 text-slate-900">
                <Info className={`h-4 w-4 ${isReferral ? 'text-amber-600' : 'text-emerald-600'}`} />
                <span>Clinical Triage Summary</span>
              </h4>
              {isReferral ? (
                <p>
                  The model detected features consistent with high-risk lesions (e.g. potential melanoma, basal cell carcinoma, or actinic keratosis). <strong>Schedule a specialist referral or tele-dermatology review within 7-14 days.</strong>
                </p>
              ) : (
                <p>
                  No high-risk visual features flagged. The lesion demonstrates features consistent with benign nevi or keratosis. <strong>Log as routine and advise patient to re-check if changes occur.</strong>
                </p>
              )}
            </div>

            {/* 7-Class Taxonomy Probability Breakdown Card */}
            {analysis.sub_diagnoses && analysis.sub_diagnoses.length > 0 && (
              <div className="space-y-2 bg-slate-50 p-3.5 rounded-2xl border border-slate-200">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700 block">7-Class HAM10000 Taxonomy Distribution</span>
                <div className="space-y-1.5 text-xs">
                  {analysis.sub_diagnoses.slice(0, 4).map((sub) => (
                    <div key={sub.class_code} className="space-y-0.5">
                      <div className="flex justify-between items-center text-[11px]">
                        <span className={`font-semibold ${sub.is_malignant ? 'text-amber-900' : 'text-slate-700'}`}>
                          {sub.name} {sub.is_malignant && '⚠️'}
                        </span>
                        <span className="font-mono text-slate-600 font-bold">{(sub.probability * 100).toFixed(1)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${sub.is_malignant ? 'bg-amber-500' : 'bg-blue-600'}`}
                          style={{ width: `${Math.max(sub.probability * 100, 3)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommended Protocol Checklist */}
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Recommended Next Protocol</span>
              <ul className="space-y-2 text-xs">
                {isReferral ? (
                  <>
                    <li className="flex items-start space-x-2 text-slate-700">
                      <PhoneCall className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                      <span>Contact District Tele-Dermatologist / PHC Specialist for case review.</span>
                    </li>
                    <li className="flex items-start space-x-2 text-slate-700">
                      <Calendar className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
                      <span>Provide patient with a follow-up appointment slip for specialist clinic.</span>
                    </li>
                  </>
                ) : (
                  <>
                    <li className="flex items-start space-x-2 text-slate-700">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
                      <span>Document baseline lesion photo in community health records.</span>
                    </li>
                    <li className="flex items-start space-x-2 text-slate-700">
                      <Calendar className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
                      <span>Advise routine follow-up during next monthly health visit.</span>
                    </li>
                  </>
                )}
              </ul>
            </div>

            {/* Patient Log Form */}
            <div className="pt-2 border-t border-slate-100 space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">Log Case to Registry</span>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Patient ID / ABHA ID</label>
                  <div className="relative">
                    <User className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      placeholder="e.g. PAT-9842"
                      value={patientId}
                      onChange={(e) => setPatientId(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 mb-1">Clinical Notes (Optional)</label>
                  <div className="relative">
                    <FileText className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      placeholder="Lesion location, symptoms..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:bg-white focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {logError && (
                <p className="text-xs text-amber-700 bg-amber-50 p-2 rounded-lg border border-amber-200">{logError}</p>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                <button
                  type="button"
                  onClick={onReset}
                  className="inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition"
                >
                  <RotateCcw className="h-4 w-4" />
                  <span>Discard & Retake</span>
                </button>

                <button
                  type="button"
                  onClick={handleSaveCase}
                  disabled={isLogging}
                  className={`inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl text-white text-xs font-bold shadow-md transition transform active:scale-95 disabled:opacity-50 ${
                    isReferral 
                      ? 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 shadow-amber-500/20' 
                      : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/20'
                  }`}
                >
                  <span>{isLogging ? 'Logging Case...' : isReferral ? 'Log Referral & Continue' : 'Log Routine & Continue'}</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>

            </div>

          </div>
        </div>

        {/* Clinical Disclaimer Banner */}
        <div className="bg-slate-900 text-slate-300 px-6 py-3 border-t border-slate-800 text-[11px] flex items-center space-x-2">
          <ShieldAlert className="h-4 w-4 text-blue-400 shrink-0" />
          <p>
            <strong className="text-white">Medical Triage Disclaimer:</strong> DermScan AI is an AI clinical decision support tool designed for triage assistance, not definitive diagnosis. Final clinical management must follow local health guidelines and registered medical officer evaluation.
          </p>
        </div>

      </div>

    </div>
  );
}
