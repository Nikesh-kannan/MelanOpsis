'use client';

import React, { useEffect, useState } from 'react';
import { Cpu, Eye, Sparkles, CheckCircle, Loader2, ShieldCheck } from 'lucide-react';

interface ScanAnimationProps {
  imageSrc: string;
}

export default function ScanAnimation({ imageSrc }: ScanAnimationProps) {
  const [currentStep, setCurrentStep] = useState<number>(0);

  const steps = [
    { label: 'Applying OpenCV Hair Removal & Artifact Inpainting', icon: Eye },
    { label: 'Enhancing Lesion Contrast via CLAHE Filter', icon: Sparkles },
    { label: 'Running PyTorch EfficientNet-B0 Triage Inference', icon: Cpu },
  ];

  useEffect(() => {
    const timer1 = setTimeout(() => setCurrentStep(1), 500);
    const timer2 = setTimeout(() => setCurrentStep(2), 1100);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  return (
    <div className="w-full max-w-xl mx-auto bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-xl space-y-6">
      
      {/* Scanning Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-2">
          <div className="h-3 w-3 rounded-full bg-cyan-500 animate-ping" />
          <span className="text-sm font-bold text-slate-900">AI Diagnostic Pipeline Active</span>
        </div>
        <span className="text-xs font-mono text-cyan-700 bg-cyan-50 px-2.5 py-1 rounded-full border border-cyan-100">
          Target: &lt; 2.0s
        </span>
      </div>

      {/* Lesion Image Container with Medical Laser Scan Overlay */}
      <div className="relative aspect-4/3 w-full rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 shadow-inner flex items-center justify-center">
        <img
          src={imageSrc}
          alt="Lesion scanning"
          className="w-full h-full object-cover opacity-85 scale-105"
        />

        {/* Bounding Target Overlay */}
        <div className="absolute inset-0 bg-medical-grid pointer-events-none" />
        
        {/* Laser Scanner Line */}
        <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#38bdf8] animate-scan" />

        {/* Center Target Box */}
        <div className="absolute inset-12 border border-cyan-400/50 rounded-xl pointer-events-none flex items-center justify-center">
          <div className="w-full h-full border border-dashed border-cyan-300/30 rounded-lg flex items-center justify-center">
            <span className="text-[10px] text-cyan-300 font-mono tracking-widest bg-slate-900/80 px-2 py-1 rounded border border-cyan-500/30 uppercase">
              Analyzing Cellular Patterns
            </span>
          </div>
        </div>
      </div>

      {/* Step Progress Checklist */}
      <div className="space-y-3 pt-2">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isDone = currentStep > idx;
          const isCurrent = currentStep === idx;

          return (
            <div
              key={idx}
              className={`flex items-center justify-between p-3 rounded-xl border text-xs font-medium transition-all ${
                isDone
                  ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                  : isCurrent
                  ? 'bg-cyan-50 border-cyan-200 text-cyan-900 shadow-xs'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-1.5 rounded-lg ${isDone ? 'bg-emerald-100 text-emerald-700' : isCurrent ? 'bg-cyan-100 text-cyan-700' : 'bg-slate-200 text-slate-400'}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <span>{step.label}</span>
              </div>

              <div>
                {isDone ? (
                  <CheckCircle className="h-4 w-4 text-emerald-600" />
                ) : isCurrent ? (
                  <Loader2 className="h-4 w-4 text-cyan-600 animate-spin" />
                ) : (
                  <span className="h-2 w-2 rounded-full bg-slate-300 inline-block" />
                )}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
