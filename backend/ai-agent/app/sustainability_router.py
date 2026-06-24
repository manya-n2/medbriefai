# app/sustainability_router.py

from fastapi import APIRouter

from app.services.sustainability_service import get_sustainability_metrics
from app.schema.sustainability_schema import SustainabilityResponse

router = APIRouter(
    prefix="/sustainability",
    tags=["Sustainable Healthcare"]
)


@router.get(
    "/metrics",
    response_model=SustainabilityResponse
)
def fetch_metrics():
    return get_sustainability_metrics()