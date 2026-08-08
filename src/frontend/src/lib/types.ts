export interface SubDiagnosisItem {
  class_code: string;
  name: string;
  probability: number;
  is_malignant: boolean;
}

export interface AnalyzeResponse {
  result: 'refer' | 'no_flag';
  confidence: number;
  risk_score: number;
  processing_time_ms: number;
  case_id: string;
  image_url: string;
  gradcam_heatmap_url?: string;
  sub_diagnoses?: SubDiagnosisItem[];
}

export interface Case {
  case_id: string;
  image_filename: string;
  image_url: string;
  result: 'refer' | 'no_flag';
  confidence: number;
  risk_score?: number;
  patient_id?: string;
  notes?: string;
  processing_time_ms: number;
  created_at: string;
  gradcam_heatmap_url?: string;
  sub_diagnoses?: SubDiagnosisItem[];
}

export interface CaseListResponse {
  total: number;
  page: number;
  limit: number;
  cases: Case[];
}

export interface WeeklyTrendItem {
  day: string;
  referrals: number;
  routine: number;
  total: number;
}

export interface StatsResponse {
  total_cases: number;
  referral_cases: number;
  no_flag_cases: number;
  referral_rate_pct: number;
  cases_this_week: number;
  avg_confidence_pct: number;
  avg_processing_time_ms: number;
  weekly_trend: WeeklyTrendItem[];
}

export interface HealthResponse {
  status: string;
  version: string;
  model_loaded: boolean;
}
