from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Case
from app.db.schemas import StatsResponse

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_cases = db.query(Case).count()
    
    if total_cases == 0:
        return StatsResponse(
            total_cases=0,
            referral_cases=0,
            no_flag_cases=0,
            referral_rate_pct=0.0,
            cases_this_week=0,
            avg_confidence_pct=0.0,
            avg_processing_time_ms=0,
            weekly_trend=[]
        )

    referral_cases = db.query(Case).filter(Case.result == "refer").count()
    no_flag_cases = db.query(Case).filter(Case.result == "no_flag").count()
    
    referral_rate_pct = round((referral_cases / total_cases) * 100, 1)
    
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    cases_this_week = db.query(Case).filter(Case.created_at >= one_week_ago).count()
    
    avg_conf = db.query(func.avg(Case.confidence)).scalar() or 0.0
    avg_time = db.query(func.avg(Case.processing_time_ms)).scalar() or 0
    
    # Generate 7-day trend breakdown
    weekly_trend = []
    for i in range(6, -1, -1):
        day_date = datetime.utcnow().date() - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        day_refer = db.query(Case).filter(
            Case.created_at >= day_start, 
            Case.created_at <= day_end,
            Case.result == "refer"
        ).count()
        
        day_routine = db.query(Case).filter(
            Case.created_at >= day_start, 
            Case.created_at <= day_end,
            Case.result == "no_flag"
        ).count()
        
        weekly_trend.append({
            "day": day_date.strftime("%a %b %d"),
            "referrals": day_refer,
            "routine": day_routine,
            "total": day_refer + day_routine
        })

    return StatsResponse(
        total_cases=total_cases,
        referral_cases=referral_cases,
        no_flag_cases=no_flag_cases,
        referral_rate_pct=referral_rate_pct,
        cases_this_week=cases_this_week,
        avg_confidence_pct=round(float(avg_conf) * 100, 1),
        avg_processing_time_ms=int(avg_time),
        weekly_trend=weekly_trend
    )
