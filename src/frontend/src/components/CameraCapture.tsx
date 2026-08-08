'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Camera, RefreshCw, AlertCircle, CheckCircle2, SwitchCamera, X } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

export default function CameraCapture({ onCapture, onCancel }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [error, setError] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState<boolean>(true);

  const startCamera = async () => {
    setIsInitializing(true);
    setError(null);

    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: any) {
      console.error('Camera error:', err);
      setError('Unable to access device camera. Please allow camera permissions or upload an image file instead.');
    } finally {
      setIsInitializing(false);
    }
  };

  useEffect(() => {
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [facingMode]);

  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `lesion_capture_${Date.now()}.jpg`, { type: 'image/jpeg' });
          if (stream) {
            stream.getTracks().forEach((track) => track.stop());
          }
          onCapture(file);
        }
      }, 'image/jpeg', 0.92);
    }
  };

  const toggleFacingMode = () => {
    setFacingMode((prev) => (prev === 'environment' ? 'user' : 'environment'));
  };

  return (
    <div className="relative w-full max-w-xl mx-auto bg-slate-900 rounded-2xl overflow-hidden shadow-2xl border border-slate-800">
      
      {/* Top Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-950/80 text-white border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Camera className="h-4 w-4 text-cyan-400" />
          <span className="text-sm font-semibold tracking-wide">Live Dermatoscopic Capture</span>
        </div>
        <button
          onClick={onCancel}
          className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title="Close Camera"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Video Stream Area */}
      <div className="relative aspect-4/3 w-full bg-black flex items-center justify-center overflow-hidden">
        {error ? (
          <div className="p-6 text-center text-slate-300 max-w-sm">
            <AlertCircle className="h-10 w-10 text-amber-500 mx-auto mb-3" />
            <p className="text-sm text-slate-200 mb-4">{error}</p>
            <button
              onClick={startCamera}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Retry Camera</span>
            </button>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            <canvas ref={canvasRef} className="hidden" />

            {/* Medical Target Reticle & Auto-Focus Overlay */}
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
              <div className="w-56 h-56 rounded-full border-2 border-emerald-400 border-dashed relative animate-pulse flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <div className="w-5 h-5 border-t-3 border-l-3 border-emerald-400 absolute top-2 left-2" />
                <div className="w-5 h-5 border-t-3 border-r-3 border-emerald-400 absolute top-2 right-2" />
                <div className="w-5 h-5 border-b-3 border-l-3 border-emerald-400 absolute bottom-2 left-2" />
                <div className="w-5 h-5 border-b-3 border-r-3 border-emerald-400 absolute bottom-2 right-2" />
                <div className="text-center space-y-1">
                  <span className="text-[10px] tracking-wider text-emerald-300 font-mono bg-slate-950/80 px-2 py-0.5 rounded uppercase border border-emerald-500/40 block">
                    Target Aligned & In Focus
                  </span>
                  <span className="text-[9px] text-slate-400 block font-sans">
                    Keep mole inside reticle
                  </span>
                </div>
              </div>
            </div>

            {isInitializing && (
              <div className="absolute inset-0 bg-slate-900/90 flex flex-col items-center justify-center text-cyan-400">
                <RefreshCw className="h-8 w-8 animate-spin mb-2" />
                <span className="text-xs font-medium text-slate-300">Initializing Camera Sensor...</span>
              </div>
            )}
          </>
        )}
      </div>

      {/* Controls Bar */}
      <div className="flex items-center justify-between px-6 py-4 bg-slate-950/90 border-t border-slate-800">
        <button
          onClick={toggleFacingMode}
          disabled={!!error}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 text-xs font-medium transition disabled:opacity-50"
        >
          <SwitchCamera className="h-4 w-4" />
          <span className="hidden sm:inline">Flip Camera</span>
        </button>

        <button
          onClick={handleCapture}
          disabled={!!error || isInitializing}
          className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 transition active:scale-95 disabled:opacity-50"
        >
          <Camera className="h-5 w-5" />
          <span>Capture Photo</span>
        </button>

        <button
          onClick={onCancel}
          className="px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
        >
          Cancel
        </button>
      </div>

    </div>
  );
}
