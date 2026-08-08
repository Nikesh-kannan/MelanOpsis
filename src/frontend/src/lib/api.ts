import { AnalyzeResponse, Case, CaseListResponse, StatsResponse, HealthResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function analyzeImage(imageFile: File | Blob): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', imageFile, 'lesion_photo.jpg');

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return res.json();
}

export async function logCase(caseData: {
  case_id: string;
  image_filename: string;
  image_url: string;
  result: 'refer' | 'no_flag';
  confidence: number;
  risk_score?: number;
  patient_id?: string;
  notes?: string;
  processing_time_ms: number;
}): Promise<Case> {
  const res = await fetch(`${API_BASE}/api/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(caseData),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to log case' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return res.json();
}

export async function getCases(params: {
  search?: string;
  result?: string;
  page?: number;
  limit?: number;
}): Promise<CaseListResponse> {
  const query = new URLSearchParams();
  if (params.search) query.append('search', params.search);
  if (params.result) query.append('result', params.result);
  if (params.page) query.append('page', params.page.toString());
  if (params.limit) query.append('limit', params.limit.toString());

  const res = await fetch(`${API_BASE}/api/cases?${query.toString()}`, {
    cache: 'no-store',
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch case list (${res.status})`);
  }

  return res.json();
}

export async function getCaseDetail(caseId: string): Promise<Case> {
  const res = await fetch(`${API_BASE}/api/cases/${caseId}`, {
    cache: 'no-store',
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch case detail (${res.status})`);
  }

  return res.json();
}

export async function getStats(): Promise<StatsResponse> {
  const res = await fetch(`${API_BASE}/api/stats`, {
    cache: 'no-store',
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch stats (${res.status})`);
  }

  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
    if (!res.ok) return { status: 'offline', version: '1.0.0', model_loaded: false };
    return res.json();
  } catch {
    return { status: 'offline', version: '1.0.0', model_loaded: false };
  }
}

export function getFullImageUrl(urlPath: string): string {
  if (!urlPath) return '';
  if (urlPath.startsWith('http://') || urlPath.startsWith('https://') || urlPath.startsWith('data:')) {
    return urlPath;
  }
  return `${API_BASE}${urlPath.startsWith('/') ? '' : '/'}${urlPath}`;
}
