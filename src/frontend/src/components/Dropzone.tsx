'use client';

import React, { useState, useRef } from 'react';
import { Upload, Camera, Image as ImageIcon, FileCheck } from 'lucide-react';

interface DropzoneProps {
  onFileSelect: (file: File) => void;
  onOpenCamera: () => void;
}

export default function Dropzone({ onFileSelect, onOpenCamera }: DropzoneProps) {
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        onFileSelect(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      
      {/* Primary Drag & Drop Card */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-3xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-200 bg-white/80 backdrop-blur-xs shadow-xs group ${
          isDragOver
            ? 'border-cyan-500 bg-cyan-50/50 scale-[1.01]'
            : 'border-slate-300 hover:border-cyan-400 hover:bg-slate-50/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/bmp"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Upload Icon & Ripple */}
        <div className="mx-auto w-16 h-16 rounded-2xl bg-cyan-50 border border-cyan-100 flex items-center justify-center text-cyan-600 mb-4 group-hover:scale-110 group-hover:bg-cyan-100/80 transition-transform">
          <Upload className="h-8 w-8 stroke-[2]" />
        </div>

        <h3 className="text-lg font-bold text-slate-900 mb-1">
          Upload Skin Lesion Photo
        </h3>
        <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
          Drag & drop a dermatoscopic or high-resolution close-up photo here, or click to browse files from your device.
        </p>

        {/* Action Buttons inside Dropzone */}
        <div className="flex flex-wrap items-center justify-center gap-3" onClick={(e) => e.stopPropagation()}>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition"
          >
            <ImageIcon className="h-4 w-4" />
            <span>Select File</span>
          </button>

          <span className="text-xs text-slate-400 font-medium">or</span>

          <button
            type="button"
            onClick={onOpenCamera}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-semibold shadow-xs transition"
          >
            <Camera className="h-4 w-4" />
            <span>Capture with Camera</span>
          </button>
        </div>

        <div className="mt-6 flex items-center justify-center space-x-4 text-[11px] text-slate-400 font-medium border-t border-slate-100 pt-4">
          <span className="flex items-center space-x-1">
            <FileCheck className="h-3.5 w-3.5 text-cyan-500" />
            <span>Supported: JPG, PNG, WEBP</span>
          </span>
          <span>•</span>
          <span>Max Size: 15MB</span>
        </div>
      </div>

    </div>
  );
}
