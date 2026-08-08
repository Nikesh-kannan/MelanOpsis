from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime
import uuid
from app.db.database import Base

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    image_filename = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    result = Column(String, nullable=False)  # "refer" or "no_flag"
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_score = Column(Float, nullable=True)  # Raw high-risk probability
    patient_id = Column(String, nullable=True, default="Anonymous Patient")
    notes = Column(String, nullable=True, default="")
    processing_time_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
