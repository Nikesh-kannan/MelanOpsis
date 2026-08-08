from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class SubDiagnosisItem(BaseModel):
    class_code: str
    name: str
    probability: float
    is_malignant: bool

class AnalyzeResponse(BaseModel):
    result: str = Field(..., description="'refer' or 'no_flag'")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    risk_score: float = Field(..., description="Raw probability score for high-risk lesion")
    processing_time_ms: int = Field(..., description="Analysis execution time in milliseconds")
    case_id: str = Field(..., description="UUID identifier for the uploaded case")
    image_url: str = Field(..., description="URL path to access the stored image")
    gradcam_heatmap_url: Optional[str] = Field(None, description="URL to Grad-CAM heatmap visualization")
    sub_diagnoses: Optional[List[SubDiagnosisItem]] = Field(None, description="7-class taxonomy distribution")

class CaseCreate(BaseModel):
    case_id: str
    image_filename: str
    image_url: str
    result: str
    confidence: float
    risk_score: Optional[float] = None
    patient_id: Optional[str] = "Anonymous Patient"
    notes: Optional[str] = ""
    processing_time_ms: int

class CaseResponse(BaseModel):
    case_id: str
    image_filename: str
    image_url: str
    result: str
    confidence: float
    risk_score: Optional[float] = None
    patient_id: Optional[str] = None
    notes: Optional[str] = None
    processing_time_ms: int
    created_at: datetime
    gradcam_heatmap_url: Optional[str] = None
    sub_diagnoses: Optional[List[SubDiagnosisItem]] = None

    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    total: int
    page: int
    limit: int
    cases: List[CaseResponse]

class StatsResponse(BaseModel):
    total_cases: int
    referral_cases: int
    no_flag_cases: int
    referral_rate_pct: float
    cases_this_week: int
    avg_confidence_pct: float
    avg_processing_time_ms: int
    weekly_trend: List[dict]

class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
