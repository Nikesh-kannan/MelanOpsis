from fastapi import APIRouter
from app.config import VERSION
from app.db.schemas import HealthResponse
from app.models.inference import inference_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health():
    return HealthResponse(
        status="healthy",
        version=VERSION,
        model_loaded=inference_service.is_loaded
    )
