from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.db.models import Case
from app.db.schemas import CaseCreate, CaseResponse, CaseListResponse

router = APIRouter()

@router.post("/cases", response_model=CaseResponse)
def log_or_update_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db)
):
    existing_case = db.query(Case).filter(Case.case_id == case_data.case_id).first()
    if existing_case:
        existing_case.patient_id = case_data.patient_id or existing_case.patient_id
        existing_case.notes = case_data.notes or existing_case.notes
        existing_case.result = case_data.result
        existing_case.confidence = case_data.confidence
        if case_data.risk_score is not None:
            existing_case.risk_score = case_data.risk_score
        db.commit()
        db.refresh(existing_case)
        return existing_case
    else:
        new_case = Case(
            case_id=case_data.case_id,
            image_filename=case_data.image_filename,
            image_url=case_data.image_url,
            result=case_data.result,
            confidence=case_data.confidence,
            risk_score=case_data.risk_score,
            patient_id=case_data.patient_id or "Anonymous Patient",
            notes=case_data.notes or "",
            processing_time_ms=case_data.processing_time_ms
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        return new_case

@router.get("/cases", response_model=CaseListResponse)
def list_cases(
    search: Optional[str] = Query(None, description="Search by Patient ID or Case ID"),
    result: Optional[str] = Query(None, description="Filter by result: 'refer' or 'no_flag'"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Case)
    
    if result:
        query = query.filter(Case.result == result)
        
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Case.patient_id.like(search_pattern)) | 
            (Case.case_id.like(search_pattern)) |
            (Case.notes.like(search_pattern))
        )
        
    total = query.count()
    cases = query.order_by(desc(Case.created_at)).offset((page - 1) * limit).limit(limit).all()
    
    return CaseListResponse(
        total=total,
        page=page,
        limit=limit,
        cases=cases
    )

@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case record not found.")
    return case
