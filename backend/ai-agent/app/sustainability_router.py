# app/sustainability_router.py

from fastapi import APIRouter

from app.services.sustainability_service import (
    get_sustainability_metrics
)

from app.schema.sustainability_schema import (
    SustainabilityRequest,
    SustainabilityResponse
)

from app.tools import extract_entities as extract_tool
from app.tools import check_interactions as interaction_tool


router = APIRouter(
    prefix="/sustainability",
    tags=["Sustainable Healthcare"]
)


@router.post(
    "/metrics",
    response_model=SustainabilityResponse
)
def fetch_metrics(
        request: SustainabilityRequest
):

    extracted = extract_tool.run(
        request.clinical_note
    )

    medications = extracted.get(
        "medications",
        []
    )

    interactions = (
        interaction_tool.run(medications)
        if len(medications) >= 2
        else {
            "details": [],
            "interactions_found": False
        }
    )

    interaction_count = len(
        interactions.get(
            "details",
            []
        )
    )

    interactions_found = interactions.get(
        "interactions_found",
        False
    )

    return get_sustainability_metrics(
        request.clinical_note,
        interaction_count,
        interactions_found
    )