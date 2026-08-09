'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Stethoscope, ShieldCheck, CheckCircle2, ArrowRight, RefreshCw, AlertCircle, HeartPulse } from 'lucide-react';
import Dropzone from '../components/Dropzone';
import CameraCapture from '../components/CameraCapture';
import ScanAnimation from '../components/ScanAnimation';
import ResultCard from '../components/ResultCard';
import { analyzeImage } from '../lib/api';
import { AnalyzeResponse, Case } from '../lib/types';

export default function CapturePage() {
  const router = useRouter();

  const [mode, setMode] = useState<'idle' | 'camera' | 'analyzing' | 'result' | 'success'>('idle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewSrc, setPreviewSrc] = useState<string>('');
  
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loggedCaseInfo, setLoggedCaseInfo] = useState<Case | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewSrc(objectUrl);
    setErrorMessage(null);
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;

    setMode('analyzing');
    setErrorMessage(null);

    try {
      // Small intentional delay so the scan line visual animation completes one full sweep nicely
      const [res] = await Promise.all([
        analyzeImage(selectedFile),
        new Promise((resolve) => setTimeout(resolve, 1800))
      ]);
      setAnalysisResult(res);
      setMode('result');
    } catch (err: any) {
      console.error('Analysis error:', err);
      setErrorMessage(err.message || 'Failed to communicate with analysis backend server.');
      setMode('idle');
    }
  };

  const handleReset = () => {
    setMode('idle');
    setSelectedFile(null);
    setPreviewSrc('');
    setAnalysisResult(null);
    setErrorMessage(null);
    setLoggedCaseInfo(null);
  };

  const handleLoggedSuccess = (logged: Case) => {
    setLoggedCaseInfo(logged);
    setMode('success');
  };

  return (
    <div className="space-y-8">
      
      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-100/70 border border-blue-200 text-blue-800 text-xs font-semibold">
          <HeartPulse className="h-4 w-4 text-blue-600" />
          <span>Point-of-Care Skin Lesion Triage</span>
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight sm:text-4xl">
          AI Lesion Triage & Referral
        </h1>
        <p className="text-sm text-slate-600 leading-relaxed">
          Capture or upload a lesion photograph for instant automated feature extraction and high-risk referral guidance.
        </p>
      </div>

      {/* Global Error Alert */}
      {errorMessage && (
        <div className="max-w-2xl mx-auto p-4 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 text-sm flex items-start space-x-3 shadow-xs">
          <AlertCircle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong className="block font-bold">Analysis System Alert</strong>
            <span>{errorMessage} Make sure the backend server is running and reachable.</span>
          </div>
        </div>
      )}

      {/* MODE 1: Camera Modal Stream */}
      {mode === 'camera' && (
        <CameraCapture
          onCapture={(file) => {
            handleFileSelect(file);
            setMode('idle');
          }}
          onCancel={() => setMode('idle')}
        />
      )}

      {/* MODE 2: Idle & Image Selected View */}
      {mode === 'idle' && (
        <div className="space-y-6">
          {!selectedFile ? (
            <Dropzone
              onFileSelect={handleFileSelect}
              onOpenCamera={() => setMode('camera')}
            />
          ) : (
            /* Image Preview & Analyze CTA Box */
            <div className="max-w-xl mx-auto bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xl space-y-6 text-center">
              <div className="relative aspect-4/3 w-full rounded-2xl overflow-hidden border border-slate-200 shadow-inner bg-slate-900 mx-auto">
                <img src={previewSrc} alt="Selected lesion" className="w-full h-full object-cover" />
                <div className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur-xs text-white text-xs px-3 py-1 rounded-full border border-slate-700">
                  Ready for Inspection
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition"
                >
                  Change Image
                </button>

                <button
                  type="button"
                  onClick={handleStartAnalysis}
                  className="inline-flex items-center space-x-2 px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition transform active:scale-95"
                >
                  <Stethoscope className="h-5 w-5" />
                  <span>Analyze Lesion Photo</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* MODE 3: Analyzing Scanning Screen */}
      {mode === 'analyzing' && previewSrc && (
        <ScanAnimation imageSrc={previewSrc} />
      )}

      {/* MODE 4: Result Screen */}
      {mode === 'result' && analysisResult && previewSrc && (
        <ResultCard
          analysis={analysisResult}
          originalImageSrc={previewSrc}
          onReset={handleReset}
          onLoggedSuccess={handleLoggedSuccess}
        />
      )}

      {/* MODE 5: Case Successfully Logged Screen */}
      {mode === 'success' && loggedCaseInfo && (
        <div className="max-w-xl mx-auto bg-white rounded-3xl p-8 border border-emerald-200 shadow-xl text-center space-y-6">
          <div className="mx-auto w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-inner">
            <CheckCircle2 className="h-10 w-10" />
          </div>

          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Case Registered</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">Case Record Logged to Registry</h2>
            <p className="text-xs text-slate-500 mt-1">
              Case ID <span className="font-mono font-bold text-slate-800">{loggedCaseInfo.case_id}</span> has been stored with encrypted references in SQLite.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              onClick={handleReset}
              className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-bold shadow-xs transition"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Triage Next Patient</span>
            </button>

            <button
              onClick={() => router.push('/cases')}
              className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold shadow-xs transition"
            >
              <span>View Case Registry</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
